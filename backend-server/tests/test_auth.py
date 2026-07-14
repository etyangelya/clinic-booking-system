from tests.conftest import DOCTOR_PASSWORD, future_slot


def _login(client, email, password=DOCTOR_PASSWORD):
    return client.post("/auth/login", data={"username": email, "password": password})


def test_login_with_correct_credentials_returns_token(client, doctor):
    response = _login(client, doctor.email)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_wrong_password_returns_401(client, doctor):
    response = _login(client, doctor.email, password="wrong-password")
    assert response.status_code == 401


def test_my_appointments_without_token_returns_401(client):
    response = client.get("/doctors/me/appointments")
    assert response.status_code == 401


def test_doctor_a_token_cannot_see_doctor_b_appointments(client, doctor, other_doctor):
    slot_a = future_slot(hour=9)
    slot_b = future_slot(hour=10)
    client.post(
        "/appointments",
        json={
            "doctor_id": doctor.id,
            "patient_name": "Patient A",
            "patient_email": "patient-a@example.com",
            "slot_time": slot_a.isoformat(),
        },
    )
    client.post(
        "/appointments",
        json={
            "doctor_id": other_doctor.id,
            "patient_name": "Patient B",
            "patient_email": "patient-b@example.com",
            "slot_time": slot_b.isoformat(),
        },
    )

    token_a = _login(client, doctor.email).json()["access_token"]
    response = client.get("/doctors/me/appointments", headers={"Authorization": f"Bearer {token_a}"})

    assert response.status_code == 200
    appointments = response.json()
    assert len(appointments) == 1
    assert appointments[0]["doctor_id"] == doctor.id
