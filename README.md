# 🕺 Bot Joged Afiliasi Shopee

Bot Telegram untuk mengelola & mempromosikan video joged afiliasi Shopee.

---

## 📁 Struktur File

```
joged_bot/
├── bot.py          # File utama bot
├── database.py     # Manajemen database SQLite
├── config.py       # Konfigurasi token & admin
├── requirements.txt
├── Procfile        # Untuk Railway
└── README.md
```

---

## ⚙️ Konfigurasi Sebelum Deploy

### 1. Dapatkan Token Bot
- Buka Telegram → cari **@BotFather**
- Ketik `/newbot` → ikuti instruksi
- Salin TOKEN yang diberikan

### 2. Dapatkan ID Telegram Kamu (Admin)
- Chat **@userinfobot** di Telegram
- Salin angka ID kamu

### 3. (Opsional) Siapkan Channel
- Buat channel Telegram
- Tambahkan bot sebagai **Admin** di channel
- Salin ID channel (format: `-100xxxxxxxxx` atau `@namachannel`)

---

## 🚀 Deploy ke Railway

### Langkah 1 — Buat Akun Railway
- Daftar di [railway.app](https://railway.app) (gratis)

### Langkah 2 — Upload File
- Buat repositori GitHub baru
- Upload semua file ini ke repo tersebut

### Langkah 3 — Buat Project di Railway
1. Klik **New Project**
2. Pilih **Deploy from GitHub repo**
3. Pilih repo kamu

### Langkah 4 — Set Environment Variables
Di Railway → tab **Variables**, tambahkan:

| Key | Value |
|-----|-------|
| `TOKEN` | token bot dari BotFather |
| `ADMIN_IDS` | ID telegram kamu (contoh: `123456789`) |
| `CHANNEL_ID` | ID channel (opsional, contoh: `@channelkamu`) |

### Langkah 5 — Deploy
- Railway otomatis deploy setelah variabel diset
- Cek tab **Logs** untuk memastikan bot berjalan

---

## 🎮 Cara Pakai Bot

### Sebagai User
| Perintah | Fungsi |
|----------|--------|
| `/start` | Buka menu utama |
| Pilih video | Lihat detail + link Shopee |

### Sebagai Admin
| Perintah | Fungsi |
|----------|--------|
| `/admin` | Buka panel admin |
| ➕ Tambah Video | Input judul, deskripsi, link video, link Shopee |
| 📋 Daftar Video | Lihat & hapus video |
| 📊 Statistik Klik | Lihat total klik per video |
| 📢 Post ke Channel | Kirim video ke channel Telegram |

---

## 📊 Fitur Utama

- ✅ Panel admin via Telegram (tanpa coding)
- ✅ Database SQLite (data tersimpan permanen)
- ✅ Lacak klik per video
- ✅ Post otomatis ke channel Telegram
- ✅ Tambah/hapus video via chat

---

## 🛠️ Jalankan Lokal (Opsional)

```bash
pip install -r requirements.txt
python bot.py
```

Atau set environment variable manual:
```bash
TOKEN=xxx ADMIN_IDS=123456789 python bot.py
```
