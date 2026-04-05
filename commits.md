# BLM3522 Proje 1 - Commit Dokümanı

Bu dosya, projedeki tüm commitleri tek tek inceleyip hocanın kolayca anlayacağı şekilde hazırlanmıştır.
İnceleme doğrudan git geçmişi üzerinden yapılmıştır.

## 1) 369233a32b5d6f1c070001d03dd3fb9740bfb96f
- Kısa hash: `369233a`
- Mesaj: initialize spring boot with postgresql and jpa configuration and react
- Etki: 25 dosya, +4333 / -0 satır

Yapılan iş:
- Projenin temel omurgası bu committe kuruldu: backend için Spring Boot, frontend için React + Vite başlangıç yapısı oluşturuldu.
- Backend tarafında Maven wrapper, `pom.xml`, ana uygulama sınıfı ve test sınıfı eklenerek çalıştırılabilir bir Java servis altyapısı hazırlandı.
- `application.properties` ile veritabanı bağlantısı/JPA yapılandırmasının temeli atıldı; PostgreSQL odaklı çalışma düzeni başlatıldı.
- Frontend tarafında Vite giriş noktaları (`main.jsx`, `App.jsx`, `index.html`) ve temel stil dosyaları eklenerek arayüz çatısı kuruldu.
- Paket yönetimi dosyaları (`package.json`, `package-lock.json`) ile frontend bağımlılıkları tanımlandı.
- Kısacası bu commit, sonraki tüm geliştirmelerin üzerine inşa edildiği başlangıç sürümüdür.

