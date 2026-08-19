# EduNex AI

EduNex AI is a role-aware school assistant. It connects the existing Flask chat endpoint to a locally hosted Ollama model through LangChain, while authentication and authorization remain under Flask control.

## Current capabilities

- Session-authenticated demo roles: student, parent, teacher, and principal
- Role-aware local AI chat through `POST /api/chat`
- Bounded temporary conversation context stored in the signed browser session
- Safe, user-friendly handling when Ollama is unavailable
- Responsive dark interface with a canvas starfield, abstract AI orb, and reduced-motion support
- Reserved school-tool catalog with no database or SQL access

## Security boundary

The model receives the role obtained from the authenticated Flask session. It cannot change roles, access a database, run SQL, or call school tools. Model instructions support safe behavior, but backend authorization remains the security boundary.

Attendance, analytics, support requests, voice, and long-term memory are not connected yet. EduNex AI must say so rather than inventing information.

## Windows PowerShell setup

```powershell
cd C:\Users\Admin\Documents\Codex\2026-08-19\cr\edunex-ai
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure `SECRET_KEY` and password hashes in `.env`. Never commit this file.

## Ollama setup

The defaults are:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
AI_TEMPERATURE=0.2
AI_MAX_CONTEXT_MESSAGES=6
OLLAMA_TIMEOUT_SECONDS=60
```

Check local models and pull the configured one only if missing:

```powershell
ollama list
ollama pull llama3.2
ollama run llama3.2
```

The integration uses the current `langchain_ollama.ChatOllama` package.

## Run and test

```powershell
python app.py
pytest -q
```

Open `http://127.0.0.1:5000`, sign in, then send a message. If the AI is unavailable, confirm Ollama is running and test it with `ollama run llama3.2`.

## Demo users

| Username | Role |
| --- | --- |
| `rahul` | Student |
| `mrs-sharma` | Parent |
| `mr-patil` | Teacher |
| `dr-deshmukh` | Principal |

Passwords are local-only values in `.env`.

## Structure

```text
edunex-ai/
├── ai/                 # prompts, LangChain/Ollama service, session memory, future tools
├── auth/               # session authentication and role enforcement
├── static/             # visual, chat, and starfield modules
├── templates/          # login and assistant workspace
├── tests/
├── app.py
├── config.py
└── requirements.txt
```
