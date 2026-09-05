from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    segment: Mapped[str] = mapped_column(String, default="standard")
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False)


class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    customer_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String, default="pending")


class PaymentEvent(Base):
    __tablename__ = "payment_events"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_type: Mapped[str] = mapped_column(String)
    customer_id: Mapped[str] = mapped_column(String, index=True)
    subscription_id: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[float] = mapped_column(Float)
    failure_reason: Mapped[str] = mapped_column(String)
    attempt_number: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, index=True)
    customer_id: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float)
    recovery_probability: Mapped[float] = mapped_column(Float)
    action: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    recovered_amount: Mapped[float] = mapped_column(Float, default=0)
    diagnosis: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)
    policy_status: Mapped[str] = mapped_column(String)
    requires_human: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, index=True)
    customer_id: Mapped[str] = mapped_column(String)
    event: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String, default="-")
    result: Mapped[str] = mapped_column(String)
    policy_status: Mapped[str] = mapped_column(String, default="N/A")
    detail: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
