# =========================================================
# Developed by: LastPerson07 × RexBots
# Telegram: @RexBots_Official | @THEUPDATEDGUYS
# =========================================================
import os
import asyncio
import random
import time
import shutil
import aiohttp

import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant,
    InviteHashExpired, UsernameNotOccupied, AuthKeyUnregistered,
    UserDeactivated, UserDeactivatedBan
)
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    Message, CallbackQuery, InputMediaPhoto
)

try:
    from pyrogram.enums import ButtonStyle
    BUTTON_STYLE_SUPPORTED = True
except ImportError:
    BUTTON_STYLE_SUPPORTED = False

# =========================================================
# Premium Emojis
# =========================================================

E_WARN    = "⚠️"
E_INFO    = "ℹ️"
E_CROWN   = "👑"
E_SPARK   = "✨"
E_CHECK   = "✅"
E_BOLT    = "⚡"
E_GEAR    = "⚙️"
E_STAR    = "🌟"
E_STOP    = "🛑"
E_GREEN   = "🟢"
E_RED     = "🔴"
E_LINK    = "🔗"
E_BATCH   = "📦"
E_PENCIL  = "✏️"
E_TIP     = "💡"
E_IMAGE   = "🖼"
E_STATS   = "📊"
E_PAYMENT = "💳"
E_CHANNEL = "📢"
E_DEV     = "👨‍💻"

# =========================================================
# Custom Telegram Emoji IDs
# =========================================================

ICON_INFO      = "5431449001532594346"
ICON_WARN      = "5431376038628171216"
ICON_HELP      = "5431449001532594346"
ICON_DEV       = "5431376038628171216"
ICON_BACK      = "5431376038628171216"
ICON_GEAR      = "5431376038628171216"
ICON_PENCIL    = "5431376038628171216"
ICON_TRASH     = "5431376038628171216"
ICON_REFRESH   = "5431376038628171216"
ICON_PREMIUM   = "5431449001532594346"
ICON_PAYMENT   = "5431449001532594346"
ICON_IMAGE     = "5431376038628171216"
ICON_STATS     = "5431376038628171216"
ICON_CHANNEL   = "5431376038628171216"
ICON_CLOSE     = "5431376038628171216"
ICON_HOME      = "5431449001532594346"
ICON_LIST      = "5431449001532594346"
ICON_DELETE    = "5431376038628171216"
ICON_EDIT      = "5431376038628171216"
ICON_PLAN      = "5431449001532594346"
ICON_WARNING   = "5431376038628171216"

from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
import math
from logger import LOGGER
logger = LOGGER(__name__)

# =========================================================

SUBSCRIPTION   = os.environ.get('SUBSCRIPTION', 'https://l.arzfun.com/oxGhB')
FREE_LIMIT_SIZE  = 2 * 1024 * 1024 * 1024
FREE_LIMIT_DAILY = 10
UPI_ID  = os.environ.get("UPI_ID", "971916880@ybl")
QR_CODE = os.environ.get("QR_CODE", "https://l.arzfun.com/oxGhB")

REACTIONS = [
    "👍", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬",
    "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱",
    "🥴", "😍", "🐳", "❤️‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌",
    "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴",
    "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝",
    "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒",
    "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂️", "🤷‍♀️",
    "😡", "💎", "👑", "🔥", "⚡", "🌟", "✨", "💫", "🪄", "🎯",
    "🥇", "🎖", "🛡", "🚀", "🦄", "🐉", "👾", "🤖", "😎", "🤩",
    "🥳", "💯", "❤️‍🔥", "💘", "💝", "💖", "💗", "💓", "💞", "💕",
    "🏆", "⚜️"
]

dev_text = "👨‍💻 Mind Behind This Bot:\n• @anujedits76\n• @anujedits76"
channels_text = "📢 Official Channels:\n• @anujedits76\n• @anujedits76\n\nStay updated for new features!"

WARNING_TEXT = """<b>⚠️ Important Warning</b>

<blockquote><b>📌 Please Read Before Using:</b>

• This bot saves restricted/private content using your Telegram session.
• Never share your session string with anyone.
• Use at your own risk — misuse may lead to account restrictions.
• Bot is for personal use only, not for mass downloading.
• Developer is not responsible for any account ban or data loss.</blockquote>

<i>By using this bot, you agree to the above terms.</i>
"""


