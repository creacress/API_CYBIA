import tkinter as tk
from tkinter import ttk, messagebox
from api import MyAPI
import requests
import re 
import threading

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.last_api_response = None
        # Configuration de la fenêtre principale
        self.title("Détecteur de Toxicité")
        self.geometry("600x500")  # Taille de la fenêtre

        # Style
        self.style = ttk.Style(self)
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TRadiobutton", font=("Helvetica", 10))

        # Créer une instance de l'API.
        self.api = MyAPI()

    
        # Charger la session
        self.load_session_button = ttk.Button(self, text="Charger la Session", command=self.load_session)
        self.load_session_button.pack(pady=5)
        # Zone de texte pour le texte à analyser.
        self.text_field_label = ttk.Label(self, text="Texte à analyser:")
        self.text_field_label.pack(pady=5)
        self.text_field = ttk.Entry(self, font=("Helvetica", 12), width=50)
        self.text_field.pack(pady=10)

        # Bouton pour envoyer la requête à l'API.
        self.submit_button = ttk.Button(self, text="Analyser", command=self.async_send_request)
        self.submit_button.pack(pady=10)

        # Zone de texte pour afficher la réponse de l'API.
        self.response_field = ttk.Label(self, text="", font=("Helvetica", 12), wraplength=500)
        self.response_field.pack(pady=20)

        # Options de feedback
        self.feedback_label = ttk.Label(self, text="La prédiction est-elle correcte ?")
        self.feedback_label.pack(pady=5)
        self.feedback_var = tk.StringVar(value="None")
        self.yes_button = ttk.Radiobutton(self, text="Oui", variable=self.feedback_var, value="Correct")
        self.yes_button.pack()
        self.no_button = ttk.Radiobutton(self, text="Non", variable=self.feedback_var, value="Incorrect")
        self.no_button.pack()

        # Options de feedback supplémentaires
        self.type_label = ttk.Label(self, text="Type de Toxicité :")
        self.type_label.pack(pady=5)
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(self, textvariable=self.type_var, 
                                  values=["Insulte", "Harcèlement", "Discours Haineux","Terrorisme", "Autre"])
        self.type_combobox.pack(pady=5)

        self.confidence_label = ttk.Label(self, text="Confiance dans le Feedback :")
        self.confidence_label.pack(pady=5)
        self.confidence_var = tk.StringVar()
        self.confidence_combobox = ttk.Combobox(self, textvariable=self.confidence_var, 
                                        values=["Pas sûr", "Modérément sûr", "Très sûr"])
        self.confidence_combobox.pack(pady=5)

        self.comment_label = ttk.Label(self, text="Commentaires supplémentaires :")
        self.comment_label.pack(pady=5)
        self.comment_field = ttk.Entry(self, font=("Helvetica", 12), width=50)
        self.comment_field.pack(pady=10)

        # Bouton pour enregistrer le feedback
        self.save_feedback_button = ttk.Button(self, text="Enregistrer le Feedback", command=self.save_feedback)
        self.save_feedback_button.pack(pady=20)

        # Ajout d'un historique de requêtes
        self.history = []
        self.history_label = ttk.Label(self, text="Historique des requêtes", font=("Helvetica", 12))
        self.history_label.pack()
        self.history_listbox = tk.Listbox(self, height=6, width=50)
        self.history_listbox.pack()

        # Bouton pour enregistrer et charger la session
        self.save_session_button = ttk.Button(self, text="Enregistrer la Session", command=self.save_session)
        self.save_session_button.pack(pady=5)

    
    # Fonction pour mettre à jour l'historique
    def update_history(self, text, response):
        entry = f"Texte: {text[:30]}... - Réponse: {response}"
        self.history.append(entry)
        self.history_listbox.insert(tk.END, entry)
        
    
    def async_send_request(self):
        threading.Thread(target=self.send_request).start()

    def send_request(self):
        text = self.text_field.get()
        if not text.strip():  # Vérifie si le texte est vide ou ne contient que des espaces
            messagebox.showwarning("Attention", "Veuillez entrer du texte à analyser.")
            return

        # Préparation de la requête
        url = "http://127.0.0.1:8000/detect/"  # Remplacez par l'URL de votre endpoint
        data = {'text': text}

        # Envoi de la requête à l'API
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # Cela déclenchera une exception pour les réponses non réussies

            # Traitement de la réponse
            if response.status_code == 200:
                self.last_api_response = response.json()
                # Formatage et affichage de la réponse
                response_text = f"Réponse de l'API: Toxicité: {self.last_api_response['is_toxic_probabilities']:.2f}, Non-toxicité: {self.last_api_response['is_not_toxic_probabilities']:.2f}"
                self.response_field.config(text=response_text)
                # Mise à jour de l'historique
                self.update_history(text, response_text)
            else:
                self.response_field.config(text="Erreur lors de la récupération de la réponse de l'API.")
        except requests.exceptions.RequestException as e:
            self.response_field.config(text=f"Erreur lors de l'envoi de la requête: {e}")


    def send_feedback(self, feedback_data):
        # Préparer l'URL pour l'envoi du feedback
        url = "http://127.0.0.1:8000/feedback/"
        
        # Envoyer les données de feedback à l'API
        try:
            response = requests.post(url, json=feedback_data)
            response.raise_for_status()  # Vérifier les erreurs de réponse
            self.response_field.config(text=f"Réponse enregistrée : {response.text}")
        except Exception as e:
            self.response_field.config(text=f"Erreur lors de l'envoi du feedback: {e}")


    def save_feedback(self):
        # Récupérer le texte et le feedback
        text = self.text_field.get()
        feedback_correctness = self.feedback_var.get()
        feedback_type = self.type_var.get()
        feedback_confidence = self.confidence_var.get()
        feedback_comments = self.comment_field.get()

        # Utiliser la probabilité de toxicité de la dernière réponse de l'API comme score de toxicité
        if self.last_api_response and 'is_toxic_probabilities' in self.last_api_response:
            toxicity_score = self.last_api_response['is_toxic_probabilities']
        else:
            # Gestion d'erreur ou valeur par défaut si le score n'est pas trouvé
            messagebox.showerror("Erreur", "Aucune donnée de toxicité valide trouvée pour le feedback.")
            return

        feedback_data = {
            "text": text,
            "toxicity_score": toxicity_score,
            "user_feedback": {
                "correctness": feedback_correctness,
                "type": feedback_type,
                "confidence": feedback_confidence,
                "comments": feedback_comments
            }
        }
        self.send_feedback(feedback_data)

        # Afficher un message de confirmation
        messagebox.showinfo("Feedback", "Feedback enregistré avec succès.")

        # Réinitialiser les champs
        self.text_field.delete(0, tk.END)
        self.feedback_var.set("None")
        self.type_combobox.set('')
        self.confidence_combobox.set('')
        self.comment_field.delete(0, tk.END)
    
        # Mise à jour de l'historique avec la dernière réponse et le feedback
        if self.last_api_response is not None:
            history_entry = f"{text[:30]}... - Score de toxicité: {toxicity_score}, Feedback: {feedback_correctness}"
            self.update_history(text, history_entry)
            print(f"Texte: {text}, Score de Toxicité: {toxicity_score}, Feedback: {feedback_correctness}")
    
    def save_session(self):
        with open("session.txt", "w") as file:
            for entry in self.history:
                file.write(entry + "\n")
        messagebox.showinfo("Session", "Session enregistrée avec succès.")


    def load_session(self):
        try:
            with open("session.txt", "r") as file:
                self.history_listbox.delete(0, tk.END)  # Nettoyage de la liste avant le chargement
                for line in file:
                    self.history_listbox.insert(tk.END, line.strip())
                    self.history.append(line.strip())  # Mise à jour de l'historique en mémoire
        except FileNotFoundError:
            messagebox.showwarning("Session", "Aucune session précédente trouvée.")
 
if __name__ == "__main__":
    app = App()
    app.mainloop()
