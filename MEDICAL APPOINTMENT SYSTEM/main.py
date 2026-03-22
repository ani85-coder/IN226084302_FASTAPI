from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
import math

app = FastAPI()

# =========================
# DATA
# =========================
doctors = [
    {
        "id": 1,
        "name": "Dr. Mehta",
        "specialization": "Cardiologist",
        "fee": 1200,
        "experience_years": 12,
        "is_available": True,
    },
    {
        "id": 2,
        "name": "Dr. Shah",
        "specialization": "Dermatologist",
        "fee": 900,
        "experience_years": 8,
        "is_available": True,
    },
    {
        "id": 3,
        "name": "Dr. Patil",
        "specialization": "Pediatrician",
        "fee": 1000,
        "experience_years": 10,
        "is_available": False,
    },
    {
        "id": 4,
        "name": "Dr. Rao",
        "specialization": "General",
        "fee": 700,
        "experience_years": 6,
        "is_available": True,
    },
    {
        "id": 5,
        "name": "Dr. Kapoor",
        "specialization": "Cardiologist",
        "fee": 1500,
        "experience_years": 15,
        "is_available": True,
    },
    {
        "id": 6,
        "name": "Dr. Iyer",
        "specialization": "General",
        "fee": 650,
        "experience_years": 5,
        "is_available": True,
    },
]

appointments = []
appt_counter = 1


# =========================
# MODELS
# =========================
class AppointmentRequest(BaseModel):
    patient_name: str = Field(..., min_length=2)
    doctor_id: int = Field(..., gt=0)
    date: str = Field(..., min_length=8)
    reason: str = Field(..., min_length=5)
    appointment_type: str = Field(default="in-person")
    senior_citizen: bool = False


class NewDoctor(BaseModel):
    name: str = Field(..., min_length=2)
    specialization: str = Field(..., min_length=2)
    fee: int = Field(..., gt=0)
    experience_years: int = Field(..., gt=0)
    is_available: bool = True


# =========================
# HELPERS
# =========================
def find_doctor(doctor_id: int):
    for doctor in doctors:
        if doctor["id"] == doctor_id:
            return doctor
    return None


def find_appointment(appointment_id: int):
    for appt in appointments:
        if appt["appointment_id"] == appointment_id:
            return appt
    return None


def calculate_fee(base_fee: int, appointment_type: str, senior_citizen: bool = False):
    if appointment_type == "video":
        original_fee = base_fee * 0.8
    elif appointment_type == "emergency":
        original_fee = base_fee * 1.5
    else:
        original_fee = float(base_fee)

    discounted_fee = original_fee
    if senior_citizen:
        discounted_fee = original_fee * 0.85

    return round(original_fee, 2), round(discounted_fee, 2)


def filter_doctors_logic(
    specialization=None,
    max_fee=None,
    min_experience=None,
    is_available=None,
):
    filtered = doctors

    if specialization is not None:
        filtered = [
            d for d in filtered
            if d["specialization"].lower() == specialization.lower()
        ]

    if max_fee is not None:
        filtered = [d for d in filtered if d["fee"] <= max_fee]

    if min_experience is not None:
        filtered = [d for d in filtered if d["experience_years"] >= min_experience]

    if is_available is not None:
        filtered = [d for d in filtered if d["is_available"] == is_available]

    return filtered


# =========================
# DAY 1 - BASIC GET
# =========================
@app.get("/")
def home():
    return {"message": "Welcome to MediCare Clinic"}


@app.get("/doctors")
def get_doctors():
    available_count = sum(1 for doctor in doctors if doctor["is_available"])
    return {
        "doctors": doctors,
        "total": len(doctors),
        "available_count": available_count,
    }


@app.get("/appointments")
def get_appointments():
    return {
        "appointments": appointments,
        "total": len(appointments),
    }


