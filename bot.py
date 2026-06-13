import logging
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters,
    ConversationHandler
)
from config import TOKEN, ADMIN_IDS, CHANNEL_ID
from database import (
    init_db, get_all_videos, get_video_by_id,
    add_video, delete_video, log_click, get_stats
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# States untuk ConversationHandler (tambah video)
TUNGGU_JUDUL, TUNGGU_DESKRIPSI, TUNGGU_LINK_VIDEO, TUNGGU_LINK_SHOPEE = range(4)

# ─────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def menu_utama_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Lihat Video Joged", callback_data="lihat_video")],
        [InlineKeyboardButton("🛍️ Info Shopee Afiliasi", callback_data="info_afiliasi")],
    ])

def admin_menu_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Tambah Video", callback_data="admin_tambah")],
        [InlineKeyboardButton("📋 Daftar Video", callback_data="admin_daftar")],
        [InlineKeyboardButton("📊 Statistik Klik", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Post ke Channel", callback_data="admin_post")],
    ])

# ─────────────────────────────────────────────
# USER: /start
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"👋 Halo *{user.first_name}*!\n\n"
        "Selamat datang di *Bot Joged Afiliasi* 🕺\n\n"
        "Temukan video joged viral + link produk Shopee-nya!\n"
        "Klik & belanja sekalian~ 🛍️"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=menu_utama_markup())

# ─────────────────────────────────────────────
# USER: Lihat video
# ─────────────────────────────────────────────

async def lihat_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    videos = get_all_videos()
    if not videos:
        await query.edit_message_text(
            "😔 Belum ada video. Tunggu update ya!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="kembali")]])
        )
        return

    keyboard = [[InlineKeyboardButton(f"🎵 {v['judul']}", callback_data=f"video_{v['id']}")] for v in videos]
    keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="kembali")])

    await query.edit_message_text(
        "🎬 *Pilih video joged:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def detail_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    video_id = int(query.data.split("_")[1])
    video = get_video_by_id(video_id)

    if not video:
        await query.edit_message_text("❌ Video tidak ditemukan.")
        return

    # Buat link tracker klik
    log_click(video_id, query.from_user.id)

    keyboard = [
        [InlineKeyboardButton("🎬 Tonton Video", url=video["link_video"])],
        [InlineKeyboardButton("🛒 Beli di Shopee!", url=video["link_shopee"])],
        [InlineKeyboardButton("🔙 Kembali", callback_data="lihat_video")],
    ]

    await query.edit_message_text(
        f"🎵 *{video['judul']}*\n\n"
        f"📝 {video['deskripsi']}\n\n"
        f"⬇️ Klik tombol di bawah untuk tonton & belanja!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def info_afiliasi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🛍️ *Shopee Afiliasi*\n\n"
        "Setiap pembelian lewat link kami, kamu dapet produk kece sesuai video joged!\n\n"
        "✅ Harga terjamin\n"
        "✅ Bebas ongkir\n"
        "✅ Produk ori\n\n"
        "📩 Pertanyaan? Hubungi admin.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="kembali")]])
    )

async def kembali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "👋 Menu Utama\n\nPilih salah satu di bawah:",
        reply_markup=menu_utama_markup()
    )

# ─────────────────────────────────────────────
# ADMIN: /admin
# ─────────────────────────────────────────────

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Kamu bukan admin.")
        return
    await update.message.reply_text(
        "🔧 *Panel Admin*\n\nPilih aksi:",
        parse_mode="Markdown",
        reply_markup=admin_menu_markup()
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    stats = get_stats()
    text = "📊 *Statistik Klik Afiliasi*\n\n"
    if not stats:
        text += "Belum ada data klik."
    else:
        for s in stats:
            text += f"🎵 *{s['judul']}*\n👆 Klik: {s['total_klik']}\n\n"

    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")]])
    )

async def admin_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    videos = get_all_videos()
    if not videos:
        await query.edit_message_text(
            "📋 Belum ada video.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")]])
        )
        return

    keyboard = [[InlineKeyboardButton(f"🗑️ Hapus: {v['judul']}", callback_data=f"hapus_{v['id']}")] for v in videos]
    keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")])

    await query.edit_message_text(
        "📋 *Daftar Video* (klik untuk hapus):",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def hapus_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    video_id = int(query.data.split("_")[1])
    video = get_video_by_id(video_id)
    if video:
        delete_video(video_id)
        await query.edit_message_text(
            f"✅ Video *{video['judul']}* berhasil dihapus.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")]])
        )
    else:
        await query.edit_message_text("❌ Video tidak ditemukan.")

