from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class UserSession(Base):
    """User session model"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), unique=True, nullable=False)
    user_data = Column(JSON)  # Store user preferences, context
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    expires_at = Column(DateTime)

class ServiceRequest(Base):
    """Service request model"""
    __tablename__ = 'service_requests'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255), nullable=False)
    service_type = Column(String(100), nullable=False)
    location = Column(String(255))
    vendors_data = Column(JSON)  # Store vendor list
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Booking(Base):
    """Booking model"""
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(String(100), unique=True, nullable=False)
    session_id = Column(String(255), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    vendor_phone = Column(String(20))
    service_type = Column(String(100))
    status = Column(String(50), default='confirmed')  # confirmed, cancelled, completed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class VendorCache(Base):
    """Vendor cache model"""
    __tablename__ = 'vendor_cache'
    
    id = Column(Integer, primary_key=True)
    service_type = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)
    vendor_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)