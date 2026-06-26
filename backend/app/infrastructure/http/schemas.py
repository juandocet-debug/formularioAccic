import unicodedata

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.domain.courses import normalize_courses


class RegistrationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first_name: str = Field(min_length=2, max_length=80)
    second_name: str | None = Field(default=None, max_length=80)
    first_last_name: str = Field(min_length=2, max_length=80)
    second_last_name: str | None = Field(default=None, max_length=80)
    document_number: str = Field(min_length=5, max_length=30)
    phone: str = Field(min_length=7, max_length=30)
    group_id: int
    interested_courses: list[str] = Field(default_factory=list, min_length=1)

    @field_validator("first_name", "second_name", "first_last_name", "second_last_name", "document_number", "phone")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.strip().split())
        return cleaned or None

    @field_validator("first_name", "second_name", "first_last_name", "second_last_name")
    @classmethod
    def validate_name_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if any(not (character == " " or unicodedata.category(character).startswith("L")) for character in value):
            raise ValueError("Los nombres y apellidos solo deben contener letras y espacios.")
        return value

    @field_validator("document_number", "phone")
    @classmethod
    def validate_numeric_text(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Documento y telefono solo deben contener numeros.")
        return value

    @field_validator("interested_courses")
    @classmethod
    def clean_courses(cls, value: list[str]) -> list[str]:
        courses = normalize_courses(value)
        if not courses:
            raise ValueError("Selecciona al menos un curso de interes.")
        return courses


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=8, max_length=120)
