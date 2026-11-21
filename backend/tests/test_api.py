from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_returns_success() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "stage": "foundation-backend"}


def test_support_message_responds_with_authorized_rule() -> None:
    response = client.post("/support/messages", json={"message": "Onde vejo o rastreio?"})

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "regra"
    assert body["intent"] == "entrega"
    assert body["requires_human"] is False
    assert body["correlation_id"] == body["audit"]["correlation_id"]
    assert body["audit"]["rule_id"] == "FAQ-TRACKING-001"
    assert body["audit"]["duration_ms"] >= 0
    assert body["audit"]["knowledge_source"] == "knowledge/faq-exemplo.md"
    assert "nao consulta pedidos" in body["answer"].casefold()


def test_uncovered_message_is_escalated() -> None:
    response = client.post(
        "/support/messages",
        json={"message": "Preciso alterar o endereco cadastrado"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "humano"
    assert body["intent"] == "desconhecida"
    assert body["requires_human"] is True
    assert body["audit"]["reason_code"] == "NO_AUTHORIZED_RULE_MATCH"
    assert body["audit"]["rule_id"] is None


def test_blank_message_is_rejected() -> None:
    response = client.post("/support/messages", json={"message": "   "})

    assert response.status_code == 422


def test_exchange_is_escalated_without_inventing_policy() -> None:
    response = client.post("/support/messages", json={"message": "Posso trocar o produto?"})

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "humano"
    assert body["intent"] == "troca"
    assert body["requires_human"] is True
    assert "nao esta disponivel" in body["answer"].casefold()

