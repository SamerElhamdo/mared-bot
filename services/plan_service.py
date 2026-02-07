"""
Plan management service
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from database.models import Plan
from database.base import get_session
import logging

logger = logging.getLogger(__name__)


class PlanService:
    @staticmethod
    def get_all_plans() -> List[Plan]:
        """Get all plans"""
        with get_session() as session:
            return session.query(Plan).order_by(Plan.id).all()
    
    @staticmethod
    def get_plan(plan_id: int) -> Optional[Plan]:
        """Get plan by ID"""
        with get_session() as session:
            return session.query(Plan).filter(Plan.id == plan_id).first()
    
    @staticmethod
    def create_plan(name: str, name_ar: str, duration: str, duration_days: int,
                   price: float, currency: str = "USDT", is_active: bool = True) -> Plan:
        """Create a new plan"""
        from database.models import PlanDuration
        
        with get_session() as session:
            plan = Plan(
                name=name,
                name_ar=name_ar,
                duration=PlanDuration(duration),
                duration_days=duration_days,
                price=price,
                currency=currency,
                is_active=is_active
            )
            session.add(plan)
            session.commit()
            session.refresh(plan)
            logger.info(f"Created plan {plan.id}: {name}")
            return plan
    
    @staticmethod
    def update_plan(plan_id: int, **kwargs) -> bool:
        """Update plan"""
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return False
            
            for key, value in kwargs.items():
                if hasattr(plan, key):
                    setattr(plan, key, value)
            
            session.commit()
            logger.info(f"Updated plan {plan_id}")
            return True
    
    @staticmethod
    def delete_plan(plan_id: int) -> bool:
        """Delete plan"""
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return False
            
            session.delete(plan)
            session.commit()
            logger.info(f"Deleted plan {plan_id}")
            return True

