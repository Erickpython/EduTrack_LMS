# EduTrack LMS – Learning Made Accessible Anywhere

## 📘 Introduction
**EduTrack LMS** is a lightweight, offline-friendly Learning Management System designed for schools with limited internet connectivity. It enables students to register, log in, access lessons, view notes and videos, take quizzes, and track their learning progress.  

Built using **Flask (Python)**, EduTrack provides both **Student** and **Admin/Teacher** dashboards for seamless content management and learning delivery.

This system supports **UN Sustainable Development Goal 4 (SDG4)** — *Quality Education for All* by improving access to digital learning resources. The website is live and accessible at: *(https://edutrack-fjzc.onrender.com/)*

---

## 🎯 Problem Statement (SDG 4 – Quality Education)
Many schools—especially in rural and low-resource environments—face issues such as:

- Limited or unstable internet access  
- No structured digital learning systems  
- Difficulty tracking student progress  
- Poor distribution of educational materials  
- Teachers lacking centralized management tools  

**EduTrack LMS** addresses these challenges by offering a simple, offline-capable LMS that supports lesson delivery, learner tracking, and student engagement.

By enabling equal access to quality learning materials, this solution contributes directly to **SDG4**: ensuring inclusive and equitable quality education for all.

---

## 🧩 Features

### 👨‍🎓 Student Features
- Student registration and login  
- Access to lessons based on grade level  
- View lesson notes, videos, and summaries  
- Complete quizzes and assessments  
- Automatic progress tracking  
- Locked/Unlocked lesson navigation  

### 🧑‍🏫 Admin/Teacher Features
- Secure admin registration using an **access code**  
- Lesson, subject, and grade management  
- Upload and edit videos, notes, and quizzes  
- View student list and their progress  
- Full administrative dashboard  

---

## 🛠️ Implementation Overview
EduTrack LMS is implemented using:

- **Flask** for backend logic  
- **Jinja2** for template rendering  
- **SQLAlchemy ORM** for database operations  
- **SQLite** database for simple deployments  
- **Bootstrap 5 + Custom CSS** for the UI  
- **CSRF Protection & Session Management** for security  
- **MVC-like structure** for clean organization  

The system is optimized for offline or limited-connectivity environments and is easily extendable.

---

## 🗂️ Database ER Diagram

**ER Diagram:**  
`![ER Diagram](LINK_HERE)`

### Entities
- **Student**
- **Admin**
- **Grade**
- **Subject**
- **Lesson**
- **Progress**
- **Quizes**

### Relationships
- One **Grade** → Many **Subjects**  
- One **Subject** → Many **Lessons**  
- One **Student** → Many **Progress Records**  
- One **Lesson** → Many **Progress Records**  
- One **Admin** → Manages many entities  

---

## 📸 Screenshots

- **Home Page** – `LINK_HERE`  
- **Student Dashboard** – `LINK_HERE`  
- **Admin Dashboard** – `LINK_HERE`  
- **Lesson View** – `LINK_HERE`  
- **Quiz Page** – `LINK_HERE`  

---

## 👨‍💻 Contributors

### 💡 Idea Originator
**Cassie Bedel**  
LinkedIn: *(https://www.linkedin.com/in/cassie-bedel-5b9271106/)*  
Cassie conceptualized the idea of creating an LMS that can function offline and improve student learning outcomes.

### 👨‍💻 Lead Developer
**Erick Wambugu**  
LinkedIn: *(https://www.linkedin.com/in/erick-wambugu-425a15161/)*
Full system development — backend, UI, admin dashboard, student dashboard, lesson management, and progress tracking.

---

## 🧰 Technologies Used

| Category | Technology |
|----------|------------|
| Backend | Python Flask |
| Database | SQLite (via SQLAlchemy) |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Security | CSRF Protection, Access Code Auth |
| Deployment | PythonAnywhere / Render / Offline setups |

---

## 🚀 How to Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/your-repository/EduTrack-LMS.git
cd EduTrack-LMS

2. Install Requirements

pip install -r requirements.txt

3. Run the App

python app.py

4. Open in Browser

http://127.0.0.1:5000/


---

🔑 Admin Access

ADMIN_ACCESS_CODE=Admin@123

Only individuals who have this code can create an admin account.


---

📄 License

© 2025 EduTrack LMS  
All Rights Reserved.

This project is NOT open-source.

No part of this codebase, UI design, or documentation may be copied, reused, redistributed, or modified without written permission from the original contributors.


---

⭐ Final Notes

EduTrack LMS is designed for real schools with real needs. Its offline-first architecture, structured learning flow, and teacher dashboard make it ideal for primary and junior schools looking to digitize learning affordably.
