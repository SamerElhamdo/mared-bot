from sqlalchemy.orm import Session, joinedload
from typing import Optional
from database.models import Payment, PaymentStatus, Plan
from database.base import get_session
from services.subscription_service import SubscriptionService
import logging

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def create_payment(user_id: int, plan_id: int, amount: float, currency: str = "USDT",
                      provider: str = "manual", wallet_address: str = None, network: str = None) -> Payment:
        """Create a new payment record"""
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise ValueError(f"Plan with id {plan_id} not found")
            
            payment = Payment(
                user_id=user_id,
                plan_id=plan_id,
                amount=amount,
                currency=currency,
                network=network,
                status=PaymentStatus.PENDING,
                provider=provider,
                wallet_address=wallet_address,
            )
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            network_info = f" on {network}" if network else ""
            logger.info(f"Created payment {payment.id} for user {user_id}, amount: {amount} {currency}{network_info}")
            return payment
    
    @staticmethod
    def confirm_payment(payment_id: int, transaction_id: str = None) -> bool:
        """Confirm a payment and activate subscription"""
        with get_session() as session:
            payment = session.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return False
            
            if payment.status == PaymentStatus.COMPLETED:
                logger.warning(f"Payment {payment_id} already completed")
                return False
            
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            if transaction_id:
                payment.transaction_id = transaction_id
            session.commit()
            
            # Create or activate subscription
            subscription = SubscriptionService.get_active_subscription(payment.user_id)
            if not subscription:
                subscription = SubscriptionService.create_subscription(
                    payment.user_id,
                    payment.plan_id,
                    is_trial=False
                )
            else:
                SubscriptionService.activate_subscription(subscription.id)
            
            payment.subscription_id = subscription.id
            session.commit()
            
            logger.info(f"Confirmed payment {payment_id}, activated subscription {subscription.id}")
            return True
    
    @staticmethod
    def get_payment(payment_id: int) -> Optional[Payment]:
        """Get payment by ID with user loaded eagerly"""
        with get_session() as session:
            return session.query(Payment).options(
                joinedload(Payment.user)
            ).filter(Payment.id == payment_id).first()
    
    @staticmethod
    def get_user_payments(user_id: int) -> list:
        """Get all payments for a user"""
        with get_session() as session:
            return session.query(Payment).filter(
                Payment.user_id == user_id
            ).order_by(Payment.created_at.desc()).all()
    
    @staticmethod
    def get_pending_payments(user_id: int) -> list:
        """Get pending payments for a user"""
        with get_session() as session:
            return session.query(Payment).filter(
                Payment.user_id == user_id,
                Payment.status == PaymentStatus.PENDING
            ).all()

