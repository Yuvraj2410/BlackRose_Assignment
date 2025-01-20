from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from uuid import uuid4
import time
import random
import sqlite3
import threading
from datetime import datetime
import asyncio


app = FastAPI()

# Store users and tokens
users_db = {"user1": '123', 'user2':'321'} # Sample username-password pairs
tokens_db = {} # store active session tokens

# Initialize SQLite database
db_connection = sqlite3.connect('random_numbers.db', check_same_thread=False)
db_cursor = db_connection.cursor()

# Create table to store random numbers
db_cursor.execute("""
CREATE TABLE IF NOT EXISTS random_numbers (
                  timestamp TEXT PRIMARY KEY,
                  value INTEGER
                  )
""")
db_connection.commit()

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

# Function to generate and store random numbers
def generate_random_numbers():
    while True:
        # Generate a random number
        random_number = random.randint(1,100) # Random number between 1 and 100

        # Get the current timestamp
        timestamp = datetime.now().isoformat()

        # Store in the database
        try:
            db_cursor.execute('INSERT INTO random_numbers (timestamp, value) VALUES (?,?)', (timestamp, random_number))
            db_connection.commit()
            print(f'stored: {timestamp} -> {random_number}')
        except sqlite3.IntegrityError:
            print(f'Duplicate timestamp detected: {timestamp}')

        # Wait for 1 sec
        threading.Event().wait(1)

# Start random number generation in a background thread
threading.Thread(target=generate_random_numbers, daemon=True).start()

# WebSocket endpoint to stream random numbers
@app.websocket('/ws/random_numbers')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try: 
        while True:
            # Fetch the latest random number from the database
            conn = sqlite3.connect('random_numbers.db')
            cursor = conn.cursor()
            cursor.execute('SELECT timestamp, value FROM random_numbers WHERE timestamp = (SELECT MAX(timstamp) FROM random_numbers)')
            latest = cursor.fetchone()
            conn.close()

            if latest:
                timestamp, value = latest
                # Send the random number and timestamp to the client 
                await websocket.send_text(f'Timestamp: {timestamp}, Value: {value}')
            else:
                await websocket.send_text('No data available yet.')
            
            # Wait for 1 second before sending the next number
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print('Client disconnected.')