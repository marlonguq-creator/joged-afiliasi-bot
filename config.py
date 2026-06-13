import os

# ─────────────────────────────────────────────
# WAJIB DIISI
# ─────────────────────────────────────────────

# Token dari @BotFather
TOKEN = os.getenv("TOKEN", "ISI_TOKEN_BOT_KAMU")

# ID Telegram admin (bisa lebih dari satu)
# Cara cari ID kamu: chat @userinfobot di Telegram
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")
]

# ID Channel untuk auto-post (format: @namachannel atau -100xxxxxxxxx)
# Kosongkan jika tidak pakai channel
CHANNEL_ID = os.getenv("CHANNEL_ID", "")
