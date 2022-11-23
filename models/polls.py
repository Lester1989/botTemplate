from __future__ import annotations
import random
from models.base import Base,engine
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Table, func)
from sqlalchemy.orm import Session
from datetime import datetime, timezone

class Poll(Base):
    __tablename__ = 'polls'
    guild_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, primary_key=True)
    name = Column(String(255), primary_key=True)
    description = Column(String(255), nullable=False)
    anonymous = Column(Boolean, nullable=False)
    closed = Column(Boolean, default=False)

    def __repr__(self):
        return f"Poll(guild_id={self.guild_id},creator_id={self.creator_id},name={self.name},description={self.description},anonymous={self.anonymous})"

    @staticmethod
    def get_all( guild_id:int) -> list[Poll]:
        with Session(engine) as session:
            return session.query(Poll).filter(Poll.guild_id == guild_id).all()

    @staticmethod
    def get_for_creator( guild_id:int, creator_id:int, ) -> list[Poll]:
        with Session(engine) as session:
            return session.query(Poll).filter(Poll.guild_id == guild_id, Poll.creator_id == creator_id).all()

    @staticmethod
    def get( guild_id:int, creator_id:int,name:str) -> Poll:
        with Session(engine) as session:
            return session.query(Poll).filter(Poll.guild_id == guild_id, Poll.creator_id == creator_id, Poll.name == name).first() # type: ignore

    @staticmethod
    def create( guild_id:int, **kwargs) -> Poll:
        '''
        ## kwargs:
        * creator_id : int
        * name : str
        * description : str
        * anonymous : bool'''
        with Session(engine) as session:
            data = Poll(guild_id=guild_id, **kwargs)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    @staticmethod
    def update( guild_id:int, creator_id:int,name:str, **kwargs) -> None:
        '''
        ## kwargs:
        * description : str
        * anonymous : bool
        * closed : bool'''

        with Session(engine) as session:
            session.query(Poll).filter(Poll.guild_id == guild_id, Poll.creator_id == creator_id, Poll.name == name).update(kwargs) # type: ignore
            session.commit()

    @staticmethod
    def delete( guild_id:int, creator_id:int,name:str) -> None:
        with Session(engine) as session:
            session.query(Poll).filter(Poll.guild_id == guild_id, Poll.creator_id == creator_id, Poll.name == name).delete() # type: ignore
            session.commit()

    @staticmethod
    def delete_all( guild_id:int) -> None:
        with Session(engine) as session:
            session.query(Poll).filter(Poll.guild_id == guild_id).delete()
            session.commit()


class PollParticipant(Base):
    __tablename__ = 'poll_participants'
    guild_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, primary_key=True)
    name = Column(String(255), primary_key=True)
    user_id = Column(Integer, primary_key=True)

    def __repr__(self):
        return f"PollParticipants(guild_id={self.guild_id},creator_id={self.creator_id},name={self.name},user_id={self.user_id})"

    @staticmethod
    def get_all_for_poll( guild_id:int,creator_id:int,name:str) -> list[PollParticipant]:
        with Session(engine) as session:
            return session.query(PollParticipant).filter(PollParticipant.guild_id == guild_id, PollParticipant.creator_id == creator_id, PollParticipant.name == name).all()

    @staticmethod
    def create( guild_id:int,creator_id:int,name:str, user_id:int) -> PollParticipant:
        with Session(engine) as session:
            data = PollParticipant(guild_id=guild_id,creator_id=creator_id,name=name,user_id=user_id)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data
        

