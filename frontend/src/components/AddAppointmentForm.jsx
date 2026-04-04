import { useState } from 'react';
import { appointmentApi } from '../services/api';
import '../styles/AddAppointmentForm.css';

export default function AddAppointmentForm({ patientId, patientName, onAppointmentAdded }) {
  const [formData, setFormData] = useState({
    appointmentDateTime: '',
    reason: '',
    notes: ''
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
      const newAppointment = await appointmentApi.schedule(patientId, {
        appointmentDateTime: formData.appointmentDateTime,
        reason: formData.reason,
        notes: formData.notes
      });
      
      setSuccess(true);
      setFormData({
        appointmentDateTime: '',
        reason: '',
        notes: ''
      });
      onAppointmentAdded(newAppointment);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Randevu oluşturulurken hata oluştu');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!patientId) {
    return (
      <div className="add-appointment-form">
        <p className="no-selection">Randevu eklemek için sol taraftan bir hasta seçin.</p>
      </div>
    );
  }

  return (
    <div className="add-appointment-form">
      <h2>Randevu Ekle - {patientName}</h2>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Randevu başarıyla oluşturuldu!</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="appointmentDateTime">Tarih ve Saat *</label>
          <input
            type="datetime-local"
            id="appointmentDateTime"
            name="appointmentDateTime"
            value={formData.appointmentDateTime}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="reason">Randevu Sebebi</label>
          <input
            type="text"
            id="reason"
            name="reason"
            value={formData.reason}
            onChange={handleChange}
            placeholder="Örn: Kontrol, İlaç, Muayene"
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Notlar</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Ek notlar (opsiyonel)"
            rows="3"
          />
        </div>

        <button type="submit" className="btn-submit" disabled={loading}>
          {loading ? 'Oluşturuluyor...' : 'Randevu Ekle'}
        </button>
      </form>
    </div>
  );
}
