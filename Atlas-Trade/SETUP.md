# Atlas-Trade Kurulum Rehberi

Bu dosyayı Grok Bot’a yapıştırarak veya adım adım takip ederek masayı kurabilirsin.

---

## 1. Gereksinimler

- Grok Bot erişimi (X Premium / Super / Ultra veya Cursor Pro+ / Ultra)
- Grok Bot masaüstü veya mobil uygulaması
- (Opsiyonel) Hyperliquid / Binance / başka borsa hesabı (sadece research için şart değil)

---

## 2. Botları Oluştur

Grok Bot’ta **6 ayrı bot** oluştur. İsimleri birebir şöyle koy:

1. **Tarayıcı**
2. **Haberci**
3. **Giriş-Çıkış**
4. **Şüpheci**
5. **Risk**
6. **Günlükçü**

Her botun sohbetini aç ve `bots/` klasöründeki ilgili dosyanın **tamamını** yapıştır.  
Sonuna şunu ekle:

```
Bunu hatırla. Bundan sonra bu rolü oyna.
```

---

## 3. Grup Sohbetini Kur

1. Yeni **Group Chat** oluştur.
2. To: alanına 6 botu ekle (Grok Bot bir grupta en fazla 6 bot kabul eder).
3. Grup adını **Atlas Masası** koy.
4. Aşağıdaki mesajı gruba gönder:

```
@everyone Masa kuralları:

1. Gruba yaz, birbirinize iş devredin.
2. Sıra:
   - Tarayıcı bulur
   - Haberci açıklar
   - Giriş-Çıkış plan önerir
   - Risk kontrol eder
   - Şüpheci son kararı yazar (AL / BEKLE / GEÇ)
   - Günlükçü kaydeder
3. Kimse emir vermez. Kararı ve emri sadece ben veririm.
4. Her öneri için kısa ve net ol.
5. Bu kuralları hatırla.
```

---

## 4. İlk Test

Gruba şunu yaz:

```
@Tarayıcı BTC’ye bak. Son 4 saatte anormal bir hareket var mı?
```

Botlar sırayla cevap vermeli. Şüpheci en sonda **AL / BEKLE / GEÇ** demeli.

---

## 5. Risk Limitlerini Ayarla

`config/risk-limits.example.md` dosyasını kopyala → `desk/risk-limits.md` yap.

İçine kendi limitlerini yaz:

- Günlük maksimum zarar (%)
- Tek işlemde risk edilecek sermaye (%)
- Maksimum açık pozisyon sayısı
- Kullanacağın marketler (BTC, ETH, SOL vb.)

---

## 6. Çalışma Klasörleri

Grok Bot’un workspace’inde şu klasörleri oluştur (veya bu depodaki `desk/` klasörünü kullan):

```
/workspace/atlas-trade/
├── proposals/     # Her işlem fikri için bir dosya
├── journal/       # Günlük kayıtlar
├── briefs/        # Kısa piyasa özetleri
└── data/          # Ham veriler, watchlist vs.
```

---

## 7. Günlük Kullanım

### Sabah rutini örneği:
```
@Tarayıcı Bugün hangi coinlerde anormal hacim var? Top 5 listele.
```

### Bir fırsat geldiğinde:
```
@Haberci Bu hareketin nedenini bul.
@Giriş-Çıkış Giriş, stop ve hedef öner.
@Risk Bu plan risk limitlerime uyuyor mu?
@Şüpheci Son kararını ver.
```

### Gün sonu:
```
@Günlükçü Bugünkü tüm kararları ve sonuçları özetle.
```

---

## 8. Güvenlik Kontrol Listesi

- [ ] 6 bot oluşturuldu ve talimatları yapıştırıldı
- [ ] Grup sohbeti kuruldu ve kurallar yazıldı
- [ ] Risk limitleri dosyası dolduruldu
- [ ] API anahtarı varsa sadece **trade** yetkisi var (withdraw yok)
- [ ] İlk 1 hafta sadece paper / research modunda çalışılacak
- [ ] Her işlemde Şüpheci’nin **AL** demesi bekleniyor

---

Kurulum bittikten sonra gruba şunu yazabilirsin:

```
Atlas Masası hazır. İlk taramayı başlat.
```