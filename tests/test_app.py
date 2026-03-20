import pytest
from app import app


def test_root():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert 'Welcome to TDD Service' in response.get_data(as_text=True)
