# PHAROS

**Pharmaceutical Health Advice & Recommendations Online System**

An offline pharmacy desktop application built for my A-Level Computer Science project using Python, CustomTkinter and SQLite.

## Features

- Account registration and login.
- A searchable catalogue of 42 pharmacy products, with category filtering and product images.
- Symptom questionnaires using decision trees.
- Prescription records linked to user accounts, with options to add, view, edit and delete records.
- Light and dark themes.

## Run locally

Use Python 3 with Tkinter installed. Run these commands from the project directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

The app creates `pharos.db` on first launch and seeds its product catalogue. Register a new account through the interface. Keep the working directory set to the project root so the database and relative image paths resolve correctly.

## Files

| File | Purpose |
| --- | --- |
| `main.py` | Desktop interface, symptom decision trees and initial product catalogue |
| `authManager.py` | Registration and login logic |
| `dbManager.py` | SQLite schema and database operations |
| `images/` | Product images |
| `test.py` | Original empty placeholder; no automated tests are provided |

## Project limitations

This is an educational prototype. Symptom advice and product information are not clinically validated. It should not be used for real patient care.

The original authentication implementation stores passwords in plaintext. Use only dummy credentials and fictional prescription details when trying the app.

Local databases, user accounts and prescription records are excluded from version control. The application source is preserved as supplied; this upload adds repository documentation and setup files.
