import os
import uuid
import asyncio
import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.filters import Command
from aiogram.types import Message

TOKEN = "8182538234:AAFEGKHgv4axI3oUhwNHkarirlm_mtT4hxg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("👋 Salom! Instagram videolarini yuklash uchun video linkini yuboring.")

async def download_instagram_video(video_url: str) -> str | None:
    """Instagram videolarini `yt-dlp` orqali yuklab olish"""
    file_name = f"video_{uuid.uuid4()}.mp4"
    file_path = os.path.join(os.getcwd(), file_name)

    try:
        ydl_opts = {"outtmpl": file_path, "quiet": True, "format": "best"}
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts).download([video_url]))
        return file_path
    except Exception as e:
        print(f"❌ Yuklab olishda xatolik: {e}")
        return None

@dp.message()
async def download_video(message: Message):
    video_url = message.text.strip()

    if not video_url.startswith("https://www.instagram.com/"):
        await message.reply("❌ Iltimos, to‘g‘ri Instagram video havolasini yuboring!")
        return

    # 🔍 1. Link tekshirilmoqda
    msg = await message.reply("🔍 Link tekshirilmoqda...")
    await asyncio.sleep(3)
    await msg.edit_text("📥 Video serverga yuklanmoqda...")
    await asyncio.sleep(3)

    # 📤 3. Telegramga yuklanmoqda (bu xabar o‘chmaydi)
    msg = await msg.edit_text("📤 Telegramga yuklanmoqda...")

    # 📌 Video yuklash
    downloaded_file = await download_instagram_video(video_url)

    if downloaded_file:
        video = FSInputFile(downloaded_file)
        await bot.send_video(chat_id=message.chat.id, video=video, caption="✅ Video tayyor!")
        os.remove(downloaded_file)  # Yuklangan videoni o‘chirish
        await msg.delete()  # "Telegramga yuklanmoqda..." xabarini o‘chirish
    else:
        await msg.edit_text("❌ Videoni yuklab bo‘lmadi! Boshqa linkni sinab ko‘ring.")

async def main():
    print("🤖 Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