class script(object):

    START_TXT = """<b>👋 Hello {},</b>
<b>🤖 I am <a href=https://t.me/{}>{}</a></b>
<i>Your Professional Restricted Content Saver Bot.</i>
<blockquote><b>🚀 System Status: 🟢 Online</b>
<b>⚡ Performance: 10x High-Speed Processing</b>
<b>🔐 Security: End-to-End Encrypted</b>
<b>📊 Uptime: 99.9% Guaranteed</b></blockquote>
<b>👇 Select an Option Below to Get Started:</b>
"""

    HELP_TXT = """<b>📚 Comprehensive Help & User Guide</b>
<blockquote><b>1️⃣ Public Channels (No Login Required)</b></blockquote>
• Forward or send the post link directly.
• Compatible with any public channel or group.
• <i>Example Link:</i> <code>https://t.me/channel/123</code>
<blockquote><b>2️⃣ Private/Restricted Channels (Login Required)</b></blockquote>
• Use <code>/login</code> to securely connect your Telegram account.
• Send the private link (e.g., <code>t.me/c/123...</code>).
• Bot accesses content using your authenticated session.
<blockquote><b>3️⃣ Batch Downloading Mode</b></blockquote>
• Initiate with <code>/batch</code> for multiple files.
• Follow interactive prompts for seamless processing.
<blockquote><b>🛑 Free User Limitations:</b></blockquote>
• <b>Daily Quota:</b> 10 Files / 24 Hours
• <b>File Size Cap:</b> 2GB Maximum
<blockquote><b>💎 Premium Membership Benefits:</b></blockquote>
• Unlimited Downloads & No Restrictions.
• Priority Support & Advanced Features.
"""

    ABOUT_TXT = """<b>ℹ️ About This Bot</b>
<blockquote><b>╭────[ 🧩 𝐀𝐍𝐔𝐉 ]────⍟</b>
<b>├⍟ 🤖 Bot Name : <a href=http://t.me/save_restricted_content_ak_bot>Save Content</a></b>
<b>├⍟ 👨‍💻 Developer : <a href=https://t.me/anujedits76>𝐀𝐍𝐔𝐉 𝐊𝐔𝐌𝐀𝐑</a></b>
<b>├⍟ 📚 Library : <a href='https://docs.pyrogram.org/'>Pyrogram Async</a></b>
<b>├⍟ 🐍 Language : <a href='https://www.python.org/'>Python 3.11+</a></b>
<b>├⍟ 🗄 Database : <a href='https://www.mongodb.com/'>MongoDB Atlas Cluster</a></b>
<b>├⍟ 📡 Hosting : Dedicated High-Speed VPS</b>
<b>╰───────────────⍟</b></blockquote>
"""

    PREMIUM_TEXT = """<b>💎 Premium Membership Plans</b>
<b>Unlock Unlimited Access & Advanced Features!</b>
<blockquote><b>✨ Key Benefits:</b>
<b>♾️ Unlimited Daily Downloads</b>
<b>📂 Support for 4GB+ File Sizes</b>
<b>⚡ Instant Processing (Zero Delay)</b>
<b>🖼 Customizable Thumbnails</b>
<b>📝 Personalized Captions</b>
<b>🛂 24/7 Priority Support</b></blockquote>
<blockquote><b>💳 Pricing Options:</b></blockquote>
• <b>1 Month Plan:</b> ₹554 / $6 (Billed Monthly)
• <b>3 Month Plan:</b> ₹1660 / $17.98 (Save 20%)
• <b>Lifetime Access:</b> ₹3000 / $32.5 (One-Time Payment)
<blockquote><b>👇 Secure Payment:</b></blockquote>
<b>💸 UPI ID:</b> <code>{}</code>
<b>📸 QR Code:</b> <a href='{}'>Scan to Pay</a>
<i>After Payment: Send Screenshot to Admin for Instant Activation.</i>
"""

    PROGRESS_BAR = """\
<b>⚡ Processing Task...</b>
<blockquote>
<b>Progress: {bar} {percentage:.1f}%</b>
<b>🚀 Speed:</b> <code>{speed}/s</code>
<b>💾 Size:</b> <code>{current} of {total}</code>
<b>⏱ Elapsed:</b> <code>{elapsed}</code>
<b>⏳ ETA:</b> <code>{eta}</code>
</blockquote>
"""

    CAPTION = """<b><a href="https://t.me/anujedits76"></a></b>\n\n<b>⚜️ Powered By : <a href="https://t.me/anujedits76">𝐀𝐍𝐔𝐉 𝐊𝐔𝐌𝐀𝐑</a></b>"""

    LIMIT_REACHED = """<b>🚫 Daily Limit Exceeded</b>
<b>Your 10 free saves for today have been used.</b>
<i>Quota resets automatically after 24 hours from first download.</i>
<blockquote><b>🔓 Upgrade to Premium for Unlimited Access!</b></blockquote>
Remove all restrictions and enjoy seamless downloading.
"""

    SIZE_LIMIT = """<b>⚠️ File Size Exceeded</b>
<b>Free tier limited to 2GB per file.</b>
<blockquote><b>🔓 Upgrade to Premium</b></blockquote>
Download files up to 4GB and beyond with no limits!
"""


