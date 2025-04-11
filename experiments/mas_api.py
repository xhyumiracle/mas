from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
import uuid
from sqlmodel import Session, select, or_, and_, col, delete
import uvicorn
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import json
from pydantic import BaseModel
from typing import List, Optional

from app.auth.utils import VerifyToken
from app.database import create_db_and_tables, get_session
from app.models import Conversation, ConversationListItem, Message, User

from mas.orch import Orchestrator, MockOrch
from mas.curator import ModelCurator, ToolCurator
from mas.flow import AgentTaskFlow
from mas.agent import Agent, MockAgent, AgnoAgent
from mas.message import Message
from mas.flow.executor.sequential import SequentialExecutor

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_system()
    yield

app = FastAPI(
    title="MAS API",
    description="API for Multi-Agent System Chat",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],  # Allows all origins
    allow_origins=["http://localhost:5174", "https://dev.chatolm.com", "https://chatolm.com", "https://www.chatolm.com"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

auth = VerifyToken()

# Global variables
orch = None


# Pydantic models for request and response
class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[uuid.UUID] = None

class TaskItem(BaseModel):
    type: str
    action: str
    agent: Optional[str] = None
    content: str

class ChatResponseData(BaseModel):
    id: str
    role: str = "assistant"
    requestId: str = "sync"
    tokenCount: int = 0
    tasks: List[TaskItem]

class ChatResponse(BaseModel):
    data: ChatResponseData
    statusCode: int = 200
    message: str = "ok"

class StreamEventType(str, Enum):
    INIT_CONVERSATION = "init_conversation"
    TASK_GRAPH = "task_graph"
    AGENT_RESPONSE = "agent_response"
    FINAL_ANSWER = "final_answer"
    ERROR = "error"
    DONE = "done"

class StreamTaskItem(BaseModel):
    type: str  # markdown/mermaid
    action: str
    agent: Optional[str] = None
    content: str

class StreamEvent(BaseModel):
    event: StreamEventType
    data: StreamTaskItem | dict

async def initialize_system():
    """Initialize the MAS system"""
    global orch

    orch = MockOrch()

class OptionalHTTPBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

# 实例化可选HTTP Bearer
optional_http_bearer = OptionalHTTPBearer(auto_error=False)


async def get_current_user(
    session: Session = Depends(get_session),
    token: Optional[HTTPAuthorizationCredentials] = Security(optional_http_bearer)
) -> Optional[User]:
    """
    验证Auth0令牌并返回当前用户
    如果用户不存在于数据库中，则创建新用户
    """
 
    if not token:
        return None
    
    try:
        # 验证令牌
        payload = await auth.verify(token)
        
        # 从令牌中获取用户标识符
        auth0_id = payload.get("sub")
        if not auth0_id:
            raise auth.UnauthorizedException(detail="invalid token")
        
        # 在数据库中查找用户
        statement = select(User).where(User.auth0_id == auth0_id)
        results = session.exec(statement)
        user = results.first()
        
        if not user:
            email = payload.get("email", f"{auth0_id}@example.com")
            
            new_user = User(
                auth0_id=auth0_id,
                email=email
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            return new_user
        
        return user
    except Exception as e:
        # 其他异常也返回None
        return None

async def event_generator(request: Request, question: str, conversation_id: uuid.UUID, session: Session):
    def format_sse(event: StreamEvent) -> str:
        data = event.data.model_dump_json() if isinstance(event.data, BaseModel) else json.dumps(event.data)
        return f"event: {event.event.value}\ndata: {data}\n\n"
        
        
    if await request.is_disconnected():
        print("Client disconnected")
        return

    event = StreamEvent(
        event=StreamEventType.INIT_CONVERSATION,
        data=StreamTaskItem(
            type="conversationid",
            action=question,
            content=str(conversation_id)
        )        )
    yield format_sse(event)
    
    task_graph = orch.generate(query=question)

    curators = [ToolCurator(), ModelCurator()]
    agent_task_graph = task_graph
    for curator in curators:
        agent_task_graph = curator.curate(agent_task_graph)

    print("Curation done")
    agent_task_graph.pprint()
    mermaid_code = agent_task_graph.generate_mermaid_code()

    actions = []
    task_graph_action = {
        "type": "mermaid",
        "action": "task graph",
        "content": mermaid_code,
        }
    actions.append(task_graph_action)

    event = StreamEvent(
        event=StreamEventType.TASK_GRAPH,
        data=StreamTaskItem(
        type="mermaid",
        action="任务流程图",
        content=mermaid_code
        )
    )
    yield format_sse(event)

    try:
        flow = AgentTaskFlow(
            cls_Agent=MockAgent,
            executor=SequentialExecutor(),
        )
        flow.build(agent_task_graph)

        for response in flow.run():
            # content = repr(response["content"])
            content = "test"
            agent_graph_action = {
                "type": "markdown",
                "action": "prompt",
                "content": content,
                "agent_id": "mas",
            }
            actions.append(agent_graph_action)

            event = StreamEvent(
                event=StreamEventType.AGENT_RESPONSE,
                data=StreamTaskItem(
                type="markdown",
                action="prompt",
                content=content
                )
            )
            yield format_sse(event)

        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=json.dumps(actions)
        )
        session.add(ai_message)
        session.commit()
    except Exception as e:
        event = StreamEvent(
            event=StreamEventType.ERROR,
            data={"message": f"代理图构建失败: {str(e)}"}
        )
        yield format_sse(event)
            
    # 发送完成事件
    event = StreamEvent(
        event=StreamEventType.DONE,
        data={"message": "Stream completed"}
    )
    yield format_sse(event)

@app.post("/api/chat/stream")
async def chat_stream(request: Request,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)):
    """Stream chat responses using SSE"""
    if not chat_request.question.strip():
        raise HTTPException(status_code=400, detail="Empty question")
    
    is_authenticated = current_user is not None

    conversation_id = chat_request.conversation_id
    conversation = None
    
    if is_authenticated:
        # 如果没有提供对话ID，创建新对话
        if not conversation_id:
            conversation = Conversation(
                title=chat_request.question[:20] + ("..." if len(chat_request.question) > 20 else ""),
                user_id=current_user.id
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            conversation_id = conversation.id
        else:
            # 检查对话是否存在且属于当前用户
            statement = select(Conversation).where(
                and_(
                    Conversation.id == conversation_id,
                    Conversation.user_id == current_user.id
                )
            )
            results = session.exec(statement)
            conversation = results.first()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="conversation not found")
        
        if conversation:
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            session.commit()
        
        # 保存用户消息
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=chat_request.question
        )
        session.add(user_message)
        session.commit()
    elif conversation_id is not None:
        raise HTTPException(status_code=404, detail="conversation not found")

    return StreamingResponse(
        event_generator(request, chat_request.question, conversation_id, session),
        media_type="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Encoding": "none",
            "Access-Control-Allow-Origin": "*",
        },
    )

