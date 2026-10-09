import uuid
import pytest
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_logging_and_secret_redaction(db_session):
    audit_service = AuditService(db_session)
    org_id = uuid.uuid4()
    user_id = uuid.uuid4()

    # Log action containing a sensitive password key in metadata
    metadata = {
        "user_email": "test@acme.com",
        "password": "SuperSecretPassword123!",
        "secret": "hidden_secret",
        "file_size": 1024,
    }

    log_entry = await audit_service.log_event(
        action="DOCUMENT_UPLOADED",
        resource_type="Document",
        organization_id=org_id,
        user_id=user_id,
        resource_id="doc_123",
        metadata=metadata,
    )

    assert log_entry.action == "DOCUMENT_UPLOADED"
    assert log_entry.organization_id == org_id
    # Verify sensitive password and secret keys were automatically redacted
    assert "password" not in log_entry.metadata_json
    assert "secret" not in log_entry.metadata_json
    assert log_entry.metadata_json["user_email"] == "test@acme.com"

    # Retrieve audit logs
    logs = await audit_service.list_org_audit_logs(org_id)
    assert len(logs) == 1
    assert logs[0].action == "DOCUMENT_UPLOADED"
