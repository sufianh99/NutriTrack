import pytest


@pytest.fixture
def app():
    from app import create_app, db as _db
    from config import TestConfig

    application = create_app(TestConfig)
    with application.app_context():
        _db.create_all()
        yield application
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
