# Klinik Randevu ve Hasta Takip Sistemi - Erkim Berk Ünsal

## 📋 Proje Açıklaması

Bu proje, BLM3522 Bulut Bilişim dersi kapsamında geliştirilmiş bir **çift katmanlı web uygulamasıdır**. Kliniklerin randevu yönetimi ve hasta takibini kolaylaştırmak için tasarlanmıştır. Sistem; hasta bilgilerini yönetmeyi, randevu planlamayı ve randevu durumlarını takip etmeyi mümkün kılar.

### 🎯 Amaç

- Hasta bilgilerinin merkezi bir yerde toplanması ve yönetilmesi
- Klinik randevuları planlamak ve düzenlemek
- Randevu durumlarını (Planlandı, Tamamlandı, İptal Edildi) takip etmek
- RESTFUL API'nin frontend uygulaması ile entegrasyonunu göstermek
- Bulut platformlarında dağıtılabilir, ölçeklenebilir bir mimari sunmak

---

## 🛠️ Teknoloji Yığını

### Backend
- **Framework:** Spring Boot 4.0.5
- **Dil:** Java 17
- **Veritabanı:** PostgreSQL
- **ORM:** Hibernate (JPA)
- **Build Tool:** Maven
- **Bağımlılıklar:**
  - Spring Boot Starter Web (REST API)
  - Spring Boot Starter Data JPA (Veritabanı işlemleri)
  - Lombok (Boilerplate kod azaltma)
  - PostgreSQL Driver

### Frontend
- **Framework:** React 19.2.4
- **Build Tool:** Vite 5.4.21
- **Stil:** CSS3
- **Paket Yöneticisi:** npm
- **Runtime:** Node.js

