from pydantic import BaseModel

class Item(BaseModel):
    text: str

# Schema pour la création d'un utilisateur
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Schema pour la représentation d'un utilisateur
class User(BaseModel):
    id: int
    username: str
    email: str
