# FastAPI, SQLAlchemy, and admin routes import

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes.onboarding import admin_routes
from models.base import Base
from models.onboarding.admin_models import AdminUser

from sqlalchemy.orm import Session
from db import get_db, engine


app = FastAPI()

# CORS middleware
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],  # Change to specific origins in production
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

 # DB connection and get_db now imported from db.py

# Health check endpoint
@app.get("/health")
def health_check():
	print("Health check endpoint called.")
	return {"status": "ok"}


# Create tables on startup
@app.on_event("startup")
def on_startup():
	print("Creating database tables if not exist...")
	Base.metadata.create_all(bind=engine)
	print("Database tables ready.")



# Include admin routes
app.include_router(admin_routes.router)

# Include notification routes
from routes.notification import notification_routes
app.include_router(notification_routes.router)


# Include location matrix routes
from routes.location_matrix import location_matrix_routes
app.include_router(location_matrix_routes.router)

# Allow running with python main.py on any IP and port
if __name__ == "__main__":
	import uvicorn
	uvicorn.run(
		"main:app",
		host="0.0.0.0",
		port=8000,
		reload=True
	)
