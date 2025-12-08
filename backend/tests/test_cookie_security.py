from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.api.deps import get_db

client = TestClient(app)

def test_login_sets_secure_cookie():
    # Patch crud.authenticate inside the route module
    with patch("app.api.routes.login.crud.authenticate") as mock_auth:
        # Setup mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = True
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
        assert "SameSite=Strict" in set_cookie
        
        # Clean up
        app.dependency_overrides = {}

def test_access_resource_with_cookie():
    # Test that we can access a protected resource using the cookie
    
    # We mock jwt.decode to return a valid payload
    with patch("app.api.deps.jwt.decode") as mock_jwt_decode, \
         patch("app.api.deps.Session.get") as mock_user_get:
             
        mock_jwt_decode.return_value = {"sub": "1"}
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.is_superuser = False
        mock_user_get.return_value = mock_user
        
        # Override DB
        app.dependency_overrides[get_db] = lambda: MagicMock()

        # Set cookie in client
        # Note: TestClient cookies handling might need domain path matching or just simple setting
        client.cookies.set("access_token", "Bearer mocktoken")
        
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == 200
        assert response.json()["id"] == 1
        
        # Clean up
        app.dependency_overrides = {}
        client.cookies.clear()
