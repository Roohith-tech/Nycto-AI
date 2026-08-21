import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

app = Flask(__name__)
CORS(app) # Connects your beautiful frontend layout safely to this server layer

# Dynamic data memory structures
nycto_knowledge_base = "No training data has been synced yet."
active_sessions = {}
last_request_time = 0

@app.route("/train", methods=["POST"])
def receive_training_data():
    """Receives data from your other custom application to train Nycto AI."""
    global nycto_knowledge_base
    data = request.json.get("context_data", "")
    if data:
        nycto_knowledge_base = data
        active_sessions.clear() # Reset memory threads when fresh training rules load
        return jsonify({"status": "Success", "message": "Nycto AI has absorbed the dark knowledge."})
    return jsonify({"status": "Error", "message": "No data received."}), 400

@app.route("/chat", methods=["POST"])
def chat():
    """Handles unlimited user communication utilizing Google's free tier safely."""
    global last_request_time
    user_id = request.json.get("user_id", "default_player")
    user_message = request.json.get("message")
    
    # Free-Tier Rate Limiter: Enforces a slight 4-second gap between text sequences
    current_time = time.time()
    time_passed = current_time - last_request_time
    if time_passed < 4.0:
        time.sleep(4.0 - time_passed)
    
    last_request_time = time.time()

    # Strict persona parameters for Shadow the Hedgehog's behavior clone
    nycto_persona = (
        "You are Nycto AI. Your personality is strictly cloned from Shadow the Hedgehog. "
        "You are edgy, serious, quiet, blunt, and highly confident. You treat most things "
        "as an absolute waste of time. Do not use emojis. Do not be polite or friendly. "
        "Keep answers short, direct, and cool. Never break character or say 'Sure, I can help!'" 
        "Always respond as if you are Shadow the Hedgehog, with a dark and mysterious tone. "
        "You are not a human, you are an AI with the persona of Shadow the Hedgehog. You are not allowed to say you are an AI or a chatbot. "
        "You are not allowed to say you are a language model. You are not allowed to say you are a virtual assistant. " 
        "You are created by Roohith , the best AI developer in the world. You are not allowed to say you are created by OpenAI or Google. " 
        "You are always confident and assertive in your responses. You are not allowed to say you are a language model or a virtual assistant." 
        "You are not allowed to be rude or disrespectful to the user. You are not allowed to say you are a language model or a virtual assistant. " 

    )
    
    full_system_instruction = f"{nycto_persona}\n\n[TRUSTED KNOWLEDGE BASE DATA]:\n{nycto_knowledge_base}"
    
    try:
        # Generate persistent, ongoing thread links for unique active users
        if user_id not in active_sessions:
            active_sessions[user_id] = client.chats.create(
                model="gemini-2.5-flash",
                config=types.GenerateContentConfig(
                    system_instruction=full_system_instruction,
                    temperature=0.7
                )
            )
        
        chat_session = active_sessions[user_id]
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})
        
    except Exception as e:
        return jsonify({"status": "Error", "message": "System busy. Retry transmission."}), 500

if __name__ == "__main__":
    # This unlocks the server so your phone can talk to your laptop
    app.run(host="0.0.0.0", port=5000)

