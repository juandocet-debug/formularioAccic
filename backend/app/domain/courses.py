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
    allowed = set(AVAILABLE_COURSES)
    clean_courses: list[str] = []
    for course in courses:
        cleaned = " ".join(course.strip().split())
        if cleaned in allowed and cleaned not in clean_courses:
            clean_courses.append(cleaned)
    return clean_courses
