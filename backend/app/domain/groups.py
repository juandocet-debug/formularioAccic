from dataclasses import dataclass


GROUP_CAPACITY = 100


@dataclass(frozen=True)
class TrainingGroup:
    id: int
    name: str
    place: str
    days: str
    schedule: str


TRAINING_GROUPS: tuple[TrainingGroup, ...] = (
    TrainingGroup(1, "Grupo 1", "Salon Comunal Monteblanco", "Lunes y Miercoles", "8:00 a 10:00 a.m."),
    TrainingGroup(2, "Grupo 2", "Salon Comunal Monteblanco", "Lunes y Miercoles", "10:00 a.m. a 12:00 m."),
    TrainingGroup(3, "Grupo 3", "Salon Comunal Monteblanco", "Lunes y Miercoles", "1:00 a 3:00 p.m."),
    TrainingGroup(4, "Grupo 4", "Salon Comunal Monteblanco", "Lunes y Miercoles", "3:00 a 5:00 p.m."),
    TrainingGroup(5, "Grupo 5", "CDC El Virrey", "Martes y Jueves", "8:00 a 10:00 a.m."),
    TrainingGroup(6, "Grupo 6", "CDC El Virrey", "Martes y Jueves", "10:00 a.m. a 12:00 m."),
    TrainingGroup(7, "Grupo 7", "CDC El Virrey", "Martes y Jueves", "1:00 a 3:00 p.m."),
    TrainingGroup(8, "Grupo 8", "CDC El Virrey", "Martes y Jueves", "3:00 a 5:00 p.m."),
    TrainingGroup(9, "Grupo 9", "Salon Comunal Almirante Padilla", "Viernes y Sabados", "8:00 a 10:00 a.m."),
    TrainingGroup(10, "Grupo 10", "Salon Comunal Almirante Padilla", "Viernes y Sabados", "10:00 a.m. a 12:00 m."),
)


def get_group(group_id: int) -> TrainingGroup | None:
    return next((group for group in TRAINING_GROUPS if group.id == group_id), None)