# =========================================================
# Safe InlineKeyboardButton builder
# =========================================================

def make_button(text, callback_data=None, url=None, icon_custom_emoji_id=None, style=None):
    kwargs = {"text": text}
    if callback_data:
        kwargs["callback_data"] = callback_data
    if url:
        kwargs["url"] = url
    if icon_custom_emoji_id and BUTTON_STYLE_SUPPORTED:
        kwargs["icon_custom_emoji_id"] = icon_custom_emoji_id
    if style and BUTTON_STYLE_SUPPORTED:
        kwargs["style"] = style
    return InlineKeyboardButton(**kwargs)


# =========================================================
# Helper: Build Start Buttons
# =========================================================

def get_start_buttons():
    return InlineKeyboardMarkup([
        [
            make_button("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="buy_premium", icon_custom_emoji_id=ICON_PREMIUM),
            make_button("🆘 ʜᴇʟᴘ", callback_data="help_btn", icon_custom_emoji_id=ICON_HELP),
        ],
        [
            make_button("⚙️ sᴇᴛᴛɪɴɢs", callback_data="settings_btn", icon_custom_emoji_id=ICON_GEAR),
            make_button("📋 ᴍʏ ᴘʟᴀɴ", callback_data="myplan_btn", icon_custom_emoji_id=ICON_PLAN),
        ],
        [
            make_button("📢 ᴄʜᴀɴɴᴇʟs", callback_data="channels_info", icon_custom_emoji_id=ICON_CHANNEL),
            make_button("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about_btn", icon_custom_emoji_id=ICON_INFO),
        ],
        [
            make_button("⚠️ ᴡᴀʀɴɪɴɢ", callback_data="warning_btn", icon_custom_emoji_id=ICON_WARNING),
        ],
        [
            make_button("👨‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ", callback_data="dev_info", icon_custom_emoji_id=ICON_DEV),
        ]
    ])


# =========================================================
# Utility Functions
# =========================================================

def humanbytes(size):
    if not size:
        return "0B"
    power = 2 ** 10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "") +
        ((str(hours) + "h, ") if hours else "") +
        ((str(minutes) + "m, ") if minutes else "") +
        ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2] if tmp else "0s"


class batch_temp(object):
    IS_BATCH = {}


def get_message_type(msg):
    if getattr(msg, 'document', None): return "Document"
    if getattr(msg, 'video', None):    return "Video"
    if getattr(msg, 'photo', None):    return "Photo"
    if getattr(msg, 'audio', None):    return "Audio"
    if getattr(msg, 'text', None):     return "Text"
    return None


# =========================================================
# Wallhaven Image Fetcher — ANIME + PEOPLE ONLY
# categories=011 → Anime + People (General off)
# =========================================================

WALLHAVEN_API_KEY = "FsXt5pwoerVZrsV3DwhRctls8YzUev9H"

