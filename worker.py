import asyncio
from playwright.async_api import async_playwright
import socketio
import json
import base64
import time

# Config
TARGET_URL = 'https://www.binance.com/tr/markets/overview'
FOUND_KEYWORD = 'stream'
LOCAL_SERVER = 'http://localhost:5151'

# Socket.IO İstemci
sio = socketio.AsyncClient()

async def main():
    try:
        await sio.connect(LOCAL_SERVER)
        print("Connected to server.")
    except Exception as e:
        print(f"Connection error: {e}")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print(f"Loading: {TARGET_URL}")

        setup_socket_listener(page)

        try:
            await page.goto(TARGET_URL)
        except Exception:
            print("Warning during page load (can be ignored)")

        input('\nPress ENTER when data starts flowing...')

        print("\nListening for data...")

        await asyncio.Future()

def setup_socket_listener(page):
    def handle_websocket(ws):
        if FOUND_KEYWORD in ws.url:
            print(f"[SOCKET] {ws.url}")

            def handle_frame(frame):
                try:
                    raw_data = None
                    is_binary = False
                    if isinstance(frame, str):
                        raw_data = frame
                        is_binary = False
                    elif isinstance(frame, bytes):
                        raw_data = frame
                        is_binary = True
                    elif hasattr(frame, 'text') and callable(frame.text):
                         raw_data = frame.text()
                         is_binary = False
                    elif hasattr(frame, 'text'):
                         raw_data = frame.text
                         is_binary = False
                    
                    if raw_data is None: return

                    data_to_send = ""
                    
                    log_len = len(raw_data) if raw_data else 0
                    print(f"[IN] {'BIN' if is_binary else 'TXT'} | Size: {log_len}")

                    if is_binary:
                        try:
                            data_to_send = raw_data.decode('utf-8')
                            
                            if not all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in data_to_send[:50]):
                                raise ValueError("Not readable text")
                                
                        except Exception:
                            print("  Binary data, encoding to base64")
                            b64_str = base64.b64encode(raw_data).decode('ascii')
                            data_to_send = json.dumps({
                                'type': 'binary_base64',
                                'content': b64_str
                            })
                    else:
                        data_to_send = raw_data

                    if len(data_to_send) > 5:
                        print(f"  Data: {data_to_send[:100]}...")
                        
                        asyncio.create_task(sio.emit('stream_data', {
                            'type': 'websocket',
                            'sourceUrl': ws.url,
                            'timestamp': int(time.time() * 1000),
                            'data': data_to_send
                        }))

                except Exception as err:
                    print(f"Parse error: {err}")

            ws.on("framereceived", handle_frame)
            ws.on("close", lambda: print("[SOCKET CLOSED]"))

    page.on("websocket", handle_websocket)

if __name__ == "__main__":
    asyncio.run(main())