# DBD v2 - Binance Veri Akış Dinleyici

Real-time Binance pazar verilerini WebSocket aracılığıyla yakalarken ve işlerken, bu veriler üzerinde çeşitli analiz yapmak için geliştirilmiş bir Python projesidir.

## 📋 Proje Yapısı

```
dbd-v2/
├── keyword_finder.py      # WebSocket URL'lerini keşfetmek için
├── worker.py              # Veri toplayan istemci
├── server.py              # Merkezi sunucu & veri işleyici
├── requirements.txt       # Proje bağımlılıkları
└── README.md
```

## 🎯 Bileşenler

### 1. **keyword_finder.py** - Ağ Keşif Aracı
Binance web sitesinin arka planda açılan WebSocket bağlantılarını izler:
- Tarayıcı açılır ve Binance sitesine gidilir
- Tüm HTTP isteklerini ve WebSocket URL'lerini gösterir
- Ortak kelimeyi (ör: "stream", "socket") bulmanıza yardımcı olur
- Veri akışını incelemek için kullanılır

**Çalıştırma:**
```bash
python keyword_finder.py
```

### 2. **worker.py** - Veri Toplayıcısı (İstemci)
Binance'den canlı pazar verilerini toplayıp sunucuya gönderir:
- Playwright ile browser otomasyonu yapar
- WebSocket listener'ı kurarak gelen veri akışını yakalar
- Toplanan verileri Socket.IO üzerinden sunucuya iletir
- `FOUND_KEYWORD` ve `TARGET_URL` ayarlarını kullanır

**Ayarlar:**
```python
TARGET_URL = 'https://www.binance.com/tr/markets/overview'
FOUND_KEYWORD = 'stream'  # Keşfedilen ortak kelime
LOCAL_SERVER = 'http://localhost:5151'
```

**Çalıştırma:**
```bash
python worker.py
```

### 3. **server.py** - Merkezi Sunucu & İşleyici
Socket.IO aracılığıyla worker'dan veri alıp işler:
- Port 5151'de dinler ve worker'ları bağlanmasını bekler
- Gelen Binance verilerini yapılandırılmış formata dönüştürür
- Fiyat değişimlerini hesaplar (açılış → kapanış)
- İşlenen verileri tablo halinde gösterir

**Çalıştırma:**
```bash
python server.py
```

## 🛠️ Gereksinimler & Kurulum

### Gerekli Paketler
```
playwright           # Tarayıcı otomasyonu
python-socketio      # Socket.IO istemci/sunucu
aiohttp             # Async HTTP kütüphanesi
tabulate            # Tablo görüntüleme
```

### Kurulum Adımları

1. **Python 3.8+ yüklü olduğundan emin olun**

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Playwright tarayıcılarını yükleyin:**
```bash
playwright install
```

## 🚀 Kullanım

### Adım 1: Sunucuyu Başlatın
Yeni bir terminal açın ve şu komutu çalıştırın:
```bash
python server.py
```
Çıkti: `📡 SERVER: 5151 portunda dinlemeye başladı...`

### Adım 2: Worker'ı Çalıştırın
Başka bir terminal açın:
```bash
python worker.py
```
- Chrome tarayıcısı otomatik açılır
- Binance sitesi yüklenir
- Dashboard'da veri akışı başlaması için **ENTER** tuşuna basın

### Adım 3: Verileri İzleyin
Sunucu terminali'nde gelen veriler işlenerek tablolar halinde gösterilir:
```
│ Sembol     │ Fiyat     │ Değişim    │
├────────────┼───────────┼────────────┤
│ BTCUSDT    │ 45000.50  │ +2.35%     │
│ ETHUSDT    │ 3200.00   │ -1.20%     │
```

## 🔍 İlk Defa Kullanılıyorsa

Eğer bu ilk defa ise ve hangi WebSocket URL'sinin kullanılacağını bilmiyorsanız:

```bash
python keyword_finder.py
```

1. Tarayıcı açılacak ve Binance'ye gidecek
2. Network trafiğini izleyin
3. Benzer WebSocket URL'lerini bulun
4. Ortak kelimeyi (ör: "stream") notu alın
5. Bu kelimeyi `worker.py`'de `FOUND_KEYWORD` değişkenine yazın

## 📊 Desteklenen Veri

Server şu bilgileri işler:
- **Sembol**: Kripto çifti (BTCUSDT, ETHUSDT, vb.)
- **Fiyat**: Son kapanış fiyatı
- **Değişim**: Açılış ile kapanış arasındaki yüzde değişim
- **Zaman**: Verilerin alındığı zaman

## 🔧 Ayarlamalar

### server.py
```python
# Port numarası değiştirmek için:
app.router.add_get('/', index)
web.run_app(app, port=5151)  # Farklı port
```

### worker.py
```python
# Hedef URL değiştirmek:
TARGET_URL = 'https://www.binance.com/tr/spot'

# WebSocket keyword'ü değiştirmek:
FOUND_KEYWORD = 'socket'

# Sunucu adresini değiştirmek:
LOCAL_SERVER = 'http://localhost:5151'
```

## ⚠️ Sık Sorunlar

**Sorun**: Worker "Sunucu bağlantı hatası" veriyor
- **Çözüm**: Sunucunun çalışıp çalışmadığını kontrol edin. Server'ı önce başlatın.

**Sorun**: Tarayıcıda veri akmıyor
- **Çözüm**: Binance'nin JavaScript'le veri yüklediğini bekleyin. ENTER tuşuna basmadan önce biraz bekleyin.

**Sorun**: WebSocket verisi boş geliyor
- **Çözüm**: `FOUND_KEYWORD` değişkenini keyword_finder.py ile doğru bulduğunuz kelimeye ayarlayın.

## 📝 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.

## 💡 İpuçları

- Worker ve Server'ı aynı anda açık tutun
- Browser'ı kapatmayın; otomatik tarayıcı oturumudur
- Server'daki tablolarda fiyat değişimlerini gerçek zamanlı takip edin
- Binance API yerine bu yöntem tercih edilirse daha düşük seviyeli veri akışına erişebilirsiniz
