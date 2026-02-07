from sqlalchemy.orm import Session
from database.models import User
from database.base import get_session
from utils.referral_code import generate_referral_code
from typing import Optional


class UserService:
    @staticmethod
    def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None, 
                          last_name: str = None, language_code: str = "ar") -> User:
        """Get existing user or create new one"""
        with get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if not user:
                referral_code = generate_referral_code()
                # Ensure unique referral code
                while session.query(User).filter(User.referral_code == referral_code).first():
                    referral_code = generate_referral_code()
                
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                    referral_code=referral_code,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Update user info if changed
                if username != user.username or first_name != user.first_name or last_name != user.last_name:
                    user.username = username
                    user.first_name = first_name
                    user.last_name = last_name
                    session.commit()
            
            return user
    
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        with get_session() as session:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def get_user_by_referral_code(referral_code: str) -> Optional[User]:
        """Get user by referral code"""
        with get_session() as session:
            return session.query(User).filter(User.referral_code == referral_code).first()
    
    @staticmethod
    def can_use_free_trial(telegram_id: int) -> bool:
        """Check if user can use free trial"""
        user = UserService.get_user_by_telegram_id(telegram_id)
        return user is not None and not user.free_trial_used
    
    @staticmethod
    def mark_free_trial_used(telegram_id: int):
        """Mark free trial as used for user"""
        with get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.free_trial_used = True
                session.commit()

