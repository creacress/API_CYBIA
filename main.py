import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from schemas import Item, UserCreate, User
from dependencies import get_ai_model, DBSessionUser, DBSessionFeedback
from models import BaseUser, BaseFeedback, engine_user, engine_feedback, User as DBUser, Feedback
from sqlalchemy.orm import Session
import json

# Configuration de la logistique
logging.basicConfig(level=logging.INFO)

# Créez les tables dans les bases de données (une seule fois)
BaseUser.metadata.create_all(bind=engine_user)
BaseFeedback.metadata.create_all(bind=engine_feedback)

app = FastAPI(title="CYBIA API", description="API de détection de toxicité", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes
    allow_headers=["*"],  # Autorise tous les headers
)

# Schéma Pydantic pour le feedback enrichi
class FeedbackInput(BaseModel):
    text: str
    toxicity_score: float
    correctness: str
    toxicity_type: str = Field(default=None)
    user_confidence: str = Field(default=None)
    user_comments: str = Field(default=None)


@app.post("/users/", response_model=User)
def create_user(user_data: UserCreate, db: Session = Depends(DBSessionUser)):
    with db:
        db_user = DBUser.create_user(user_data.username, user_data.email, user_data.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

@app.get("/", response_class=HTMLResponse)
async def homepage():
    html_content = """
    <html>
        <head>
            <title>CYBIA - Détecteur de Toxicité</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: navy; }
                ul { list-style-type: none; padding: 0; }
                li { margin: 10px 0; }
                a { color: darkblue; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Bienvenue dans CYBIA</h1>
            <p>CYBIA est une API dédiée à la détection de la toxicité dans le texte.</p>
            <ul>
                <li><a href='/docs'>Documentation de l'API</a></li>
                <li><a href='/detect/'>Détecter la toxicité</a></li>
                <li><a href='/feedback/'>Soumettre un feedback</a></li>
                <li><a href='/users/'>Créer un utilisateur</a></li>
            </ul>
        </body>
    </html>
    """
    return html_content



@app.post("/detect/")
async def detect_toxicity(item: Item):
    with get_ai_model() as model:
        prediction = model.predict_toxicity(item.text)
    return prediction

@app.post("/feedback/")
async def receive_feedback(feedback_data: FeedbackInput, db: Session = Depends(DBSessionFeedback)):
    new_feedback = Feedback(
        text=feedback_data.text,
        toxicity_score=feedback_data.toxicity_score,
        user_feedback=json.dumps({
            "correctness": feedback_data.correctness,
            "type": feedback_data.toxicity_type,
            "confidence": feedback_data.user_confidence,
            "comments": feedback_data.user_comments
        })
    )

    with db:
        db.add(new_feedback)
        db.commit()
    return {"message": "Feedback received"}

if __name__ == '__main__':
    app.run()