class PollQuestion(Base):
    __tablename__ = 'pollquestions'
    guild_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, primary_key=True)
    name = Column(String(255), primary_key=True)
    question_nr = Column(Integer, primary_key=True)
    question_text = Column(String(255), nullable=False)
    is_yes_no = Column(Boolean, nullable=False)
    options = Column(String(255), nullable=False)

    OPTION_SEPERATOR:str = '#@#'

    def __repr__(self):
        return f"PollQuestion(guild_id={self.guild_id},creator_id={self.creator_id},name={self.name},question_nr={self.question_nr},question={self.question_text},is_yes_no={self.is_yes_no},options={self.options})"

    @property
    def options_dict(self) -> dict[str,str]:
        '''
        Returns a dict with the options 
        option_name : option_text
        '''
        if self.is_yes_no:
            return {'yes':'Yes','no':'No'}
        return {f'op-{k}':v for k,v in enumerate(str(self.options).split(self.OPTION_SEPERATOR))}

    @staticmethod
    def get_next_question_nr( guild_id:int, creator_id:int,name:str,question_nr:int) -> int:
        with Session(engine) as session:
            if next_question := session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id, PollQuestion.creator_id == creator_id, PollQuestion.name == name, PollQuestion.question_nr > question_nr).order_by(PollQuestion.question_nr).first():
                return int(next_question.question_nr)
        return -1

    @staticmethod
    def build_options_dict( options:list[str]) -> str:
        return PollQuestion.OPTION_SEPERATOR.join(options)

    @staticmethod
    def get_all_for_poll( guild_id:int,creator_id:int,name:str) -> list[PollQuestion]:
        with Session(engine) as session:
            return session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id,PollQuestion.creator_id == creator_id,PollQuestion.name == name).order_by(PollQuestion.question_nr).all()

    @staticmethod
    def get( guild_id:int, creator_id:int,name:str,question_nr:int) -> PollQuestion:
        with Session(engine) as session:
            return session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id,PollQuestion.creator_id == creator_id,PollQuestion.name == name,PollQuestion.question_nr == question_nr).first() # type: ignore

    @staticmethod
    def create( guild_id:int, **kwargs) -> PollQuestion:
        """# Create a new poll question
        ## kwargs:
            * creator_id
            * name
            * question_nr
            * question_text
            * is_yes_no
            * options"""
        
        with Session(engine) as session:
            data = PollQuestion(guild_id=guild_id, **kwargs)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    @staticmethod
    def update( guild_id:int, creator_id:int,name:str,question_nr:int, **kwargs) -> None:
        '''
        kwargs:
            question_text
            is_yes_no
            options
        '''
        with Session(engine) as session:
            session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id,PollQuestion.creator_id == creator_id,PollQuestion.name == name,PollQuestion.question_nr == question_nr).update(kwargs) # type: ignore
            session.commit()

    @staticmethod
    def delete( guild_id:int, creator_id:int,name:str,question_nr:int) -> None:
        with Session(engine) as session:
            session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id,PollQuestion.creator_id == creator_id,PollQuestion.name == name,PollQuestion.question_nr == question_nr).delete()
            session.commit()

    @staticmethod
    def delete_all( guild_id:int,creator_id:int,name:str,) -> None:
        with Session(engine) as session:
            session.query(PollQuestion).filter(PollQuestion.guild_id == guild_id,PollQuestion.creator_id == creator_id,PollQuestion.name == name).delete()
            session.commit()

class PollAnswer(Base):
    __tablename__ = 'pollanswers'
    guild_id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, primary_key=True)
    name = Column(String(255), primary_key=True)
    question_nr = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    answer = Column(String(255), nullable=False)

    def __repr__(self):
        return f"PollAnswer(guild_id={self.guild_id},creator_id={self.creator_id},name={self.name},question_nr={self.question_nr},user_id={self.user_id},answer={self.answer})"

    @staticmethod
    def get_all_for_poll( guild_id:int,creator_id:int,name:str) -> list[PollAnswer]:
        with Session(engine) as session:
            return session.query(PollAnswer).filter(PollAnswer.guild_id == guild_id,PollAnswer.creator_id == creator_id,PollAnswer.name == name).order_by(PollAnswer.question_nr).all()

    @staticmethod
    def get_all_for_question( guild_id:int, creator_id:int,name:str,question_nr:int) -> list[PollAnswer]:
        with Session(engine) as session:
            return session.query(PollAnswer).filter(PollAnswer.guild_id == guild_id,PollAnswer.creator_id == creator_id,PollAnswer.name == name,PollAnswer.question_nr == question_nr).all()

    @staticmethod
    def create(guild_id:int,creator_id:int,name:str,question_nr:int,user_id:int,answer:str) -> PollAnswer:
        with Session(engine) as session:
            data = PollAnswer(guild_id=guild_id,creator_id=creator_id,name=name,question_nr=question_nr,user_id=user_id,answer=answer)
            session.add(data)
            session.commit()
            session.refresh(data)
            return data

    @staticmethod
    def delete( guild_id:int,creator_id:int,name:str,question_nr:int) -> None:
        with Session(engine) as session:
            session.query(PollAnswer).filter(PollAnswer.guild_id == guild_id,PollAnswer.creator_id == creator_id,PollAnswer.name == name,PollAnswer.question_nr == question_nr).delete()
            session.commit()

    @staticmethod
    def delete_all_for_poll( guild_id:int,creator_id:int,name:str,) -> None:
        with Session(engine) as session:
            session.query(PollAnswer).filter(PollAnswer.guild_id == guild_id,PollAnswer.creator_id == creator_id,PollAnswer.name == name).delete()
            session.commit()

    @staticmethod
    def delete_all_of_user_for_poll( guild_id:int,creator_id:int,name:str,user_id:int) -> None:
        with Session(engine) as session:
            session.query(PollAnswer).filter(PollAnswer.guild_id == guild_id,PollAnswer.creator_id == creator_id,PollAnswer.name == name,PollAnswer.user_id == user_id).delete()
            session.commit()