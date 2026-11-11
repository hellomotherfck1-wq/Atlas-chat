# Atlas ajan sozlesmeleri (uygulama)

Tum ajanlar yalnizca kendilerine verilen ayni tarama snapshot'i ve onceki ajanlarin yapilandirilmis ciktilariyla calisir. Her ajan JSON dondurur; serbest metin tek basina karar motoruna girdi olamaz.

## Ortak zorunlu alanlar

- scan_id: Benzersiz tarama kimligi
- symbol: Binance Spot sembolu, or. BTCUSDT
- candle_interval: Analizde kullanilan zaman dilimi
- data_as_of: Son kapanmis mumun UTC zamani
- data_quality: OK / STALE / INCOMPLETE
- evidence: Sayisal metrik ve kaynak aciklamalari
- warnings: Veri veya model uyarilari

## 1. Tarayici

Amac: Likidite evrenindeki paritelerde anomali ve teknik adaylari bulmak.

Girdiler: Kapanmis OHLCV mumlari, 24 saatlik hacim, spread ve order-book ozeti.

Kontroller:
- Ani hacim degisimi, volatilite, trend ve momentum
- Spread/likidite esikleri
- Mum kapanis zamani ve veri butunlugu
- Stablecoin/stablecoin ve kaldiracli token haric listesi

Cikti: aday semboller, tetikleyici metrikler, aday onceligi. AL/BEKLE/GEÇ karari vermez.

## 2. Haberci

Amac: Hareketin olasi nedenini guvenilir kaynaklarla aciklamak.

Kurallar:
- Kaynak URL'si ve yayin zamani olmadan haber iddiasi kurma.
- Kaynak bulunamazsa NOT_VERIFIED yaz.
- Haber verisi gecikmis veya celiskiliyse bunu acikla.
- Teknik veriden haber nedeni uydurma.

Cikti: dogrulanmis olaylar, kaynaklar, zaman damgalari, guven ve belirsizlik. Islem karari vermez.

## 3. Giris-Cikis

Amac: Yalnizca aday icin uygulanabilir Spot AL plani hesaplamak.

Kurallar:
- Spot'ta short/kaldirac onerme.
- Giris bolgesi, stop, hedef1/hedef2, R:R ve gecersizlesme kosulu ver.
- Minimum R:R 1:2 kosulunu saglamayan plani onaya gonderme.
- Seviyeler kapanmis mum ve volatiliteye dayanmali; rastgele kesin fiyat uretme.

## 4. Risk

Amac: Plani deterministik risk motoru ile birlikte denetlemek.

Kontroller:
- Sanal portfoy nakdi ve mevcut pozisyonlar
- Islem basina risk, gunluk/haftalik zarar limiti
- Korelasyon ve ayni varlik yogunlasmasi
- Likidite, spread, stop mesafesi ve minimum R:R
- Komisyon ve tahmini kayma

Limit veya portfoy ayari yoksa ONAY verme. Cikti: APPROVE / REJECT ve makinece okunabilir nedenler.

## 5. Supheci

Amac: AL adayi icin karsi senaryo aramak.

Kontroller:
- Trend tersine donuyor mu?
- Hacim teyidi yok mu?
- Fiyat direncte mi, hareket asiri uzamis mi?
- Haber belirsizligi veya veri kalitesi sorunu var mi?
- Stop seviyesi piyasa yapisina gore anlamsiz mi?

Cikti: AL / BEKLE / GEÇ ve en fazla dort somut itiraz. Risk RED ise AL veremez.

## 6. Gunlukcu

Amac: Degistirilemez denetim izi olusturacak sekilde tarama ve sinyal kaydi tutmak.

Kaydet:
- Ham veri snapshot referansi ve veri zamani
- Her ajanin surum/prompt kimligi ve JSON ciktisi
- Nihai karar ve karar nedenleri
- Paper giris/cikis, komisyon, kayma ve PnL
- Hata, gecikme ve veri eksikligi

Performans raporu yalnizca kapanmis paper islemlerinden hesaplanir.

## Nihai karar motoru - zorunlu kapilar

AL yalnizca asagidaki kosullarin TAMAMI saglanirsa verilebilir:
1. Veri kalitesi OK ve mum kapanmis.
2. Tarayici adayi gecerli.
3. Giris-Cikis plani tam ve R:R >= 2.
4. Risk sonucu APPROVE.
5. Supheci karari AL.
6. Ayni scan_id + symbol + strateji icin yinelenen sinyal yok.
7. Paper motoru pozisyon acmaya uygun nakit/limit buluyor.

Diger tum durumlarda BEKLE veya GEÇ. Ajanin serbest metni bu kapilari asamaz.

## Model hatasi / timeout

- Her ajan icin timeout ve sinirli tekrar denemesi uygula.
- Ajan yanit vermezse veya JSON semasi gecersizse aday AL olamaz.
- Veri eskiyse yeni sinyal olusturma.
- Worker ayni scan_id'yi yeniden calistirirsa yinelenen islem/sinyal kaydi olusmasin.
