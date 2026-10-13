import pytest

@pytest.mark.asyncio
async def test_assist(client):
    await client.post(
        "/api/tickets",
        json={
            "subject": "Cannot reset MFA",
            "body": "User lost phone and cannot approve MFA prompts.",
            "resolution": "Enrolled backup codes and reset authenticator via admin console.",
            "tags": "auth,mfa",
        },
    )
    r = await client.post(
        "/api/assist",
        json={
            "subject": "MFA locked out",
            "body": "Customer changed phones and is stuck on MFA.",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["similar"]
    assert "draft_reply" in body
