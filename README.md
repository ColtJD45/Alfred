# Alfred v0.3.1 - README

Alfred is a lightweight AI assistant project powered by a FastAPI backend, a React frontend, OpenAI GPT models for the main agent, and a LLaMA 3 local model running via Ollama for secondary agents.

## Demo

![Demo of feature](./assets/demo_v0.3.0.gif)

## Features

- Web-based chat interface for interacting with Alfred in real time
- Short-term memory for smooth, context-aware conversations
- Long-term memory stored in a user-specific SQLite database for personalization and recall
- User-specific memory handling for both short-term and long-term contexts
- Detailed weather reports for any location via the OpenWeatherMap API
    _Uses OpenCageData for accurate geolocation_
- Uses GPT-4 via OpenAI for main agent reasoning, with local LLaMA3 for memory tools and context lookups

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

Set up your environment variables:

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

```plaintext
alfred_v0.1.3/
│
├── main.py
├── backend/
│   ├── .venv      # Python virtual environment (not committed)
│   ├── nodes/     # Nodes (child agents)
│   ├── utils/     # Tools and SQLite database utilities
│   ├── .env       # Backend environment variables
│   ├── alfred_memory.db       # Database (auto-generated)
│   ├── main.py    # FastAPI backend entry point
│   └── requirements.txt       # Python dependencies
│
├── frontend/ # React frontend
│   ├── public/
│   ├── src/       # Main UI source (/components/Chat.jsx)
│   ├── .env       # Frontend environment variables
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt # Python dependencies (or pyproject.toml)
├── README.md # This file

```



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
- Ensure Ollama is installed and the `llama3:8b` model is downloaded. Test the llm alone in terminal to ensure it is responding.
- Check internet connectivity if styles or icons don’t load (Google Fonts & FontAwesome use CDNs). These links are in `/frontend/index.html`.

---

## 📍 Version v0.3.1 - Development Build

## Future Upgrades:

- Include Gmail monitoring to automatically create tasks via Zapier when email sent to home email address for things like:
  - Furnace filter change alerts
  - `Fixd` alerts for auto maintenance
  - Home insurance yearly reviews
  - Hot tub maintenance via monitoring app
  - Cold plunge maintenance via monitoring app
  - Smoke detector battery changes via home maintenance app
  - Home server maintenance and error faults via iDRAC email alerts
  - Automatically create a task to call and schedule dog grooming/healthcare via reminder emails
  - Create template for setting up any creation of a task based on received emails

- Add streaming to cut down user wait times

## Future Future upgrades
- Implement `OpenAI API` with curated promting to analyze these emails and create these tasks based on:
  - Schedule availability
  - Urgency of specific task
  - Combination of like tasks for efficiency
  - Ability to change an already created tasks for room for a more important/urgent task

- Add streaming to cut down user wait times

- Enable more abilities to `memory_node`
  - Fine tune `check_for_longterm_memory`
  - Fine tune search for `get_context` for accuracy and latency

---

*Thank you for checking out Alfred! Feel free to contribute or report issues.*

