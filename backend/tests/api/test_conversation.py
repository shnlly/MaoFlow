import pytest
from httpx import AsyncClient
from app.models.conversation import MessageRole, MessageType

@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient):
    """测试创建会话"""
    response = await client.post("/conversations", json={
        "title": "Test Conversation",
        "description": "This is a test conversation",
        "user_id": "test-user",
        "model": "gpt-3.5-turbo"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert data["user_id"] == "test-user"
    assert data["model"] == "gpt-3.5-turbo"
    assert "id" in data
    assert len(data["messages"]) == 0

@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient):
    """测试获取用户的所有会话"""
    # 创建两个会话
    for i in range(2):
        await client.post("/conversations", json={
            "title": f"Test Conversation {i}",
            "user_id": "test-user",
            "model": "gpt-3.5-turbo"
        })
    
    response = await client.get("/conversations/test-user")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Test Conversation 0"
    assert data[1]["title"] == "Test Conversation 1"

@pytest.mark.asyncio
async def test_get_conversation_detail(client: AsyncClient):
    """测试获取会话详情"""
    # 创建会话
    response = await client.post("/conversations", json={
        "title": "Test Conversation",
        "user_id": "test-user",
        "model": "gpt-3.5-turbo"
    })
    conversation_id = response.json()["id"]
    
    # 添加消息
    await client.post(f"/conversations/{conversation_id}/messages", json={
        "role": MessageRole.USER.value,
        "type": MessageType.TEXT.value,
        "content": "Hello, AI!"
    })
    
    # 获取会话详情
    response = await client.get(f"/conversations/{conversation_id}/detail")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Conversation"
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "Hello, AI!"

@pytest.mark.asyncio
async def test_add_message(client: AsyncClient):
    """测试添加消息到会话"""
    # 创建会话
    response = await client.post("/conversations", json={
        "title": "Test Conversation",
        "user_id": "test-user",
        "model": "gpt-3.5-turbo"
    })
    conversation_id = response.json()["id"]
    
    # 添加消息
    response = await client.post(f"/conversations/{conversation_id}/messages", json={
        "role": MessageRole.USER.value,
        "type": MessageType.TEXT.value,
        "content": "Hello, AI!",
        "tokens": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello, AI!"
    assert data["role"] == MessageRole.USER.value
    assert data["type"] == MessageType.TEXT.value
    assert data["tokens"] == 10

@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient):
    """测试删除会话"""
    # 创建会话
    response = await client.post("/conversations", json={
        "title": "Test Conversation",
        "user_id": "test-user",
        "model": "gpt-3.5-turbo"
    })
    conversation_id = response.json()["id"]
    
    # 删除会话
    response = await client.delete(f"/conversations/{conversation_id}")
    assert response.status_code == 200
    
    # 验证会话已被删除
    response = await client.get(f"/conversations/{conversation_id}/detail")
    assert response.status_code == 404 