@app.get("/doctors/summary")
def doctors_summary():
    available_count = sum(1 for doctor in doctors if doctor["is_available"])
    most_experienced = max(doctors, key=lambda d: d["experience_years"])
    cheapest_fee = min(d["fee"] for d in doctors)

    specialization_count = {}
    for doctor in doctors:
        spec = doctor["specialization"]
        specialization_count[spec] = specialization_count.get(spec, 0) + 1

    return {
        "total_doctors": len(doctors),
        "available_count": available_count,
        "most_experienced_doctor": most_experienced["name"],
        "cheapest_consultation_fee": cheapest_fee,
        "specialization_counts": specialization_count,
    }


# =========================
# DAY 3 FILTER ROUTE
# =========================
@app.get("/doctors/filter")
def filter_doctors(
    specialization: str | None = None,
    max_fee: int | None = None,
    min_experience: int | None = None,
    is_available: bool | None = None,
):
    filtered = filter_doctors_logic(
        specialization=specialization,
        max_fee=max_fee,
        min_experience=min_experience,
        is_available=is_available,
    )
    return {
        "doctors": filtered,
        "count": len(filtered),
    }


# =========================
# DAY 6 SEARCH / SORT / PAGE / BROWSE
# FIXED ROUTES FIRST
# =========================
@app.get("/doctors/search")
def search_doctors(keyword: str):
    matches = [
        doctor for doctor in doctors
        if keyword.lower() in doctor["name"].lower()
        or keyword.lower() in doctor["specialization"].lower()
    ]

    if not matches:
        return {"message": "No doctors found for this keyword", "total_found": 0}

    return {"doctors": matches, "total_found": len(matches)}


@app.get("/doctors/sort")
def sort_doctors(sort_by: str = "fee", order: str = "asc"):
    allowed_sort = ["fee", "name", "experience_years"]
    allowed_order = ["asc", "desc"]

    if sort_by not in allowed_sort:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort}"}

    if order not in allowed_order:
        return {"error": f"Invalid order. Allowed: {allowed_order}"}

    reverse = order == "desc"
    sorted_list = sorted(doctors, key=lambda d: d[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "doctors": sorted_list,
    }


@app.get("/doctors/page")
def doctors_page(page: int = Query(1, ge=1), limit: int = Query(3, ge=1)):
    total = len(doctors)
    total_pages = math.ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "doctors": doctors[start:end],
    }


@app.get("/appointments/active")
def active_appointments():
    active = [
        appt for appt in appointments
        if appt["status"] in ["scheduled", "confirmed"]
    ]
    return {"appointments": active, "total": len(active)}


@app.get("/appointments/search")
def search_appointments(patient_name: str):
    results = [
        appt for appt in appointments
        if patient_name.lower() in appt["patient_name"].lower()
    ]
    return {"appointments": results, "total_found": len(results)}


@app.get("/appointments/sort")
def sort_appointments(sort_by: str = "fee", order: str = "asc"):
    allowed_sort = ["fee", "date"]
    allowed_order = ["asc", "desc"]

    if sort_by not in allowed_sort:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort}"}

    if order not in allowed_order:
        return {"error": f"Invalid order. Allowed: {allowed_order}"}

    reverse = order == "desc"
    sorted_list = sorted(appointments, key=lambda a: a[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "appointments": sorted_list,
    }


@app.get("/appointments/page")
def appointments_page(page: int = Query(1, ge=1), limit: int = Query(3, ge=1)):
    total = len(appointments)
    total_pages = math.ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "appointments": appointments[start:end],
    }


@app.get("/appointments/by-doctor/{doctor_id}")
def appointments_by_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    doctor_appointments = [
        appt for appt in appointments if appt["doctor_id"] == doctor_id
    ]
    return {
        "doctor_id": doctor_id,
        "doctor_name": doctor["name"],
        "appointments": doctor_appointments,
        "total": len(doctor_appointments),
    }


@app.get("/doctors/browse")
def browse_doctors(
    keyword: str | None = None,
    sort_by: str = "fee",
    order: str = "asc",
    page: int = Query(1, ge=1),
    limit: int = Query(4, ge=1),
):
    allowed_sort = ["fee", "name", "experience_years"]
    allowed_order = ["asc", "desc"]

    if sort_by not in allowed_sort:
        return {"error": f"Invalid sort_by. Allowed: {allowed_sort}"}

    if order not in allowed_order:
        return {"error": f"Invalid order. Allowed: {allowed_order}"}

    result = doctors

    if keyword:
        result = [
            doctor for doctor in result
            if keyword.lower() in doctor["name"].lower()
            or keyword.lower() in doctor["specialization"].lower()
        ]

    reverse = order == "desc"
    result = sorted(result, key=lambda d: d[sort_by], reverse=reverse)

    total = len(result)
    total_pages = math.ceil(total / limit) if total > 0 else 0
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "doctors": paginated,
    }


