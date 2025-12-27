"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, get_db
from api.main import app

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create test database."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database_connected" in data
        assert "timestamp" in data
    
    def test_data_endpoint_empty(self, client):
        """Test data endpoint with empty database."""
        response = client.get("/api/v1/data")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "request_id" in data
        assert "api_latency_ms" in data
        assert data["total"] == 0
        assert len(data["data"]) == 0
    
    def test_data_endpoint_pagination(self, client):
        """Test pagination parameters."""
        response = client.get("/api/v1/data?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10
    
    def test_data_endpoint_filtering(self, client):
        """Test filtering by source."""
        response = client.get("/api/v1/data?source=coinpaprika")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_data_endpoint_coin_filter(self, client):
        """Test filtering by coin_id."""
        response = client.get("/api/v1/data?coin_id=btc-bitcoin")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint."""
        response = client.get("/api/v1/stats")
        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "total_records" in data
        assert "request_id" in data
        assert "api_latency_ms" in data
    
    def test_invalid_page_number(self, client):
        """Test invalid page number."""
        response = client.get("/api/v1/data?page=0")
        assert response.status_code == 422  # Validation error
    
    def test_page_size_limits(self, client):
        """Test page size limits."""
        response = client.get("/api/v1/data?page_size=2000")
        assert response.status_code == 422  # Exceeds max page size
    
    def test_api_latency_tracking(self, client):
        """Test that API latency is tracked."""
        response = client.get("/api/v1/data")
        assert response.status_code == 200
        data = response.json()
        assert "api_latency_ms" in data
        assert isinstance(data["api_latency_ms"], (int, float))
        assert data["api_latency_ms"] >= 0
    
    def test_request_id_uniqueness(self, client):
        """Test that request IDs are unique."""
        response1 = client.get("/api/v1/data")
        response2 = client.get("/api/v1/data")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["request_id"] != data2["request_id"]
