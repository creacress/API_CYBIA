import os

# Assurez-vous que le chemin d'accès est correct et n'inclut pas de guillemets supplémentaires
model_path = '/home/creacress/Documents/Python_Project/CYBIA/API_CYBIA/data/cybia_V_0'

if os.path.exists(model_path):
    print("Le chemin d'accès au modèle est correct.")
else:
    print("Le chemin d'accès au modèle est incorrect.")
