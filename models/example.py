from __future__ import annotations
import random
from models.base import Base,engine
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Table, func)
from sqlalchemy.orm import Session
from datetime import datetime, timezone

class ExampleData(Base):
    __tablename__ = 'example'
    id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, nullable=False)
    textvalue = Column(String(255), nullable=False)
    numbervalue = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def __repr__(self):
        return f"ExampleData(id={self.id},guild_id={self.guild_id},textvalue={self.textvalue},numbervalue={self.numbervalue},created_at={self.created_at},updated_at={self.updated_at})"


    @staticmethod
    def get_all( guild_id:int) -> list[ExampleData]:
        with Session(engine) as session:
            return session.query(ExampleData).filter(ExampleData.guild_id == guild_id).all()

    @staticmethod
    def get( guild_id:int, id:int) -> ExampleData:
        with Session(engine) as session:
            return session.query(ExampleData).filter(ExampleData.guild_id == guild_id, ExampleData.id == id).first()  # type: ignore

    @staticmethod
    def create( guild_id:int, textvalue:str, numbervalue:int) -> ExampleData:
        with Session(engine) as session:
            data = ExampleData(guild_id=guild_id, textvalue=textvalue, numbervalue=numbervalue)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    @staticmethod
    def update( guild_id:int, id:int, textvalue:str, numbervalue:int):
        with Session(engine) as session:
            session.query(ExampleData).filter(ExampleData.guild_id == guild_id, ExampleData.id == id).update({ExampleData.textvalue:textvalue,ExampleData.numbervalue:numbervalue})  # type: ignore
            session.commit()

    @staticmethod
    def delete( guild_id:int, id:int) -> None:
        with Session(engine) as session:
            session.query(ExampleData).filter(ExampleData.guild_id == guild_id, ExampleData.id == id).delete()
            session.commit()

    @staticmethod
    def delete_all( guild_id:int) -> None:
        with Session(engine) as session:
            session.query(ExampleData).filter(ExampleData.guild_id == guild_id).delete()
            session.commit()
