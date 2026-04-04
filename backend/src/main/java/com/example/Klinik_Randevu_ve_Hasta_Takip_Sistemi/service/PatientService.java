package com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.service;

import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.entity.Patient;
import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.repository.PatientRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import jakarta.persistence.EntityNotFoundException;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Service
public class PatientService {

    @Autowired
    private PatientRepository patientRepository;

    public Patient createPatient(Patient patient) {
        validateDateOfBirth(patient.getDateOfBirth());
        return patientRepository.save(patient);
    }

    public Patient updatePatient(Long id, Patient patientDetails) {
        validateDateOfBirth(patientDetails.getDateOfBirth());
        
        Patient patient = patientRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found with id: " + id));

        patient.setFirstName(patientDetails.getFirstName());
        patient.setLastName(patientDetails.getLastName());
        patient.setPhoneNumber(patientDetails.getPhoneNumber());
        patient.setEmail(patientDetails.getEmail());
        patient.setDateOfBirth(patientDetails.getDateOfBirth());
        patient.setMedicalHistory(patientDetails.getMedicalHistory());

        return patientRepository.save(patient);
    }

    public Patient getPatientById(Long id) {
        return patientRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Patient not found with id: " + id));
    }

    public List<Patient> getAllPatients() {
        return patientRepository.findAll();
    }

    public void deletePatient(Long id) {
        if (!patientRepository.existsById(id)) {
            throw new EntityNotFoundException("Patient not found with id: " + id);
        }
        patientRepository.deleteById(id);
    }

    public Optional<Patient> getPatientByEmail(String email) {
        return patientRepository.findByEmail(email);
    }

    public Optional<Patient> getPatientByPhoneNumber(String phoneNumber) {
        return patientRepository.findByPhoneNumber(phoneNumber);
    }

    private void validateDateOfBirth(LocalDate dateOfBirth) {
        if (dateOfBirth == null) {
            throw new IllegalArgumentException("Doğum tarihi boş olamaz");
        }
        
        if (dateOfBirth.isAfter(LocalDate.now())) {
            throw new IllegalArgumentException("Doğum tarihi geçmiş bir tarih olmalıdır");
        }
    }
}
