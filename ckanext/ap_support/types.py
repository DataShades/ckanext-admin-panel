from typing import Any, TypedDict


class TicketData(TypedDict):
    subject: str
    text: str
    author_id: str
    category: str


class DictizedMessage(TypedDict):
    id: int
    ticket_id: int
    content: str
    author: dict[str, Any]
    created_at: str
    updated_at: str | None


class DictizedTicket(TypedDict):
    id: int
    subject: str
    status: str
    text: str
    author: dict[str, Any]
    assignee: dict[str, Any] | None
    created_at: str
    updated_at: str
    messages: list[DictizedMessage]
