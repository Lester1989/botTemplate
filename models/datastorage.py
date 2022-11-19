
from models.base import Base,engine

from models.example import ExampleData

# Base.metadata.drop_all(engine,checkfirst=True)
Base.metadata.create_all(engine,checkfirst=True)