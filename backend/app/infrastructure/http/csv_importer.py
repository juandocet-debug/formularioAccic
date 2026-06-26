import csv
import io
import re
import unicodedata
from typing import Any

from pydantic import ValidationError

from app.infrastructure.http.schemas import RegistrationInput

MAX_CSV_BYTES = 2 * 1024 * 1024
MAX_CSV_ROWS = 1000

FIELD_ALIASES = {
    "full_name": {"nombre", "nombre completo", "full_name", "name"},
    "first_name": {"primer_nombre", "primer nombre", "first_name", "nombre_1"},
    "second_name": {"segundo_nombre", "segundo nombre", "second_name", "nombre_2"},
    "first_last_name": {"primer_apellido", "primer apellido", "first_last_name", "apellido", "apellido_1"},
    "second_last_name": {"segundo_apellido", "segundo apellido", "second_last_name", "apellido_2"},
    "document_number": {
        "documento",
        "numero_documento",
        "numero de documento",
        "document_number",
        "cedula",
        "identificacion",
    },
    "phone": {"telefono", "celular", "phone"},
    "group_id": {"grupo", "group_id", "id_grupo", "grupo_id"},
    "interested_courses": {"cursos", "cursos_interes", "cursos de interes", "interested_courses"},
}


def parse_registration_csv(content: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if len(content) > MAX_CSV_BYTES:
        return [], [{"row": None, "document_number": "", "message": "El CSV supera el tamano maximo de 2 MB."}]

    text = _decode_csv(content)
    reader = _build_reader(text)
    if not reader.fieldnames:
        return [], [{"row": None, "document_number": "", "message": "El CSV no tiene encabezados."}]

    header_map = _build_header_map(reader.fieldnames)
    missing = [
        field
        for field in ("document_number", "phone", "group_id", "interested_courses")
        if field not in header_map
    ]
    if "full_name" not in header_map and ("first_name" not in header_map or "first_last_name" not in header_map):
        missing.append("nombre")
    if missing:
        return [], [{"row": None, "document_number": "", "message": f"Faltan columnas obligatorias: {', '.join(missing)}."}]

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for index, raw_row in enumerate(reader, start=2):
        if index > MAX_CSV_ROWS + 1:
            errors.append({"row": index, "document_number": "", "message": f"Solo se permiten {MAX_CSV_ROWS} filas por carga."})
            break
        if not any((value or "").strip() for value in raw_row.values()):
            continue

        payload = _row_to_payload(raw_row, header_map)
        try:
            valid = RegistrationInput(**payload).model_dump()
            valid["_row_number"] = index
            rows.append(valid)
        except ValidationError as error:
            errors.append(
                {
                    "row": index,
                    "document_number": payload.get("document_number", ""),
                    "message": _validation_message(error),
                }
            )

    return rows, errors


def _decode_csv(content: bytes) -> str:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def _build_reader(text: str) -> csv.DictReader:
    sample = text[:2048]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    return csv.DictReader(io.StringIO(text), dialect=dialect)


def _build_header_map(fieldnames: list[str]) -> dict[str, str]:
    normalized = {_normalize_header(name): name for name in fieldnames if name}
    header_map: dict[str, str] = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                header_map[field] = normalized[alias]
                break
    return header_map


def _row_to_payload(row: dict[str, str | None], header_map: dict[str, str]) -> dict[str, Any]:
    def value(field: str) -> str:
        return (row.get(header_map[field]) or "").strip()

    name_parts = _split_full_name(value("full_name")) if "full_name" in header_map else None
    return {
        "first_name": name_parts["first_name"] if name_parts else value("first_name"),
        "second_name": name_parts["second_name"] if name_parts else value("second_name") if "second_name" in header_map else "",
        "first_last_name": name_parts["first_last_name"] if name_parts else value("first_last_name"),
        "second_last_name": name_parts["second_last_name"] if name_parts else value("second_last_name") if "second_last_name" in header_map else "",
        "document_number": _digits(value("document_number")),
        "phone": _digits(value("phone")) or "0000000",
        "group_id": _parse_group(value("group_id")),
        "interested_courses": _parse_courses(value("interested_courses")),
    }


def _normalize_header(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    normalized = "".join(character for character in normalized if not unicodedata.combining(character))
    return re.sub(r"\s+", " ", normalized.replace("-", "_"))


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value)


def _parse_group(value: str) -> int:
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else 0


def _parse_courses(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;|,]", value) if item.strip()]


def _split_full_name(value: str) -> dict[str, str]:
    parts = value.split()
    if len(parts) >= 4:
        return {
            "first_name": parts[0],
            "second_name": parts[1],
            "first_last_name": parts[2],
            "second_last_name": " ".join(parts[3:]),
        }
    if len(parts) == 3:
        return {
            "first_name": parts[0],
            "second_name": "",
            "first_last_name": parts[1],
            "second_last_name": parts[2],
        }
    if len(parts) == 2:
        return {
            "first_name": parts[0],
            "second_name": "",
            "first_last_name": parts[1],
            "second_last_name": "",
        }
    return {
        "first_name": parts[0] if parts else "",
        "second_name": "",
        "first_last_name": "",
        "second_last_name": "",
    }


def _validation_message(error: ValidationError) -> str:
    messages = [str(item.get("msg", "Dato invalido")) for item in error.errors()]
    return " ".join(messages)
