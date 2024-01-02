from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import datetime
import json

# Configuration de la base de données pour les utilisateurs
DATABASE_USER_URL = "sqlite:///./users.db"
engine_user = create_engine(DATABASE_USER_URL)
SessionLocalUser = sessionmaker(autocommit=False, autoflush=False, bind=engine_user)
BaseUser = declarative_base()

# Configuration de la base de données pour les feedbacks
DATABASE_FEEDBACK_URL = "sqlite:///./feedback.db"
engine_feedback = create_engine(DATABASE_FEEDBACK_URL)
SessionLocalFeedback = sessionmaker(autocommit=False, autoflush=False, bind=engine_feedback)
BaseFeedback = declarative_base()

# Classe User
class User(BaseUser):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    @staticmethod
    def create_user(username: str, email: str, password: str, pwd_context: CryptContext):
        hashed_password = pwd_context.hash(password)
        return User(username=username, email=email, hashed_password=hashed_password)

class Feedback(BaseFeedback):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    toxicity_score = Column(Float)  # Modification de String à Float pour stocker des valeurs numériques
    user_feedback = Column(String)  # Cette colonne peut maintenant contenir un JSON simple
    additional_info = Column(Text)  # Nouveau champ pour stocker des informations de feedback enrichies sous forme de JSON
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    def set_additional_info(self, info_dict):
        self.additional_info = json.dumps(info_dict)

    def get_additional_info(self):
        return

# Contexte pour le hashage de mot de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Création des tables dans la base de données
BaseUser.metadata.create_all(bind=engine_user)
BaseFeedback.metadata.create_all(bind=engine_feedback)
