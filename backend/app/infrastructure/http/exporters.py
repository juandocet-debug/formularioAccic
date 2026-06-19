from io import BytesIO

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


HEADERS = ["ID", "Documento", "Nombre", "Telefono", "Cursos de interes", "Grupo", "Lugar", "Dias", "Horario", "Fecha"]


def build_excel(rows: list[dict]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Respuestas"
    sheet.append(HEADERS)
    for row in rows:
        sheet.append(_row_values(row))

    for column in sheet.columns:
        length = max(len(str(cell.value or "")) for cell in column)
        sheet.column_dimensions[column[0].column_letter].width = min(max(length + 2, 12), 42)

    stream = BytesIO()
    workbook.save(stream)
    return stream.getvalue()


def build_pdf(rows: list[dict]) -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(stream, pagesize=landscape(letter), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    table = Table([HEADERS, *[_row_values(row) for row in rows]], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d145f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#8f80ff")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    doc.build([table])
    return stream.getvalue()


def _row_values(row: dict) -> list[str]:
    full_name = " ".join(
        item
        for item in [row["first_name"], row.get("second_name"), row["first_last_name"], row.get("second_last_name")]
        if item
    )
    return [
        str(row["id"]),
        str(row["document_number"]),
        full_name,
        str(row["phone"]),
        ", ".join(row.get("interested_courses", [])),
        str(row["group_name"]),
        str(row["place"]),
        str(row["days"]),
        str(row["schedule"]),
        str(row["created_at"]),
    ]
