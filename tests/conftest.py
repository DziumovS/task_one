import pytest
import lib_app
from yoyo import read_migrations, get_backend
from settings.main import host, user, password, db


@pytest.fixture()
def app():
    app = lib_app.app
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(autouse=True)
def create_tables_data():
    backend = get_backend(f"postgres://{user}:{password}@{host}/{db}")
    migrations = read_migrations('./migrations')
    yield backend.apply_migrations(backend.to_apply(migrations))
    sorted_migrations = sorted(migrations, key=lambda x: x.id, reverse=True)
    backend.rollback_migrations(sorted_migrations)
