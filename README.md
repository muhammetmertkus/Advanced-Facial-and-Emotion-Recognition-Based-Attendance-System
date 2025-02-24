# Gelişmiş Yüz ve Duygu Tanıma Tabanlı Yoklama Sistemi

![Proje Durumu](https://img.shields.io/badge/Proje%20Durumu-Aktif-brightgreen)
![Katkıda Bulunanlar](https://img.shields.io/badge/Katk%C4%B1da%20Bulunanlar-4-blue)
![Lisans](https://img.shields.io/badge/Lisans-MIT-orange)

## 🤝 Proje Paydaşları

- [19erdprlk03](https://github.com/19erdprlk03)
- [AlpaslanCamdibi](https://github.com/AlpaslanCamdibi)
- [ipekbulgurcu](https://github.com/ipekbulgurcu)
- [muhammetmertkus](https://github.com/muhammetmertkus)


## 🎯 Hedef

Bu proje, yüz ve duygu tanıma teknolojilerini kullanarak otomatik ve güvenilir bir yoklama sistemi geliştirmeyi amaçlamaktadır. Eğitim kurumları, iş yerleri ve etkinlik organizatörleri için katılım takibini optimize etmeyi hedeflemektedir.

## 🧝‍🧍 Hedef Kitle

- Eğitim kurumları
- İş yerleri
- Etkinlik organizatörleri
- 18-65 yaş arası teknoloji kullanıcıları

## 🚧 Zorluklar

1. Gerçek zamanlı ve doğru yüz tanıma sağlama.
2. Duygu tanıma algoritmalarını etkili bir şekilde entegre etme.
3. Veri gizliliği ve güvenliğini sağlama.
4. Farklı ışık ve ortam koşullarında tutarlı performans gösterme.

## 💡 Çözüm

Proje, yüz tanıma ve duygu analizi işlevlerini bir Qt tabanlı kullanıcı arayüzü ile birleştiren gelişmiş bir sistem geliştirmiştir. Kullanılan başlıca teknolojiler:

- **Yüz Tanıma:** `face_recognition` kütüphanesi ile yüksek doğruluk oranına sahip yüz tanıma.
- **Duygu Analizi:** `DeepFace` kütüphanesi ile yaş, cinsiyet, ırk ve duyguların analizi.
- **Görüntü İşleme:** `OpenCV` kullanılarak gerçek zamanlı kamera akışı.
- **Veri Yönetimi:** `Pandas` ile yoklama verilerinin CSV formatında saklanması.
- **GUI:** `PySide6` ile kullanıcı dostu bir arayüz.

## 🔧 Kullanılan Kütüphaneler ve İşlevleri

### 1. **Python Kütüphaneleri**
- **`os`, `sys`, `threading`:** Dosya ve sistem işlemleri, paralel programlama.
- **`pickle`:** Yüz verilerinin saklanması ve yüklenmesi.
- **`pandas`:** Yoklama verilerinin işlenmesi ve raporlanması.

### 2. **Görüntü İşleme**
- **`OpenCV (cv2)`:** Gerçek zamanlı görüntü akışı ve işleme.
- **`numpy`:** Görüntü matrislerini işleme.

### 3. **Yüz Tanıma ve Duygu Analizi**
- **`face_recognition`:** Yüz algılama ve tanıma.
- **`DeepFace`:** Duygu, yaş, cinsiyet ve ırk analizi.

### 4. **GUI (Grafiksel Kullanıcı Arayüzü)**
- **`PySide6.QtWidgets`:** Qt arayüz bileşenleri (butonlar, etiketler, giriş kutuları).
- **`PySide6.QtCore`:** İş parçacığı ve sinyal mekanizması.
- **`PySide6.QtGui`:** Görselleri ve çerçeveleri işleme.

## 👤 Kullanıcı Hikayesi: Ayşe'nin Deneyimi

Ayşe, 35 yaşında bir öğretmen ve sınıfındaki öğrencilerin yoklamasını daha verimli bir şekilde almak istiyor.

1. **Keşif:** GitHub üzerinden projeyi indirir.
2. **Kurulum:** Bağımlılıkları yükler ve uygulamayı çalıştırır.
3. **Kullanım:**
   - Öğrencilerin yüz verilerini sisteme kaydeder.
   - Ders sırasında kamerayı başlatarak yoklamayı gerçek zamanlı alır.
4. **Sonuç:** Otomatik oluşturulan yoklama raporları ile zaman tasarrufu sağlar ve detaylı analizlere ulaşır.

## 📈 Öğrenilen Dersler ve Gelecek Planları

1. Geri bildirimler, kullanıcı dostu arayüzün önemini vurguladı.
2. Duygu tanıma özelliği, öğrencilerin derse katılım seviyelerini değerlendirmede etkili oldu.
3. **Gelecek Planlar:**
   - Bulut tabanlı veri depolama.
   - Mobil uygulama entegrasyonu.
   - Daha gelişmiş raporlama araçları.

## 🎓 Sonuç

Bu proje, yüz tanıma ve duygu analizi teknolojilerinin, kullanıcı dostu bir GUI ile birleştirilerek yoklama sistemlerini nasıl optimize edebileceğini göstermiştir. Eğitim ve iş dünyasında katılım takibini otomatikleştirerek verimliliği artırmaktadır.

