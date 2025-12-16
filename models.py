from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite Veritabanı Bağlantısı
DATABASE_URL = "sqlite:///todos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class PomodoroSession(Base):
    __tablename__ = "pomodoro_sessions"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Session Type
    session_type = Column(String, nullable=False, index=True)  # 'pomodoro' | 'short_break' | 'coffee_break'
    
    # Time Tracking
    start_time = Column(DateTime, nullable=False, default=datetime.now)
    end_time = Column(DateTime, nullable=True)  # NULL if abandoned
    
    # Duration (in seconds)
    planned_duration = Column(Integer, nullable=False)
    actual_duration = Column(Integer, nullable=True)
    
    # Completion Status
    completed = Column(Boolean, default=False, index=True)
    
    # Date for daily aggregation
    date = Column(DateTime, nullable=False, default=datetime.now, index=True)

# Tabloları oluştur
Base.metadata.create_all(bind=engine)
