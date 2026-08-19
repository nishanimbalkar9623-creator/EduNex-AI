# EduNex AI Phase 1 Architecture

The current integration establishes the following security boundary:

```text
Browser → Flask endpoint → session identity → role-aware prompt + bounded memory → LangChain → Ollama
```

The frontend may send natural-language text, but it does not supply the authenticated identity or role. `current_demo_user()` derives both from the signed Flask session. `ai.llm` uses `langchain_ollama.ChatOllama` with environment configuration. The conversation window is deliberately short and stored only in the session.

`ai.tools` is a disabled catalog, not an executable tool layer. Future attendance and AI tools must call service-layer permission checks before querying or mutating data. The model never receives database access, SQL, or secrets.
