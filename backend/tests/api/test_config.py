import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user_config(client: AsyncClient):
    """测试创建用户配置"""
    response = await client.post("/config/user", json={
        "api_key": "test-api-key",
        "base_url": "https://api.test.com/v1",
        "ai_model": "gpt-4",
        "temperature": 0.8,
        "max_tokens": 1000,
        "user_id": "test-user"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["api_key"] == "test-api-key"
    assert data["user_id"] == "test-user"
    assert data["ai_model"] == "gpt-4"

@pytest.mark.asyncio
async def test_get_user_config(client: AsyncClient):
    """测试获取用户配置"""
    # 先创建配置
    await client.post("/config/user", json={
        "api_key": "test-api-key",
        "user_id": "test-user"
    })
    
    # 获取配置
    response = await client.get("/config/user/test-user")
    assert response.status_code == 200
    data = response.json()
    assert data["api_key"] == "test-api-key"
    assert data["user_id"] == "test-user"

@pytest.mark.asyncio
async def test_update_user_config(client: AsyncClient):
    """测试更新用户配置"""
    # 先创建配置
    await client.post("/config/user", json={
        "api_key": "test-api-key",
        "user_id": "test-user"
    })
    
    # 更新配置
    response = await client.put("/config/user/test-user", json={
        "api_key": "new-api-key",
        "ai_model": "gpt-4"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["api_key"] == "new-api-key"
    assert data["ai_model"] == "gpt-4"

@pytest.mark.asyncio
async def test_delete_user_config(client: AsyncClient):
    """测试删除用户配置"""
    # 先创建配置
    await client.post("/config/user", json={
        "api_key": "test-api-key",
        "user_id": "test-user"
    })
    
    # 删除配置
    response = await client.delete("/config/user/test-user")
    assert response.status_code == 200
    
    # 验证配置已被删除
    response = await client.get("/config/user/test-user")
    assert response.status_code == 404 