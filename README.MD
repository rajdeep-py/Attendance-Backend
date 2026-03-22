# Attendance Backend

## Setup & Run

1. **Clone the repository**
2. **Create and activate a virtual environment:**
	```bash
	python3 -m venv venv
	source venv/bin/activate
	```
3. **Install dependencies:**
	```bash
	pip install -r requirements.txt
	```
4. **Configure environment variables:**
	- Create a `.env` file in the root directory with the following:
	  ```env
	  DATABASE_URL=postgresql://<pgadmin_user>:<pgadmin_password>@localhost:5432/<your_db>
	  ```
5. **Start the server:**
	```bash
	uvicorn main:app --reload
	```

## API Endpoints
- `POST /admin/register` — Register new admin
- `POST /admin/login` — Admin login
- `GET /admin/health` — Health check
