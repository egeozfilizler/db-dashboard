from aiohttp import web
import socketio
import json
from datetime import datetime
from tabulate import tabulate # pip install tabulate

# Socket.IO Sunucu Kurulumu (CORS izinleri ile)
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

print("Server listening on port 5151")

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
    print(f"Worker connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Worker disconnected: {sid}")

@sio.event
async def stream_data(sid, payload):
    try:
        # Binance miniTicker verisi kontrolü
        data_content = payload.get('data')
        
        if isinstance(data_content, str) and "miniTicker" in data_content:
            parsed = json.loads(data_content)
            items = parsed.get('data', [])

            readable_data = []
            for item in items:
                readable_data.append({
                    "Sembol": item.get('s'),
                    "Fiyat": float(item.get('c')),
                    "Hacim": f"{float(item.get('q')):.2f}",
                    "Degisim": calculate_change(item.get('o'), item.get('c'))
                })

            print(f"\n[BINANCE] {datetime.now().strftime('%H:%M:%S')}")
            print(tabulate(readable_data[:10], headers="keys", tablefmt="pretty"))

        else:
            print("\n[DATA]")
            print(f"  Source: {payload.get('sourceUrl')}")
            
            content = json.dumps(data_content) if isinstance(data_content, (dict, list)) else str(data_content)
            print(f"  Content: {content[:200]}...")

    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == '__main__':
    web.run_app(app, port=5151)