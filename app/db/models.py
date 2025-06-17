from sqlalchemy import String, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String)
    coins_balance: Mapped[int] = mapped_column(default=0)
    is_banned: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    giveaways = relationship("Giveaway", back_populates="owner")
    participants = relationship("Participant", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    gifts = relationship("Gift", back_populates="user")
    withdrawals = relationship("WithdrawRequest", back_populates="user")


class Giveaway(Base):
    __tablename__ = "giveaways"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    emoji: Mapped[str] = mapped_column(String, nullable=False)
    target_value: Mapped[int] = mapped_column(nullable=False)
    price_per_attempt: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String)
    status: Mapped[str] = mapped_column(default="active")  # active | finished
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="giveaways")
    participants = relationship("Participant", back_populates="giveaway")
    transactions = relationship("Transaction", back_populates="giveaway")


# 🧍 Участие в розыгрыше
class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    giveaway_id: Mapped[int] = mapped_column(ForeignKey("giveaways.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    giveaway = relationship("Giveaway", back_populates="participants")
    user = relationship("User", back_populates="participants")
    attempts = relationship("Attempt", back_populates="participant")


# 🎯 Попытки (броски emoji)
class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"))
    emoji_value: Mapped[int]
    is_winner: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    participant = relationship("Participant", back_populates="attempts")


# 💳 Транзакции (Coins)
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int]
    type: Mapped[str]  # topup | entry_fee | commission | referral_bonus | organizer_reward
    related_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    giveaway_id: Mapped[int | None] = mapped_column(ForeignKey("giveaways.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id], back_populates="transactions")
    giveaway = relationship("Giveaway", back_populates="transactions")


# ⭐️ Подарки Telegram Stars
class Gift(Base):
    __tablename__ = "gifts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    stars: Mapped[int]
    message_id: Mapped[int | None] = mapped_column(nullable=True)
    processed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user = relationship("User", back_populates="gifts")


# 📈 Рефералы
class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    giveaway_id: Mapped[int | None] = mapped_column(ForeignKey("giveaways.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


# 💸 Заявки на вывод
class WithdrawRequest(Base):
    __tablename__ = "withdraw_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount_coins: Mapped[int]
    status: Mapped[str] = mapped_column(default="pending")  # pending | approved | rejected
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user = relationship("User", back_populates="withdrawals")
