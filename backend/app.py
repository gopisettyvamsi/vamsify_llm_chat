from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import json
import html
from pathlib import Path
from llm_handler import LLMHandler
from conversation import ConversationManager
from config import HOST, PORT

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)

# Initialize LLM and conversation manager
print("Initializing LLM Chat Application...")
llm = LLMHandler()
conversation = ConversationManager()
print("✓ Application ready!")

# Serve frontend
@app.route('/')
def index():
    """Serve the main chat interface."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files (CSS, JS)."""
    return send_from_directory(app.static_folder, path)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": llm.is_loaded()
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages (non-streaming)."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data['message'].strip()
        conversation_id = data.get('conversation_id')
        
        if conversation_id:
            conversation.set_conversation(conversation_id)
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400
            
        if len(user_message) > 4000:
            return jsonify({"error": "Message too long"}), 400
        
        user_message = html.escape(user_message)
        prompt = conversation.get_prompt(user_message)
        response = llm.generate(prompt, stream=False)
        
        conversation.add_message('user', user_message)
        conversation.add_message('assistant', response)
        
        return jsonify({
            "response": response,
            "conversation_id": conversation.current_conversation_id,
            "history": conversation.get_history()
        })
    except Exception as e:
        print(f"Error in /chat: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/stream', methods=['POST'])
def stream():
    """Stream response with Server-Sent Events."""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400
        
        user_message = data['message'].strip()
        conversation_id = data.get('conversation_id')
        
        if conversation_id:
            conversation.set_conversation(conversation_id)
            
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        if len(user_message) > 4000:
            return jsonify({"error": "Message too long"}), 400
            
        user_message = html.escape(user_message)
        prompt = conversation.get_prompt(user_message)
        
        def generate_stream():
            full_response = ""
            try:
                for token in llm.generate(prompt, stream=True):
                    full_response += token
                    yield f"data: {json.dumps({'token': token})}\n\n"
                
                # Save to database after completion
                conversation.add_message('user', user_message)
                conversation.add_message('assistant', full_response)
                
                yield f"data: {json.dumps({
                    'done': True, 
                    'conversation_id': conversation.current_conversation_id
                })}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(generate_stream(), mimetype='text/event-stream')
    except Exception as e:
        print(f"Error in /stream: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/conversations', methods=['GET'])
def list_conversations():
    """Get list of conversations."""
    return jsonify(conversation.get_conversations())

@app.route('/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation."""
    cid = conversation.create_conversation()
    return jsonify({"id": cid})

@app.route('/conversations/<cid>', methods=['GET'])
def get_conversation(cid):
    """Get specific conversation history."""
    if conversation.set_conversation(cid):
        return jsonify({
            "id": cid,
            "history": conversation.get_history()
        })
    return jsonify({"error": "Conversation not found"}), 404

@app.route('/conversations/<cid>', methods=['DELETE'])
def delete_conversation(cid):
    """Delete a conversation."""
    conversation.delete_conversation(cid)
    return jsonify({"status": "deleted"})

@app.route('/clear', methods=['POST'])
def clear_history():
    """Clear current conversation history."""
    conversation.clear_history()
    return jsonify({"status": "cleared"})


if __name__ == '__main__':
    print(f"\n{'='*60}")
    print(f"🚀 Starting Vamsify LLM Chat Server")
    print(f"{'='*60}")
    print(f"📍 URL: http://localhost:{PORT}")
    print(f"💬 Open your browser and start chatting!")
    print(f"{'='*60}\n")
    
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
