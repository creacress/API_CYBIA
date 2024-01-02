# Importations nécessaires
from ai_model import AIModel
from flask import Flask, request
from models import Feedback, BaseFeedback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, exc
import json

class MyAPI:
    def __init__(self):
        # Création d'une instance de AIModel
        self.ai_model = AIModel()

    def detect_toxicity(self, text):
        try:
            # Utiliser AIModel pour obtenir la prédiction
            prediction = self.ai_model.predict_toxicity(text)
            # Formatage de la réponse
            return f"Toxicité: {prediction['is_toxic_probabilities']:.2f}, Non-toxicité: {prediction['is_not_toxic_probabilities']:.2f}"
        except Exception as e:
            # Gérer les exceptions (par exemple, texte vide ou trop long)
            return str(e)

app = Flask(__name__)

# Connect to the database
engine = create_engine('sqlite:///./feedback.db')
BaseFeedback.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        # S'assurer que 'data' est un dictionnaire
        if not isinstance(data, dict):
            raise ValueError("Invalid data format")
        
        # Assurer la présence de toutes les clés nécessaires
        required_fields = ['text', 'toxicity_score', 'feedback']
        if not all(field in data for field in required_fields):
            raise ValueError("Missing data fields")

        feedback_info = data['feedback']
        # Validation des données supplémentaires
        if not isinstance(feedback_info, dict):
            raise ValueError("Invalid feedback format")

        new_feedback = Feedback(
            text=data['text'],
            toxicity_score=float(data['toxicity_score']),
            user_feedback=json.dumps(feedback_info)  # Stocker les informations de feedback sous forme de JSON
        )

        with DBSession() as session:
            session.add(new_feedback)
            session.commit()
            return "Feedback submitted successfully"
    except exc.SQLAlchemyError as e:
        # Gérer les exceptions spécifiques à SQLAlchemy
        print(f"Database Error: {str(e)}")
        return f"Database error occurred: {str(e)}", 500
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"An error occurred: {str(e)}", 400

if __name__ == '__main__':
    app.run()