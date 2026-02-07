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
                name="1 Month Plan",
                name_ar="الخطة الشهرية (شهر واحد)",
                name_en="1 Month Plan",
                duration=PlanDuration.MONTHLY,
                duration_days=30,
                price=30.00,
                currency="USDT",
                is_active=True,
            ),
            Plan(
                name="3 Months Plan",
                name_ar="الخطة الربع سنوية (3 أشهر)",
                name_en="3 Months Plan",
                duration=PlanDuration.MONTHLY,
                duration_days=90,
                price=80.00,
                currency="USDT",
                is_active=True,
            ),
            Plan(
                name="6 Months Plan",
                name_ar="الخطة النصف سنوية (6 أشهر)",
                name_en="6 Months Plan",
                duration=PlanDuration.MONTHLY,
                duration_days=180,
                price=150.00,
                currency="USDT",
                is_active=True,
            ),
            Plan(
                name="12 Months Plan",
                name_ar="الخطة السنوية (12 شهر)",
                name_en="12 Months Plan",
                duration=PlanDuration.YEARLY,
                duration_days=365,
                price=280.00,
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

