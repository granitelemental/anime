import os

from sqlalchemy.dialects import postgresql
from sqlalchemy import create_engine, Column, Integer, String, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BaseModel = declarative_base()

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'test')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'test')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'test')

engine = create_engine(f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/{POSTGRES_DB}", echo = True)

Session = sessionmaker(bind=engine)
session = Session()

engine.connect()

def bulk_upsert_or_insert(items, model, index_elements, update=False):
    if len(items) == 0:
        return None
    """
    items = list of dicts, 
    model - db model, 
    index_elements - list of fields to identify unique items in db, 
    update - whether update is needed in case of item existance """
    keys = items[0].keys()
    insert_stmt = postgresql.insert(model.__table__).values(items)
    update_stmt = insert_stmt.on_conflict_do_update(
    index_elements = index_elements,
    set_={key: getattr(insert_stmt.excluded, key) for key in keys}
    )
    do_nothing_stmt = insert_stmt.on_conflict_do_nothing(
    index_elements = index_elements
    )
    stmt = update_stmt if update else do_nothing_stmt
    engine.execute(stmt)
    return None

def upsert(item, model, index_elements):
    bulk_upsert_or_insert(items = [item], model=model, index_elements=index_elements, update=True)

class Title(BaseModel):
    __tablename__ = 'titles'

    id = Column(Integer, primary_key = True, autoincrement = True, nullable = False)
    name = Column(String, nullable=False)
    ru = Column(String)
    date = Column(Integer, nullable = False)
    data = Column(JSON)

    # __table_args__ = (
    #     UniqueConstraint("name", "date", name="name_date_uc"),
    # )

BaseModel.metadata.create_all(engine)