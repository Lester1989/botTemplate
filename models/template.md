a basic model class could start with the template below. Just replace the XXXXXX and modify the functions and columns

```python

from __future__ import annotations
import random
from models.base import Base,engine
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Table, func)
from sqlalchemy.orm import Session
from datetime import datetime, timezone

class XXXXXX(Base):
    __tablename__ = 'XXXXXXs'.lower()
    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=False)

    def __repr__(self):
        return f"XXXXXX {self.id}: guild_id={self.guild_id}"


    @staticmethod
    def get_all( guild_id:int) -> list[XXXXXX]:
        with Session(engine) as session:
            return session.query(XXXXXX).filter(XXXXXX.guild_id == guild_id).all()

    @staticmethod
    def get( guild_id:int, id:int) -> XXXXXX:
        with Session(engine) as session:
            return session.query(XXXXXX).filter(XXXXXX.guild_id == guild_id, XXXXXX.id == id).first()  # type: ignore

    @staticmethod
    def create( guild_id:int, **kwargs) -> XXXXXX:
        with Session(engine) as session:
            data = XXXXXX(guild_id=guild_id, **kwargs)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    @staticmethod
    def update( guild_id:int, id:int, **kwargs) -> None:
        with Session(engine) as session:
            session.query(XXXXXX).filter(XXXXXX.guild_id == guild_id, XXXXXX.id == id).update(kwargs)  # type: ignore
            session.commit()

    @staticmethod
    def delete( guild_id:int, id:int) -> None:
        with Session(engine) as session:
            session.query(XXXXXX).filter(XXXXXX.guild_id == guild_id, XXXXXX.id == id).delete()
            session.commit()

    @staticmethod
    def delete_all( guild_id:int) -> None:
        with Session(engine) as session:
            session.query(XXXXXX).filter(XXXXXX.guild_id == guild_id).delete()
            session.commit()


```