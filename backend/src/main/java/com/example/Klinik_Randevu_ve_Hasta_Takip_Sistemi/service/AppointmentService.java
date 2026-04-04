package com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.service;

import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.entity.Appointment;
import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.entity.Patient;
import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.repository.AppointmentRepository;
import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.repository.PatientRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import jakarta.persistence.EntityNotFoundException;
import java.time.LocalDateTime;
import java.util.List;

@Service
public class AppointmentService {

    @Autowired
    private AppointmentRepository appointmentRepository;

    @Autowired
    private PatientRepository patientRepository;

    public Appointment createAppointment(Appointment appointment) {
        validateAppointmentDateTime(appointment.getAppointmentDateTime());
        return appointmentRepository.save(appointment);
    }

    public Appointment updateAppointment(Long id, Appointment appointmentDetails) {
        validateAppointmentDateTime(appointmentDetails.getAppointmentDateTime());

        Appointment appointment = appointmentRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Appointment not found with id: " + id));

        appointment.setAppointmentDateTime(appointmentDetails.getAppointmentDateTime());
        appointment.setReason(appointmentDetails.getReason());
        appointment.setNotes(appointmentDetails.getNotes());
        appointment.setStatus(appointmentDetails.getStatus());
        appointment.setPatient(appointmentDetails.getPatient());

        return appointmentRepository.save(appointment);
    }

    public Appointment getAppointmentById(Long id) {
        return appointmentRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Appointment not found with id: " + id));
    }

    public List<Appointment> getAllAppointments() {
        return appointmentRepository.findAll();
    }

    public List<Appointment> getAppointmentsByPatientId(Long patientId) {
        if (!patientRepository.existsById(patientId)) {
            throw new EntityNotFoundException("Patient not found with id: " + patientId);
        }
        return appointmentRepository.findByPatientId(patientId);
    }

    public List<Appointment> getAppointmentsByStatus(String status) {
        return appointmentRepository.findByStatus(status);
    }

    public void deleteAppointment(Long id) {
        if (!appointmentRepository.existsById(id)) {
            throw new EntityNotFoundException("Appointment not found with id: " + id);
        }
        appointmentRepository.deleteById(id);
    }

    public Appointment scheduleAppointment(Long patientId, Appointment appointment) {
        validateAppointmentDateTime(appointment.getAppointmentDateTime());

        Patient patient = patientRepository.findById(patientId)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found with id: " + patientId));

        appointment.setPatient(patient);
        appointment.setStatus("SCHEDULED");

        return appointmentRepository.save(appointment);
    }

    private void validateAppointmentDateTime(LocalDateTime appointmentDateTime) {
        if (appointmentDateTime == null) {
            throw new IllegalArgumentException("Randevu tarihi boş olamaz");
        }

        if (appointmentDateTime.isBefore(LocalDateTime.now())) {
            throw new IllegalArgumentException("Randevu tarihi şu anki tarihten ileri olmalıdır");
        }
    }
}