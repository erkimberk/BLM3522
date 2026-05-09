"""
Trash Bin Fill Level Sensor Simulator
Çöp kutusu doluluk sensörü - Fiziksel hacim ve ağırlık simülasyonu
"""

import random
from datetime import datetime


class TrashBinSensor:
    """
    Çöp kutusu doluluk sensörü simülasyonu
    
    Özellikler:
    - fill_level: Doluluk yüzdesi (0-100%)
    - weight_kg: Çöp ağırlığı (kg)
    - collection_needed: Boşaltma gerekli mi?
    - last_collection: Son boşaltma zamanı
    """

    def __init__(self, location_id: str = "Street Corner", max_weight_kg: float = 50.0):
        """
        Sensörü başlat.
        
        Args:
            location_id: Sensörün konumu
            max_weight_kg: Maksimum kapasite (kg)
        """
        self.location_id = location_id
        self.max_weight_kg = max_weight_kg
        self.current_weight_kg = random.uniform(5, 20)  # Başlangıç ağırlığı
        self.daily_accumulation = 0

    def simulate_trash_accumulation(self):
        """
        Her çağrıldığında çöp miktarı artır.
        (Gerçek dünyada çöpler sabit zaman aralıklarında atılır)
        """
        # Günün saatine göre çöp atılma oranı (simülasyon)
        # Peak hours: 12:00-14:00, 18:00-20:00
        hourly_trash = random.uniform(0.5, 3.0)  # kg/hour
        self.current_weight_kg = min(self.max_weight_kg, self.current_weight_kg + hourly_trash)
        self.daily_accumulation += hourly_trash

    def empty_bin(self):
        """
        Çöp kutusunu boşalt (collection service çağrılmış).
        """
        self.current_weight_kg = 0
        self.daily_accumulation = 0

    def generate_data(self) -> dict:
        """
        Gerçekçi çöp doluluk verisi üret.
        
        Returns:
            dict: Çöp doluluk verileri
        """
        # Çöp birikimi simülasyonu
        self.simulate_trash_accumulation()

        # Doluluk yüzdesi
        fill_percent = (self.current_weight_kg / self.max_weight_kg) * 100
        fill_percent = min(100, max(0, fill_percent))

        # Boşaltma gerekli mi?
        needs_collection = fill_percent >= 85

        return {
            "timestamp": datetime.now().isoformat(),
            "device": "trash-bin-001",
            "location": self.location_id,
            "metric": "fill_level",
            "fill_percentage": round(fill_percent, 2),
            "weight_kg": round(self.current_weight_kg, 2),
            "max_capacity_kg": self.max_weight_kg,
            "daily_accumulation_kg": round(self.daily_accumulation, 2),
            "collection_needed": needs_collection,
            "collection_urgency": self._get_urgency(fill_percent),
        }

    def _get_urgency(self, fill_percent: float) -> str:
        """
        Doluluk seviyesine göre aciliyet belirle.
        
        Args:
            fill_percent: Doluluk yüzdesi
            
        Returns:
            str: "low", "medium", "high", "critical"
        """
        if fill_percent < 33:
            return "low"
        elif fill_percent < 66:
            return "medium"
        elif fill_percent < 85:
            return "high"
        else:
            return "critical"
