const API_BASE_URL = 'http://localhost:8080/api';

// Patient API Calls
export const patientApi = {
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/patients`);
    if (!response.ok) throw new Error('Failed to fetch patients');
    return response.json();
  },

  getById: async (id) => {
    const response = await fetch(`${API_BASE_URL}/patients/${id}`);
    if (!response.ok) throw new Error('Failed to fetch patient');
    return response.json();
  },

  create: async (patient) => {
    const response = await fetch(`${API_BASE_URL}/patients`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patient),
    });
    if (!response.ok) throw new Error('Failed to create patient');
    return response.json();
  },

  update: async (id, patient) => {
    const response = await fetch(`${API_BASE_URL}/patients/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patient),
    });
    if (!response.ok) throw new Error('Failed to update patient');
    return response.json();
  },

  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/patients/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete patient');
  },

  getByEmail: async (email) => {
    const response = await fetch(`${API_BASE_URL}/patients/email/${email}`);
    if (!response.ok) throw new Error('Failed to fetch patient by email');
    return response.json();
  },

  getByPhoneNumber: async (phoneNumber) => {
    const response = await fetch(`${API_BASE_URL}/patients/phone/${phoneNumber}`);
    if (!response.ok) throw new Error('Failed to fetch patient by phone');
    return response.json();
  },
};

// Appointment API Calls
export const appointmentApi = {
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/appointments`);
    if (!response.ok) throw new Error('Failed to fetch appointments');
    return response.json();
  },

  getById: async (id) => {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}`);
    if (!response.ok) throw new Error('Failed to fetch appointment');
    return response.json();
  },

  create: async (appointment) => {
    const response = await fetch(`${API_BASE_URL}/appointments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointment),
    });
    if (!response.ok) throw new Error('Failed to create appointment');
    return response.json();
  },

  update: async (id, appointment) => {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointment),
    });
    if (!response.ok) throw new Error('Failed to update appointment');
    return response.json();
  },

  delete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete appointment');
  },

  getByPatientId: async (patientId) => {
    const response = await fetch(`${API_BASE_URL}/appointments/patient/${patientId}`);
    if (!response.ok) throw new Error('Failed to fetch appointments');
    return response.json();
  },

  getByStatus: async (status) => {
    const response = await fetch(`${API_BASE_URL}/appointments/status/${status}`);
    if (!response.ok) throw new Error('Failed to fetch appointments by status');
    return response.json();
  },

  schedule: async (patientId, appointment) => {
    const response = await fetch(`${API_BASE_URL}/appointments/schedule/${patientId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(appointment),
    });
    if (!response.ok) throw new Error('Failed to schedule appointment');
    return response.json();
  },

  complete: async (id) => {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to complete appointment');
    return response.json();
  },

  cancel: async (id) => {
    const response = await fetch(`${API_BASE_URL}/appointments/${id}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!response.ok) throw new Error('Failed to cancel appointment');
    return response.json();
  },
};
