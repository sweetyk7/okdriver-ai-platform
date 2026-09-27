"""
Government Database Integration Router (Mock APIs).
Simulates lookups against VAHAN, SARTHI, eGujCop (CCTNS).
In production, these would call real government API endpoints.
"""
from fastapi import APIRouter
import random

router = APIRouter()

# --- Sample data pools for realistic mock responses ---
_NAMES = ["Rajesh Kumar Patel", "Amit Shah", "Priya Sharma", "Vikram Singh Rajput",
          "Meera Ben Desai", "Harsh Patel", "Anita Rao", "Suresh Mehta"]
_VEHICLES = ["Maruti Suzuki Dzire", "Hyundai i20", "Tata Nexon", "Honda City",
             "Mahindra XUV500", "Toyota Innova", "Kia Seltos", "Maruti Ertiga"]
_RTOS = ["GJ-01 Ahmedabad", "GJ-02 Mehsana", "GJ-03 Rajkot", "GJ-05 Surat",
         "GJ-06 Vadodara", "GJ-10 Jamnagar", "GJ-12 Anand", "GJ-15 Junagadh"]


@router.get("/vahan/{plate_number}")
def lookup_vahan(plate_number: str):
    """
    Simulate VAHAN database lookup for vehicle registration details.
    VAHAN is the national vehicle registration database maintained by MoRTH.
    """
    return {
        "plate": plate_number,
        "owner": random.choice(_NAMES),
        "vehicle_type": random.choice(["Car - Sedan", "Car - SUV", "Two-Wheeler", "Auto-Rickshaw", "Bus"]),
        "make_model": random.choice(_VEHICLES),
        "fuel_type": random.choice(["Petrol", "Diesel", "CNG", "Electric"]),
        "color": random.choice(["White", "Black", "Silver", "Red", "Blue"]),
        "registration_date": f"20{random.randint(15,24)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "insurance_valid": random.choice([True, True, True, False]),
        "fitness_valid": random.choice([True, True, True, False]),
        "rto": random.choice(_RTOS),
        "status": random.choice(["Active", "Active", "Active", "Suspended", "Blacklisted"]),
        "challan_pending": random.randint(0, 5),
        "source": "VAHAN (Mock)"
    }


@router.get("/sarthi/{license_number}")
def lookup_sarthi(license_number: str):
    """
    Simulate SARTHI database lookup for driving license details.
    SARTHI is the national driving license database.
    """
    return {
        "license_number": license_number,
        "name": random.choice(_NAMES),
        "father_name": random.choice(_NAMES),
        "dob": f"19{random.randint(70,99)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "valid_from": f"20{random.randint(15,22)}-01-01",
        "valid_till": f"20{random.randint(28,35)}-01-01",
        "vehicle_classes": random.choice([["LMV"], ["LMV", "MCWG"], ["LMV", "HMV"], ["MCWG"]]),
        "status": random.choice(["Valid", "Valid", "Valid", "Expired", "Suspended"]),
        "violations": random.randint(0, 8),
        "blood_group": random.choice(["A+", "B+", "O+", "AB+", "O-"]),
        "issuing_rto": random.choice(_RTOS),
        "source": "SARTHI (Mock)"
    }


@router.get("/egujcop/{person_id}")
def lookup_egujcop(person_id: str):
    """
    Simulate eGujCop (CCTNS) criminal record lookup.
    eGujCop is Gujarat Police's Crime and Criminal Tracking Network.
    """
    has_record = random.random() < 0.3  # 30% chance of having a record
    return {
        "person_id": person_id,
        "name": random.choice(_NAMES) if has_record else "No Match Found",
        "criminal_record": has_record,
        "fir_count": random.randint(1, 5) if has_record else 0,
        "cases": [
            {"fir_no": f"FIR/{random.randint(2020,2026)}/{random.randint(100,999)}",
             "section": random.choice(["IPC 379", "IPC 420", "IPC 302", "IPC 354"]),
             "status": random.choice(["Under Investigation", "Chargesheeted", "Convicted"])}
        ] if has_record else [],
        "wanted": has_record and random.random() < 0.2,
        "last_known_district": random.choice(["Ahmedabad", "Surat", "Rajkot", "Vadodara"]) if has_record else None,
        "source": "eGujCop/CCTNS (Mock)"
    }


@router.get("/nafis/{fingerprint_id}")
def lookup_nafis(fingerprint_id: str):
    """
    Simulate NAFIS (National Automated Fingerprint Identification System) lookup.
    """
    has_match = random.random() < 0.15
    return {
        "fingerprint_id": fingerprint_id,
        "match_found": has_match,
        "match_confidence": round(random.uniform(0.85, 0.99), 3) if has_match else 0,
        "matched_person": random.choice(_NAMES) if has_match else None,
        "criminal_record": has_match,
        "source": "NAFIS (Mock)"
    }
