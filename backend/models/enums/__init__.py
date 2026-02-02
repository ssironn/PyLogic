from enum import Enum

class EnrollmentStatus(str, Enum):
    ACTIVE = 'ativo'
    INACTIVE = 'inativo'
    PENDING = 'pendente'

class ContentType(str, Enum):
    FOLDER = 'pasta'
    FILE = 'arquivo'
    EXTERNAL_LINK = 'link_externo'
    YOUTUBE = 'youtube'

class ContentVisibility(str, Enum):
    PUBLIC = 'publico'
    PRIVATE = 'privado'
    RESTRICTED = 'restrito'

class AccessType(str, Enum):
    READ = 'leitura'
    WRITE = 'escrita'
    COMMENT = 'comentario'
    DOWNLOAD = 'download'

class ActionType(str, Enum):
    VIEW = 'visualizacao'
    DOWNLOAD = 'download'
    UPLOAD = 'upload'
    DELETE = 'exclusao'

class ProgressStatus(str, Enum):
    NOT_STARTED = 'nao_iniciado'
    IN_PROGRESS = 'em_andamento'
    COMPLETED = 'concluido'

class NotificationType(str, Enum):
    INFO = 'info'
    WARNING = 'aviso'
    SUCCESS = 'sucesso'
    ERROR = 'erro'


class QuestionDifficulty(str, Enum):
    EASY = 'facil'
    MEDIUM = 'medio'
    HARD = 'dificil'
    EXPERT = 'especialista'


class AnswerStatus(str, Enum):
    PENDING = 'pendente'
    APPROVED = 'aprovado'
    REJECTED = 'rejeitado'
