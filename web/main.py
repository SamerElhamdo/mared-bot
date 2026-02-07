"""
Web UI Admin Panel for Mared Bot
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import hashlib
import secrets
from datetime import datetime

from database.base import get_session
from database.models import Plan, User, Subscription, Payment, SubscriptionStatus, PaymentStatus, PlanDuration
from services.plan_service import PlanService
from services.subscription_service import SubscriptionService
from services.user_service import UserService
from services.payment_service import PaymentService
from config.settings import settings

app = FastAPI(title="Mared Bot Admin Panel")

# Templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Simple session storage (in production, use proper session management)
sessions = {}


def get_db():
    """Dependency to get database session"""
    with get_session() as session:
        yield session


def check_admin_session(request: Request) -> bool:
    """Check if user has valid admin session"""
    session_id = request.cookies.get("admin_session")
    if not session_id or session_id not in sessions:
        return False
    return True


def require_admin(request: Request):
    """Dependency to require admin authentication"""
    if not check_admin_session(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    """Handle login"""
    # Simple password check (in production, use proper authentication)
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    if password == admin_password:
        # Create session
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = {
            "user_id": "admin",
            "login_time": datetime.now()
        }
        
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="admin_session", value=session_id, httponly=True)
        return response
    else:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "كلمة المرور غير صحيحة"}
        )


@app.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    session_id = request.cookies.get("admin_session")
    if session_id:
        sessions.pop(session_id, None)
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="admin_session")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, _: bool = Depends(require_admin)):
    """Admin dashboard"""
    with get_session() as session:
        total_users = session.query(User).count()
        active_subscriptions = session.query(Subscription).filter(
            Subscription.status == SubscriptionStatus.ACTIVE
        ).count()
        pending_payments = session.query(Payment).filter(
            Payment.status == PaymentStatus.PENDING
        ).count()
        total_revenue = session.query(
            func.sum(Payment.amount)
        ).filter(
            Payment.status == PaymentStatus.COMPLETED
        ).scalar() or 0
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_users": total_users,
        "active_subscriptions": active_subscriptions,
        "pending_payments": pending_payments,
        "total_revenue": float(total_revenue)
    })


@app.get("/plans", response_class=HTMLResponse)
async def plans_page(request: Request, _: bool = Depends(require_admin)):
    """Plans management page"""
    with get_session() as session:
        plans = session.query(Plan).order_by(Plan.id).all()
    
    return templates.TemplateResponse("plans.html", {
        "request": request,
        "plans": plans
    })


@app.get("/api/plans")
async def get_plans_api(_: bool = Depends(require_admin)):
    """Get all plans (API)"""
    with get_session() as session:
        plans = session.query(Plan).order_by(Plan.id).all()
        return JSONResponse(content=[
            {
                "id": p.id,
                "name": p.name,
                "name_ar": p.name_ar,
                "duration": p.duration.value,
                "duration_days": p.duration_days,
                "price": float(p.price),
                "currency": p.currency,
                "is_active": p.is_active
            }
            for p in plans
        ])


@app.post("/api/plans")
async def create_plan_api(
    request: Request,
    name: str = Form(...),
    name_ar: str = Form(...),
    duration: str = Form(...),
    duration_days: int = Form(...),
    price: float = Form(...),
    currency: str = Form("USDT"),
    is_active: bool = Form(True),
    _: bool = Depends(require_admin)
):
    """Create new plan"""
    try:
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
            return JSONResponse(content={"success": True, "plan_id": plan.id})
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@app.put("/api/plans/{plan_id}")
async def update_plan_api(
    plan_id: int,
    request: Request,
    _: bool = Depends(require_admin)
):
    """Update plan"""
    data = await request.json()
    try:
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Plan not found"}
                )
            
            if "name" in data:
                plan.name = data["name"]
            if "name_ar" in data:
                plan.name_ar = data["name_ar"]
            if "duration" in data:
                plan.duration = PlanDuration(data["duration"])
            if "duration_days" in data:
                plan.duration_days = data["duration_days"]
            if "price" in data:
                plan.price = data["price"]
            if "currency" in data:
                plan.currency = data["currency"]
            if "is_active" in data:
                plan.is_active = data["is_active"]
            
            session.commit()
            return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@app.delete("/api/plans/{plan_id}")
async def delete_plan_api(plan_id: int, _: bool = Depends(require_admin)):
    """Delete plan"""
    try:
        with get_session() as session:
            plan = session.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Plan not found"}
                )
            session.delete(plan)
            session.commit()
            return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


@app.get("/subscriptions", response_class=HTMLResponse)
async def subscriptions_page(request: Request, _: bool = Depends(require_admin)):
    """Subscriptions management page"""
    with get_session() as session:
        subscriptions = session.query(Subscription).join(User).join(Plan).order_by(
            Subscription.created_at.desc()
        ).limit(100).all()
    
    return templates.TemplateResponse("subscriptions.html", {
        "request": request,
        "subscriptions": subscriptions
    })


@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, _: bool = Depends(require_admin)):
    """Users management page"""
    with get_session() as session:
        users = session.query(User).order_by(User.created_at.desc()).limit(100).all()
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users
    })


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, _: bool = Depends(require_admin)):
    """Settings page"""
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": {
            "BOT_TOKEN": settings.BOT_TOKEN[:10] + "..." if settings.BOT_TOKEN else "",
            "CHANNEL_ID": settings.CHANNEL_ID,
            "FREE_TRIAL_DAYS": settings.FREE_TRIAL_DAYS,
            "USDT_TRC20_ADDRESS": settings.USDT_TRC20_ADDRESS,
            "USDT_BSC_ADDRESS": settings.USDT_BSC_ADDRESS,
        }
    })


@app.post("/api/subscriptions/{subscription_id}/activate")
async def activate_subscription_api(
    subscription_id: int,
    _: bool = Depends(require_admin)
):
    """Activate subscription manually"""
    try:
        with get_session() as session:
            subscription = session.query(Subscription).filter(
                Subscription.id == subscription_id
            ).first()
            if not subscription:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "error": "Subscription not found"}
                )
            
            # Activate subscription
            subscription.status = SubscriptionStatus.ACTIVE
            session.commit()
            
            # Add user to channel
            from bot.channel_manager import ChannelManager
            from aiogram import Bot
            bot = Bot(token=settings.BOT_TOKEN)
            channel_manager = ChannelManager(bot)
            await channel_manager.add_user(subscription.user.telegram_id)
            await bot.session.close()
            
        return JSONResponse(content={"success": True})
    except Exception as e:
        import traceback
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e), "traceback": traceback.format_exc()}
        )


@app.post("/api/payments/{payment_id}/confirm")
async def confirm_payment_api(
    payment_id: int,
    _: bool = Depends(require_admin)
):
    """Confirm payment manually"""
    try:
        success = PaymentService.confirm_payment(payment_id)
        if success:
            return JSONResponse(content={"success": True})
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Payment confirmation failed"}
            )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

