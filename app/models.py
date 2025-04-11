from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
import uuid

class UserBase(SQLModel):
    auth0_id: str = Field(index=True, unique=True)
    username: Optional[str] = None
    email: str = Field(index=True, unique=True)

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    conversations: List["Conversation"] = Relationship(back_populates="user")

class ConversationBase(SQLModel):
    title: str = Field(default="new conversation", max_length=255)


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class MessageBase(SQLModel):
    role: str = Field(default="user")
    content: str


class Message(MessageBase, table=True):
    __tablename__ = "messages"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    conversation: Conversation = Relationship(back_populates="messages")


class ConversationListItem(SQLModel):
    id: uuid.UUID
    title: str
    updated_at: datetime


class MessageItem(SQLModel):
    role: str
    content: str
    created_at: datetime


class ConversationDetail(SQLModel):
    id: uuid.UUID
    title: str
    messages: List[MessageItem]