WALLHAVEN_QUERIES = [
    # ── Anime ──────────────────────────────────────────
    "anime+girl+portrait",
    "anime+portrait+face",
    "anime+girl+close+up",
    "anime+beautiful+face",
    "anime+school+girl",
    "anime+school+uniform",
    "anime+sailor+uniform",
    "anime+fantasy+girl",
    "anime+magic+girl",
    "anime+witch+girl",
    "anime+elf+girl",
    "anime+princess",
    "anime+dark+girl",
    "anime+gothic+girl",
    "anime+demon+girl",
    "anime+vampire+girl",
    "anime+girl+sakura",
    "anime+girl+nature",
    "anime+girl+sunset",
    "anime+girl+rain",
    "anime+girl+snow",
    "anime+girl+flowers",
    "anime+girl+forest",
    "anime+girl+summer",
    "anime+girl+winter",
    "anime+girl+spring",
    "anime+girl+autumn",
    "anime+kawaii+girl",
    "anime+cute+girl",
    "anime+chibi+girl",
    "anime+warrior+girl",
    "anime+sword+girl",
    "anime+ninja+girl",
    "anime+knight+girl",
    "anime+cyberpunk+girl",
    "anime+girl+ocean",
    "anime+girl+sky",
    "anime+girl+clouds",
    "anime+mermaid",
    "anime+girl+night",
    "anime+girl+stars",
    "anime+girl+moon",
    "anime+girl+galaxy",
    "anime+pink+hair+girl",
    "anime+blue+hair+girl",
    "anime+white+hair+girl",
    "anime+silver+hair+girl",
    "anime+red+hair+girl",
    "anime+blonde+anime+girl",
    "anime+girl+smile",
    "anime+girl+serious",
    "anime+kimono+girl",
    "anime+yukata+girl",
    "anime+shrine+maiden",
    "anime+japanese+girl",
    "anime+waifu",
    "anime+girl+4k",
    "anime+girl+aesthetic",
    "anime+girl+minimal",
    "anime+cherry+blossom",
    "anime+boy+cool",
    "anime+couple",
    "anime+art",
    # ── People ─────────────────────────────────────────
    "beautiful+girl+portrait",
    "asian+girl+portrait+4k",
    "aesthetic+girl+photography",
    "beautiful+woman+4k",
    "girl+nature+portrait",
    "model+photography+portrait",
    "cute+girl+wallpaper",
    "pretty+girl+face+portrait",
    "girl+sunset+photography",
    "woman+aesthetic+wallpaper",
    "girl+flowers+photography",
    "beautiful+eyes+portrait",
    "girl+rain+photography",
    "woman+forest+portrait",
    "girl+city+night+photography",
]


