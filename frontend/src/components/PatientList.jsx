import { useState, useEffect } from 'react';
import { patientApi } from '../services/api';
import '../styles/PatientList.css';

export default function PatientList({ onPatientSelect, refreshTrigger }) {
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPatients();
  }, [refreshTrigger]);

  const fetchPatients = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await patientApi.getAll();
      setPatients(data);
    } catch (err) {
      setError('Hastalar yüklenemedi');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Bu hastayı silmek istediğinize emin misiniz?')) {
      try {
        await patientApi.delete(id);
        setPatients(patients.filter(p => p.id !== id));
      } catch (err) {
        setError('Hasta silinirken hata oluştu');
        console.error(err);
      }
    }
  };

  if (loading) return <div className="loading">Yükleniyor...</div>;

  return (
    <div className="patient-list">
      <h2>Hastalar</h2>
      {error && <div className="error">{error}</div>}
      
      {patients.length === 0 ? (
        <p className="no-data">Henüz hasta kaydı bulunmamaktadır.</p>
      ) : (
        <table className="patients-table">
          <thead>
            <tr>
              <th>Ad</th>
              <th>Soyad</th>
              <th>Email</th>
              <th>Telefon</th>
              <th>İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {patients.map(patient => (
              <tr key={patient.id}>
                <td>{patient.firstName}</td>
                <td>{patient.lastName}</td>
                <td>{patient.email}</td>
                <td>{patient.phoneNumber}</td>
                <td>
                  <button 
                    className="btn-view" 
                    onClick={() => onPatientSelect(patient)}
                  >
                    Randevular
                  </button>
                  <button 
                    className="btn-delete" 
                    onClick={() => handleDelete(patient.id)}
                  >
                    Sil
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
