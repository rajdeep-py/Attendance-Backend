# Attendance Backend

## Features

- Admin and Employee onboarding and authentication
- Employee leave requests and approval workflow
- Holiday management per admin
- Location matrix for geo-fenced attendance
- Employee attendance with selfie and location validation (check-in/check-out)
- Salary slip upload, update, and download
- Notification system for admins and employees
- All uploads (photos, PDFs) stored in organized folders

## File Structure

```
Attendance-Backend/
├── db.py
├── main.py
├── requirements.txt
├── .env
├── README.MD
├── models/
│   ├── base.py
│   ├── attendance/
│   │   └── attendance_models.py
│   ├── help_center/
│   │   └── help_center_models.py
│   ├── holidays/
│   │   └── holiday_models.py
│   ├── leaves/
│   │   └── leave_request_models.py
│   ├── location_matrix/
│   │   └── location_matrix_models.py
│   ├── notification/
│   │   └── notification_models.py
│   ├── onboarding/
│   │   ├── admin_models.py
│   │   └── employee_models.py
│   └── salary_slip/
│       └── salary_slip_models.py
├── routes/
│   ├── attendance/
│   │   └── attendance_routes.py
│   ├── help_center/
│   │   └── help_center_routes.py
│   ├── holidays/
│   │   └── holiday_routes.py
│   ├── leaves/
│   │   └── leave_request_routes.py
│   ├── location_matrix/
│   │   └── location_matrix_routes.py
│   ├── notification/
│   │   └── notification_routes.py
│   ├── onboarding/
│   │   ├── admin_routes.py
│   │   └── employee_routes.py
│   └── salary_slip/
│       └── salary_slip_routes.py
├── uploads/
│   ├── attendance/
│   ├── profile_photo/
│   └── salary/
└── venv/
```

## How to Clone and Start the Backend Server

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd Attendance-Backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Create a .env file in the root directory with:
     ```
     DATABASE_URL=postgresql://<pgadmin_user>:<pgadmin_password>@localhost:5432/<your_db>
     ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload
   ```

## PostgreSQL Setup (pgAdmin)

1. **Create a new database**
   - Open pgAdmin and connect to your PostgreSQL server.
   - Right-click on Databases → Create → Database.
   - Name it (e.g., attendance_db).

2. **Create a user (if needed)**
   - Go to Login/Group Roles → Create → Login/Group Role.
   - Set username and password.
   - Under "Privileges", set "Can login?" to Yes.

3. **Grant privileges**
   - In the Query Tool, run:
     ```sql
     GRANT ALL PRIVILEGES ON DATABASE <your_db> TO <pgadmin_user>;
     ```

4. **Update your .env file**
   - Use the username, password, and database name you created.

5. **Run the backend**
   - The server will auto-create tables on startup.