from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import backref, relationship
from typing_extensions import Self

from ckan import model, types
from ckan.plugins import toolkit as tk

from ckanext.ap_support.types import DictizedMessage, DictizedTicket, TicketData

log = logging.getLogger(__name__)


class Ticket(tk.BaseModel):
    __tablename__ = "ap_support_ticket"

    class Status:
        opened = "opened"
        closed = "closed"

    id = Column(Integer, primary_key=True)
    subject = Column(Text)
    status = Column(Text, default=Status.opened)
    text = Column(Text)
    category = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    author_id = Column(Text, ForeignKey(model.User.id), nullable=False)

    author = relationship(
        model.User,
        backref=backref("tickets", cascade="all, delete"),
    )

    messages = relationship(
        "TicketMessage",
        backref="ticket",
        order_by="TicketMessage.created_at",
        cascade="all, delete",
    )

    def __str__(self):
        return f"Ticket #{self.id}: {self.subject}"

    @classmethod
    def get(cls, ticket_id: str) -> Self | None:
        query = model.Session.query(cls).filter(cls.id == ticket_id)

        return query.one_or_none()

    @classmethod
    def get_list(cls, statuses: list[str] | None = None) -> list[Self]:
        """Get a list of tickets.

        Args:
            statuses: Filter by ticket status.
        """
        query = model.Session.query(cls)

        if statuses:
            query = query.filter(cls.status.in_(statuses))

        query = query.order_by(cls.updated_at.desc())

        return query.all()

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    @classmethod
    def add(cls, ticket_data: TicketData) -> DictizedTicket:
        ticket = cls(
            subject=ticket_data["subject"],
            category=ticket_data["category"],
            text=ticket_data["text"],
            author_id=ticket_data["author_id"],
        )

        model.Session.add(ticket)
        model.Session.commit()

        return ticket.dictize({})

    def dictize(self, context: types.Context) -> DictizedTicket:
        return DictizedTicket(
            id=int(self.id),
            subject=str(self.subject),
            status=str(self.status),
            text=str(self.text),
            author=self.author.as_dict(),
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
            messages=[msg.dictize(context) for msg in self.messages],
        )

class TicketMessage(tk.BaseModel):
    __tablename__ = "ap_support_ticket_message"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("ap_support_ticket.id"), nullable=False)
    author_id = Column(Text, ForeignKey(model.User.id), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author = relationship(model.User)
    ticket = relationship("Ticket", backref="ticket_messages")

    @classmethod
    def get(cls, message_id: int) -> Self | None:
        query = model.Session.query(cls).filter(cls.id == message_id)
        return query.one_or_none()

    @classmethod
    def add(cls, ticket_id: int, author_id: str, content: str) -> Self:
        message = cls(ticket_id=ticket_id, author_id=author_id, content=content)
        model.Session.add(message)
        model.Session.commit()

        return message

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)

    def update(self, content: str) -> None:
        self.content = content
        self.updated_at = datetime.utcnow()

    def dictize(self, context: types.Context) -> DictizedMessage:
        return DictizedMessage(
            id=int(self.id),
            ticket_id=int(self.ticket.id),
            content=str(self.content),
            author=self.author.as_dict(),
            created_at=self.created_at.isoformat(),
            updated_at=self.updated_at.isoformat(),
        )
