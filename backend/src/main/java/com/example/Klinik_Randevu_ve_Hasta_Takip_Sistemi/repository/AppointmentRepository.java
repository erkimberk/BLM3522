package com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.repository;

import com.example.Klinik_Randevu_ve_Hasta_Takip_Sistemi.entity.Appointment;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AppointmentRepository extends JpaRepository<Appointment, Long> {
    List<Appointment> findByPatientId(Long patientId);
    List<Appointment> findByStatus(String status);
}