@app.get("/api/conversations", response_model=List[ConversationListItem])
async def list_conversations(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有对话列表，只返回id和标题
    """
    is_authenticated = current_user is not None
    if not is_authenticated:
        return []
    session = next(get_session())
    
    statement = select(Conversation).where(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc())
    
    results = session.exec(statement)
    conversations = results.all()
    
    return [
        ConversationListItem(
            id=conv.id,
            title=conv.title,
            updated_at=conv.updated_at
        ) for conv in conversations
    ]

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    """
    获取特定对话的详情，包括所有消息历史
    """
    session = next(get_session())
    
    # 检查对话是否存在且属于当前用户
    statement = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    results = session.exec(statement)
    conversation = results.first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    # 获取该对话的所有消息
    statement = select(Message).where(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc())
    
    results = session.exec(statement)
    messages = results.all()

    response_data = {
        "id": str(conversation.id),
        "title": conversation.title,
        "messages": []
    }
    
    for msg in messages:
        message_data = {
            "id": str(msg.id),
            "role": msg.role,
            "created_at": msg.created_at.isoformat()
        }
        
        if msg.role == "user":
            # 用户消息直接使用原始内容
            message_data["content"] = msg.content
        else:  # 助手消息 (role == "assistant")
            try:
                # 尝试解析JSON内容
                content_data = json.loads(msg.content)
                message_data["content"] = content_data  # 直接返回解析后的JSON对象
            except json.JSONDecodeError:
                # 解析失败，使用原始内容
                message_data["content"] = msg.content
        
        response_data["messages"].append(message_data)
    
    # 直接返回字典而不使用Pydantic模型
    return response_data


class ConversationInfo(BaseModel):
    id: str
    title: str
    updated_at: str


@app.get("/api/conversations/{conversation_id}/exists", response_model=ConversationInfo)
def check_conversation_exists(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """检查特定会话是否存在，如果存在则返回会话信息"""
    # 查询会话
    statement = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    results = session.exec(statement)
    conversation = results.first()
    
    # 如果会话不存在，返回404错误
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    # 返回会话信息
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "updated_at": conversation.updated_at.isoformat()
    }

class CreateConversationRequest(BaseModel):
    title: Optional[str] = "new conversation"

# 创建会话的响应模型
class CreateConversationResponse(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str

# 创建新会话接口
@app.post("/api/conversations", response_model=CreateConversationResponse)
def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """创建一个新的空会话"""
    # 创建新会话
    new_conversation = Conversation(
        id=uuid.uuid4(),
        user_id=current_user.id,
        title=request.title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    session.add(new_conversation)
    session.commit()
    session.refresh(new_conversation)
    
    return {
        "id": str(new_conversation.id),
        "title": new_conversation.title,
        "created_at": new_conversation.created_at.isoformat(),
        "updated_at": new_conversation.updated_at.isoformat()
    }

class UpdateTitleRequest(BaseModel):
    title: str

@app.put("/api/conversations/{conversation_id}/title")
def update_conversation_title(
    conversation_id: uuid.UUID,
    request: UpdateTitleRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """更新特定会话的标题"""
    # 检查会话是否存在且属于当前用户
    statement = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    results = session.exec(statement)
    conversation = results.first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    # 更新标题
    conversation.title = request.title
    session.add(conversation)
    session.commit()
    
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "updated_at": conversation.updated_at.isoformat()
    }

@app.delete("/api/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """删除特定会话及其所有消息"""
    statement = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    results = session.exec(statement)
    conversation = results.first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    try:
        # 先删除关联的消息
        delete_messages_stmt = delete(Message).where(
            Message.conversation_id == conversation_id
        )
        session.exec(delete_messages_stmt)
        
        # 然后删除会话
        session.delete(conversation)
        session.commit()
        
        return {"status": "success", "message": "conversation deleted"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"failed to delete conversation: {str(e)}"
        )

@app.get("/api/health")
async def health_check():
    """Endpoint to check if the API is running."""
    return {"status": "healthy", "agents_loaded": len(agent_pool) if agent_pool else 0}

if __name__ == "__main__":
    create_db_and_tables()
    uvicorn.run("mas_api:app", host="0.0.0.0", port=8000, reload=True)