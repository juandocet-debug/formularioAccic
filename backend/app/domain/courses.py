import unicodedata


AVAILABLE_COURSES: tuple[str, ...] = (
    "Curso de Gastronomía Ancestral",
    "Curso de Maquillaje",
    "Curso de Tejidos",
    "Curso de Joyería Artesanal",
    "Curso de Agricultura Urbana",
    "Curso de Bricolaje Creativo (DIY)",
    "Curso de Productos con Resina Epóxica",
    "Curso de Experiencias Comestibles",
    "Curso de Arcilla",
    "Curso de Estampados Artesanales",
)


def normalize_courses(courses: list[str]) -> list[str]:
    allowed_by_key = {_course_key(course): course for course in AVAILABLE_COURSES}
    allowed_by_key.update(
        {
            "gastronomia": "Curso de Gastronomía Ancestral",
            "gastronomia ancestral": "Curso de Gastronomía Ancestral",
            "maquillaje": "Curso de Maquillaje",
            "tejidos": "Curso de Tejidos",
            "joyeria artesanal": "Curso de Joyería Artesanal",
            "agricultura urbana": "Curso de Agricultura Urbana",
            "bricolaje creativo": "Curso de Bricolaje Creativo (DIY)",
            "diy": "Curso de Bricolaje Creativo (DIY)",
            "resina epoxica": "Curso de Productos con Resina Epóxica",
            "productos con resina epoxica": "Curso de Productos con Resina Epóxica",
            "experiencias comestibles": "Curso de Experiencias Comestibles",
            "arcilla": "Curso de Arcilla",
            "estampados artesanales": "Curso de Estampados Artesanales",
        }
    )
    clean_courses: list[str] = []
    for course in courses:
        matched = allowed_by_key.get(_course_key(course))
        if matched and matched not in clean_courses:
            clean_courses.append(matched)
    return clean_courses


def _course_key(value: str) -> str:
    cleaned = " ".join(value.strip().split()).lower()
    normalized = unicodedata.normalize("NFKD", cleaned)
    return "".join(character for character in normalized if not unicodedata.combining(character))
