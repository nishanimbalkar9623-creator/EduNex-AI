def test_chat_requires_login(client):
    assert client.post("/api/chat", json={"message": "Hello"}).status_code == 401


def test_chat_returns_service_response(client):
    client.post("/api/auth/login", json={"username": "rahul", "password": "test-password"})
    response = client.post("/api/chat", json={"message": "Hello there"})
    assert response.status_code == 200
    assert response.json["success"] is True
    assert "Hello there" in response.json["response"]


def test_chat_keeps_session_context(client, app):
    seen_history = []

    def service(_user, message, history):
        seen_history.append(history)
        return f"reply: {message}"

    app.config["CHAT_SERVICE"] = service
    client.post("/api/auth/login", json={"username": "rahul", "password": "test-password"})
    client.post("/api/chat", json={"message": "My name is Rahul."})
    client.post("/api/chat", json={"message": "What is my name?"})
    assert len(seen_history[0]) == 0
    assert seen_history[1][0].content == "My name is Rahul."


def test_clear_chat_history(client):
    client.post("/api/auth/login", json={"username": "rahul", "password": "test-password"})
    client.post("/api/chat", json={"message": "Hello"})
    assert client.delete("/api/chat/history").status_code == 200


def test_ollama_unavailable_returns_friendly_error(client, app):
    from ai.llm import AIServiceUnavailable

    def unavailable(*_args):
        raise AIServiceUnavailable("EduNex AI is temporarily unable to connect to its AI service. Please make sure Ollama is running and try again.")

    app.config["CHAT_SERVICE"] = unavailable
    client.post("/api/auth/login", json={"username": "rahul", "password": "test-password"})
    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 503
    assert "Ollama" in response.json["error"]
