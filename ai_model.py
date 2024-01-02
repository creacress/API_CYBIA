import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch.nn.functional as F
from fastapi import HTTPException

class AIModel:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("camembert-base")
        self.model = AutoModelForSequenceClassification.from_pretrained("/home/creacress/Documents/Python_Project/CYBIA/API_CYBIA/data/cybia_V_0", local_files_only=True)
        self.device = "mps" if torch.backends.mps.is_available() else "cpu"
        self.model.to(self.device)

    def predict_toxicity(self, text):
        if not text.strip():
            raise HTTPException(status_code=400, detail="Le texte d'entrée ne peut pas être vide ou ne contenir que des espaces.")

        max_length = 512
        if len(text) > max_length:
            raise HTTPException(status_code=400, detail=f"La longueur du texte dépasse la limite de {max_length} caractères.")

        inputs = self.tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
            is_toxic_probabilities = probabilities[0].tolist()

        return {
            "text": text,
            "is_toxic_probabilities": is_toxic_probabilities[1],
            "is_not_toxic_probabilities": is_toxic_probabilities[0]
        }

