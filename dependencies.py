from contextlib import contextmanager
from models import SessionLocalUser, SessionLocalFeedback
from ai_model import AIModel

@contextmanager

def DBSessionUser():
    db = SessionLocalUser()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def DBSessionFeedback():
    db = SessionLocalFeedback()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_ai_model():
    model = AIModel()
    try:
        yield model
    finally:

        pass