from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from settings import DATABASE_FILENAME

# Crear una engine sqlalchemy
engine = create_engine(f'sqlite:///./{DATABASE_FILENAME}', echo=False)


# habilito la constraint de foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    # importo modelos
    import board.models
    import game.models
    import gameState.models
    import player.models
    import figureCards.models
    import movementCards.models
    import partial_movement.models

    # se crean las tablas
    Base.metadata.create_all(engine)

    print("Base de datos inicializada")
    
def get_db(session=None):
    if session:
        try:
            yield session
        finally:
            pass
    else:
        db= SessionLocal()
        try:
            db.execute(text('PRAGMA foreign_keys = ON')) 
            yield db
        finally:
            db.close()
        

def check_foreign_keys():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA foreign_keys;")).scalar()
        print(f"Foreign keys status: {'ON' if result == 1 else 'OFF'}")