# LifeTag – Smart Emergency Healthcare System

## Overview
LifeTag is a smart emergency healthcare system designed to provide instant access to critical patient data using unique LifeTag IDs and QR codes. It reduces delays caused by manual hospital records and enables faster and more efficient medical response during emergencies.

---

## Features
- Unique LifeTag ID for every user  
- QR code generation for quick access to patient data  
- Doctor access system to view patient details instantly  
- Patient-controlled data sharing  
- Upload and manage medical reports  
- Appointment booking system  
- No need for manual hospital data entry  

---

## Tech Stack
- Frontend: HTML, CSS  
- Backend: Python (Flask)  
- Database: JSON (for simulation)  
- QR Code generation  

---

## Problem Statement
In emergency situations, accessing a patient’s medical history takes time and often requires manual data entry. This delay can lead to critical inefficiencies in treatment and decision-making.

---

## Solution
LifeTag addresses this issue by providing a QR-based system linked to a centralized patient profile. It allows healthcare professionals to access essential medical data instantly and securely.

---

## How It Works
1. User registers and receives a unique LifeTag ID  
2. A QR code is generated for the user  
3. In an emergency, the QR code is scanned  
4. The doctor accesses patient details through the system  
5. Medical history and reports are available immediately  

---

## Project Structure
```
LifeTag/
│── app.py
│── users.json
│── appointments.json
│
├── templates/
├── static/
├── uploads/
├── qr/
├── qr_images/
├── sensor/
```

---

## How to Run
1. Clone the repository:
   git clone https://github.com/your-username/lifetag.git

2. Navigate to the folder:
   cd lifetag

3. Install dependencies:
   pip install flask

4. Run the application:
   python app.py

---

## Future Improvements
- Integration with real hospital databases  
- Secure authentication system  
- Cloud-based storage for medical records  
- Real-time emergency alert system  
- Hardware-based LifeTag device integration  

---

## Contributing
Contributions are welcome. Feel free to fork the repository and submit improvements.

---

## Contact
Created by Vidisha Adhiya  adhiyavidisha@gmail.com
Open to feedback, collaboration, and opportunities.
