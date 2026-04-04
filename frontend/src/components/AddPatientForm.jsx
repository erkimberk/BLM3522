import { useState } from 'react';
import { patientApi } from '../services/api';
import '../styles/AddPatientForm.css';

export default function AddPatientForm({ onPatientAdded }) {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phoneNumber: '',
    dateOfBirth: '',
    medicalHistory: ''
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const newPatient = await patientApi.create(formData);
      setSuccess(true);
      setFormData({
        firstName: '',
        lastName: '',
        email: '',
        phoneNumber: '',
        dateOfBirth: '',
        medicalHistory: ''
      });
      onPatientAdded(newPatient);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Hasta kaydedilirken hata oluştu');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-patient-form">
      <h2>Yeni Hasta Ekle</h2>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Hasta başarıyla kaydedildi!</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="firstName">Ad *</label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              required
              placeholder="Ad"
            />
          </div>
          <div className="form-group">
            <label htmlFor="lastName">Soyadı *</label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              required
              placeholder="Soyadı"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="email">Email *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Email"
            />
          </div>
          <div className="form-group">
            <label htmlFor="phoneNumber">Telefon *</label>
            <input
              type="tel"
              id="phoneNumber"
              name="phoneNumber"
              value={formData.phoneNumber}
              onChange={handleChange}
              required
              placeholder="Telefon"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="dateOfBirth">Doğum Tarihi *</label>
            <input
              type="date"
              id="dateOfBirth"
              name="dateOfBirth"
              value={formData.dateOfBirth}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="medicalHistory">Tıbbi Geçmiş</label>
          <textarea
            id="medicalHistory"
            name="medicalHistory"
            value={formData.medicalHistory}
            onChange={handleChange}
            placeholder="Hastanın tıbbi geçmişi (opsiyonel)"
            rows="4"
          />
        </div>

        <button type="submit" className="btn-submit" disabled={loading}>
          {loading ? 'Kaydediliyor...' : 'Hasta Ekle'}
        </button>
      </form>
    </div>
  );
}
