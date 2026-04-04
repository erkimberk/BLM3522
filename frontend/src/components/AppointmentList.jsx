import { useState, useEffect } from 'react';
import { appointmentApi } from '../services/api';
import '../styles/AppointmentList.css';

export default function AppointmentList({ patientId, patientName, refreshTrigger }) {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (patientId) {
      fetchAppointments();
    }
  }, [patientId, refreshTrigger]);

  const fetchAppointments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await appointmentApi.getByPatientId(patientId);
      setAppointments(data);
    } catch (err) {
      setError('Randevular yüklenemedi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bu randevuyu silmek istediğinize emin misiniz?')) {
      try {
        await appointmentApi.delete(id);
        setAppointments(appointments.filter(a => a.id !== id));
      } catch (err) {
        setError('Randevu silinirken hata oluştu');
        console.error(err);
      }
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SCHEDULED':
        return '#ffc107';
      case 'COMPLETED':
        return '#28a745';
      case 'CANCELLED':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const formatDateTime = (dateTime) => {
    return new Date(dateTime).toLocaleString('tr-TR');
  };

  if (!patientId) {
    return (
      <div className="appointment-list">
        <p className="no-selection">Randevularını görmek için sol taraftan bir hasta seçin.</p>
      </div>
    );
  }

  if (loading) return <div className="loading">Yükleniyor...</div>;

  return (
    <div className="appointment-list">
      <h2>Randevular - {patientName}</h2>
      {error && <div className="error">{error}</div>}
      
      {appointments.length === 0 ? (
        <p className="no-data">Bu hastanın randevusu bulunmamaktadır.</p>
      ) : (
        <div className="appointments-container">
          {appointments.map(appointment => (
            <div key={appointment.id} className="appointment-card">
              <div className="appointment-header">
                <span 
                  className="status-badge" 
                  style={{ backgroundColor: getStatusColor(appointment.status) }}
                >
                  {appointment.status}
                </span>
                <button 
                  className="btn-delete-small" 
                  onClick={() => handleDelete(appointment.id)}
                  title="Randevuyu sil"
                >
                  ✕
                </button>
              </div>
              
              <div className="appointment-details">
                <div className="detail-item">
                  <span className="label">Tarih & Saat:</span>
                  <span className="value">{formatDateTime(appointment.appointmentDateTime)}</span>
                </div>
                
                {appointment.reason && (
                  <div className="detail-item">
                    <span className="label">Sebep:</span>
                    <span className="value">{appointment.reason}</span>
                  </div>
                )}
                
                {appointment.notes && (
                  <div className="detail-item">
                    <span className="label">Notlar:</span>
                    <span className="value">{appointment.notes}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
