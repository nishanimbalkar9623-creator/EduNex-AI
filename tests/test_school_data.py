def login(client, username):
    response = client.post("/api/auth/login", json={"username": username, "password": "test-password"})
    assert response.status_code == 200


def ask(client, message):
    response = client.post("/api/chat", json={"message": message})
    assert response.status_code == 200
    assert response.json["source"] == "school_data"
    return response.json["response"]


def test_student_can_check_own_attendance(client):
    login(client, "rahul")
    response = ask(client, "What is my attendance percentage this month?")
    assert "Rahul's attendance" in response


def test_student_cannot_check_another_student(client):
    login(client, "rahul")
    assert "only view your own" in ask(client, "What is Priya's attendance?")


def test_parent_can_check_child_but_not_unrelated_student(client):
    login(client, "mrs-sharma")
    assert "Rahul's attendance" in ask(client, "What is Rahul's attendance this month?")
    assert "only view attendance for your own child" in ask(client, "What is Priya's attendance?")


def test_teacher_can_check_authorized_student_and_class(client):
    login(client, "mr-patil")
    assert "Priya's attendance" in ask(client, "What is Priya's attendance?")
    assert "Class 10-A attendance" in ask(client, "Show class 10-A attendance")


def test_principal_can_check_student_and_school_summary(client):
    login(client, "dr-deshmukh")
    assert "Aarav's attendance" in ask(client, "What is Aarav's attendance?")
    assert "School attendance" in ask(client, "What is the overall school attendance?")


def test_study_question_is_sent_to_ai_service(client):
    login(client, "rahul")
    response = client.post("/api/chat", json={"message": "Explain fractions to me."})
    assert "source" not in response.json
    assert "Explain fractions" in response.json["response"]
