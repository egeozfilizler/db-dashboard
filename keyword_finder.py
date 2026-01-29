import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Tarayıcıyı başlat
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Tarayıcı açıldı.")
        
        await page.goto('https://www.binance.com/tr/markets/overview')

        # Kullanıcı giriş yaptıktan sonra devam et
        input('\nSiteye giriş yap, veriler akmaya başlayınca ENTER bas...')

        print("\nDinleme başladı. URL'leri kontrol et (stream, socket, feed gibi kelimeler ara):\n")

        # WebSocket trafiğini yakala
        def on_websocket(ws):
            print(f"[WS] {ws.url}")
            
            def on_frame(frame):
                try:
                    payload = ""
                    if isinstance(frame, str):
                        payload = frame
                    elif isinstance(frame, bytes):
                        # Binary veriyi atla veya decode etmeyi dene
                        return 
                    
                    if payload:
                        print(f"  Data: {payload[:100]}...")
                except Exception:
                    pass
            
            ws.on("framereceived", on_frame)

        page.on("websocket", on_websocket)

        # HTTP isteklerini logla
        def on_request(request):
            if request.resource_type in ['image', 'stylesheet', 'font', 'script']:
                return
            print(f"[HTTP] {request.url}")

        page.on("request", on_request)

        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())