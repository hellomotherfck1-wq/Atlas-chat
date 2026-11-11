# Atlas Trade — ilk çalışan sürüm

## Özellikler
- Binance Spot public market-data; API key/secret gerekmez.
- Backend her 15 dakikada tarama yapar; tarama PWA kapalıyken sunucuda sürer.
- 50 yüksek hacimli USDT Spot paritesi, 15m mum, kapanmış mum analizi.
- Açıklanabilir kural tabanlı Tarayıcı / Haberci / Giriş-Çıkış / Şüpheci / Risk / Günlükçü adımları.
- SQLite sinyal günlüğü, sanal işlemler, komisyon/kayma sonrası PnL ve Performans sayfası.
- **Gerçek emir endpoint'i veya Binance trade API anahtarı yoktur.**

> İlk sürüm gerçek LLM ajanları ya da haber entegrasyonu değildir. Haberci haber teyidi olmadığını açıkça belirtir. Sinyaller yatırım tavsiyesi değildir; önce uzun süre paper modda gözlemleyin.

## Yerel çalıştırma (Docker)
Docker Desktop kurulu iken:
```bash
cd Atlas-Trade/app
docker compose up --build
```
Arayüz: http://localhost:5173 — API dokümanı: http://localhost:8000/docs

## Test
```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install pytest
pytest -q
```

## Sınırlar
- İlk açılışta ilk tarama otomatik başlar, sonraki taramalar 15 dakikada birdir.
- Tarama manuel tetiklenebilir.
- Paper bakiye 10.000 USDT; ilk ayarlar config örneğindeki limitlerdir.
- İlk sürümde tek kullanıcı ve yerel SQLite. Kalıcı internet erişimi için sunucuda Docker deploy edin; bilgisayar kapalıyken yerel kurulum tarama yapmaz.
- Henüz mobil push bildirim, kullanıcı girişi, haber API'si ve gerçek LLM ajanları yoktur.
