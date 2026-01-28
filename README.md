# 🤖 Offline LLM Chat Application

A zero-cost chat application using a locally hosted open-source LLM. Runs completely offline after initial setup with no external API dependencies.

## ✨ Features

- 💰 **Zero Cost** - All open-source, no API keys needed
- 🔒 **100% Private** - Runs completely offline after setup
- 🚀 **Streaming Responses** - Real-time token-by-token generation
- 💬 **Conversation Memory** - Maintains context across messages
- 🎨 **Modern UI** - Beautiful dark-themed chat interface
- ⚡ **CPU Optimized** - Runs on standard laptop hardware

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS) → Flask Backend → llama-cpp-python → Local LLM Model
```

## 📋 Requirements

- Python 3.9 or higher
- 4GB+ RAM (8GB recommended)
- ~1GB free disk space for model
- Modern web browser

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd offline-llm-chat
pip install -r requirements.txt
```

> **Note**: Installing `llama-cpp-python` may take a few minutes as it compiles C++ code.

### 2. Configure (Optional)

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` to customize:
- Model selection
- System prompt
- Memory settings
- Port configuration

### 3. Run the Application

```bash
cd backend
python app.py
```

**First run**: The application will automatically download the LLM model (~800MB). This takes 2-5 minutes depending on your internet speed.

**Subsequent runs**: The model is cached locally, so startup is instant.

### 4. Open in Browser

Navigate to: **http://localhost:5000**

Start chatting with your private AI assistant!

## 📁 Project Structure

```
offline-llm-chat/
├── backend/
│   ├── app.py              # Flask server with REST API
│   ├── llm_handler.py      # LLM loading and inference
│   ├── conversation.py     # Memory management
│   └── config.py           # Configuration
├── frontend/
│   ├── index.html          # Chat interface
│   ├── style.css           # Styling
│   └── app.js              # Client logic
├── models/                 # Model storage (auto-created)
├── requirements.txt        # Python dependencies
├── .env.example            # Configuration template
└── README.md               # This file
```

## 🔧 Configuration

### Model Selection

By default, the app uses **Llama 3.2 1B** (Q4_K_M quantized, ~800MB).

To use a different model, edit `.env`:

```env
MODEL_NAME=your-model-name.gguf
MODEL_URL=https://huggingface.co/path/to/model.gguf
```

**Recommended models:**
- **Llama 3.2 1B** - Fast, efficient (default)
- **Phi-3 Mini 3.8B** - Better quality, slower
- **TinyLlama 1.1B** - Fastest, basic quality

### System Prompt

Customize the AI's behavior in `.env`:

```env
SYSTEM_PROMPT=You are a helpful coding assistant specializing in Python.
```

### Memory Settings

Control conversation history:

```env
MAX_HISTORY_MESSAGES=10    # Number of messages to remember
MAX_TOKENS=512             # Max tokens per response
TEMPERATURE=0.7            # Creativity (0.0-1.0)
```

## 🌐 API Endpoints

### POST `/chat`
Send a message and get a complete response.

**Request:**
```json
{
  "message": "Hello, who are you?"
}
```

**Response:**
```json
{
  "response": "I'm an AI assistant...",
  "history": [...]
}
```

### POST `/stream`
Send a message and get a streaming response (Server-Sent Events).

**Request:**
```json
{
  "message": "Tell me a story"
}
```

**Response:** SSE stream with tokens

### POST `/clear`
Clear conversation history.

### GET `/health`
Check server and model status.

## 🎯 Usage Tips

1. **First Message**: The first response may be slower as the model initializes
2. **Context**: The AI remembers the last 10 messages by default
3. **Long Responses**: Adjust `MAX_TOKENS` in `.env` for longer responses
4. **Performance**: Close other applications for better performance
5. **Offline**: After the model downloads, disconnect from internet - it still works!

## 🔒 Security & Privacy

- **No Data Collection**: Everything runs locally
- **No Internet Required**: After initial model download
- **Prompt Injection Protection**: System prompt is isolated
- **Input Validation**: Messages are sanitized and length-limited

## ⚡ Performance

**Expected speeds on modern CPU:**
- **1B models**: 10-20 tokens/second
- **3-4B models**: 5-10 tokens/second

**Response times:**
- Typical message: 1-3 seconds
- Long response: 5-10 seconds

## 🐛 Troubleshooting

### Model won't download
- Check internet connection
- Verify MODEL_URL in `.env`
- Try downloading manually and place in `models/` folder

### Out of memory errors
- Use a smaller model (1B instead of 3B)
- Reduce `MAX_HISTORY_MESSAGES`
- Reduce `N_CTX` in `config.py`

### Slow responses
- Close other applications
- Use a smaller model
- Reduce `MAX_TOKENS`

### Port already in use
- Change `PORT` in `.env`
- Kill process using port 5000: `netstat -ano | findstr :5000`

## 🚀 Future Enhancements

- [ ] Multiple conversation threads
- [ ] Model switching at runtime
- [ ] GPU acceleration support
- [ ] Voice input/output
- [ ] RAG (document Q&A)
- [ ] Persistent chat history
- [ ] Markdown rendering
- [ ] Code syntax highlighting

## 📝 License

This project uses open-source components:
- **Flask** - BSD License
- **llama-cpp-python** - MIT License
- **Models** - Check individual model licenses

## 🤝 Contributing

This is a demonstration project. Feel free to fork and customize for your needs!

## 📚 Learn More

- [llama-cpp-python Documentation](https://github.com/abetlen/llama-cpp-python)
- [Hugging Face Model Hub](https://huggingface.co/models)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Built with for privacy-focused AI enthusiasts**
