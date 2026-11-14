from app import app


def test_home():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["status"] == "Employee API is running - Jenkins webhook test successful!"


def test_health():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "UP"


def test_get_employees():
    client = app.test_client()
    response = client.get("/employees")

    assert response.status_code == 200
    assert len(response.json) == 3


def test_get_employee():
    client = app.test_client()
    response = client.get("/employees/1")

    assert response.status_code == 200
    assert response.json["name"] == "Rahul"


def test_employee_not_found():
    client = app.test_client()
    response = client.get("/employees/999")

    assert response.status_code == 404
