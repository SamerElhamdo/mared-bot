"""
Script to initialize default subscription plans
Run this after setting up the database
"""
from database.base import get_session, init_db
from database.models import Plan, PlanDuration

def init_plans():
    """Initialize default plans"""
    init_db()
    
    with get_session() as session:
        # Check if plans already exist
        existing = session.query(Plan).count()
        if existing > 0:
            print("Plans already exist. Skipping initialization.")
            return
        
        plans = [
            Plan(
                name="Weekly Plan",
                name_ar="الخطة الأسبوعية",
                name_en="Weekly Plan",
                duration=PlanDuration.WEEKLY,
                duration_days=7,
                price=10.00,
                currency="USDT",
                is_active=True,
            ),
            Plan(
                name="Monthly Plan",
                name_ar="الخطة الشهرية",
                name_en="Monthly Plan",
                duration=PlanDuration.MONTHLY,
                duration_days=30,
                price=30.00,
                currency="USDT",
                is_active=True,
            ),
            Plan(
                name="Yearly Plan",
                name_ar="الخطة السنوية",
                name_en="Yearly Plan",
                duration=PlanDuration.YEARLY,
                duration_days=365,
                price=300.00,
                currency="USDT",
                is_active=True,
            ),
        ]
        
        for plan in plans:
            session.add(plan)
        
        session.commit()
        print(f"Initialized {len(plans)} plans successfully!")

if __name__ == "__main__":
    init_plans()

