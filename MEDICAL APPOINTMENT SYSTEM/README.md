# Medical Appointment System

A simple FastAPI-based **Medical Appointment System** that manages doctors and appointments using in-memory Python lists. This project is suitable for learning core FastAPI concepts such as routing, path parameters, query parameters, Pydantic models, CRUD operations, helper functions, filtering, searching, sorting, and pagination.

## Features

- View all doctors
- View a doctor by ID
- View doctor summary
- Filter doctors by specialization, fee, experience, and availability
- Add, update, and delete doctors
- Book appointments
- Confirm, cancel, and complete appointments
- Search, sort, and paginate doctors
- Search, sort, and paginate appointments
- Browse doctors with combined search + sort + pagination

## Tech Stack

- Python 3.10+
- FastAPI
- Uvicorn
- Pydantic

## Project Structure

```text
.
├── main.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Create and activate a virtual environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Project

Start the FastAPI server with:

```bash
uvicorn main:app --reload
```

After running the server, open:

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Main Endpoints

### Basic Routes
- `GET /` → Welcome message
- `GET /doctors` → Get all doctors
- `GET /doctors/{doctor_id}` → Get one doctor by ID
- `GET /appointments` → Get all appointments
- `GET /doctors/summary` → Doctor summary

### Appointment Features
- `POST /appointments` → Book an appointment
- `POST /appointments/{appointment_id}/confirm` → Confirm appointment
- `POST /appointments/{appointment_id}/cancel` → Cancel appointment
- `POST /appointments/{appointment_id}/complete` → Complete appointment
- `GET /appointments/active` → Get active appointments
- `GET /appointments/by-doctor/{doctor_id}` → Appointments by doctor

### Doctor Management
- `POST /doctors` → Add a doctor
- `PUT /doctors/{doctor_id}` → Update doctor fee/availability
- `DELETE /doctors/{doctor_id}` → Delete doctor

### Filter / Search / Sort / Pagination
- `GET /doctors/filter`
- `GET /doctors/search`
- `GET /doctors/sort`
- `GET /doctors/page`
- `GET /doctors/browse`
- `GET /appointments/search`
- `GET /appointments/sort`
- `GET /appointments/page`

## Example Appointment Request

Use this JSON in Swagger for `POST /appointments`:

```json
{
  "patient_name": "Ankita",
  "doctor_id": 1,
  "date": "2026-03-22",
  "reason": "Chest pain",
  "appointment_type": "video",
  "senior_citizen": false
}
```

## Notes

- This project uses **in-memory storage**, so data resets when the server restarts.
- `appt_counter` is used to generate unique appointment IDs.
- Fixed routes like `/doctors/summary` should be placed above variable routes like `/doctors/{doctor_id}`.

## Submission Tips

- Keep all code in a fresh `main.py`
- Test every endpoint in Swagger UI
- Take screenshots as required in the assignment
- Use clear comments in code for better readability

## License

This project is for educational use.
