from sqlmodel import Session, create_engine


DATABASE_URL = f"sqlite:///database.db"
engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as db:
        yield db