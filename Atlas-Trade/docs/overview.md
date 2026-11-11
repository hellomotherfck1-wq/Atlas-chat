# Atlas-Trade Genel Bakış

## Nedir?

Atlas-Trade, Grok Bot üzerinde çalışan **6 uzman botlu** bir alım-satım masasıdır.  
Botlar birlikte çalışır, tartışır ve her fikre net bir karar (AL / BEKLE / GEÇ) verir.  
Son emri her zaman kullanıcı verir.

## Neden 6 Bot?

Tek bir modele her şeyi yüklemek yerine rolleri ayırıyoruz:

- Tarama ayrı
- Haber/neden analizi ayrı
- Plan ayrı
- Risk ayrı
- Şüphecilik (devil’s advocate) ayrı
- Kayıt ayrı

Bu yapı, hem daha disiplinli karar üretiyor hem de hataları azaltıyor.

## Çalışma Akışı

```
Tarayıcı → Haberci → Giriş-Çıkış → Risk → Şüpheci → Günlükçü
                              ↓
                         Kullanıcı Onayı
                              ↓
                         Emir (manuel)
```

## Güvenlik Felsefesi

- Botlar emir vermez
- Risk limitleri yazılıdır
- Şüpheci’nin “AL” demesi zorunludur
- İlk dönem paper/research zorunludur

## Geliştirme Yol Haritası (İsteğe Bağlı)

- [ ] Watchlist otomatik güncelleme
- [ ] Hyperliquid / Binance read-only entegrasyonu
- [ ] Günlük raporun otomatik dosyaya yazılması
- [ ] Haftalık performans analizi
- [ ] Paper trading simülasyonu

---

Bu iskelet sade başlar. İhtiyaca göre genişletilebilir.