from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import Optional, List
from database.models import Subscription, SubscriptionStatus, Plan, User
from database.base import get_session
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    @staticmethod
    def create_subscription(user_id: int, plan_id: int, is_trial: bool = False) -> Subscription:
        """Create a new subscription"""
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise ValueError(f"Plan with id {plan_id} not found")
            
            start_date = datetime.utcnow()
            if is_trial:
                end_date = start_date + timedelta(days=settings.FREE_TRIAL_DAYS)
            else:
                end_date = start_date + timedelta(days=plan.duration_days)
            
            subscription = Subscription(
                user_id=user_id,
                plan_id=plan_id,
                status=SubscriptionStatus.TRIAL if is_trial else SubscriptionStatus.ACTIVE,
                start_date=start_date,
                end_date=end_date,
                is_trial=is_trial,
            )
            session.add(subscription)
            session.commit()
            session.refresh(subscription)
            
            logger.info(f"Created subscription {subscription.id} for user {user_id}, trial: {is_trial}")
            return subscription
    
    @staticmethod
    def get_active_subscription(user_id: int) -> Optional[Subscription]:
        """Get active subscription for user"""
        with get_session() as session:
            return session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.ACTIVE
            ).first()
    
    @staticmethod
    def get_trial_subscription(user_id: int) -> Optional[Subscription]:
        """Get trial subscription for user"""
        with get_session() as session:
            return session.query(Subscription).filter(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatus.TRIAL
            ).first()
    
    @staticmethod
    def expire_subscription(subscription_id: int):
        """Expire a subscription"""
        with get_session() as session:
            subscription = session.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            if subscription:
                subscription.status = SubscriptionStatus.EXPIRED
                session.commit()
                logger.info(f"Expired subscription {subscription_id}")
    
    @staticmethod
    def check_and_expire_subscriptions():
        """Check and expire subscriptions that have passed their end date"""
        with get_session() as session:
            now = datetime.utcnow()
            expired = session.query(Subscription).filter(
                Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]),
                Subscription.end_date < now
            ).all()
            
            for subscription in expired:
                subscription.status = SubscriptionStatus.EXPIRED
                logger.info(f"Auto-expired subscription {subscription.id} for user {subscription.user_id}")
            
            session.commit()
            return len(expired)
    
    @staticmethod
    def get_user_subscriptions(user_id: int) -> List[Subscription]:
        """Get all subscriptions for a user"""
        with get_session() as session:
            return session.query(Subscription).options(
                joinedload(Subscription.plan)
            ).filter(
                Subscription.user_id == user_id
            ).order_by(Subscription.created_at.desc()).all()
    
    @staticmethod
    def has_active_subscription(user_id: int) -> bool:
        """Check if user has active subscription"""
        subscription = SubscriptionService.get_active_subscription(user_id)
        return subscription is not None
    
    @staticmethod
    def activate_subscription(subscription_id: int):
        """Activate a subscription (e.g., after payment confirmation)"""
        with get_session() as session:
            subscription = session.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            if subscription:
                subscription.status = SubscriptionStatus.ACTIVE
                subscription.is_trial = False
                session.commit()
                logger.info(f"Activated subscription {subscription_id}")