Değişen dosyalar:
- `backend/.gitattributes` (+2/-0)
- `backend/.gitignore` (+33/-0)
- `backend/.mvn/wrapper/maven-wrapper.properties` (+3/-0)
- `backend/mvnw` (+295/-0)
- `backend/mvnw.cmd` (+189/-0)
- `backend/pom.xml` (+111/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/KlinikRandevuVeHastaTakipSistemiApplication.java` (+13/-0)
- `backend/src/main/resources/application.properties` (+16/-0)
- `backend/src/test/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/KlinikRandevuVeHastaTakipSistemiApplicationTests.java` (+13/-0)
- `frontend/.gitignore` (+24/-0)
- `frontend/README.md` (+16/-0)
- `frontend/eslint.config.js` (+29/-0)
- `frontend/index.html` (+13/-0)
- `frontend/package-lock.json` (+3089/-0)
- `frontend/package.json` (+27/-0)
- `frontend/public/favicon.svg` (+1/-0)
- `frontend/public/icons.svg` (+24/-0)
- `frontend/src/App.css` (+184/-0)
- `frontend/src/App.jsx` (+121/-0)
- `frontend/src/assets/hero.png` (binary)
- `frontend/src/assets/react.svg` (+1/-0)
- `frontend/src/assets/vite.svg` (+1/-0)
- `frontend/src/index.css` (+111/-0)
- `frontend/src/main.jsx` (+10/-0)
- `frontend/vite.config.js` (+7/-0)

---

## 2) a1e638c43dd047f3e1ed1d4088010f92e2db4025
- Kısa hash: `a1e638c`
- Mesaj: add patient and appointment entities with jpa repositories
- Etki: 4 dosya, +102 / -0 satır

Yapılan iş:
- Domain modeli bu committe tanımlandı: `Patient` ve `Appointment` entity sınıfları oluşturuldu.
- Veritabanı tablolarının uygulamadaki karşılıkları netleştirildi; alanlar ve ilişki yapısı backend tarafında somutlaştırıldı.
- Her iki entity için JPA repository sınıfları eklenerek veri erişim katmanı hazırlandı.
- Bu adım sayesinde servis katmanının kullanacağı kalıcı veri erişim altyapısı kurulmuş oldu.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/entity/Appointment.java` (+35/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/entity/Patient.java` (+41/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/repository/AppointmentRepository.java` (+13/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/repository/PatientRepository.java` (+13/-0)

---

## 3) df5eeb4a4030a4a7d3a02319c9a649e6ac64066a
- Kısa hash: `df5eeb4`
- Mesaj: implement patient and appointment services
- Etki: 2 dosya, +132 / -0 satır

Yapılan iş:
- Business logic katmanı oluşturuldu: `PatientService` ve `AppointmentService` sınıfları eklendi.
- Repository ile controller arasına servis katmanı konularak katmanlı mimari güçlendirildi.
- Hasta ve randevu işlemleri için temel CRUD iş akışları servis metotlarıyla merkezi hale getirildi.
- Böylece ileride yapılacak doğrulama/iş kuralı eklemeleri için uygun bir merkez oluşturuldu.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/service/AppointmentService.java` (+74/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/service/PatientService.java` (+58/-0)

---

## 4) 463c4306940cb3bb30f838acad11f879b70440e7
- Kısa hash: `463c430`
- Mesaj: implement patient and appointment rest controllers with cors configuration
- Etki: 3 dosya, +150 / -0 satır

Yapılan iş:
- Dış dünyaya açılan REST API katmanı kuruldu: `PatientController` ve `AppointmentController` eklendi.
- Service katmanındaki işlemler HTTP endpoint’lerine bağlandı ve JSON tabanlı veri akışı aktif edildi.
- Frontend-backend haberleşmesi için CORS yapılandırması (`CorsConfig`) eklendi.
- Bu commit ile birlikte proje “çift katmanlı web uygulaması” gereksinimini teknik olarak karşılar hale geldi.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/config/CorsConfig.java` (+19/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/controller/AppointmentController.java` (+67/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/controller/PatientController.java` (+64/-0)

---

## 5) 1f246ecbcc7a218197b7f76792b88a21c447b540
- Kısa hash: `1f246ec`
- Mesaj: create api service with fetch client
- Etki: 1 dosya, +119 / -0 satır

Yapılan iş:
- Frontend’de merkezi API istemcisi oluşturuldu (`api.js`).
- Backend endpoint’lerine erişim tek noktadan yönetilir hale getirildi.
- Fetch tabanlı çağrılar için ortak hata yakalama ve yanıt işleme düzeni kuruldu.
- Bileşenlerin doğrudan URL yazmadan servis metotlarıyla çalışması sağlandı, böylece bakım kolaylaştı.

Değişen dosyalar:
- `frontend/src/services/api.js` (+119/-0)

---

## 6) 2897fd9c400b3d76e014c72fa8a838fd6c6de1aa
- Kısa hash: `2897fd9`
- Mesaj: added patient list and added patient form components with styling
- Etki: 4 dosya, +454 / -0 satır

Yapılan iş:
- Hasta yönetimi için iki temel arayüz parçası geliştirildi: hasta listesi ve hasta ekleme formu.
- Kullanıcıların hasta bilgilerini görüntülemesi ve yeni kayıt oluşturması mümkün hale geldi.
- Form alanları ve liste görünümü için ayrı stil dosyaları eklenerek okunabilir ve tutarlı bir UI oluşturuldu.
- API istemcisi ile UI katmanının birlikte çalıştığı ilk somut iş akışı bu committe tamamlandı.

Değişen dosyalar:
- `frontend/src/components/AddPatientForm.jsx` (+147/-0)
- `frontend/src/components/PatientList.jsx` (+88/-0)
- `frontend/src/styles/AddPatientForm.css` (+120/-0)
- `frontend/src/styles/PatientList.css` (+99/-0)

---

## 7) 84dad208062a8eb6b9185bd5c75ff8230db886d3
- Kısa hash: `84dad20`
- Mesaj: added appointment components and app integration with styling
- Etki: 6 dosya, +621 / -262 satır

Yapılan iş:
- Randevu ekleme ve randevu listeleme bileşenleri eklendi.
- `App.jsx` ve `App.css` güncellenerek hasta ve randevu ekranları tek uygulama akışında birleştirildi.
- Randevu tarafına ait form/list bileşenleri için özel stiller yazıldı.
- Bu commit, projenin “hasta + randevu” fonksiyonlarını uçtan uca görünür hale getiren ana entegrasyon adımıdır.

Değişen dosyalar:
- `frontend/src/App.css` (+96/-150)
- `frontend/src/App.jsx` (+53/-112)
- `frontend/src/components/AddAppointmentForm.jsx` (+110/-0)
- `frontend/src/components/AppointmentList.jsx` (+122/-0)
- `frontend/src/styles/AddAppointmentForm.css` (+114/-0)
- `frontend/src/styles/AppointmentList.css` (+126/-0)

---

## 8) 3edf37acc4549857c1f62ce6309a51bc66ff6921
- Kısa hash: `3edf37a`
- Mesaj: reconfigure Corsconfig.java
- Etki: 1 dosya, +1 / -1 satır

Yapılan iş:
- CORS yapılandırmasında nokta düzeltmesi yapıldı.
- Frontend’den gelen isteklerin backend tarafından sorunsuz kabul edilmesi için ayar satırı revize edildi.
- Küçük ama kritik bir entegrasyon düzeltmesi olduğu için tek dosyada minimal değişiklik yapıldı.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/config/CorsConfig.java` (+1/-1)

---

## 9) 5ab932e44e109fb6b616e3b82f21ccc1a908c508
- Kısa hash: `5ab932e`
- Mesaj: layout fix
- Etki: 7 dosya, +122 / -193 satır

Yapılan iş:
- Arayüzün genel düzeni (layout) yeniden dengelendi ve görsel tutarsızlıklar giderildi.
- `index.css` üzerinde kapsamlı temizlik yapılarak global stiller sadeleştirildi.
- Form ve liste sayfalarının hem bileşen yapısı hem CSS’i birlikte revize edilerek daha stabil bir kullanıcı deneyimi sağlandı.
- Bu commit bir özellik eklemekten çok, mevcut ekranların kullanılabilirliğini artıran iyileştirme adımıdır.

Değişen dosyalar:
- `frontend/src/App.css` (+33/-18)
- `frontend/src/components/PatientList.jsx` (+36/-34)
- `frontend/src/index.css` (+10/-104)
- `frontend/src/styles/AddAppointmentForm.css` (+10/-12)
- `frontend/src/styles/AddPatientForm.css` (+10/-12)
- `frontend/src/styles/AppointmentList.css` (+5/-7)
- `frontend/src/styles/PatientList.css` (+18/-6)

---

## 10) 13051bd8c09c5945bdd36374f91bf669640bdf05
- Kısa hash: `13051bd`
- Mesaj: bidirectional relationship json loop fix
- Etki: 3 dosya, +10 / -0 satır

Yapılan iş:
- Hasta-randevu arasındaki çift yönlü ilişki nedeniyle oluşan JSON sonsuz döngü problemi giderildi.
- Entity seviyesinde JSON serileştirme davranışı düzenlenerek API yanıtlarının güvenli üretilmesi sağlandı.
- Frontend tarafındaki `vite.config.js` güncellemesiyle geliştirme ortamı bağlantı akışı daha kararlı hale getirildi.
- Bu commit, backend yanıtlarının frontend’de sağlıklı tüketilmesi açısından kritik bir hata düzeltmesidir.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/entity/Appointment.java` (+4/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/entity/Patient.java` (+2/-0)
- `frontend/vite.config.js` (+4/-0)

---

## 11) 2522431c9279a3dfb96e5d9e9e0ea6d52d1ecd64
- Kısa hash: `2522431`
- Mesaj: date control
- Etki: 4 dosya, +53 / -1 satır

Yapılan iş:
- Tarih alanlarına ilişkin doğrulama kontrolleri eklendi.
- Backend servis katmanında geçersiz tarih verilerine karşı ek kurallar yazıldı.
- Frontend form bileşenlerinde kullanıcı girişini yönlendiren tarih kontrolleri artırıldı.
- Böylece yanlış tarih formatı/geçmiş-gelecek tarih tutarsızlığı gibi hataların hem istemci hem sunucu tarafında yakalanması hedeflendi.

Değişen dosyalar:
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/service/AppointmentService.java` (+17/-1)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/service/PatientService.java` (+14/-0)
- `frontend/src/components/AddAppointmentForm.jsx` (+12/-0)
- `frontend/src/components/AddPatientForm.jsx` (+10/-0)

---

## 12) 09d3480cb1568990e7843abaea416a815b4dc13e
- Kısa hash: `09d3480`
- Mesaj: appointment status functions and readme update
- Etki: 7 dosya, +865 / -8 satır

Yapılan iş:
- Randevu durum yönetimi özelliği eklendi: planlanan randevunun tamamlandı veya iptal edildi olarak güncellenmesi sağlandı.
- Backend tarafında `AppointmentService` içine durum değiştirme iş kuralları eklendi ve `AppointmentController` üzerinden ilgili endpoint’ler açıldı.
- Frontend tarafında `AppointmentList` bileşenine durum aksiyonları (tamamlama/iptal) bağlandı; kullanıcı etkileşimi ve görsel geri bildirimler güncellendi.
- `api.js` içinde yeni endpoint çağrıları tanımlanarak frontend-backend entegrasyonu tamamlandı.
- Randevu kartı stilinde butonlar ve durum görünümü için CSS güncellemeleri yapıldı.
- Dokümantasyon tarafında proje anlatımı güncellendi: kök `README.md` eklendi ve commit döküm dosyası (`commits.md`) oluşturuldu.

Değişen dosyalar:
- `README.md` (+479/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/controller/AppointmentController.java` (+12/-0)
- `backend/src/main/java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/service/AppointmentService.java` (+24/-0)
- `commits.md` (+228/-0)
- `frontend/src/components/AppointmentList.jsx` (+65/-8)
- `frontend/src/services/api.js` (+18/-0)
- `frontend/src/styles/AppointmentList.css` (+39/-0)
