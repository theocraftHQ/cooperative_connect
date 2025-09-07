from typing import List, Optional
from pydantic import Field
from coop_connect.root.utils.base_schemas import AbstractModel
from datetime import datetime
from coop_connect.root.coop_enums import QuestionType
import uuid


class Choice(AbstractModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    value: Optional[str] = None  # can be used as "machine value"


class Question(AbstractModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    description: Optional[str] = None
    required: bool = False
    type: QuestionType
    choices: Optional[List[Choice]] = None  # only for choice-type questions

    # Validation constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    # File upload-specific
    allowed_file_types: Optional[List[str]] = None  # e.g., ["jpg", "png", "pdf"]
    max_file_size_mb: Optional[int] = None
    max_files: Optional[int] = None


class Form(AbstractModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.now())
    published: bool = False
    questions: List[Question] = []


# Response Models

class Answer(AbstractModel):
    question_id: str

    # Generic answers
    text: Optional[str] = None
    number: Optional[float] = None
    date: Optional[str] = None   # ISO YYYY-MM-DD
    time: Optional[str] = None   # HH:MM

    # Choice answers
    choice_id: Optional[str] = None        # for SINGLE_CHOICE or DROPDOWN
    choice_ids: Optional[List[str]] = None  # for MULTIPLE_CHOICE

    # File upload answers (list of uploaded file URLs/paths)
    files: Optional[List[str]] = None


class FormResponse(AbstractModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    form_id: str
    user_id: uuid.UUID
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    answers: List[Answer]
