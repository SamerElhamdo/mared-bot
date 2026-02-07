from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from database.models import Referral, ReferralPoint, User
from database.base import get_session
import logging

logger = logging.getLogger(__name__)

# Points awarded for successful referral
REFERRAL_POINTS = 10


class ReferralService:
    @staticmethod
    def process_referral(referrer_id: int, referred_id: int) -> Optional[Referral]:
        """Process a referral when a new user signs up"""
        # Prevent self-referral
        if referrer_id == referred_id:
            logger.warning(f"Self-referral attempted: user {referrer_id}")
            return None
        
        with get_session() as session:
            # Check if referral already exists
            existing = session.query(Referral).filter(
                Referral.referrer_id == referrer_id,
                Referral.referred_id == referred_id
            ).first()
            
            if existing:
                logger.warning(f"Referral already exists: {referrer_id} -> {referred_id}")
                return existing
            
            # Create referral record
            referral = Referral(
                referrer_id=referrer_id,
                referred_id=referred_id,
                points_awarded=REFERRAL_POINTS,
            )
            session.add(referral)
            
            # Award points to referrer
            point = ReferralPoint(
                user_id=referrer_id,
                points=REFERRAL_POINTS,
                description=f"Referral bonus for user {referred_id}",
                referral_id=referral.id,
            )
            session.add(point)
            session.commit()
            session.refresh(referral)
            
            logger.info(f"Processed referral: {referrer_id} -> {referred_id}, awarded {REFERRAL_POINTS} points")
            return referral
    
    @staticmethod
    def get_user_total_points(user_id: int) -> int:
        """Get total points for a user"""
        with get_session() as session:
            result = session.query(
                func.sum(ReferralPoint.points)
            ).filter(ReferralPoint.user_id == user_id).scalar()
            return int(result) if result else 0
    
    @staticmethod
    def get_user_points_history(user_id: int) -> list:
        """Get points history for a user"""
        with get_session() as session:
            return session.query(ReferralPoint).filter(
                ReferralPoint.user_id == user_id
            ).order_by(ReferralPoint.created_at.desc()).all()
    
    @staticmethod
    def deduct_points(user_id: int, points: int, description: str = None) -> bool:
        """Deduct points from user (for redemption)"""
        total_points = ReferralService.get_user_total_points(user_id)
        
        if total_points < points:
            logger.warning(f"Insufficient points for user {user_id}: {total_points} < {points}")
            return False
        
        with get_session() as session:
            point = ReferralPoint(
                user_id=user_id,
                points=-points,  # Negative for deduction
                description=description or f"Points redemption: {points} points",
            )
            session.add(point)
            session.commit()
            
            logger.info(f"Deducted {points} points from user {user_id}")
            return True
    
    @staticmethod
    def get_referral_stats(user_id: int) -> dict:
        """Get referral statistics for a user"""
        with get_session() as session:
            total_referrals = session.query(Referral).filter(
                Referral.referrer_id == user_id
            ).count()
            
            total_points = ReferralService.get_user_total_points(user_id)
            
            return {
                "total_referrals": total_referrals,
                "total_points": total_points,
            }

