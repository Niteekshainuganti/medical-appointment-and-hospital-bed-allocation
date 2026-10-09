"""
Reproducible Synthetic Data Generator for Hospital Management System.
Generates realistic synthetic patients, doctors, appointment slots, wards, beds, and emergency cases.
Supports fixed random seed for 100% reproducible benchmarking across dataset sizes (1k, 5k, 10k, 50k, 100k).
Includes seeded typos in 12% of patient name fields for fuzzy search validation.
"""

import random
import json
import os
from typing import Dict, List, Any

FIRST_NAMES = [
    "Aarav", "Ananya", "Rahul", "Priya", "Vikram", "Sneha", "Rohan", "Kavya", "Aditya", "Neha",
    "Siddharth", "Pooja", "Arjun", "Riya", "Karan", "Ishita", "Dev", "Meera", "Varun", "Simran",
    "John", "Emily", "Michael", "Sarah", "David", "Jessica", "Daniel", "Amanda", "James", "Jennifer"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Rao", "Gupta", "Kumar", "Singh", "Joshi", "Nair",
    "Chowdhury", "Deshmukh", "Iyer", "Banerjee", "Mehta", "Smith", "Johnson", "Williams", "Brown", "Jones"
]

SPECIALTIES = [
    "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "Oncology", "General Medicine", "Surgical ICU"
]

WARD_TYPES = [
    {"name": "Cardiology Ward", "type": "Cardiology", "capacity": 40},
    {"name": "Neurology Ward", "type": "Neurology", "capacity": 30},
    {"name": "Orthopedics Ward", "type": "Orthopedics", "capacity": 35},
    {"name": "Pediatrics Ward", "type": "Pediatrics", "capacity": 25},
    {"name": "General ICU", "type": "ICU", "capacity": 20},
    {"name": "Emergency Ward", "type": "Emergency", "capacity": 30},
    {"name": "Surgical Ward", "type": "Surgical ICU", "capacity": 30},
    {"name": "General Medical Ward", "type": "General Medicine", "capacity": 50}
]

def seed_typo(name: str, rng: random.Random) -> str:
    """
    Introduces realistic spelling typos into 12% of patient names.
    (e.g., insertion, deletion, or substitution of characters)
    """
    if len(name) < 4 or rng.random() > 0.12:
        return name

    chars = list(name)
    typo_type = rng.choice(["insert", "delete", "substitute", "swap"])
    pos = rng.randint(1, len(chars) - 2)

    if typo_type == "insert":
        chars.insert(pos, rng.choice("abcdefghijklmnopqrstuvwxyz"))
    elif typo_type == "delete":
        del chars[pos]
    elif typo_type == "substitute":
        chars[pos] = rng.choice("aeiou") if chars[pos].lower() in "aeiou" else rng.choice("bcdfghjklmnpqrstvwxyz")
    elif typo_type == "swap" and pos < len(chars) - 1:
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]

    return "".join(chars)


