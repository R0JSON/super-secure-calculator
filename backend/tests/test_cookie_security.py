from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.api.deps import get_db
import uuid

client = TestClient(app)

def test_login_sets_secure_cookie():
    # Patch crud.authenticate inside the route module
    with patch("app.api.routes.login.crud.authenticate") as mock_auth:
        # Setup mock user
        user_id = uuid.uuid4()
        mock_user = MagicMock()
        mock_user.id = user_id
        mock_user.is_active = True
        mock_user.email = "test@example.com"
        mock_auth.return_value = mock_user
        
        # Override DB dependency
        app.dependency_overrides[get_db] = lambda: MagicMock()
        
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "password"}
        )
        
        assert response.status_code == 200
        
        # Check Set-Cookie header
        set_cookie = response.headers.get("set-cookie")
        assert set_cookie is not None
        assert "access_token=" in set_cookie
        assert "HttpOnly" in set_cookie
        assert "Secure" in set_cookie
        # Case might vary, checking for lowercase which is common
        assert "SameSite=strict" in set_cookie
        
        # Clean up
        app.dependency_overrides = {}

def test_access_resource_with_cookie():
    # Test that we can access a protected resource using the cookie
    
    user_id = uuid.uuid4()

    # We mock jwt.decode to return a valid payload
    with patch("app.api.deps.jwt.decode") as mock_jwt_decode:
             
        mock_jwt_decode.return_value = {"sub": str(user_id)}
        
        # Use a simple class to avoid MagicMock issues with Pydantic validation
        class MockUser:
            id = user_id
            email = "test@example.com"
            full_name = "Test User"
            is_active = True
            is_superuser = False
        
        mock_user = MockUser()
        
        # Create a mock session
        mock_session = MagicMock()
        # When session.get is called, return our mock_user
        mock_session.get.return_value = mock_user
        
        # Override DB dependency to return our configured mock_session
        app.dependency_overrides[get_db] = lambda: mock_session

        # Set cookie in client
        client.cookies.set("access_token", "Bearer mocktoken")
        
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        assert response.json()["id"] == str(user_id)
        
        # Clean up
        app.dependency_overrides = {}
        client.cookies.clear()
