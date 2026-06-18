# Fingerprint Attendance System

A desktop-based Fingerprint Attendance System built with Python, PyQt6, MongoDB, and SecuGen Fingerprint SDK. The application provides patient registration, fingerprint enrollment, attendance tracking, dashboard monitoring, and patient management features.

## Features

### Authentication

* Secure login system
* Forgot password functionality
* Organization-based access control

### Patient Registration

* Register new patients
* Capture fingerprint templates
* Store demographic information
* Department assignment
* Fingerprint duplicate detection

### Fingerprint Verification

* Real-time fingerprint scanning
* Biometric template matching
* Duplicate registration prevention
* Attendance identification using fingerprint recognition

### Attendance Management

* One-touch attendance marking
* Daily attendance validation
* Duplicate attendance prevention
* Real-time attendance processing

### Dashboard

* Today's attendance statistics
* Total patient count
* Department-wise attendance logs
* Real-time scanner integration
* Live attendance monitoring

### Patient Management

* View patient records
* Update patient information
* Update fingerprint templates
* Delete patient records
* Serial number management

### Notifications

* Toast notifications
* Success modals
* Error handling and logging
* Scanner status indicators

---

## Technology Stack

### Frontend

* PyQt6

### Backend

* Python

### Database

* MongoDB Atlas
* PyMongo

### Biometric Device

* SecuGen Hamster Pro 20 (HU20)
* SecuGen FDx SDK Pro

### Additional Libraries

* Pillow
* NumPy
* Python Dotenv
* DNSPython

---

## Project Structure

```text
Fingerprint_system/
│
├── assets/
├── sdk/
├── database/
│   ├── mongodb_connection.py
│   ├── organization_repository.py
│   ├── patient_repository.py
│   ├── attendance_repository.py
│   └── attendance_worker.py
│
├── utils/
│   ├── scanner_manager.py
│   ├── enrollment.py
│   ├── verification.py
│   ├── session.py
│   ├── sidebar.py
│   ├── toast_notification.py
│   ├── update_patient_dialog.py
│   └── delete_patient_dialog.py
│
├── windows_pages/
│   ├── auth_pages/
│   └── pages/
│
├── main.py
└── requirements.txt
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd Fingerprint_system
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows:

```bash
.venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```env
MONGO_URI=your_mongodb_connection_string
DATABASE_NAME=fingerprint_attendance
```

---

## Running the Application

```bash
python main.py
```

---

## Hardware Requirements

* SecuGen Hamster Pro 20 (HU20)
* Windows Operating System
* SecuGen SDK DLL files

Required SDK files:

```text
sdk/
├── sgfplib.dll
├── sgfpamx.dll
```

---

## Database Collections

### organizations

Stores organization details and authentication data.

### patients

Stores patient information and fingerprint templates.

### attendance

Stores daily attendance records.

### deleted_patients

Stores archived patient records after deletion.

---

## Security Features

* Environment variable configuration
* Organization-based data separation
* Fingerprint duplicate detection
* Attendance duplication prevention
* Exception logging
* Database connection validation

---

## Future Enhancements

* Attendance reports
* Excel export
* PDF reports
* Multi-device support
* Attendance analytics
* Cloud synchronization

---

## Author

Developed using Python, PyQt6, MongoDB, and SecuGen Fingerprint SDK.