async def fetch_random_image() -> str:
    fallback = "https://l.arzfun.com/duLNg"

    try:
        query = random.choice(WALLHAVEN_QUERIES)
        page  = random.randint(1, 3)

        # categories=011 → Anime(0=off, 1=anime, 1=people)
        url = (
            f"https://wallhaven.cc/api/v1/search"
            f"?categories=011"
            f"&purity=100"
            f"&q={query}"
            f"&sorting=random"
            f"&page={page}"
            f"&apikey={WALLHAVEN_API_KEY}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                data = await resp.json()
                images = data.get("data", [])

                if not images:
                    url_fallback = (
                        f"https://wallhaven.cc/api/v1/search"
                        f"?categories=011"
                        f"&purity=100"
                        f"&sorting=random"
                        f"&apikey={WALLHAVEN_API_KEY}"
                    )
                    async with session.get(url_fallback, timeout=aiohttp.ClientTimeout(total=10)) as resp2:
                        data2 = await resp2.json()
                        images = data2.get("data", [])

                if not images:
                    return fallback

                chosen    = random.choice(images)
                image_url = chosen.get("path", fallback)

                logger.info(f"Wallhaven | Query: {query} | Page: {page} | Image: {image_url}")
                return image_url

    except Exception as e:
        logger.error(f"Wallhaven fetch failed: {e}")
        return fallback


# =========================================================

async def downstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as f:
                txt = f.read()
            await client.edit_message_text(chat, message.id, txt)
        except Exception:
            pass
        await asyncio.sleep(5)


async def upstatus(client, statusfile, message, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r", encoding='utf-8') as f:
                txt = f.read()
            await client.edit_message_text(chat, message.id, txt)
        except Exception:
            pass
        await asyncio.sleep(5)


_progress_cache: dict = {}
_progress_start_time: dict = {}


def progress(current, total, message, transfer_type):
    user_id = message.from_user.id if message.from_user else None

    if user_id and batch_temp.IS_BATCH.get(user_id) is True:
        raise Exception("Cancelled")

    now = time.time()
    task_id = f"{message.chat.id}_{message.id}_{transfer_type}"

    if task_id not in _progress_start_time:
        _progress_start_time[task_id] = now

    last_time = _progress_cache.get(task_id, 0)

    if (now - last_time) > 5 or current == total:
        try:
            elapsed = now - _progress_start_time[task_id]
            percentage = (current * 100 / total) if total > 0 else 0
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0

            filled = int(percentage / 5)
            bar = '█' * filled + ' ' * (20 - filled)

            status = script.PROGRESS_BAR.format(
                bar=bar,
                percentage=percentage,
                current=humanbytes(current),
                total=humanbytes(total),
                speed=humanbytes(speed),
                elapsed=TimeFormatter(int(elapsed * 1000)),
                eta=TimeFormatter(int(eta * 1000))
            )

            status_file = f"{message.chat.id}_{message.id}_{transfer_type}status.txt"
            with open(status_file, "w", encoding='utf-8') as f:
                f.write(status)

            _progress_cache[task_id] = now

            if current == total:
                _progress_start_time.pop(task_id, None)
                _progress_cache.pop(task_id, None)

        except Exception:
            pass


# =========================================================
# Command Handlers
# =========================================================

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except Exception:
        pass

    photo_url = await fetch_random_image()
    bot = await client.get_me()

    await client.send_photo(
        chat_id=message.chat.id,
        photo=photo_url,
        caption=script.START_TXT.format(
            message.from_user.mention, bot.username, bot.first_name
        ),
        reply_markup=get_start_buttons(),
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [make_button("❌ ᴄʟᴏsᴇ", callback_data="close_btn", icon_custom_emoji_id=ICON_CLOSE)]
    ])
    await client.send_message(
        chat_id=message.chat.id,
        text=script.HELP_TXT,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["plan", "myplan", "premium"]))
async def send_plan(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [make_button("📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ", url="https://t.me/anujedits76", icon_custom_emoji_id=ICON_PAYMENT)],
        [make_button("❌ ᴄʟᴏsᴇ", callback_data="close_btn", icon_custom_emoji_id=ICON_CLOSE)]
    ])
    await client.send_photo(
        chat_id=message.chat.id,
        photo=SUBSCRIPTION,
        caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE),
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply_text("❌ Batch Process Cancelled Successfully.")


# =========================================================
# Settings Panel
# =========================================================

async def settings_panel(client, callback_query):
    user_id = callback_query.from_user.id
    is_premium = await db.check_premium(user_id)
    badge = "💎 Premium Member" if is_premium else "👤 Standard User"

    buttons = InlineKeyboardMarkup([
        [make_button("📜 ᴄᴏᴍᴍᴀɴᴅ ʟɪsᴛ",      callback_data="cmd_list_btn",  icon_custom_emoji_id=ICON_LIST)],
        [make_button("📊 ᴜsᴀɢᴇ sᴛᴀᴛs",         callback_data="user_stats_btn", icon_custom_emoji_id=ICON_STATS)],
        [make_button("🗑 ᴅᴜᴍᴘ ᴄʜᴀᴛ sᴇᴛᴛɪɴɢs", callback_data="dump_chat_btn",  icon_custom_emoji_id=ICON_DELETE)],
        [make_button("🖼 ᴍᴀɴᴀɢᴇ ᴛʜᴜᴍʙɴᴀɪʟ",  callback_data="thumb_btn",      icon_custom_emoji_id=ICON_IMAGE)],
        [make_button("📝 ᴇᴅɪᴛ ᴄᴀᴘᴛɪᴏɴ",       callback_data="caption_btn",    icon_custom_emoji_id=ICON_EDIT)],
        [make_button("⬅️ ʜᴏᴍᴇ",               callback_data="start_btn",      icon_custom_emoji_id=ICON_HOME)]
    ])

    text = (
        f"<b>⚙️ Settings Dashboard</b>\n\n"
        f"<b>Account Status:</b> {badge}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n\n"
        f"<i>Customize and manage your bot preferences below:</i>"
    )

    await callback_query.edit_message_caption(
        caption=text,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )


