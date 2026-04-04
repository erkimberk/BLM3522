import { useState } from 'react';
import PatientList from './components/PatientList';
import AddPatientForm from './components/AddPatientForm';
import AppointmentList from './components/AppointmentList';
import AddAppointmentForm from './components/AddAppointmentForm';
import './App.css';

function App() {
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [refreshPatients, setRefreshPatients] = useState(0);
  const [refreshAppointments, setRefreshAppointments] = useState(0);

  const handlePatientSelected = (patient) => {
    setSelectedPatient(patient);
  };

  const handlePatientAdded = (newPatient) => {
    setRefreshPatients(prev => prev + 1);
  };

  const handleAppointmentAdded = (newAppointment) => {
    setRefreshAppointments(prev => prev + 1);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Klinik Randevu ve Hasta Takip Sistemi</h1>
        <p>Hasta ve randevu yönetimi platformu</p>
      </header>

      <div className="app-body">
        <div className="left-panel">
          <AddPatientForm onPatientAdded={handlePatientAdded} />
          <PatientList 
            onPatientSelect={handlePatientSelected}
            refreshTrigger={refreshPatients}
          />
        </div>

        <div className="right-panel">
          <div className="right-top">
            <AddAppointmentForm 
              patientId={selectedPatient?.id}
              patientName={selectedPatient ? `${selectedPatient.firstName} ${selectedPatient.lastName}` : ''}
              onAppointmentAdded={handleAppointmentAdded}
            />
          </div>
          <div className="right-bottom">
            <AppointmentList 
              patientId={selectedPatient?.id}
              patientName={selectedPatient ? `${selectedPatient.firstName} ${selectedPatient.lastName}` : ''}
              refreshTrigger={refreshAppointments}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