async def admin_post_ke_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    videos = get_all_videos()
    if not videos:
        await query.edit_message_text("😔 Tidak ada video untuk di-post.")
        return

    keyboard = [[InlineKeyboardButton(f"📢 Post: {v['judul']}", callback_data=f"postch_{v['id']}")] for v in videos]
    keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")])

    await query.edit_message_text(
        "📢 *Pilih video untuk di-post ke channel:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def post_video_ke_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return

    video_id = int(query.data.split("_")[1])
    video = get_video_by_id(video_id)

    if not video:
        await query.edit_message_text("❌ Video tidak ditemukan.")
        return

    if not CHANNEL_ID:
        await query.edit_message_text("⚠️ CHANNEL_ID belum diset di config.py")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎬 Tonton Video", url=video["link_video"])],
        [InlineKeyboardButton("🛒 Beli di Shopee!", url=video["link_shopee"])],
    ])

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=(
            f"🎵 *{video['judul']}*\n\n"
            f"📝 {video['deskripsi']}\n\n"
            f"🛍️ Cek produknya di Shopee!\n"
            f"⬇️ Klik tombol di bawah!"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    await query.edit_message_text(
        f"✅ Video *{video['judul']}* berhasil di-post ke channel!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="admin_menu")]])
    )

async def admin_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔧 *Panel Admin*\n\nPilih aksi:",
        parse_mode="Markdown",
        reply_markup=admin_menu_markup()
    )

# ─────────────────────────────────────────────
# ADMIN: Tambah video (ConversationHandler)
# ─────────────────────────────────────────────

async def admin_tambah_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Bukan admin!", show_alert=True)
        return ConversationHandler.END

    await query.edit_message_text("📝 *Tambah Video Baru*\n\nKetik *judul* video:")
    return TUNGGU_JUDUL

async def terima_judul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["judul"] = update.message.text
    await update.message.reply_text("✏️ Ketik *deskripsi* singkat video:", parse_mode="Markdown")
    return TUNGGU_DESKRIPSI

async def terima_deskripsi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["deskripsi"] = update.message.text
    await update.message.reply_text("🔗 Kirim *link video* (Telegram/YouTube/TikTok):", parse_mode="Markdown")
    return TUNGGU_LINK_VIDEO

async def terima_link_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link_video"] = update.message.text
    await update.message.reply_text("🛒 Kirim *link afiliasi Shopee*:", parse_mode="Markdown")
    return TUNGGU_LINK_SHOPEE

async def terima_link_shopee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link_shopee"] = update.message.text
    data = context.user_data

    add_video(data["judul"], data["deskripsi"], data["link_video"], data["link_shopee"])

    await update.message.reply_text(
        f"✅ *Video berhasil ditambahkan!*\n\n"
        f"🎵 Judul: {data['judul']}\n"
        f"📝 Deskripsi: {data['deskripsi']}\n"
        f"🎬 Link Video: {data['link_video']}\n"
        f"🛒 Link Shopee: {data['link_shopee']}",
        parse_mode="Markdown",
        reply_markup=admin_menu_markup()
    )
    context.user_data.clear()
    return ConversationHandler.END

async def batal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("❌ Dibatalkan.", reply_markup=admin_menu_markup())
    return ConversationHandler.END

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    init_db()

    app = Application.builder().token(TOKEN).build()

    # ConversationHandler untuk tambah video
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_tambah_start, pattern="^admin_tambah$")],
        states={
            TUNGGU_JUDUL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_judul)],
            TUNGGU_DESKRIPSI:  [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_deskripsi)],
            TUNGGU_LINK_VIDEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, terima_link_video)],
            TUNGGU_LINK_SHOPEE:[MessageHandler(filters.TEXT & ~filters.COMMAND, terima_link_shopee)],
        },
        fallbacks=[CommandHandler("batal", batal)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(conv_handler)

    app.add_handler(CallbackQueryHandler(lihat_video,           pattern="^lihat_video$"))
    app.add_handler(CallbackQueryHandler(detail_video,          pattern="^video_\d+$"))
    app.add_handler(CallbackQueryHandler(info_afiliasi,         pattern="^info_afiliasi$"))
    app.add_handler(CallbackQueryHandler(kembali,               pattern="^kembali$"))
    app.add_handler(CallbackQueryHandler(admin_stats,           pattern="^admin_stats$"))
    app.add_handler(CallbackQueryHandler(admin_daftar,          pattern="^admin_daftar$"))
    app.add_handler(CallbackQueryHandler(hapus_video,           pattern="^hapus_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_post_ke_channel, pattern="^admin_post$"))
    app.add_handler(CallbackQueryHandler(post_video_ke_channel, pattern="^postch_\d+$"))
    app.add_handler(CallbackQueryHandler(admin_menu_callback,   pattern="^admin_menu$"))

    print("✅ Bot Joged Afiliasi berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
