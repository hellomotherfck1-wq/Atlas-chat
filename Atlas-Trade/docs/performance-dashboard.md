# Atlas Performans Sayfasi - Urun Gereksinimi

## Amac
PWA icinde ana navigasyonda **Performans** adinda ayri bir sayfa olacak. Kullanici Atlas'in toplam paper trading sonucunu ve her ajanin gecmis kararlarinin olculebilir performansini yuzdesel olarak gorecek.

Bu sayfa gercek Binance hesap bakiyesi veya gercek emir performansi gostermez. Ilk surumde tum rakamlar sanal paper trading kayitlarindan hesaplanir.

## Sayfa duzeni

### 1. Genel performans kartlari
Ustte secilen donem icin:
- Net getiri: yuzde ve USDT
- Gerceklesmis net PnL: USDT
- Kazanan / kaybeden / toplam kapanan paper islem
- Kazanma orani: yuzde
- Profit factor
- Maksimum dusus (max drawdown): yuzde
- Ortalama R
- Acik sanal pozisyonlarin anlik kar/zarari ayri gosterilir

Donem filtresi: Son 7 gun / 30 gun / 90 gun / Tum zamanlar. Ayrica baslangic-bitis tarih secimi.

### 2. Bot bazli performans tablosu
Alt kisimda alti botun her biri ayri satirda gosterilir:
- Bot adi ve gorevi
- Degerlendirilen karar sayisi
- Botun katkida bulundugu kapanmis paper islem sayisi
- Bot katkili islemlerin net PnL'si (USDT)
- Bot katkili islemlerin net getirisi (yuzde)
- Kazanma orani (yuzde)
- Ortalama R
- Son karar / son degerlendirme tarihi

Satira tiklandiginda botun karar gecmisi acilir: coin, tarih, AL/BEKLE/GEÇ, gerekce, bagli paper islem, sonuc ve PnL.

### 3. Bot performansi nasil hesaplanacak?
- Ana strateji portfoyu: Nihai karar motorunun AL dedigi ve paper simulator tarafindan acildigi islemlerin tekil portfoy sonucudur.
- Bot katkisi: Her paper islem icin hangi ajan kararinin/tespitinin isleme dahil olmasina neden oldugu kaydedilir. Bir islem birden fazla ajanin katkisini tasiyorsa, bot bazli tabloda ayni islem ilgili botlarin katkili islem sayisina girer; ancak bu satirlarin PnL'leri toplanarak toplam portfoy PnL'si gibi sunulmaz.
- Bot bazli net getiri, o botun katkili islemlerinin net PnL toplam / ayni islemler icin ayrilan sabit sanal risk sermayesi olarak hesaplanir. Ortak islem birden fazla bot satirinda gorunebilir; genel portfoy toplaminda yalnizca bir kez sayilir.
- Bir botun kendi basina AL/BEKLE/GEÇ karari yoksa ona yapay islem atfedilmez. Bu durumda yuzde alaninda "—" ve "Yeterli bagimsiz islem yok" aciklamasi gosterilir; sifir kar/zarar gibi sunulmaz.
- Botlarin gorev bazli basarisi (or. Risk'in zararli plani engellemesi, Haberci'nin dogrulanmis kaynak bulmasi) PnL'den ayri bir "Gorev kalitesi" metrigi olarak raporlanir.

## Finansal hesaplama kurallari
- Net PnL = kapanis gelirleri - giris maliyeti - alis/satis komisyonlari - tahmini kayma.
- Net getiri (yuzde) = net PnL / ilgili sanal portfoy veya bot icin onceden ayrilmis sanal risk sermayesi x 100.
- Kazanma orani = net PnL pozitif olan kapanmis islemler / tum kapanmis islemler x 100.
- Profit factor = toplam pozitif net PnL / mutlak toplam negatif net PnL. Zararli islem yoksa "sonsuz"; yeterli islem yoksa "—".
- Max drawdown = portfoyun onceki zirvesinden sonraki en dusuk seviyeye yuzdesel gerilemesi.
- Acik islemlerin gerceklesmemis PnL'si gerceklesmis net getiriye dahil edilmez; ayri gosterilir.
- Komisyon ve kayma her paper islemde dusulur. Mum icinde hem stop hem hedef gorulurse, daha dusuk zaman dilimi verisiyle siralama dogrulanamiyorsa muhafazakar olarak stop once varsayilir.
- Sifir kapanmis islemde kazanma orani veya getiri uydurulmaz; "Henuz veri yok" gosterilir.
- Her metrik secilen tarih araligina ve strateji surumune bagli olur.

## Guven ve adil karsilastirma
- Botlarin rol ve prompt surumu her kararla birlikte saklanir. Prompt degisirse yeni surum ayri performans serisi olarak izlenir.
- Bot bazli PnL satirlarinda orneklem sayisi gorunur; 20'den az kapanmis katkili islemde "Dusuk orneklem" etiketi gosterilir.
- Backtest, ileri test ve canli paper sonuclari birbirine karistirilmaz; ayri sekmeler/filtreler kullanilir.
- Gecmise donuk veriyle sonradan sinyal uydurulmaz. Sinyal anindaki veri snapshot'i ve zaman damgasi saklanir.
- Botlarin ortak katkili islemlerini toplayip alti kat kar yazma hatasi engellenir. Genel portfoy PnL'si yalnizca tekil islemlerden hesaplanir.

## Kabul kriterleri
1. Mobil ve masaustu navigasyonda Performans sayfasi gorunur.
2. Genel portfoy net getiri yuzdesi ve USDT tutari gosterilir.
3. Alti bot icin ayri performans satiri ve gecmis karar listesi vardir.
4. Veri olmayan botta sahte yuzde sifir yerine "Yeterli veri yok" yazar.
5. Komisyon/kayma dusulmeden net kar gosterilmez.
6. Genel portfoy sonucu her paper islemi yalnizca bir kez sayar.
7. Donem filtresi tum kartlari, grafikleri ve tabloyu ayni tarih araligina uygular.
8. Backtest ve paper trading performansi birbirinden ayridir.
