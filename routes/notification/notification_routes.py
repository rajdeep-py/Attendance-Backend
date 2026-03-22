from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.notification.notification_models import Notification, Base
from db import get_db

router = APIRouter()

class NotificationCreate(BaseModel):
	admin_id: int
	title: str
	subtitle: str = None

class NotificationUpdate(BaseModel):
	title: str = None
	subtitle: str = None

# Create notification by admin_id
@router.post("/notifications/")
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
	notif = Notification(**notification.dict())
	db.add(notif)
	db.commit()
	db.refresh(notif)
	return {"message": "Notification created", "notification_id": notif.notification_id}

# Get all notifications
@router.get("/notifications/")
def get_all_notifications(db: Session = Depends(get_db)):
	notifs = db.query(Notification).all()
	return notifs

# Get notifications by admin_id
@router.get("/notifications/admin/{admin_id}")
def get_notifications_by_admin(admin_id: int, db: Session = Depends(get_db)):
	notifs = db.query(Notification).filter(Notification.admin_id == admin_id).all()
	return notifs

# Update notification by admin_id and notification_id
@router.put("/notifications/{notification_id}/admin/{admin_id}")
def update_notification(notification_id: int, admin_id: int, update: NotificationUpdate, db: Session = Depends(get_db)):
	notif = db.query(Notification).filter(Notification.notification_id == notification_id, Notification.admin_id == admin_id).first()
	if not notif:
		raise HTTPException(status_code=404, detail="Notification not found")
	if update.title is not None:
		notif.title = update.title
	if update.subtitle is not None:
		notif.subtitle = update.subtitle
	db.commit()
	db.refresh(notif)
	return {"message": "Notification updated", "notification_id": notif.notification_id}

# Delete notification by admin_id and notification_id
@router.delete("/notifications/{notification_id}/admin/{admin_id}")
def delete_notification(notification_id: int, admin_id: int, db: Session = Depends(get_db)):
	notif = db.query(Notification).filter(Notification.notification_id == notification_id, Notification.admin_id == admin_id).first()
	if not notif:
		raise HTTPException(status_code=404, detail="Notification not found")
	db.delete(notif)
	db.commit()
	return {"message": "Notification deleted"}