def generate_synthetic_data(num_patients: int = 1000, seed: int = 42) -> Dict[str, Any]:
    """
    Generates synthetic hospital records dataset.
    """
    rng = random.Random(seed)

    # 1. Wards & Beds
    wards = []
    beds = []
    bed_id_counter = 101

    for w_idx, wt in enumerate(WARD_TYPES):
        w_id = f"W-{w_idx + 1:02d}"
        wards.append({
            "ward_id": w_id,
            "ward_name": wt["name"],
            "ward_type": wt["type"],
            "specialty": wt["type"],
            "total_beds": wt["capacity"],
            "occupied_beds": 0
        })

        for b in range(wt["capacity"]):
            b_id = f"BED-{bed_id_counter}"
            bed_number = f"{wt['type'][:3].upper()}-{b + 1:02d}"
            # 70% available, 30% pre-occupied for initial state realism
            status = "Occupied" if rng.random() < 0.30 else "Available"
            beds.append({
                "bed_id": b_id,
                "bed_number": bed_number,
                "ward_id": w_id,
                "status": status,
                "patient_id": None if status == "Available" else f"PRE-{b_id}"
            })
            bed_id_counter += 1

    # 2. Doctors & Slots
    doctors = []
    slots = []
    slot_id_counter = 1

    doc_counter = 1
    for spec in SPECIALTIES:
        for _ in range(rng.randint(6, 10)):
            d_id = f"DOC-{doc_counter:03d}"
            d_name = f"Dr. {rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"
            doctors.append({
                "doctor_id": d_id,
                "name": d_name,
                "specialty": spec,
                "room_no": f"Room {rng.randint(101, 405)}",
                "availability": "Available"
            })
            doc_counter += 1

            # Generate slots (09:00 to 17:00 in 30-min increments)
            for hour in range(9, 17):
                for minute in (0, 30):
                    s_id = f"SLOT-{slot_id_counter:05d}"
                    start_str = f"{hour:02d}:{minute:02d}"
                    end_str = f"{hour:02d}:{minute + 25:02d}"
                    slots.append({
                        "slot_id": s_id,
                        "doctor_id": d_id,
                        "date": "2026-10-10",
                        "start_time": start_str,
                        "end_time": end_str,
                        "is_booked": False
                    })
                    slot_id_counter += 1

    # 3. Patients
    patients = []
    for i in range(1, num_patients + 1):
        p_id = f"PAT-{i:05d}"
        f_name = rng.choice(FIRST_NAMES)
        l_name = rng.choice(LAST_NAMES)
        clean_name = f"{f_name} {l_name}"
        typo_name = seed_typo(clean_name, rng)

        spec = rng.choice(SPECIALTIES)
        urgency = rng.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.50, 0.25, 0.10])[0]

        patients.append({
            "patient_id": p_id,
            "name": typo_name,
            "original_clean_name": clean_name,
            "age": rng.randint(1, 85),
            "gender": rng.choice(["Male", "Female", "Other"]),
            "phone": f"+91-98{rng.randint(10000000, 99999999)}",
            "required_specialty": spec,
            "required_ward_type": spec,
            "urgency_level": urgency,
            "preferred_doctor_id": rng.choice(doctors)["doctor_id"] if rng.random() < 0.25 else None,
            "status": "Pending Allocation"
        })

    # 4. Emergency Cases (12% of total population marked as emergency cases)
    emergencies = []
    num_emergencies = max(10, int(num_patients * 0.12))
    for i in range(num_emergencies):
        p_info = patients[i]
        emergencies.append({
            "emergency_id": f"EMG-{i + 1:04d}",
            "patient_id": p_info["patient_id"],
            "name": p_info["name"],
            "urgency_level": p_info["urgency_level"],
            "required_specialty": p_info["required_specialty"],
            "required_ward_type": p_info["required_ward_type"],
            "arrival_time_min": rng.randint(480, 1080),  # between 8 AM and 6 PM
            "vital_signs_severity": round(rng.uniform(1.2, 3.0), 2),
            "status": "Queued"
        })

    return {
        "metadata": {
            "seed": seed,
            "num_patients": num_patients,
            "num_doctors": len(doctors),
            "num_slots": len(slots),
            "num_wards": len(wards),
            "num_beds": len(beds),
            "num_emergencies": len(emergencies)
        },
        "wards": wards,
        "beds": beds,
        "doctors": doctors,
        "slots": slots,
        "patients": patients,
        "emergencies": emergencies
    }


def export_sample_data(filepath: str, num_patients: int = 1000, seed: int = 42):
    """
    Exports synthetic dataset to JSON file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    data = generate_synthetic_data(num_patients=num_patients, seed=seed)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Sample data successfully exported to '{filepath}' (Patients: {num_patients}).")


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(__file__), "sample_hospital_data.json")
    export_sample_data(out_path, num_patients=1000, seed=42)
