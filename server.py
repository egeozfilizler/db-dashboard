from aiohttp import web
import socketio
import json
from datetime import datetime
from tabulate import tabulate # pip install tabulate

# Socket.IO Sunucu Kurulumu (CORS izinleri ile)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

print("📡 SERVER: 5151 portunda dinlemeye başladı...")

def calculate_change(open_price, close_price):
    try:
        o = float(open_price)
        c = float(close_price)
        if o == 0: return "0.00%"
        change = ((c - o) / o) * 100
        return f"{change:.2f}%"
    except:
        return "0.00%"

@sio.event
async def connect(sid, environ):
    print(f"✅ WORKER BAĞLANDI (ID: {sid})")

@sio.event
async def disconnect(sid):
    print("❌ Worker düştü.")

@sio.event
async def stream_data(sid, payload):
    try:
        # ---------------------------------------------------------
        # SENARYO 1: BINANCE VERİSİ GELDİYSE (Okunabilir yap)
        # ---------------------------------------------------------
        # Node.js kodunda data string ise kontrol ediliyordu
        data_content = payload.get('data')
        
        if isinstance(data_content, str) and "miniTicker" in data_content:
            parsed = json.loads(data_content)
            items = parsed.get('data', [])

            # Veriyi haritalayalım (Mapping)
            readable_data = []
            for item in items:
                readable_data.append({
                    "Sembol": item.get('s'),           # s -> Symbol
                    "Fiyat": float(item.get('c')),     # c -> Close Price
                    "Hacim": f"{float(item.get('q')):.2f}", # q -> Quote Volume
                    "Degisim": calculate_change(item.get('o'), item.get('c'))
                })

            print(f"\n📊 [BINANCE VERİSİ İŞLENDİ] - {datetime.now().strftime('%H:%M:%S')}")
            
            # Terminalde tablo bas (İlk 5 veri)
            print(tabulate(readable_data[:10], headers="keys", tablefmt="pretty"))
            
            # TODO: Veritabanı kayıt işlemleri buraya eklenebilir.

        # ---------------------------------------------------------
        # SENARYO 2: DİĞER TİP VERİLER
        # ---------------------------------------------------------
        else:
            print("\n📦 [DİĞER VERİ PAKETİ]")
            print(f"   ├─ Kaynak: {payload.get('sourceUrl')}")
            
            content = json.dumps(data_content) if isinstance(data_content, (dict, list)) else str(data_content)
            print(f"   └─ İçerik: {content[:200]}...")

    except Exception as e:
        print(f"❌ Veri işleme hatası: {e}")

if __name__ == '__main__':
    web.run_app(app, port=5151)