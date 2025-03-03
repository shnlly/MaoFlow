import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

async def test_get_default_user(client: AsyncClient):
    """测试获取默认用户接口"""
    # 第一次调用，应该创建新用户
    response = await client.get("/api/user/default")
    assert response.status_code == 200
    data = response.json()
    
    # 验证返回的用户数据
    assert data["username"] == "test_user"
    assert data["nickname"] == "测试用户"
    assert "id" in data
    first_user_id = data["id"]
    
    # 第二次调用，应该返回同一个用户
    response = await client.get("/api/user/default")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == first_user_id

async def test_get_user_settings(client: AsyncClient):
    """测试获取用户设置接口"""
    # 先创建一个用户
    response = await client.get("/api/user/default")
    user_id = response.json()["id"]
    
    # 获取用户设置
    response = await client.get(f"/api/user/{user_id}/settings")
    assert response.status_code == 200
    settings = response.json()
    
    # 验证默认设置
    assert settings["theme"] == "light"
    assert settings["language"] == "zh-CN"
    assert settings["notifications_enabled"] is True
    assert settings["custom_settings"] == {}
    
    # 测试不存在的用户
    response = await client.get("/api/user/non-existent-id/settings")
    assert response.status_code == 404

async def test_update_user_settings(client: AsyncClient):
    """测试更新用户设置接口"""
    # 先创建一个用户
    response = await client.get("/api/user/default")
    user_id = response.json()["id"]
    
    # 更新部分设置
    update_data = {
        "theme": "dark",
        "custom_settings": {"font_size": 14}
    }
    response = await client.patch(f"/api/user/{user_id}/settings", json=update_data)
    assert response.status_code == 200
    settings = response.json()
    
    # 验证更新后的设置
    assert settings["theme"] == "dark"
    assert settings["language"] == "zh-CN"  # 未更新的设置保持默认值
    assert settings["notifications_enabled"] is True  # 未更新的设置保持默认值
    assert settings["custom_settings"] == {"font_size": 14}
    
    # 再次更新自定义设置
    update_data = {
        "custom_settings": {"color": "blue"}
    }
    response = await client.patch(f"/api/user/{user_id}/settings", json=update_data)
    assert response.status_code == 200
    settings = response.json()
    
    # 验证自定义设置被合并
    assert settings["custom_settings"] == {
        "font_size": 14,
        "color": "blue"
    }
    
    # 再次获取设置确认持久化
    response = await client.get(f"/api/user/{user_id}/settings")
    assert response.status_code == 200
    settings = response.json()
    assert settings["custom_settings"] == {
        "font_size": 14,
        "color": "blue"
    }
    
    # 测试不存在的用户
    response = await client.patch("/api/user/non-existent-id/settings", json=update_data)
    assert response.status_code == 404 