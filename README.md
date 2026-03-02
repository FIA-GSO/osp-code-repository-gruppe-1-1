# Lerngruppen-Tool

Modulare Flask-Webanwendung zur Verwaltung von Benutzerkonten, Gruppen und Gruppenaktionen mit Rollen- und Rechtekonzept, serverseitiger Validierung sowie automatisierten Tests.

---

## ✨ Features

- Benutzerregistrierung & Login
- Passwort-Hashing mit Bcrypt
- Session-basierte Authentifizierung
- Gruppen erstellen, bearbeiten, löschen
- Mitgliederverwaltung
- Gruppenaktionen
- Admin-Bereich mit Zugriffskontrolle
- CSRF-Schutz
- Serverseitige Validierung inkl. Regex & Profanity-Filter
- Pytest-Testabdeckung
- Strukturierte Blueprint-Architektur

---

## 🛠 Tech Stack

- Python 3
- Flask
- SQLAlchemy
- Flask-WTF (CSRF)
- Bcrypt
- Bootstrap 5
- Pytest

---

## 📂 Project Structure

```
.
├── main.py
├── config.py
├── extensions.py
├── mail_service.py
│
├── blueprints/
│   ├── main/
│   ├── auth/
│   ├── groups/
│   ├── admin/
│   └── common.py
│
├── database/
│   └── model/
│       ├── base.py
│       ├── accountModel.py
│       ├── groupModel.py
│       ├── groupMemberModel.py
│       └── groupActionModel.py
│
├── services/
│   └── accountService.py
│
├── utils/
│   ├── profanity.py
│   └── profanity_config.py
│
├── templates/
├── static/
└── tests/
```

---

## 🗄 Database Models

- **AccountModel** – User accounts  
- **GroupModel** – Groups  
- **GroupMemberModel** – User ↔ Group relation  
- **GroupActionModel** – Group-based actions  

---

## ⚙️ Installation

### 1. Clone repository

```bash
git clone <repo-url>
cd <project-folder>
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example`:

```bash
cp .env.example .env
```

Set required values (e.g. `SECRET_KEY`, database URI, mail config).

---

## ▶ Run Application

```bash
flask run
```

or

```bash
python main.py
```

---

## 🧪 Run Tests

```bash
pytest
```

---

## 🔐 Security

- CSRF protection
- Server-side validation
- Password hashing
- Session handling
- Role-based access control
- Input sanitization

---

## 🎨 Frontend

- Bootstrap 5
- Custom CSS
- Modal-based CRUD interactions
- Vanilla JS for dynamic behavior

---

## 🧱 Architecture

- Blueprint-based modular routing
- Service layer for business logic
- Separated models
- Centralized extensions
- Test-ready structure

