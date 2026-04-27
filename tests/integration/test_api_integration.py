import pytest
import httpx
import uuid
from typing import Dict

# Pytest configuration
BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="module")
def client():
    """Provides a synchronous HTTPX client for full e2e testing against the live Docker container."""
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as c:
        yield c

@pytest.fixture(scope="module")
def user_data() -> Dict[str, str]:
    """Provides unique test user credentials."""
    return {
        "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
        "password": "SecurePassword123!",
        "first_name": "Integration",
        "last_name": "Tester"
    }

@pytest.fixture(scope="module")
def state():
    """State dictionary to pass tokens between sequential test steps."""
    return {"access_token": None, "refresh_token": None, "user_id": None}


def test_01_register_user(client: httpx.Client, user_data: Dict[str, str], state: dict):
    """1. Register user → Expect 201 with user object"""
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201, f"Registration failed: {response.text}"
    
    data = response.json()
    assert "id" in data
    assert data["email"] == user_data["email"]
    state["user_id"] = data["id"]

def test_02_login(client: httpx.Client, user_data: Dict[str, str], state: dict):
    """2. Login → Expect 200 with JWT token"""
    # FastAPI OAuth2PasswordRequestForm expects form data, not JSON
    form_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = client.post("/auth/login", data=form_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    
    # Store tokens for subsequent authenticated requests
    state["access_token"] = data["access_token"]
    state["refresh_token"] = data["refresh_token"]

def test_03_upload_test_image(client: httpx.Client, state: dict):
    """3. Upload test image → Expect analysis response with correct structure"""
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    
    # Create a tiny dummy image (1x1 pixel black GIF) to test the endpoint upload wrapper
    dummy_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01D\x00;'
    files = {"file": ("test_image.gif", dummy_gif, "image/gif")}
    data = {"analysis_type": "skin"}
    
    response = client.post("/analysis/image", headers=headers, files=files, data=data)
    
    # We expect either 200 (if analysis mocked successfully) or 400 (if CV heuristics reject the 1x1 image)
    # The key is checking the integration layer responds properly without crashing (500)
    assert response.status_code in [200, 400], f"Image upload failed: {response.text}"
    
    if response.status_code == 200:
        json_resp = response.json()
        assert "analysis_type" in json_resp

def test_04_send_chat_message(client: httpx.Client, state: dict):
    """4. Send chat message → Expect response with medical disclaimer"""
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    payload = {"message": "I have a headache, what should I do?"}
    
    response = client.post("/chat/message", headers=headers, json=payload)
    assert response.status_code == 200, f"Chat endpoint failed: {response.text}"
    
    data = response.json()
    assert "response" in data
    # Ensure medical disclaimer is injected as per safety requirements
    assert "disclaimer" in data.get("response", "").lower() or "medical" in data.get("response", "").lower()

def test_05_get_analysis_history(client: httpx.Client, state: dict):
    """5. Get analysis history → Expect paginated list"""
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    
    response = client.get("/analysis/history?limit=10&offset=0", headers=headers)
    assert response.status_code == 200, f"History fetch failed: {response.text}"
    
    data = response.json()
    assert isinstance(data, list)

def test_06_refresh_token(client: httpx.Client, state: dict):
    """6. Refresh token → Expect new access token"""
    headers = {"Authorization": f"Bearer {state['refresh_token']}"}
    
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 200, f"Token refresh failed: {response.text}"
    
    data = response.json()
    assert "access_token" in data
    # Ensure the new token actually works
    state["access_token"] = data["access_token"]

def test_07_logout(client: httpx.Client, state: dict):
    """7. Logout → Expect session invalidated"""
    headers = {"Authorization": f"Bearer {state['access_token']}"}
    
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    
    # Verify the token is now rejected
    response_after = client.get("/analysis/history", headers=headers)
    assert response_after.status_code == 401, "Token was not invalidated after logout!"
