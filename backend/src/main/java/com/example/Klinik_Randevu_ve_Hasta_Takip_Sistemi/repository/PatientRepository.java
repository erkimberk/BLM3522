package com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.repository;

import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.entity.Patient;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface PatientRepository extends JpaRepository<Patient, Long> {
    Optional<Patient> findByEmail(String email);
    Optional<Patient> findByPhoneNumber(String phoneNumber);
}