### Diğer Teknolojiler
- **API İletişimi:** REST, Fetch API (Son zamanlarda axios hacklendiği için bilerek fect API tercih edilmiştir)
- **CORS:** Spring Boot CORS Config (frontend: http://localhost:5173)
- **JSON Serialization:** Jackson

---

## 📦 Gereksinimler

### Sistem Gereksinimleri
- JDK 17 veya daha yeni sürümü
- Node.js 16+ ve npm
- PostgreSQL 12+
- Git

### Port Gereksinikleri
- **Backend:** 8080 (Spring Boot)
- **Frontend:** 5173 (Vite Development Server)
- **PostgreSQL:** 5432

---

## 🚀 Kurulum ve Çalıştırma

### 1. Veritabanı Kurulumu

PostgreSQL'de yeni bir veritabanı oluşturun:

```sql
CREATE DATABASE klinik_db;
```

Veritabanı bağlantı bilgilerini `backend/src/main/resources/application.properties` dosyasında düzenleyin:

```properties
spring.datasource.url=jdbc:postgresql://localhost:5432/klinik_db
spring.datasource.username=postgres
spring.datasource.password=postgres
```

### 2. Backend Kurulumu ve Çalıştırması

```bash
# Backend klasörüne gitme
cd backend

# Maven ile projeyi derle ve çalıştır
./mvnw spring-boot:run

# Windows kullanıyorsanız:
mvnw.cmd spring-boot:run
```

Backend başarıyla başlatıldığında `http://localhost:8080` adresinde çalışmaya başlayacaktır.

### 3. Frontend Kurulumu ve Çalıştırması

```bash
# Frontend klasörüne gitme
cd frontend

# Bağımlılıkları yükle
npm install

# Development sunucusunu başlat
npm run dev

# Production için build et
npm run build
```

Frontend başarıyla başlatıldığında `http://localhost:5173` adresinde çalışmaya başlayacaktır.

---

## 📁 Proje Yapısı

```
BLM3522-project-1/
├── backend/                          # Spring Boot Backend
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/example/Klinik_Randevu_ve_Hasta_Takip_Sistemi/
│   │   │   │   ├── KlinikRandevuVeHastaTakipSistemiApplication.java
│   │   │   │   ├── config/              # Konfigürasyon Sınıfları
│   │   │   │   │   └── CorsConfig.java
│   │   │   │   ├── controller/          # API Controllers
│   │   │   │   │   ├── AppointmentController.java
│   │   │   │   │   └── PatientController.java
│   │   │   │   ├── entity/              # JPA Entity Sınıfları
│   │   │   │   │   ├── Patient.java
│   │   │   │   │   └── Appointment.java
│   │   │   │   ├── repository/          # Data Access Layer
│   │   │   │   │   ├── PatientRepository.java
│   │   │   │   │   └── AppointmentRepository.java
│   │   │   │   └── service/             # İş Mantığı Katmanı
│   │   │   │       ├── PatientService.java
│   │   │   │       └── AppointmentService.java
│   │   │   └── resources/
│   │   │       └── application.properties
│   │   └── test/                     # Test Sınıfları
│   ├── pom.xml                       # Maven Konfigürasyonu
│   └── mvnw/mvnw.cmd                 # Maven Wrapper
│
├── frontend/                          # React Frontend
│   ├── src/
│   │   ├── components/               # React Bileşenleri
│   │   │   ├── AppointmentList.jsx
│   │   │   ├── PatientList.jsx
│   │   │   ├── AddAppointmentForm.jsx
│   │   │   └── AddPatientForm.jsx
│   │   ├── services/                 # API Service
│   │   │   └── api.js
│   │   ├── styles/                   # CSS Dosyaları
│   │   │   ├── AppointmentList.css
│   │   │   ├── PatientList.css
│   │   │   ├── AddAppointmentForm.css
│   │   │   └── AddPatientForm.css
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
└── README.md                          # Bu Dosya
```

---

## 💾 Veritabanı Şeması

### patients Tablosu

| Sütun | Tür | Kısıtlamalar | Açıklama |
|-------|-----|-------------|----------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Hasta ID'si |
| first_name | VARCHAR(100) | NOT NULL | Adı |
| last_name | VARCHAR(100) | NOT NULL | Soyadı |
| phone_number | VARCHAR(20) | NOT NULL, UNIQUE | Telefon Numarası |
| email | VARCHAR(100) | UNIQUE | E-posta Adresi |
| date_of_birth | DATE | | Doğum Tarihi |
| gender | VARCHAR(10) | | Cinsiyet |
| address | VARCHAR(255) | | Adres |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Oluşturma Tarihi |

### appointments Tablosu

| Sütun | Tür | Kısıtlamalar | Açıklama |
|-------|-----|-------------|----------|
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Randevu ID'si |
| appointment_date_time | TIMESTAMP | NOT NULL | Randevu Tarihi ve Saati |
| reason | VARCHAR(500) | | Randevu Sebebi |
| notes | VARCHAR(500) | | Notlar |
| status | VARCHAR(50) | NOT NULL | Durum (SCHEDULED, COMPLETED, CANCELLED) |
| patient_id | BIGINT | FOREIGN KEY | İlişkili Hasta |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Oluşturma Tarihi |

---

## 🔌 API Endpoint'leri

### Hasta (Patient) API'si

#### Tüm Hastaları Getir
```
GET /api/patients
```

#### Belirli Bir Hastayı Getir
```
GET /api/patients/{id}
```

#### Yeni Hasta Ekle
```
POST /api/patients
Content-Type: application/json

{
  "firstName": "Erkim Berk",
  "lastName": "Ünsal",
  "phoneNumber": "+90 5XX XXX XXXX",
  "email": "erkim@example.com",
  "dateOfBirth": "1990-01-15",
  "gender": "Erkek",
  "address": "Ankara, Türkiye"
}
```

#### Hasta Bilgilerini Güncelle
```
PUT /api/patients/{id}
Content-Type: application/json

{
  "firstName": "Erkim Berk",
  "lastName": "Ünsal",
  "phoneNumber": "+90 5XX XXX XXXX",
  "email": "erkim@example.com",
  "dateOfBirth": "1990-01-15",
  "gender": "Erkek",
  "address": "Ankara, Türkiye"
}
```

#### Hasta Sil
```
DELETE /api/patients/{id}
```

#### E-posta ile Hasta Ara
```
GET /api/patients/email/{email}
```

#### Telefon Numarası ile Hasta Ara
```
GET /api/patients/phone/{phoneNumber}
```

---

### Randevu (Appointment) API'si

#### Tüm Randevuları Getir
```
GET /api/appointments
```

#### Belirli Bir Randevuyu Getir
```
GET /api/appointments/{id}
```

#### Yeni Randevu Oluştur
```
POST /api/appointments
Content-Type: application/json

{
  "appointmentDateTime": "2026-04-15T14:30",
  "reason": "Muayene",
  "notes": "Ek notlar...",
  "status": "SCHEDULED",
  "patient": {
    "id": 1
  }
}
```

#### Randevu Bilgilerini Güncelle
```
PUT /api/appointments/{id}
Content-Type: application/json

{
  "appointmentDateTime": "2026-04-15T14:30",
  "reason": "Muayene",
  "notes": "Ek notlar...",
  "status": "SCHEDULED",
  "patient": {
    "id": 1
  }
}
```

#### Randevu Sil
```
DELETE /api/appointments/{id}
```

#### Hastaya Ait Randevuları Getir
```
GET /api/appointments/patient/{patientId}
```

#### Duruma Göre Randevuları Getir
```
GET /api/appointments/status/{status}
```

Örnek: `/api/appointments/status/SCHEDULED`

#### Randevu Planla
```
POST /api/appointments/schedule/{patientId}
Content-Type: application/json

{
  "appointmentDateTime": "2026-04-15T14:30",
  "reason": "Muayene",
  "notes": "Ek notlar..."
}
```

#### Randevuyu Tamamlandı Olarak İşaretle
```
POST /api/appointments/{id}/complete
```

#### Randevuyu İptal Et
```
POST /api/appointments/{id}/cancel
```

---

## 🎨 Frontend Özellikleri

### Hastalar Sayfası
- Tüm hastaların listesi
- Yeni hasta ekleme formu
- Hasta bilgilerini görüntüleme
- Hasta silme işlemi

### Randevular Sayfası
- Seçilen hastanın randevularını listeleme
- Randevu ekleme formu
- Randevu durumlarını şu şekilde gösterme:
  - **Planlandı** (Sarı)
  - **Tamamlandı** (Yeşil)
  - **İptal Edildi** (Kırmızı)
- Randev durumlarını güncelleme:
  - "✓ Tamamlandı" butonu
  - "✕ İptal Et" butonu
- Randevu silme işlemi
- Tarih ve saat formatı: Türkçe yerel format

---

## 🔄 Uygulama Akışı

```
Frontend (React)
    ↓
Fetch API / REST
    ↓
Backend (Spring Boot)
    ↓
Spring Data JPA
    ↓
PostgreSQL
```

1. **Kullanıcı etkileşimi:** Frontend'de kullanıcı hasta veya randevu ekler
2. **API isteği:** React, REST API'ye HTTP isteği gönderir
3. **Sunucu işlemi:** Spring Boot, isteği işler ve iş mantığını uygular
4. **Veritabanı işlemi:** Veriler PostgreSQL'e kaydedilir/okunur
5. **Yanıt:** Backend, JSON formatında yanıt döner
6. **Görsite güncellemesi:** Frontend sayfayı günceller

---

## 🧪 Test Etme

### Manual API Testi (cURL, Postman vb.)

```bash
# Tüm hastaları getir
curl http://localhost:8080/api/patients

# Yeni hasta ekle
curl -X POST http://localhost:8080/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Mehmet",
    "lastName": "Kaya",
    "phoneNumber": "+90 5XX XXX XXXX"
  }'
```

### Frontend Testi
- Tarayıcıda `http://localhost:5173` açın
- Hasta ekle, randevu ekle, durumları değiştir işlemlerini test edin
- Konsol hatalarını (F12) kontrol edin

---

## 🚀 Bulut Platformasında Dağıtım

### AWS'de Dağıtım
- EC2 üzerinde Spring Boot uygulaması
- RDS PostgreSQL veritabanı
- S3'te frontend dağıtımı
- CloudFront CDN

### Azure'da Dağıtım
- App Service üzerinde Spring Boot
- SQL Database PostgreSQL
- Static Web App üzerinde React frontend
- Application Insights ile monitoring

### Google Cloud'da Dağıtım
- Compute Engine üzerinde uygulamalar
- Cloud SQL PostgreSQL
- Cloud Storage üzerinde statik dosyalar
- Cloud Load Balancing

*Daha detaylı bilgi için wiki'ye bakınız.*

---

## 📚 Kaynaklar

- [Spring Boot Resmi Dokümantasyonu](https://spring.io/projects/spring-boot)
- [React Resmi Dokümantasyonu](https://react.dev)
- [PostgreSQL Resmi Dokümantasyonu](https://www.postgresql.org/docs/)
- [REST API Best Practices](https://restfulapi.net/)
- [MDN Web Docs](https://developer.mozilla.org/)

---

## 👨‍💻 Geliştirici

**Proje Sahibi:** Erkim Berk Ünsal
**Dersin Adı:** BLM3522 - Bulut Bilişim ve Uygulamarı
**Proje:** Çift Katmanlı Web Uygulaması (Proje 1)  

---

## 📄 Lisans

Bu proje BLM3522 dersi kapsamında öğrenme amacıyla geliştirilmiştir.

---

## 📹 Proje Videosu

Proje hakkında detaylı bir anlatım videosu aşağıdaki linkte bulunmaktadır:

[Klinik Randevu ve Hasta Takip Sistemi - Proje Videosu](https://youtu.be/4YEXJam_Y9c)

*Video: BLM3522 Bulut Bilişim Dersi - Proje 1 Sunumu*

---

**Son Güncelleme:** 5 Nisan 2026

---

