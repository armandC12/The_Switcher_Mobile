import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database
from database.db import init_db, SessionLocal, engine as main_engine, get_db
from tests.populate_test_db import populate_database
from settings import DATABASE_FILENAME

# Test database URL
TEST_DATABASE_URL = f"sqlite:///./{DATABASE_FILENAME}"


@pytest.fixture(scope="session")
def engine():
    # Create a new engine for testing
    test_engine = create_engine(TEST_DATABASE_URL, echo=False)
    
    # Create the database if it doesn't exist
    if not database_exists(test_engine.url):
        create_database(test_engine.url)
    
    # Initialize the database
    init_db()
    
    yield test_engine
    
    # Drop the database after all tests
    drop_database(test_engine.url)


@pytest.fixture(scope="module")
def session(engine):
    # Create a new connection
    connection = engine.connect()
    
    # Begin a non-ORM transaction
    transaction = connection.begin()
    
    # Create a new session factory bound to the connection
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    
    # Create a new session
    session = TestingSessionLocal()
    
    # Populate the database with initial test data
    populate_database()
    
    yield session
    
    # Rollback the transaction
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="module")
def override_get_db(session):
    def _override_get_db():
        try:
            yield session
        finally:
            pass
    return _override_get_db
