# Alfred v0.1.3 - README

Alfred is a lightweight AI assistant project powered by a FastAPI backend, a React frontend, OpenAI GPT models for the main agent,  
and a LLaMA 3 local model running via Ollama for secondary agents.

---

## 🛠️ Setup Instructions

Make sure the following components are installed before running Alfred:

- Python 3.10+
- Node.js (v18 or later recommended) on your global machine
- [Ollama](https://ollama.com)
- `uv` or `pip` for managing Python packages
- `npm` or `pnpm` for managing frontend packages

---

## 🔑 Environment Variables

Setup your environment variables:

1. Rename `.env.example` to `.env` in both the backend and the frontend directories.
   These `.env` files will hold all of your secrets (like API keys), which the scripts will load automatically when needed.

2. Gather the necessary API keys (see instructions and placeholders inside each `.env.example`) and paste them into your `.env` files.

3. Fill in any optional configuration details you want to personalize Alfred with, such as DEFAULT_USER_ID, LOCATION, and FAMILY_NAME.

---

## 🚀 Running the Project

Run these commands in separate terminals or background processes.

1. **Start the backend server:**

    ```bash
    source venv/bin/activate  # Activate your virtual environment
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```

    - `0.0.0.0` allows access from other devices on the same network (if firewall/network permits).
    - Change `--port` if 8000 is already in use, and update your frontend `.env` accordingly.

2. **Install frontend dependencies (only once or after updating package.json):**

    ```bash
    cd frontend
    npm install
    ```

    - This will generate the `node_modules` directory with the dependencies required for the frontend.

3. **Start the frontend:**

    ```bash
    cd frontend
    npm run dev --host
    ```

    - Verify you are running this from the `frontend` directory.

4. **Start the LLaMA 3 model with Ollama:**

    ```bash
    ollama run llama3:8b
    ```

    - You can run this from any terminal; it doesn’t need to be inside the project folder or virtual environment.
    - Make sure it's running before using Alfred, as it currently powers the chat history and memory functionality.

5. **Access the frontend:**

    - On the server machine: [http://localhost:5173](http://localhost:5173)  
    - On another device in the local network: `http://<server-ip-address>:5173`

---

## 📁 Directory Structure (partial)

alfred_v0.1.3/
│
├── main.py
├── backend/
│ ├── .venv # Python virtual environment (not committed)
│ ├── nodes/ # Nodes (child agents)
│ ├── utils/ # Tools and SQLite database utilities
│ ├── .env # Backend environment variables
│ ├── alfred_memory.db # Database (auto-generated)
│ ├── main.py # FastAPI backend entry point
│ └── requirements.txt # Python dependencies
│
├── frontend/ # React frontend
│ ├── public/
│ ├── src/ # Main UI source (/components/Chat.jsx)
│ ├── .env # Frontend environment variables
│ ├── package.json
│ └── vite.config.js
│
├── requirements.txt # Python dependencies (or pyproject.toml)
├── README.md # This file


---

## 🧠 Notes

- Multi-user ID system to personalize user experience.
- User sessions and chat history are stored both locally (browser) and in the backend.
- LLaMA 3 model must be downloaded via Ollama before the first run.

---

## 📦 Dependencies (Core)

### Backend

- FastAPI  
- Langgraph  
- OpenAI  
- uvicorn  
- pydantic  
- ollama-python  

### Frontend

- React  
- Vite  
- TailwindCSS  
- FontAwesome  
- Google Fonts (via CDN)  

---

## 🔐 Security

**Avoid using sensitive or personal data.**  
User identification is via localStorage and session IDs only. No authentication yet.

- Intended for local network use only, no external access.  
- CORS is set to allow all origins by default (`allow_origins=["*"]`). Restrict to known IPs for production security.

---

## 🧪 Troubleshooting

- Minimal testing done; if making changes, watch out for potential infinite API call loops. Terminate if the app stops responding.  
- Adjust ports in backend/frontend if conflicts occur.  
- Ensure Ollama is installed and the `llama3:8b` model is downloaded. Test the llm alone in terminal to insure it is responding.
- Check internet connectivity if styles or icons don’t load (Google Fonts & FontAwesome use CDNs). These links are in `/frontend/index.html`.

---

## 📍 Version v0.1.3 — Development Build

Features:

- Web UI chat interface  
- OpenAI API powered conversation  
- OpenWeather API integration for weather info and forecasts  
- Stores prompts and AI responses in SQLite with user/session IDs and timestamps  
- Local chat history memory recall (last 20 messages by default)  

Planned Next:

- Implement additional nodes (starting with memory node)  
- Merge prior memory_llama.py features into memory_node for supervisor agent
- Enable dynamic saving and recalling of longterm memories with LLaMA3 (memory node)
- Longterm memory stored in SQLite and referenced by Alfred for personalized queries

---

*Thank you for checking out Alfred! Feel free to contribute or report issues.*

