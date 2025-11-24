import asyncio
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config.config import Config
from .models import Base

class DatabaseManager:
    """Database management for Butler"""
    
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("butler.database")
        self.engine = None
        self.SessionLocal = None
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize database connection"""
        self.logger.info("Initializing database...")
        
        try:
            # Create SQLite database
            database_url = self.config.database_url
            self.engine = create_engine(database_url, echo=self.config.DEBUG)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            self.is_initialized = True
            self.logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    def get_session(self):
        """Get database session"""
        if not self.is_initialized:
            raise Exception("Database not initialized")
        return self.SessionLocal()
    
    async def execute_query(self, query_func):
        """Execute a database query with error handling"""
        session = self.get_session()
        try:
            return query_func(session)
        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    async def shutdown(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
        self.logger.info("Database manager shut down")