# =========================
# DAY 2 + 3 POST APPOINTMENT
# =========================
@app.post("/appointments")
def create_appointment(request: AppointmentRequest):
    global appt_counter

    doctor = find_doctor(request.doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    if not doctor["is_available"]:
        return {"error": "Doctor is not available"}

    original_fee, discounted_fee = calculate_fee(
        doctor["fee"],
        request.appointment_type,
        request.senior_citizen,
    )

    appointment = {
        "appointment_id": appt_counter,
        "patient_name": request.patient_name,
        "doctor_id": request.doctor_id,
        "doctor_name": doctor["name"],
        "date": request.date,
        "reason": request.reason,
        "appointment_type": request.appointment_type,
        "senior_citizen": request.senior_citizen,
        "original_fee": original_fee,
        "fee": discounted_fee,
        "status": "scheduled",
    }

    appointments.append(appointment)
    appt_counter += 1
    doctor["is_available"] = False

    return appointment


# =========================
# DAY 4 CRUD FOR DOCTORS
# =========================
@app.post("/doctors")
def add_doctor(new_doctor: NewDoctor, response: Response):
    for doctor in doctors:
        if doctor["name"].lower() == new_doctor.name.lower():
            return {"error": "Doctor with this name already exists"}

    new_id = max(d["id"] for d in doctors) + 1 if doctors else 1

    doctor_data = {
        "id": new_id,
        "name": new_doctor.name,
        "specialization": new_doctor.specialization,
        "fee": new_doctor.fee,
        "experience_years": new_doctor.experience_years,
        "is_available": new_doctor.is_available,
    }

    doctors.append(doctor_data)
    response.status_code = 201
    return doctor_data


@app.put("/doctors/{doctor_id}")
def update_doctor(
    doctor_id: int,
    fee: int | None = None,
    is_available: bool | None = None,
):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    if fee is not None:
        doctor["fee"] = fee

    if is_available is not None:
        doctor["is_available"] = is_available

    return doctor


@app.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if not doctor:
        return {"error": "Doctor not found"}

    active_scheduled = [
        appt for appt in appointments
        if appt["doctor_id"] == doctor_id and appt["status"] == "scheduled"
    ]
    if active_scheduled:
        return {"error": "Cannot delete doctor with active scheduled appointments"}

    doctors.remove(doctor)
    return {"message": "Doctor deleted successfully", "doctor_name": doctor["name"]}


# =========================
# DAY 5 APPOINTMENT WORKFLOW
# =========================
@app.post("/appointments/{appointment_id}/confirm")
def confirm_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        return {"error": "Appointment not found"}

    appt["status"] = "confirmed"
    return {"message": "Appointment confirmed", "appointment": appt}


@app.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        return {"error": "Appointment not found"}

    appt["status"] = "cancelled"

    doctor = find_doctor(appt["doctor_id"])
    if doctor:
        doctor["is_available"] = True

    return {"message": "Appointment cancelled", "appointment": appt}


@app.post("/appointments/{appointment_id}/complete")
def complete_appointment(appointment_id: int):
    appt = find_appointment(appointment_id)
    if not appt:
        return {"error": "Appointment not found"}

    appt["status"] = "completed"

    doctor = find_doctor(appt["doctor_id"])
    if doctor:
        doctor["is_available"] = True

    return {"message": "Appointment completed", "appointment": appt}


# =========================
# VARIABLE ROUTE LAST
# =========================
@app.get("/doctors/{doctor_id}")
def get_doctor_by_id(doctor_id: int):
    doctor = find_doctor(doctor_id)
    if doctor:
        return doctor
    return {"error": "Doctor not found"}
