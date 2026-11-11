# Atlas-Trade

**6 Grok Bot ile Alım Satım Masası**

Tek bir grup sohbetinde 6 uzman bot çalışır. Her bot kendi rolünü yapar, birbirine iş devreder ve her fikre **AL / BEKLE / GEÇ** der.  
**Son kararı ve emri sen verirsin.**

Bu depo, Grok Bot üzerinde hızlı ve güvenli bir trading desk kurman için hazır iskelet sunar.

---

## Masadaki 6 Bot

| Bot | Rol | Ana Görevi |
|-----|-----|------------|
| **Tarayıcı** | Scanner | Anormal hacim, fiyat sapması ve fırsat tarar |
| **Haberci** | News Analyst | Fiyat hareketinin nedenini haber ve on-chain verilerle açıklar |
| **Giriş-Çıkış** | Entry/Exit | Giriş seviyesi, hedef, stop ve R:R önerir |
| **Şüpheci** | Devil's Advocate | Her öneriye itiraz eder, son kararı yazar (AL / BEKLE / GEÇ) |
| **Risk** | Risk Manager | Pozisyon büyüklüğü, günlük zarar limiti ve risk kurallarını kontrol eder |
| **Günlükçü** | Journalist | Tüm kararları kaydeder, günlük/haftalık özet çıkarır |

---

## Hızlı Başlangıç

1. Bu depoyu klonla veya dosyaları Grok Bot’un workspace’ine koy.
2. `SETUP.md` dosyasını takip et.
3. 6 botu oluştur ve `bots/` klasöründeki talimatları yapıştır.
4. Grup sohbeti aç, 6 botu ekle ve `rules/masa-kurallari.md` içeriğini gruba yaz.
5. İlk test: `@Tarayıcı BTC’ye bak`

Detaylı adımlar → [SETUP.md](SETUP.md)

---

## Proje Yapısı

```
Atlas-Trade/
├── README.md
├── SETUP.md
├── bots/                     # 6 botun sistem prompt'ları
│   ├── 01-tarayici.md
│   ├── 02-haberci.md
│   ├── 03-giris-cikis.md
│   ├── 04-supheci.md
│   ├── 05-risk.md
│   └── 06-gunlukcu.md
├── rules/
│   └── masa-kurallari.md     # Grup sohbet kuralları
├── config/
│   ├── risk-limits.example.md
│   └── desk.md.example
├── templates/
│   ├── proposal.md           # İşlem önerisi şablonu
│   ├── daily-report.md
│   └── journal-entry.md
├── desk/                     # Çalışma alanı (sen dolduracaksın)
│   ├── proposals/
│   ├── journal/
│   ├── briefs/
│   └── data/
└── docs/
    └── overview.md
```

---

## Güvenlik Kuralları (Çok Önemli)

- Botlar **asla** kendi başına emir vermez.
- Gerçek para kullanmadan önce sadece **research** veya **paper** modunda çalıştır.
- Borsa API anahtarı vereceksen **sadece trade yetkisi** ver, **para çekme yetkisi verme**.
- Her işlem için Şüpheci’nin **AL** demesini ve Risk’in onayını bekle.
- Günlük zarar limitini `config/risk-limits.md` dosyasında net yaz.

---

## Katkı ve Lisans

Bu iskelet eğitim ve kişisel kullanım içindir.  
Yatırım tavsiyesi değildir. Botlar yanılabilir. Risk tamamen sana aittir.

MIT License

---

**Atlas-Trade** — Emri sen verirsin.