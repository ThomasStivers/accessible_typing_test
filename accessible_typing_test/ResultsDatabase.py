"""Database including typing test results and sentences for typing."""

from contextlib import contextmanager
import logging
import os
from sqlalchemy import create_engine, func
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///data/test_results.dat", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Sentences(Base):
	"""Represents the sentences database table as a class."""

	__tablename__ = "sentences"

	id = Column(Integer, primary_key=True)
	sentence = Column(String)

	def __repr__(self):
		return f"{self.__class__.__name__}(sentence={repr(self.sentence)})"

	def randomSentence():
		"""Get a random sentence from the database.
		
		Returns:
			Sentences: A Sentences object representing 1 randomly chosen sentence.
		"""
		return Session().query(Sentences).order_by(func.random()).first()

class Results(Base):
	"""Represents the results database table."""

	__tablename__ = "results"

	id = Column(Integer, primary_key=True)
	user_name = Column(String)
	start_time = Column(DateTime)
	end_time = Column(DateTime)
	duration = Column(Integer)
	accuracy = Column(Integer)
	edit_distance = Column(Integer)
	speed = Column(Integer)
	words = Column(Integer)
	timestamp = Column(String)
	given_text = Column(String)
	typed_text = Column(String)

	def __repr__(self):
		super().__repr__(self)

@contextmanager
def session_scope():
	"""Provide a transactional scope around a series of operations."""
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()

def fillSentences():
	"""Populate the sentences table.
	
	Fill the sentences table of the database with stock sentences if it is empty.
	"""
	sentence_filename = os.path.join(os.path.dirname(__file__), "data", "sentences.txt")
	with session_scope() as session:
		if session.query(Sentences).count() == 0:
			with open(sentence_filename) as sentence_file:
				for s in sentence_file.readlines():
					session.add(Sentences(sentence=s.strip()))

if __name__ == "__main__":
	Base.metadata.create_all(engine)
	fillSentences()
	