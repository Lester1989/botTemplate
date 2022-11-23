
from models.base import Base,engine

from models.example import ExampleData
from models.polls import Poll,PollQuestion,PollAnswer,PollParticipant

# Base.metadata.drop_all(engine,checkfirst=True)
Base.metadata.create_all(engine,checkfirst=True)