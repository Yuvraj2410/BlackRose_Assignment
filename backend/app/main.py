from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from uuid import uuid4
import time

app = FastAPI()

# Store users and tokens
users_db = {"user1": '123', 'user2':'321'} # Sample username-password pairs
tokens_db = {} # store active session tokens

class TokenResponse(BaseModel):
    access_token : str
    token_type : str

@app.post('/login', response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    # Validate user credentials 
    if username not in users_db or users_db[username] != password:
        raise HTTPException(status_code=401, detail = 'Invalid username or password')
    
    # Generate a session token
    token = str(uuid4())
    tokens_db[token] = {'username':username, 'expires_at':time.time()+3600} #1-hour expiry

    return {'access_token':token, 'token_type':'bearer'}

@app.get('/protected')
def protected_route(token: str):
    # Verify token 
    if token not in tokens_db or tokens_db[token]['expires_at'] < time.time():
        raise HTTPException(status_code=401, detail='Invalid or expired token')

    return {'message': f"Hello, {tokens_db[token]['username']}! This is a protected route."}