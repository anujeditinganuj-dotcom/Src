"""
FastAPI service for:
1) Listing filenames from a TeraBox account
2) Resolving a TeraBox share URL to a downloadable/streamable video
3) Streaming or downloading that video through REST endpoints

Assumptions:
- The caller already has a valid official TeraBox access_token.
- TeraBox official endpoints are available as documented.
- Share links may optionally require a password.
- For share endpoints, docs/examples reference both terabox.com and terabox.app.
  This implementation tries both safely.
"""

import json
import os
import re
import uuid
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

app = FastAPI(title="TeraBox Video & File API", version="1.0.0")

# In-memory cache for resolved videos.
# For production, replace with Redis or a database.
RESOLVED_VIDEOS: Dict[str, Dict[str, Any]] = {}

SUPPORTED_TERABOX_HOSTS = {
    "www.terabox.com",
    "terabox.com",
    "www.terabox.app",
    "terabox.app",
    "www.teraboxshare.com",
    "teraboxshare.com",
    "www.1024terabox.com",
    "1024terabox.com",
    "www.teraboxlink.com",
    "teraboxlink.com",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".ts"
}

SHARE_BASE_CANDIDATES = [
    "https://www.terabox.com",
    "https://www.terabox.app",
]


class ResolveVideoRequest(BaseModel):
    url: str = Field(..., description="TeraBox share URL")
    access_token: str = Field(..., description="Official TeraBox access token")
    password: Optional[str] = Field(None, description="Optional 4-char extraction code")


def is_valid_terabox_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and parsed.netloc.lower() in SUPPORTED_TERABOX_HOSTS


