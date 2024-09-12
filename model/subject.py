import enum


class ExtendedEnum(enum.Enum):

    @classmethod
    def list(cls):
        return cls.__members__.values()


class Subject(ExtendedEnum):
    Math = "math", "Math"
    Physics = "physics", "Physique"
    # Chemistry = "chemistry", "Chimie"
    Other = "other", "Autre"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, description):
        self._description_ = description

    @property
    def description(self):
        return self._description_


lesson_catalog = {}


class SubjectLessons(ExtendedEnum):
    @classmethod
    def by_description(cls, description):
        for lesson in cls.list():
            if lesson.description == description:
                return lesson


class MathLessons(SubjectLessons):
    Revision = "revision", "Revision"
    Continuite = "continuitelimites", "Continuité et limites"
    Suites = "suites", "Suites réelles"
    Derivabilite = "derivabilite", "Dérivabilité"
    Reciproques = "reciproques", "Fonctions Réciproques"
    Primitives = "primitives", "Primitives"
    Integrales = "integrales", "Intégrales"
    Ln = "ln", "Fonction logarithme"
    Exp = "exponentielle", "Fonction exponentielle"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, description):
        self._description_ = description

    @property
    def description(self):
        return self._description_


class PhysicsLessons(SubjectLessons):
    Revision = "revision", "Revision"
    Condensateur = "condensateur", "Condensateur / Dipôle RC"
    Bobine = "bobine", "Bobine / Dipôle RL"
    OscillationsL = "oscillationsl", "Oscillations libres"
    OscillationsF = "oscillationsf", "Oscillations sinusoïdales"
    OscillationsLPE = "oscillationslpe", "Oscillations libres pendule"
    OscillationsFPE = "oscillationsfpe", "Oscillations sinusoïdales pendule"
    OndeM = "ondesm", "Ondes mécaniques"
    NatureOLumire = "natureolumiere", "Ondulatoire lumière"
    SpectreAtomique = "spectrea", "Spectre atomique"
    NoyauAtomique = "noyaua", "Le noyau atomique"
    Nucleaire = "nucleaire", "Réactions nucléaires"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, description):
        self._description_ = description

    @property
    def description(self):
        return self._description_


class OtherLessons(SubjectLessons):
    Revision = "autre", "Autre"

    def __new__(cls, *args, **kwds):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _, description):
        self._description_ = description

    @property
    def description(self):
        return self._description_


lesson_catalog[Subject.Math] = MathLessons
lesson_catalog[Subject.Physics] = PhysicsLessons
lesson_catalog[Subject.Other] = OtherLessons
