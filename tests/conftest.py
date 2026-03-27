import pytest
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    from app import create_app
    from app import db as _db
    from config import TestConfig

    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(app, client):
    """A test client with a logged-in user. Returns (client, user)."""
    from app import db as _db
    from app.models import User

    user = User(
        username="testuser",
        password_hash=generate_password_hash("testpass123"),
    )
    _db.session.add(user)
    _db.session.commit()

    with client.session_transaction() as sess:
        sess["_user_id"] = str(user.id)

    return client, user
