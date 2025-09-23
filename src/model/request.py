from pydantic import BaseModel

class CompletionRequest(BaseModel):
    prompt: str
    guest: bool
    attachments: list[dict] = []
    conversation_id: str | None = None
    section_id: str | None = None
    use_deep_think: bool = False
    use_auto_cot: bool = False


class AttachmentRequest(BaseModel):
    key: str
    name: str
    type: str
    file_review_state: int
    file_parse_state: int
    identifier: str
    option: dict | None = None
    md5: str | None = None
    size: int | None = None


class UploadRequest(BaseModel):
    file_type: int
    file_name: str
    file_bytes: bytes


class SessionConfigRequest(BaseModel):
    cookie: str
    device_id: str
    tea_uuid: str
    web_id: str
    room_id: str = ""
    x_flow_trace: str = ""


class SessionConfigUpdateRequest(BaseModel):
    cookie: str | None = None
    device_id: str | None = None
    tea_uuid: str | None = None
    web_id: str | None = None
    room_id: str | None = None
    x_flow_trace: str | None = None