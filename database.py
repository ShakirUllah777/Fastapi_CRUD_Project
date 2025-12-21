from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

db_url = 'postgresql://postgres:turkish777@localhost:5432/turkish'
engine = create_engine(db_url)
session = sessionmaker(autocommit= False , autoflush=False , bind= engine)






