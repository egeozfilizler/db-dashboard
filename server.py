from aiohttp import web
import socketio
import json
from datetime import datetime

# Verileri hafızada tutmak için global değişken
latest_market_data = {}

# Socket.IO Sunucu Kurulumu
# cors_allowed_origins='*' ile Socket.IO kendi CORS'unu zaten yönetiyor
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

def calculate_change(open_price, close_price):
    try:
        o = float(open_price)
        c = float(close_price)
        if o == 0: return "0.00%"
        change = ((c - o) / o) * 100
        return f"{change:.2f}%"
    except:
        return "0.00%"

# API Endpoint'i
async def get_market_data(request):
    data_list = list(latest_market_data.values())
    return web.json_response(data_list)

# Ana sayfa
async def index(request):
    return web.Response(text="API Calisiyor. Veriler icin /api/data adresine gidin.")

# Rotaları tanımla
app.router.add_get('/', index)
app.router.add_get('/api/data', get_market_data)

@sio.event
async def connect(sid, environ):
    print(f"Worker connected: {sid}")

@sio.event
async def stream_data(sid, payload):
    try:
        data_content = payload.get('data')
        
        if isinstance(data_content, str) and "miniTicker" in data_content:
            parsed = json.loads(data_content)
            items = parsed.get('data', [])

            for item in items:
                symbol = item.get('s')
                latest_market_data[symbol] = {
                    "symbol": symbol,
                    "price": float(item.get('c')),
                    "volume": float(item.get('q')),
                    "change": calculate_change(item.get('o'), item.get('c')),
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                }
            
            # Konsol çıktısını temiz tutmak için sayaç
            print(f"\r[GÜNCEL] Hafızada {len(latest_market_data)} adet coin verisi var...", end="")

    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == '__main__':
    import aiohttp_cors
    
    # CORS ayarları (Frontend'in veriyi çekebilmesi için)
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })
    
    # --- DÜZELTME BURADA YAPILDI ---
    # Sadece bizim eklediğimiz rotalara CORS ekle, hatayı engelle
    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except ValueError:
            # "/socket.io/" rotası gibi zaten ayarlanmış olanları atla
            pass

    print("Server listening on port 5151")
    web.run_app(app, port=5151)