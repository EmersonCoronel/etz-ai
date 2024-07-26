from flask import Flask, request, jsonify, session
from flask_cors import CORS
from anthropic import Anthropic
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) 
CORS(app)

anthropic = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Get or initialize conversation history
    conversation = session.get('conversation', [])
    conversation.append({"role": "user", "content": user_message})

    try:
        # Prepare the full message list for the API call
        messages = conversation

        response = anthropic.messages.create(
          model="claude-3-haiku-20240307",
          max_tokens=300,
          messages=messages,
          system="You are EtzAI, a friendly and knowledgeable AI assistant. Respond in a warm and engaging manner."
        )

        ai_response = response.content[0].text
        conversation.append({"role": "assistant", "content": ai_response})

        # Store updated conversation in session
        session['conversation'] = conversation[-10:]  # Keep last 10 messages

        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    session['conversation'] = []
    return jsonify({'message': 'Conversation reset successfully'})

if __name__ == '__main__':
    app.run(debug=True)