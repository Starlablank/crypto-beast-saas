from fastapi import FastAPI
import asyncio
import httpx
import os
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()

app = FastAPI(title="Beast SaaS - $1000/day Signals")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
AFFILIATE_LINK = "https://changenow.app.link/referral?link_id=c3a5cf5fc7587d"
CHANNEL_ID = os.getenv("CHANNEL_ID", "@BeastSolanaSignals")

bot = telegram.Bot(token=TELEGRAM_TOKEN)

async def get_hot_tokens():
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            r = await client.get("https://api.dexscreener.com/latest/dex/search?q=solana")
            data = r.json()
            pairs = data.get('pairs', [])[:20]
            hot = [p for p in pairs if p.get('chainId') == 'solana' 
                   and float(p.get('fdv', 0)) < 1000000 
                   and float(p.get('volume', {}).get('h24', 0)) > 30000]
            return hot[:6]
        except:
            return []

async def send_signal(context: ContextTypes.DEFAULT_TYPE):
    tokens = await get_hot_tokens()
    for t in tokens:
        symbol = t['baseToken']['symbol']
        address = t['baseToken']['address']
        volume = int(t.get('volume', {}).get('h24', 0))
        msg = f"""🚀 **BEAST SNIPER SIGNAL** #{symbol}

CA: `{address}`
24h Vol: ${volume:,}
Swap & Buy Now → {AFFILIATE_LINK}
Potential 10x-100x 🔥

DYOR | High risk | NFA"""
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
        except:
            pass

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ **Beast Signals Bot LIVE**\nFree signals every 3 mins.\n/buy for premium")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"""💰 Lifetime Premium = 0.1 SOL

Use my link for swaps: {AFFILIATE_LINK}""")

@app.get("/")
async def root():
    return {"status": "🔥 Beast SaaS LIVE"}

@app.get("/status")
async def status():
    return {"message": "Bot running"}

def main_telegram():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy))
    
    job_queue = application.job_queue
    job_queue.run_repeating(send_signal, interval=180, first=10)
    
    application.run_polling()

if __name__ == "__main__":
    import uvicorn
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(asyncio.to_thread(main_telegram))
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
