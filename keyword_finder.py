import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # 1. Tarayıcıyı Görünür Modda Aç
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("🚀 Tarayıcı açıldı. Lütfen hedef siteye gidin.")
        
        await page.goto('https://www.binance.com/tr/markets/overview')

        # 2. KULLANICI GİRİŞİNİ BEKLEME
        input('\n🛑 Siteye giriş yapın, dashboard verileri akmaya başlayınca ENTER tuşuna basın...')

        print("\n✅ Dinleme Başladı! Aşağıdaki URL'leri incele ve ortak kelimeyi bul (Örn: 'stream', 'socket', 'feed')...\n")

        # A) WebSocket Trafiğini İfşa Et
        def on_websocket(ws):
            print(f"🔥 [WEBSOCKET]: {ws.url}")
            
            def on_frame(frame):
                try:
                    payload = ""
                    if isinstance(frame, str):
                        payload = frame
                    elif isinstance(frame, bytes):
                        # Binary veriyi atla veya decode etmeyi dene
                        return 
                    
                    if payload:
                        print(f"   └─ Veri: {payload[:100]}...")
                except Exception:
                    pass
            
            ws.on("framereceived", on_frame)

        page.on("websocket", on_websocket)

        # B) HTTP Trafiğini İfşa Et
        def on_request(request):
            if request.resource_type in ['image', 'stylesheet', 'font', 'script']:
                return
            print(f"🔎 [HTTP]: {request.url}")

        page.on("request", on_request)

        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())