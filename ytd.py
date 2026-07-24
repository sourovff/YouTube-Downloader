import time
import os
import glob
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
import yt_dlp

TOKEN = "8940748431:AAE1IaAPZceonzmROGJ4Pz8e7WgxslaVeac"

# 🟢 /start Command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    
    welcome_card = (
        f"<b>✨ Welcome, {user_first_name}!</b>\n\n"
        "<b>⚡️ Ultra Fast YouTube & Movie Downloader</b>\n"
        "──────────────────────────────\n"
        "Send any YouTube video, Shorts, or movie link here. "
        "I will fetch high-speed download links and media streams in various qualities!\n\n"
        "<b>📌 Available Commands:</b>\n"
        "🔹 /help — User guide & instructions\n"
        "🔹 /about — System details & specs\n"
        "🔹 /ping — Server response speed\n"
        "🔹 /stats — Bot operational status"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📖 Help Guide", callback_data='cmd_help'),
            InlineKeyboardButton("ℹ️ System Info", callback_data='cmd_about')
        ]
    ]
    
    await update.message.reply_text(
        welcome_card, 
        parse_mode="HTML", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📖 /help Command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>How to Use This Bot:</b>\n"
        "──────────────────────────────\n"
        "<b>1.</b> Copy any YouTube video or movie link.\n"
        "<b>2.</b> Paste and send the URL in this chat.\n"
        "<b>3.</b> Select your desired format/quality from the menu.\n"
        "<b>4.</b> Click the generated <b>Direct Download</b> button.\n\n"
        "💡 <i>Tip: For files larger than 50MB, direct high-speed streaming links are provided to bypass Telegram restrictions.</i>"
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="HTML")
    else:
        await update.callback_query.message.reply_text(help_text, parse_mode="HTML")

# ℹ️ /about Command
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "🤖 <b>Bot Specification</b>\n"
        "──────────────────────────────\n"
        "<b>• Name:</b> YouTube Media Downloader Pro\n"
        "<b>• Core Engine:</b> Python 3 & yt-dlp\n"
        "<b>• Formats:</b> MP3, MP4 (360p - 1080p FHD)\n"
        "<b>• Status:</b> 🟢 Operational / High-Speed\n"
        "<b>• Version:</b> 3.0 Pro Edition"
    )
    if update.message:
        await update.message.reply_text(about_text, parse_mode="HTML")
    else:
        await update.callback_query.message.reply_text(about_text, parse_mode="HTML")

# ⚡️ /ping Command
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("📡 <i>Testing connection...</i>", parse_mode="HTML")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000)
    
    await msg.edit_text(f"🚀 <b>Pong!</b> Response Time: <code>{latency} ms</code>", parse_mode="HTML")

# 📊 /stats Command
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats_text = (
        "📊 <b>Bot Statistics</b>\n"
        "──────────────────────────────\n"
        "<b>• Server Status:</b> 🟢 Online\n"
        "<b>• Download Engine:</b> Updated (yt-dlp)\n"
        "<b>• Max Resolution:</b> 1080p Full HD\n"
        "<b>• Direct Stream:</b> Enabled"
    )
    await update.message.reply_text(stats_text, parse_mode="HTML")

# 🎬 Link Handler with Stylish Layout
async def handle_youtube_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text(
            "❌ <b>Invalid URL!</b>\nPlease send a valid YouTube video or shorts link.", 
            parse_mode="HTML"
        )
        return

    status_msg = await update.message.reply_text("🔍 <i>Fetching video metadata...</i>", parse_mode="HTML")

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'YouTube Video')
            duration = info.get('duration', 0)
            thumbnail = info.get('thumbnail', None)
            channel = info.get('uploader', 'Unknown Channel')

        context.user_data['url'] = url
        context.user_data['title'] = title

        # Duration formatting
        mins, secs = divmod(duration, 60)
        hours, mins = divmod(mins, 60)
        dur_str = f"{hours}h {mins}m {secs}s" if hours else f"{mins}m {secs}s"

        # Stylish Card Text
        caption_card = (
            f"🎬 <b>{title}</b>\n\n"
            f"👤 <b>Channel:</b> <code>{channel}</code>\n"
            f"⏱️ <b>Duration:</b> <code>{dur_str}</code>\n"
            f"──────────────────────────────\n"
            f"👇 <b>Select Quality / Format:</b>"
        )

        # 2x2 Keyboard Layout
        keyboard = [
            [
                InlineKeyboardButton("📱 360p (SD)", callback_data='res_360'),
                InlineKeyboardButton("🎥 480p (SD)", callback_data='res_480'),
            ],
            [
                InlineKeyboardButton("🎬 720p (HD)", callback_data='res_720'),
                InlineKeyboardButton("💎 1080p (FHD)", callback_data='res_1080'),
            ],
            [
                InlineKeyboardButton("🎧 MP3 Audio Only", callback_data='res_mp3')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await status_msg.delete()

        if thumbnail:
            await update.message.reply_photo(
                photo=thumbnail, 
                caption=caption_card, 
                reply_markup=reply_markup, 
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                caption_card, 
                reply_markup=reply_markup, 
                parse_mode="HTML"
            )

    except Exception:
        await status_msg.edit_text("❌ <b>Error:</b> Failed to extract metadata. Please verify the URL.", parse_mode="HTML")

# 🔘 Button Interaction Handler
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'cmd_help':
        await help_command(update, context)
        return
    elif data == 'cmd_about':
        await about_command(update, context)
        return

    url = context.user_data.get('url')
    title = context.user_data.get('title', 'Video')

    if not url:
        await query.message.reply_text("⚠️ <b>Session Expired!</b> Please resend the link.", parse_mode="HTML")
        return

    proc_msg = await query.message.reply_text("⏳ <i>Generating high-speed link...</i>", parse_mode="HTML")

    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        if data == 'res_mp3':
            formats = info.get('formats', [])
            audio_url = next((f['url'] for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), info.get('url'))
            
            result_card = (
                f"🎧 <b>{title}</b>\n"
                f"──────────────────────────────\n"
                f"Your high-quality audio stream is ready. Click below to download:"
            )
            download_button = InlineKeyboardMarkup([[InlineKeyboardButton("⚡️ Direct Download MP3", url=audio_url)]])
            
        else:
            res_map = {'res_360': '360', 'res_480': '480', 'res_720': '720', 'res_1080': '1080'}
            target_res = res_map.get(data, '720')

            formats = info.get('formats', [])
            selected_url = info.get('url')
            
            for f in formats:
                if f.get('height') and str(f.get('height')) == target_res and f.get('ext') == 'mp4':
                    selected_url = f.get('url')
                    break

            result_card = (
                f"🎬 <b>{title}</b>\n"
                f"📐 <b>Resolution:</b> {target_res}p\n"
                f"──────────────────────────────\n"
                f"Click below to start high-speed downloading via browser or download manager:"
            )
            download_button = InlineKeyboardMarkup([[InlineKeyboardButton(f"⚡️ Direct Download ({target_res}p)", url=selected_url)]])

        await proc_msg.delete()
        await query.message.reply_text(result_card, parse_mode="HTML", reply_markup=download_button)

    except Exception:
        await proc_msg.edit_text("❌ <b>Download Failed!</b> Please try again.", parse_mode="HTML")

# Main Runner
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    # Register Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("stats", stats_command))

    # Register Message & Callback Handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_link))
    app.add_handler(CallbackQueryHandler(button_click_handler))

    print("🚀 English Pro UI Bot is live...")
    app.run_polling()
    