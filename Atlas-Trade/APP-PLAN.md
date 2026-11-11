# Atlas-Trade Uygulama Mimari Plani

Bu belge, mevcut Grok sohbeti talimatlarini calisan, mobil uyumlu ve 15 dakikada bir otomatik analiz yapan bir uygulamaya donusturmek icin hedef mimariyi tanimlar.

## Kullanici tarafindan secilen ilk ayarlar

- Borsa: Binance Spot
- Tarama araligi: 15 dakika
- Erisim: Mobil uyumlu PWA (Android/iOS tarayicisindan kurulabilir)
- Mod: Yalnizca research + paper trading
- Emir iletimi: Kapali. Binance'e emir gonderilmez.
- Kullanici deneyimi: Kullanici yalnizca sinyal, gerekce, giris/stop/hedef ve performans kayitlarini gorur.

## Ilk surum varsayilanlari

- Evren: Binance Spot'ta islem goren, USDT kotasyonlu, likiditesi yuksek ilk 50 parite.
- Stablecoin/stablecoin, kaldiracli token, delist/TRADE disi ve yetersiz veri bulunan pariteler haric tutulur.
- Tarama evreni her gun Binance exchangeInfo ve 24 saatlik hacim verisiyle yenilenir.
- Paper portfoy bakiyesi: 10.000 USDT sanal bakiye; bu gercek hesap bakiyesi degildir ve ayarlardan degistirilebilir.
- Ornek risk limitleri baslangic degeridir; kullanici onayi olmadan gercek isleme uygulanmaz.

## Sistem bilesenleri

1. **PWA arayuzu**: Ozet, canli sinyaller, sinyal ayrintisi, paper portfoy, performans ve ayarlar.
2. **API/backend**: Kimlik dogrulama, sinyal API'leri, ayarlar, kayit ve bildirim yonetimi.
3. **Zamanlayici/worker**: Her 15 dakikada bir tarama gorevini baslatir. Gorevler idempotent olur; ayni mum araligi icin yinelenen sinyal olusturmaz.
4. **Binance Spot veri baglayicisi**: Ilk surumde yalnizca herkese acik piyasa verilerini kullanir. API anahtari gerekmez.
5. **Deterministik analiz katmani**: Mum, hacim, trend, volatilite, spread ve likidite metriklerini hesaplar.
6. **Altı uzman ajan**: Tarayici, Haberci, Giris-Cikis, Risk, Supheci ve Gunlukcu. Mevcut bot dosyalari rol tanimlarinin kaynagidir.
7. **Karar birlestirici**: Ajan cevaplarini ve sayisal risk kapilarini birlestirir. Risk reddi, eksik veri veya ajan celiskisi varsa AL karari vermez.
8. **Paper simulator**: Sanal girisleri, komisyonu, kaymayi, stop/hedef tetiklerini ve gerceklesmemis PnL'yi kaydeder.
9. **Veritabani**: Mum snapshot'lari, tarama kosulari, ajan ciktilari, sinyaller, sanal islemler ve performans metrikleri.

## 15 dakikalik tarama akisi

1. Worker, Binance sunucu saatini ve son kapanmis mumlari kontrol eder.
2. Gecerli USDT Spot evrenini ve likidite siralamasini gunceller.
3. Tum evrende hafif teknik/likidite taramasi yapar.
4. Yalnizca en guclu adaylari uzman ajanlara gonderir; boylece maliyet ve gecikme kontrol edilir.
5. Haberci kaynakli bilgiye ulasilamiyorsa haber varmis gibi davranmaz; "dogrulanamadi" yazar.
6. Giris-Cikis, kapanmis mumlara dayali giris, stop, hedef ve risk/getiri plani olusturur.
7. Risk ajani ve kodla uygulanan zorunlu risk kontrolleri plani denetler.
8. Supheci karsi senaryoyu arar ve AL/BEKLE/GEÇ kararini verir.
9. Karar motoru son kapilari uygular ve sinyali kaydeder.
10. Gunlukcu sinyalin tum girdilerini ve sonucunu kaydeder; PWA yeni sinyali gosterir.

## Karar guvenligi

- AL sinyali yalnizca yeterli ve guncel veri, uygun likidite, gecerli stop, minimum 1:2 risk/getiri, Risk EVET ve Supheci AL kosullari birlikte saglanirsa verilir.
- Herhangi bir zorunlu kosul eksikse karar BEKLE veya GEÇ olur.
- Guven puani, basari olasiligi garantisi degildir; modelin kanit ve veri kalitesini ozetler.
- Sinyaller kapanmis mum verisiyle uretilir; acik mum kaynakli repaint/erken sinyal riski engellenir.
- Backtest, ileriye donuk test ve paper trading performansi ayri raporlanir. Komisyon ve kayma hesaba katilir.
- Veri gecikmesi, Binance erisim sorunu veya worker hatasinda sistem yeni AL sinyali uretmez; durum panelde acikca gosterilir.

## Binance veri guvenligi

- Ilk surumde `data-api.binance.vision` ve herkese acik Spot REST/WebSocket market-data endpointleri kullanilir.
- API key/secret alinmaz ve istemciye gomulmez.
- Uygulamada emir gonderen kod bulunmaz. Live trading daha sonra ayri tasarim ve acik kullanici onayi gerektirir.
- Rate limit yanitlarinda geri cekilme (backoff) uygulanir; 429/418 yanitlarinda istekler zorlanmaz.

## Asgari ekranlar

- **Ozet**: Son tarama saati, sistem durumu, AL/BEKLE/GEÇ dagilimi.
- **Sinyaller**: Coin, yon (Spot AL veya izleme), giris bolgesi, stop, hedefler, R:R, guven, zaman damgasi.
- **Sinyal detayi**: Altı ajanin gerekceleri, veri snapshot'i ve reddedilme nedenleri.
- **Paper portfoy**: Sanal bakiye, acik sanal pozisyonlar, gerceklesmis/gerceklesmemis PnL.
- **Performans (ayri sayfa)**: Genel paper portfoy net getiri (%) ve USDT, bot bazli net PnL/getiri (%), kazanma orani, profit factor, max drawdown, ortalama R, islem sayisi, donem filtresi ve bot karar gecmisi. Ayrintilar: docs/performance-dashboard.md.
- **Ayarlar**: Tarama evreni, risk limitleri, sanal bakiye ve bildirimler.

## Dagitim gereksinimi

15 dakikalik taramanin telefon kapali olsa da devam etmesi icin worker ve veritabani surekli calisan bir sunucuda barindirilmalidir. PWA tek basina arka plan taramasi yapmaz. Dagitimdan once testler, gizli anahtar yonetimi, yedekleme, loglama ve hata bildirimleri tamamlanmalidir.

## Uygulama sirasi

1. Backend, veritabani semasi ve Binance public-data baglayicisi.
2. 15 dakikalik worker ve tekrar calistirma guvenligi.
3. Teknik tarayici ve aday secimi.
4. Alt ajanin yapilandirilmis JSON ciktilari ve karar birlestirici.
5. Paper simulator ve performans hesaplari.
6. PWA panelleri ve bildirimler.
7. Backtest/ileri test ve en az bir haftalik paper gozlem.

**Not:** Bu belge hedef mimaridir; uygulamanin calistigi veya paper sonuclarinin dogrulandigi anlamina gelmez.