def extract_surl(url: str) -> str:
    """
    Supports common share URL forms such as:
    - https://www.terabox.com/s/1-ABCDEFG
    - https://www.terabox.app/s/1-ABCDEFG
    - https://www.terabox.com/sharing/link?surl=ABCDEFG
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    if "surl" in qs and qs["surl"]:
        return qs["surl"][0]

    # Match /s/1-<SHORTCODE>
    match = re.search(r"/s/1-([A-Za-z0-9_-]+)", parsed.path)
    if match:
        return match.group(1)

    raise HTTPException(status_code=400, detail="Could not extract TeraBox short code (surl) from URL")


def normalize_base(url_or_host: str) -> str:
    if url_or_host.startswith("http://") or url_or_host.startswith("https://"):
        return url_or_host.rstrip("/")
    return f"https://{url_or_host.strip('/')}"


def is_video_name(filename: str) -> bool:
    lower = filename.lower()
    return any(lower.endswith(ext) for ext in VIDEO_EXTENSIONS)


def parse_boxclnd(set_cookie_header: Optional[str]) -> Optional[str]:
    if not set_cookie_header:
        return None
    match = re.search(r"BOXCLND=([^;]+)", set_cookie_header)
    return match.group(1) if match else None


def extract_items(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    if isinstance(payload.get("list"), list):
        return payload["list"]
    data = payload.get("data")
    if isinstance(data, dict) and isinstance(data.get("list"), list):
        return data["list"]
    return []


def payload_errno(payload: Dict[str, Any]) -> int:
    # Official docs commonly return errno == 0 on success
    value = payload.get("errno")
    return int(value) if isinstance(value, int) else 0


async def terabox_json(
    method: str,
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
) -> Tuple[Dict[str, Any], httpx.Response]:
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.request(method, url, params=params, data=data, headers=headers)
    try:
        payload = response.json()
    except Exception:
        raise HTTPException(
            status_code=502,
            detail=f"TeraBox returned a non-JSON response from {url}"
        )
    return payload, response


async def get_api_domain(access_token: str) -> str:
    payload, _ = await terabox_json(
        "POST",
        "https://www.terabox.com/oauth/tokeninfo",
        data={"access_token": access_token},
    )

    if payload_errno(payload) != 0:
        raise HTTPException(status_code=401, detail={"message": "Invalid or expired access_token", "upstream": payload})

    data = payload.get("data", {})
    api_domain = data.get("api_domain")
    if not api_domain:
        raise HTTPException(status_code=502, detail="tokeninfo succeeded but api_domain was missing")
    return normalize_base(api_domain)


async def list_user_files_page(
    access_token: str,
    dir_path: str,
    page: int,
    page_size: int = 100,
) -> List[Dict[str, Any]]:
    api_base = await get_api_domain(access_token)
    payload, _ = await terabox_json(
        "GET",
        f"{api_base}/openapi/api/list",
        params={
            "access_tokens": access_token,
            "dir": dir_path,
            "num": page_size,
            "page": page,  # documented in example URL
            "order": "name",
            "desc": 0,
        },
    )

    if payload_errno(payload) != 0:
        raise HTTPException(status_code=502, detail={"message": "Failed to list TeraBox files", "upstream": payload})

    return extract_items(payload)


async def list_all_filenames(
    access_token: str,
    dir_path: str = "/",
    recursive: bool = True,
) -> List[str]:
    results: List[str] = []
    page = 1

    while True:
        items = await list_user_files_page(access_token, dir_path, page, page_size=100)
        if not items:
            break

        for item in items:
            name = item.get("server_filename") or item.get("name")
            path = item.get("path")
            is_dir = bool(item.get("isdir"))

            if name:
                results.append(name)

            if recursive and is_dir and path:
                child_names = await list_all_filenames(access_token, path, recursive=True)
                results.extend(child_names)

        if len(items) < 100:
            break
        page += 1

    return results


async def verify_share_and_get_sekey(access_token: str, surl: str, password: Optional[str]) -> Tuple[str, str]:
    """
    Try documented share verification against known TeraBox domains.
    Returns (share_base, sekey).
    """
    last_error: Optional[Dict[str, Any]] = None

    for share_base in SHARE_BASE_CANDIDATES:
        try:
            payload, response = await terabox_json(
                "POST",
                f"{share_base}/openapi/share/verify",
                params={
                    "access_tokens": access_token,
                    "surl": surl,
                },
                data={
                    "pwd": password or ""
                },
            )

            # Even if upstream JSON isn't rich, the important bit is BOXCLND
            sekey = response.cookies.get("BOXCLND") or parse_boxclnd(response.headers.get("set-cookie"))

            if payload_errno(payload) == 0 and sekey:
                return share_base, sekey

            last_error = payload
        except HTTPException as exc:
            last_error = {"message": "verify failed", "detail": exc.detail}
            continue

    raise HTTPException(
        status_code=401,
        detail={
            "message": "Share verification failed. Link may require a valid password or official share access may be unavailable.",
            "upstream": last_error,
        },
    )


async def share_list_page(
    share_base: str,
    access_token: str,
    surl: str,
    sekey: str,
    page: int,
    dir_path: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    params: Dict[str, Any] = {
        "access_tokens": access_token,
        "shorturl": surl,
        "page": page,
        "num": 100,
        "sekey": sekey,
    }

    if dir_path:
        params["root"] = 0
        params["dir"] = dir_path
    else:
        params["root"] = 1

    payload, _ = await terabox_json(
        "GET",
        f"{share_base}/openapi/share/list",
        params=params,
    )

    if payload_errno(payload) != 0:
        raise HTTPException(status_code=502, detail={"message": "Failed to list share contents", "upstream": payload})

    return extract_items(payload), payload


async def collect_share_files_recursive(
    share_base: str,
    access_token: str,
    surl: str,
    sekey: str,
    dir_path: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Returns all files and the first successful payload containing share-level metadata.
    """
    all_items: List[Dict[str, Any]] = []
    share_meta: Dict[str, Any] = {}

    page = 1
    while True:
        items, payload = await share_list_page(
            share_base=share_base,
            access_token=access_token,
            surl=surl,
            sekey=sekey,
            page=page,
            dir_path=dir_path,
        )

        if not share_meta:
            share_meta = payload

        if not items:
            break

        for item in items:
            all_items.append(item)

            if bool(item.get("isdir")) and item.get("path"):
                nested_items, _ = await collect_share_files_recursive(
                    share_base, access_token, surl, sekey, item["path"]
                )
                all_items.extend(nested_items)

        if len(items) < 100:
            break
        page += 1

    return all_items, share_meta