# =========================================================
# Save Handler
# =========================================================

@Client.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text:
        return

    is_limit_reached = await db.check_limit(message.from_user.id)
    if is_limit_reached:
        btn = InlineKeyboardMarkup([
            [make_button("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="buy_premium", icon_custom_emoji_id=ICON_PREMIUM)]
        ])
        return await message.reply_photo(
            photo=SUBSCRIPTION,
            caption=script.LIMIT_REACHED,
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML
        )

    if batch_temp.IS_BATCH.get(message.from_user.id) is False:
        return await message.reply_text(
            "<b>⚠️ A Task is Currently Processing.</b>\n<i>Please wait or use /cancel to stop.</i>",
            parse_mode=enums.ParseMode.HTML
        )

    datas = message.text.split("/")
    temp = datas[-1].replace("?single", "").split("-")
    try:
        fromID = int(temp[0].strip())
    except (ValueError, IndexError):
        return await message.reply_text("<b>❌ Invalid link format.</b>", parse_mode=enums.ParseMode.HTML)

    try:
        toID = int(temp[1].strip())
    except (ValueError, IndexError):
        toID = fromID

    is_private_link = "https://t.me/c/" in message.text
    is_batch        = "https://t.me/b/" in message.text
    is_public_link  = not is_private_link and not is_batch

    batch_temp.IS_BATCH[message.from_user.id] = False

    acc = None

    try:
        for msgid in range(fromID, toID + 1):

            if batch_temp.IS_BATCH.get(message.from_user.id) is True:
                break

            if is_public_link:
                username = datas[3]
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=username,
                        message_id=msgid,
                        reply_to_message_id=message.id
                    )
                    await db.add_traffic(message.from_user.id)
                    await asyncio.sleep(1)
                    continue
                except Exception as e:
                    logger.warning(f"copy_message failed for {username}/{msgid}: {e}")

            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply(
                    "<b>🔒 Authentication Required</b>\n\n"
                    "<i>Access to this content requires login.</i>\n"
                    "<i>Use /login to securely authorize your account.</i>",
                    parse_mode=enums.ParseMode.HTML
                )
                break

            if acc is None:
                try:
                    acc = Client(
                        "saverestricted",
                        session_string=user_data,
                        api_hash=API_HASH,
                        api_id=API_ID,
                        in_memory=True,
                        max_concurrent_transmissions=10
                    )
                    await acc.connect()
                except Exception as e:
                    await message.reply(
                        f"<b>❌ Authentication Failed</b>\n\n"
                        f"<i>Session expired. Please /logout and /login again.</i>\n"
                        f"<code>{e}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    break

            if is_private_link:
                chat_target = int("-100" + datas[4])
            else:
                chat_target = datas[4] if is_batch else datas[3]

            await handle_restricted_content(client, acc, message, chat_target, msgid)
            await asyncio.sleep(2)

    finally:
        if acc is not None:
            try:
                await acc.disconnect()
            except Exception:
                pass
        batch_temp.IS_BATCH[message.from_user.id] = True


# =========================================================
# Restricted Content Handler
# =========================================================

async def handle_restricted_content(client: Client, acc, message: Message, chat_target, msgid):
    try:
        msg: Message = await acc.get_messages(chat_target, msgid)
    except Exception as e:
        logger.error(f"Error fetching message {msgid} from {chat_target}: {e}")
        return

    if not msg or msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    file_size = 0
    if msg_type == "Document" and msg.document:
        file_size = msg.document.file_size or 0
    elif msg_type == "Video" and msg.video:
        file_size = msg.video.file_size or 0
    elif msg_type == "Audio" and msg.audio:
        file_size = msg.audio.file_size or 0

    is_premium_user = await db.check_premium(message.from_user.id)

    if file_size > FREE_LIMIT_SIZE and not is_premium_user:
        btn = InlineKeyboardMarkup([
            [make_button("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="buy_premium", icon_custom_emoji_id=ICON_PREMIUM)]
        ])
        await client.send_message(
            message.chat.id, script.SIZE_LIMIT,
            reply_markup=btn,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if msg_type == "Text":
        try:
            await client.send_message(
                message.chat.id,
                msg.text,
                entities=msg.entities,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send text message: {e}")
        return

    await db.add_traffic(message.from_user.id)
    smsg = await client.send_message(
        message.chat.id,
        '<b>⬇️ Starting Download...</b>',
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )

    temp_dir = f"downloads/{message.chat.id}_{message.id}"
    os.makedirs(temp_dir, exist_ok=True)

    down_status_file = f"{message.chat.id}_{message.id}_downstatus.txt"
    up_status_file   = f"{message.chat.id}_{message.id}_upstatus.txt"

    down_task = None
    up_task   = None

    try:
        down_task = asyncio.create_task(
            downstatus(client, down_status_file, smsg, message.chat.id)
        )

        file = await acc.download_media(
            msg,
            file_name=f"{temp_dir}/",
            progress=progress,
            progress_args=(message, "down")
        )

        if os.path.exists(down_status_file):
            os.remove(down_status_file)

        down_task.cancel()
        try:
            await down_task
        except asyncio.CancelledError:
            pass

    except Exception as e:
        if os.path.exists(down_status_file):
            os.remove(down_status_file)
        if down_task and not down_task.done():
            down_task.cancel()
            try:
                await down_task
            except asyncio.CancelledError:
                pass
        if "Cancelled" in str(e):
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            await smsg.edit("❌ **Task Cancelled**")
            return
        logger.error(f"Download failed for msg {msgid}: {e}")
        await smsg.delete()
        return

    try:
        up_task = asyncio.create_task(
            upstatus(client, up_status_file, smsg, message.chat.id)
        )

        ph_path = None
        thumb_id = await db.get_thumbnail(message.from_user.id)

        if thumb_id:
            try:
                ph_path = await client.download_media(
                    thumb_id,
                    file_name=f"{temp_dir}/custom_thumb.jpg"
                )
            except Exception as e:
                logger.error(f"Custom thumb download failed: {e}")

        if not ph_path:
            try:
                if msg_type == "Video" and msg.video and msg.video.thumbs:
                    ph_path = await acc.download_media(
                        msg.video.thumbs[0].file_id,
                        file_name=f"{temp_dir}/thumb.jpg"
                    )
                elif msg_type == "Document" and msg.document and msg.document.thumbs:
                    ph_path = await acc.download_media(
                        msg.document.thumbs[0].file_id,
                        file_name=f"{temp_dir}/thumb.jpg"
                    )
            except Exception:
                pass

        custom_caption = await db.get_caption(message.from_user.id)
        if custom_caption:
            filename = file.split("/")[-1] if file else "file"
            final_caption = custom_caption.format(
                filename=filename,
                size=humanbytes(file_size)
            )
        else:
            final_caption = script.CAPTION
            if msg.caption:
                final_caption += f"\n\n{msg.caption}"

        if msg_type == "Document":
            await client.send_document(
                message.chat.id, file,
                thumb=ph_path,
                caption=final_caption,
                progress=progress,
                progress_args=(message, "up")
            )
        elif msg_type == "Video":
            await client.send_video(
                message.chat.id, file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=ph_path,
                caption=final_caption,
                progress=progress,
                progress_args=(message, "up")
            )
        elif msg_type == "Audio":
            await client.send_audio(
                message.chat.id, file,
                thumb=ph_path,
                caption=final_caption,
                progress=progress,
                progress_args=(message, "up")
            )
        elif msg_type == "Photo":
            await client.send_photo(
                message.chat.id, file,
                caption=final_caption
            )

    except Exception as e:
        logger.error(f"Upload failed for msg {msgid}: {e}")
        await smsg.edit(f"<b>❌ Upload Failed:</b> <code>{e}</code>", parse_mode=enums.ParseMode.HTML)

    finally:
        for f_path in [up_status_file, down_status_file]:
            if os.path.exists(f_path):
                try:
                    os.remove(f_path)
                except Exception:
                    pass
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
        if up_task and not up_task.done():
            up_task.cancel()
            try:
                await up_task
            except (asyncio.CancelledError, Exception):
                pass
        try:
            await client.delete_messages(message.chat.id, [smsg.id])
        except Exception:
            pass

        task_key_down = f"{message.chat.id}_{message.id}_down"
        task_key_up   = f"{message.chat.id}_{message.id}_up"
        _progress_cache.pop(task_key_down, None)
        _progress_cache.pop(task_key_up, None)
        _progress_start_time.pop(task_key_down, None)
        _progress_start_time.pop(task_key_up, None)


# =========================================================
# Callback Query Handler
# =========================================================

@Client.on_callback_query()
async def button_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    message = callback_query.message
    if not message:
        return

    if data == "dev_info":
        await callback_query.answer(text=dev_text, show_alert=True)
        return

    elif data == "channels_info":
        await callback_query.answer(text=channels_text, show_alert=True)
        return

    elif data == "warning_btn":
        buttons = InlineKeyboardMarkup([
            [make_button("⬅️ ʙᴀᴄᴋ", callback_data="start_btn", icon_custom_emoji_id=ICON_HOME)]
        ])
        await callback_query.edit_message_caption(
            caption=WARNING_TEXT,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "settings_btn":
        await settings_panel(client, callback_query)

    elif data == "myplan_btn":
        buttons = InlineKeyboardMarkup([
            [make_button("📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ", url="https://t.me/anujedits76", icon_custom_emoji_id=ICON_PAYMENT)],
            [make_button("⬅️ ʙᴀᴄᴋ", callback_data="start_btn", icon_custom_emoji_id=ICON_HOME)]
        ])
        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=SUBSCRIPTION,
                caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE)
            ),
            reply_markup=buttons
        )

    elif data == "buy_premium":
        buttons = InlineKeyboardMarkup([
            [make_button("📸 sᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ᴘʀᴏᴏғ", url="https://t.me/anujedits76", icon_custom_emoji_id=ICON_PAYMENT)],
            [make_button("⬅️ ʙᴀᴄᴋ", callback_data="start_btn", icon_custom_emoji_id=ICON_HOME)]
        ])
        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=SUBSCRIPTION,
                caption=script.PREMIUM_TEXT.format(UPI_ID, QR_CODE)
            ),
            reply_markup=buttons
        )

    elif data == "help_btn":
        buttons = InlineKeyboardMarkup([
            [make_button("⬅️ ʙᴀᴄᴋ", callback_data="start_btn", icon_custom_emoji_id=ICON_HOME)]
        ])
        await callback_query.edit_message_caption(
            caption=script.HELP_TXT,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "about_btn":
        buttons = InlineKeyboardMarkup([
            [make_button("⬅️ ʙᴀᴄᴋ", callback_data="start_btn", icon_custom_emoji_id=ICON_HOME)]
        ])
        await callback_query.edit_message_caption(
            caption=script.ABOUT_TXT,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "start_btn":
        bot = await client.get_me()
        photo_url = await fetch_random_image()

        await client.edit_message_media(
            chat_id=message.chat.id,
            message_id=message.id,
            media=InputMediaPhoto(
                media=photo_url,
                caption=script.START_TXT.format(
                    callback_query.from_user.mention,
                    bot.username,
                    bot.first_name
                )
            ),
            reply_markup=get_start_buttons()
        )

    elif data == "close_btn":
        await message.delete()

    elif data in ["cmd_list_btn", "user_stats_btn", "dump_chat_btn", "thumb_btn", "caption_btn"]:
        await callback_query.answer("🚧 Coming Soon!", show_alert=True)
        return

    try:
        await callback_query.answer()
    except Exception:
        pass
