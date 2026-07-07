# 🖐️ Fingerprint Attendance System

A professional **offline-first Fingerprint Attendance System** developed using **Python**, **PyQt6**, **MongoDB**, and the **SecuGen Fingerprint SDK**. The system is designed for clinics and organizations to manage patient registration, biometric attendance, treatment tracking, payment management, and automatic cloud synchronization.

---

# ✨ Key Features

## 🔐 Authentication & Security

- Organization-based login
- Secure password authentication
- Forgot Password support
- Role-based access (Admin / Staff)
- License validation before application startup
- Organization-specific data isolation

---

## 👤 Patient Registration

- Register new patients
- Capture fingerprint templates
- Dummy fingerprint registration
- Duplicate fingerprint detection
- Department assignment
- Consultancy fee management
- Daily payment configuration
- Paid days configuration
- Treatment information
- Automatic serial number generation

---

## 🖐️ Fingerprint Recognition

- SecuGen Hamster Pro 20 (HU20) support
- Live fingerprint scanning
- High-speed template generation
- Biometric template matching
- Duplicate fingerprint prevention
- Scanner status monitoring
- Image quality validation
- Automatic SDK initialization

---

## ✅ Attendance Management

- One-touch fingerprint attendance
- Manual attendance support
- Duplicate attendance prevention
- Department-wise token generation
- Real-time attendance processing
- Attendance deletion
- Future attendance recalculation
- Attendance history

---

## 💳 Payment & Treatment Tracking

- Consultancy management
- Payment per day
- Paid days management
- Used days calculation
- Remaining treatment days
- Last treatment day indication
- Due payment detection
- Treatment restart support

---

## 📊 Dashboard

- Today's attendance count
- Total patient count
- Department-wise attendance
- Live attendance logs
- Scanner status
- Real-time dashboard updates
- Manual attendance shortcut
- Background synchronization status

---

## 👥 Patient Management

- Search patients
- Filter by registration date
- Update patient information
- Update fingerprint
- Delete patient
- Attendance history
- Automatic serial number adjustment
- Payment update
- Treatment update

---

## 🔄 Offline First Synchronization

- Local MongoDB storage
- MongoDB Atlas synchronization
- Automatic background sync
- Internet connectivity detection
- Offline operation queue
- Automatic retry
- Organization-wise synchronization
- Cloud data consistency

---

## 🔑 License Management

- License expiry validation
- Organization verification
- Automatic license checking
- License Expired page
- Startup protection

---

## 🔔 Notifications

- Success notifications
- Warning notifications
- Error notifications
- Scanner status messages
- Attendance status messages
- Registration alerts

---

# 🏗️ System Architecture

```
User
   │
   ▼
PyQt6 Desktop Application
   │
   ├────────► Fingerprint Scanner
   │
   ├────────► MongoDB Compass (Local)
   │
   └────────► Sync Worker
                  │
          Internet Available?
              │          │
             Yes         No
              │          │
              ▼          ▼
      MongoDB Atlas   Offline Queue
```

---

# 🛠 Technology Stack

## Programming Language

- Python 3.x

## Desktop Framework

- PyQt6

## Database

- MongoDB Compass (Local)
- MongoDB Atlas (Cloud)

## Biometric Device

- SecuGen Hamster Pro 20 (HU20)
- SecuGen FDx SDK Pro

## Libraries

- PyMongo
- Pillow
- NumPy
- python-dotenv
- dnspython
- bson

---

# 📂 Project Structure

```
Fingerprint_Attendance_System/
│
├── assets/
├── sdk/
├── sync/
│   ├── sync_manager.py
│   └── sync_worker.py
│
├── database/
│   ├── mongodb_connection.py
│   ├── atlas_connection.py
│   ├── organization_repository.py
│   ├── patient_repository.py
│   ├── attendance_repository.py
│   └── attendance_worker.py
│
├── utils/
│   ├── scanner_manager.py
│   ├── enrollment.py
│   ├── verification.py
│   ├── license_manager.py
│   ├── session.py
│   ├── sidebar.py
│   ├── toast_notification.py
│   ├── update_patient_dialog.py
│   ├── delete_patient_dialog.py
│   ├── delete_attendance_dialog.py
│   ├── attendance_history_dialog.py
│   └── manual_attendance_dialog.py
│
├── windows_pages/
│   ├── auth_pages/
│   └── pages/
│
├── main.py
├── requirements.txt
└── .env
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone <repository-url>
cd Fingerprint_Attendance_System
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Activate Virtual Environment

```bash
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🗄 Database Configuration

Create a `.env` file in the project root.

```env
MONGODB_URI=your_connection_string
DATABASE_NAME=fingerprint_attendance
```

---

# ▶️ Run Application

```bash
python main.py
```

---

# 💻 Hardware Requirements

- Windows 10 / Windows 11
- SecuGen Hamster Pro 20 (HU20)
- SecuGen FDx SDK
- MongoDB Community Server
- MongoDB Compass
- Internet connection (Optional for Cloud Sync)

---

# 🗃 Database Collections

| Collection | Purpose |
|------------|---------|
| organizations | Organization details and authentication |
| patients | Patient information and fingerprint templates |
| attendance | Daily attendance records |
| deleted_patients | Backup of deleted patients |
| offline_outbox | Offline synchronization queue |

---

# 🔒 Security Features

- Organization-based authentication
- Fingerprint verification
- Duplicate fingerprint detection
- Duplicate attendance prevention
- License validation
- Role-based access control
- Exception logging
- Secure database connection
- Offline data protection

---

# 🚀 Future Enhancements

- PDF Reports
- Excel Export
- SMS Notifications
- Email Notifications
- Mobile Application
- QR Code Attendance
- Advanced Analytics Dashboard
- Multi-Branch Support

---

# 👨‍💻 Developed With

- Python
- PyQt6
- MongoDB
- MongoDB Atlas
- SecuGen Fingerprint SDK
- PyInstaller
- Inno Setup

---

## ⭐ Project Highlights

✔ Offline-First Architecture

✔ Fingerprint Authentication

✔ Automatic Cloud Synchronization

✔ Patient & Treatment Management

✔ License Protection

✔ Manual Attendance Support

✔ Real-Time Dashboard

✔ Modern PyQt6 Interface

✔ MongoDB Local + Cloud Integration
