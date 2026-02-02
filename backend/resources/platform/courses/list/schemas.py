"""Schemas para listagem de cursos."""
from apiflask import Schema
from apiflask.fields import String, DateTime, Nested, List


class ClassGroupSchema(Schema):
    """Schema para dados da turma."""
    id = String(metadata={'description': 'ID da turma'})
    name = String(metadata={'description': 'Nome da turma'})
    description = String(metadata={'description': 'Descricao da turma'})


class EnrollmentSchema(Schema):
    """Schema para dados de matricula."""
    id = String(metadata={'description': 'ID da matricula'})
    enrollment_date = DateTime(metadata={'description': 'Data de matricula'})
    status = String(metadata={'description': 'Status da matricula'})
    class_group = Nested(ClassGroupSchema, metadata={'description': 'Dados da turma'})


class CoursesListResponseSchema(Schema):
    """Schema para resposta de listagem de cursos."""
    status = String(metadata={'description': 'Status da resposta'})
    message = String(metadata={'description': 'Mensagem'})
    data = List(Nested(EnrollmentSchema), metadata={'description': 'Lista de matriculas'})