def find_first_video(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for item in items:
        name = item.get("server_filename") or item.get("name") or ""
        is_dir = bool(item.get("isdir"))
        if not is_dir and is_video_name(name):
            return item
    return None


def extract_share_meta(payload: Dict[str, Any], item: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Attempts to extract shareid / uk / fs_id from common keys seen in TeraBox payloads.
    """
    data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
    shareid = payload.get("shareid") or data.get("shareid") or item.get("shareid")
    uk = payload.get("uk") or data.get("uk") or item.get("uk")
    fs_id = item.get("fs_id") or item.get("fid") or item.get("id")
    return shareid, uk, fs_id


async def get_share_download_link(
    share_base: str,
    access_token: str,
    shareid: Any,
    uk: Any,
    sekey: str,
    fs_id: Any,
) -> str:
    payload, _ = await terabox_json(
        "GET",
        f"{share_base}/openapi/share/download",
        params={
            "access_token": access_token,
            "shareid": shareid,
            "fid_list": json.dumps([fs_id]),
            "uk": uk,
            "sekey": sekey,
        },
    )

    if payload_errno(payload) != 0:
        raise HTTPException(status_code=502, detail={"message": "Failed to get share download link", "upstream": payload})

    # Common patterns
    data = payload.get("data", payload)
    if isinstance(data, dict):
        if isinstance(data.get("list"), list) and data["list"]:
            dlink = data["list"][0].get("dlink")
            if dlink:
                return dlink
        if isinstance(payload.get("list"), list) and payload["list"]:
            dlink = payload["list"][0].get("dlink")
            if dlink:
                return dlink

    raise HTTPException(status_code=502, detail={"message": "No dlink returned by share/download", "upstream": payload})


async def proxy_upstream_stream(upstream_url: str, request: Request, as_attachment: bool, filename: str) -> StreamingResponse:
    """
    Streams bytes from the upstream TeraBox direct link to the client.
    Preserves Range requests so browsers/video players can seek.
    """
    headers: Dict[str, str] = {}

    # Forward Range for video seeking
    if range_header := request.headers.get("range"):
        headers["Range"] = range_header

    # Good hygiene; some CDNs behave better with a UA
    headers["User-Agent"] = "Mozilla/5.0 (compatible; TeraBoxVideoAPI/1.0)"

    client = httpx.AsyncClient(timeout=None, follow_redirects=True)
    req = client.build_request("GET", upstream_url, headers=headers)
    upstream = await client.send(req, stream=True)

    response_headers: Dict[str, str] = {}
    for key in ("content-type", "content-length", "accept-ranges", "content-range", "etag", "last-modified"):
        value = upstream.headers.get(key)
        if value:
            response_headers[key] = value

    disposition = "attachment" if as_attachment else "inline"
    response_headers["content-disposition"] = f'{disposition}; filename="{filename}"'

    return StreamingResponse(
        upstream.aiter_bytes(),
        status_code=upstream.status_code,
        headers=response_headers,
        media_type=upstream.headers.get("content-type", "application/octet-stream"),
        background=BackgroundTask(lambda: (upstream.aclose(), client.aclose())),
    )


@app.get("/v1/files")
async def get_filenames(
    access_token: str = Query(..., description="Official TeraBox access token"),
    dir: str = Query("/", description="Directory to list"),
    recursive: bool = Query(True, description="Recursively list nested filenames"),
    format: str = Query("json", pattern="^(json|text)$"),
):
    """
    Lists filenames from a user's TeraBox account.
    Handles pagination automatically.
    Returns only filenames, as requested.
    """
    try:
        filenames = await list_all_filenames(access_token=access_token, dir_path=dir, recursive=recursive)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}")

    if format == "text":
        return PlainTextResponse("\n".join(filenames))

    return JSONResponse(content=filenames)


@app.post("/v1/videos/resolve")
async def resolve_video(req: ResolveVideoRequest):
    """
    Validates a TeraBox share URL, resolves share contents, picks the first video file,
    gets a direct download link via documented official share/download flow,
    and stores a temporary server-side record for playback/download endpoints.
    """
    if not is_valid_terabox_url(req.url):
        raise HTTPException(status_code=400, detail="Invalid TeraBox URL")

    surl = extract_surl(req.url)

    # Verify the share link and capture share-session key
    share_base, sekey = await verify_share_and_get_sekey(
        access_token=req.access_token,
        surl=surl,
        password=req.password,
    )

    # List files in share, recursively
    items, share_meta_payload = await collect_share_files_recursive(
        share_base=share_base,
        access_token=req.access_token,
        surl=surl,
        sekey=sekey,
    )

    if not items:
        raise HTTPException(status_code=404, detail="No files found in the TeraBox share")

    video_item = find_first_video(items)
    if not video_item:
        raise HTTPException(status_code=404, detail="No supported video file found in the TeraBox share")

    shareid, uk, fs_id = extract_share_meta(share_meta_payload, video_item)
    if not all([shareid, uk, fs_id]):
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Could not extract share metadata required for share/download",
                "shareid": shareid,
                "uk": uk,
                "fs_id": fs_id,
            },
        )

    dlink = await get_share_download_link(
        share_base=share_base,
        access_token=req.access_token,
        shareid=shareid,
        uk=uk,
        sekey=sekey,
        fs_id=fs_id,
    )

    asset_id = str(uuid.uuid4())
    filename = video_item.get("server_filename") or video_item.get("name") or "video.mp4"
    RESOLVED_VIDEOS[asset_id] = {
        "asset_id": asset_id,
        "source_url": req.url,
        "share_base": share_base,
        "surl": surl,
        "filename": filename,
        "size": video_item.get("size"),
        "mime_type": "video/mp4",  # fallback; streaming endpoint will honor upstream content-type
        "dlink": dlink,
    }

    return {
        "asset_id": asset_id,
        "filename": filename,
        "size": video_item.get("size"),
        "download_url": f"/v1/videos/{asset_id}/download",
        "stream_url": f"/v1/videos/{asset_id}/stream",
    }


@app.get("/v1/videos/{asset_id}")
async def get_video_info(asset_id: str):
    """
    Returns resolved metadata for a video.
    """
    item = RESOLVED_VIDEOS.get(asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Unknown asset_id")
    return {
        "asset_id": item["asset_id"],
        "filename": item["filename"],
        "size": item["size"],
        "download_url": f"/v1/videos/{asset_id}/download",
        "stream_url": f"/v1/videos/{asset_id}/stream",
    }


@app.get("/v1/videos/{asset_id}/download")
async def download_video(asset_id: str, request: Request):
    """
    Downloads the video as an attachment.
    This streams from the upstream direct link instead of buffering whole files in memory.
    """
    item = RESOLVED_VIDEOS.get(asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Unknown asset_id")

    try:
        return await proxy_upstream_stream(
            upstream_url=item["dlink"],
            request=request,
            as_attachment=True,
            filename=item["filename"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Download failed: {exc}")


@app.get("/v1/videos/{asset_id}/stream")
async def stream_video(asset_id: str, request: Request):
    """
    Streams the video inline with Range support for browser playback.
    """
    item = RESOLVED_VIDEOS.get(asset_id)
    if not item:
        raise HTTPException(status_code=404, detail="Unknown asset_id")

    try:
        return await proxy_upstream_stream(
            upstream_url=item["dlink"],
            request=request,
            as_attachment=False,
            filename=item["filename"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Streaming failed: {exc}")


@app.get("/health")
async def health():
    return {"ok": True}


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status": exc.status_code,
            "detail": exc.detail,
        },
    )
