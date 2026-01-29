import asyncio
from playwright.async_api import async_playwright
import socketio
import json
import base64
import time

# ================= AYARLAR =================
TARGET_URL = 'https://www.binance.com/tr/markets/overview'
FOUND_KEYWORD = 'stream' # Bulduğun ortak kelime
LOCAL_SERVER = 'http://localhost:5151'
# ===========================================

# Socket.IO İstemci
sio = socketio.AsyncClient()

async def main():
    # Sunucuya bağlan
    try:
        await sio.connect(LOCAL_SERVER)
        print("🔌 Sunucuya bağlanıldı.")
    except Exception as e:
        print(f"⚠️ Sunucu bağlantı hatası: {e}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"🔗 Hedef siteye gidiliyor: {TARGET_URL}")

        # Listener kurulumu
        setup_socket_listener(page)

        try:
            await page.goto(TARGET_URL)
        except Exception:
            print("⚠️ Site yüklenirken uyarı verdi (önemsiz).")

        # Kullanıcı onayı bekleme
        input('\n🛑 Tarayıcı açıldı. Veriler akmıyorsa ENTER tuşuna bas...')

        print(f"\n🚀 Dinleme Modu Aktif! Veriler bekleniyor...")

        # Tarayıcıyı ve scripti açık tut
        await asyncio.Future()

def setup_socket_listener(page):
    def handle_websocket(ws):
        if FOUND_KEYWORD in ws.url:
            print(f"✅ SOCKET YAKALANDI: {ws.url}")

            def handle_frame(frame):
                try:
                    # --- GÜVENLİ VERİ ÇIKARMA BLOĞU (DÜZELTİLDİ) ---
                    raw_data = None
                    is_binary = False

                    # Playwright Python'da frame genellikle direkt verinin kendisidir
                    if isinstance(frame, str):
                        raw_data = frame
                        is_binary = False
                    elif isinstance(frame, bytes):
                        raw_data = frame
                        is_binary = True
                    # Nadir durumlarda veya eski versiyonlarda nesne olabilir
                    elif hasattr(frame, 'text') and callable(frame.text):
                         raw_data = frame.text()
                         is_binary = False
                    elif hasattr(frame, 'text'): # property ise
                         raw_data = frame.text
                         is_binary = False
                    
                    if raw_data is None: return

                    data_to_send = ""
                    
                    # Veri çok büyükse logu kirletmesin
                    log_len = len(raw_data) if raw_data else 0
                    print(f"📥 [GELEN] Tip: {'BINARY' if is_binary else 'TEXT'} | Boyut: {log_len}")

                    if is_binary:
                        # Binary veriyi işlemeye çalış
                        try:
                            # Utf-8 decode dene
                            data_to_send = raw_data.decode('utf-8')
                            
                            # Okunabilirlik kontrolü (Basit ASCII kontrolü)
                            if not all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in data_to_send[:50]):
                                raise ValueError("Not readable text")
                                
                        except Exception:
                            # Okunamıyorsa Base64 yap
                            print("   ⚠️ Sıkıştırılmış/Binary Veri. Base64 encode ediliyor.")
                            b64_str = base64.b64encode(raw_data).decode('ascii')
                            data_to_send = json.dumps({
                                'type': 'binary_base64',
                                'content': b64_str
                            })
                    else:
                        # Zaten text ise
                        data_to_send = raw_data

                    # Log ve Gönderim (Ping-pong filtreleme > 5 karakter)
                    if len(data_to_send) > 5:
                        print(f"   📝 Veri: {data_to_send[:100]}...")
                        
                        asyncio.create_task(sio.emit('stream_data', {
                            'type': 'websocket',
                            'sourceUrl': ws.url,
                            'timestamp': int(time.time() * 1000),
                            'data': data_to_send
                        }))

                except Exception as err:
                    print(f"❌ Parse Hatası: {err}")

            ws.on("framereceived", handle_frame)
            ws.on("close", lambda: print("🔌 SOCKET KAPANDI"))

    page.on("websocket", handle_websocket)

if __name__ == "__main__":
    asyncio.run(main())