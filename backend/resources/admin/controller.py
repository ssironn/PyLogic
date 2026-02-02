"""Controller para endpoints de administrador."""
from http import HTTPStatus

from apiflask import APIBlueprint, Schema
from apiflask.fields import String
from sqlalchemy import select

from app.extensions import db
from models import MathArea, MathSubarea
from resources.admin.auth.signin.service import AdminSigninService
from resources.admin.auth.signin.schemas import AdminSigninSchema
from resources.admin.class_groups.service import ClassGroupService
from resources.admin.class_groups.schemas import (
    ClassGroupCreateSchema,
    ClassGroupUpdateSchema,
    ClassGroupQuerySchema
)
from resources.admin.students.service import StudentService
from resources.admin.students.schemas import (
    StudentCreateSchema,
    StudentUpdateSchema,
    StudentQuerySchema
)
from resources.admin.content_nodes.service import ContentNodeService
from resources.admin.content_nodes.schemas import (
    ContentNodeCreateSchema,
    ContentNodeUpdateSchema,
    ContentNodeQuerySchema
)
from resources.admin.questions.service import QuestionService
from resources.admin.questions.schemas import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionQuerySchema
)
from resources.admin.youtube.service import get_video_info
from resources.admin.math_areas.service import MathAreaService
from resources.admin.math_areas.schemas import (
    MathAreaCreateSchema,
    MathAreaUpdateSchema,
    MathSubareaCreateSchema,
    MathSubareaUpdateSchema
)
from resources.admin.answers.service import AnswerAdminService
from resources.admin.answers.schemas import (
    AnswerReviewSchema,
    AnswerQuerySchema
)
from utils.response import ApiResponse
from utils.admin_auth import require_admin, get_current_admin_id


admin_bp = APIBlueprint('admin', __name__, url_prefix='/api/admin')


# ============== AUTH ==============

@admin_bp.post('/auth/signin')
@admin_bp.input(AdminSigninSchema)
@admin_bp.doc(tags=['Admin Auth'], summary='Admin sign in')
def signin(json_data):
    """Realiza login de administrador."""
    result = AdminSigninService.signin(json_data)

    if result.is_failure:
        return ApiResponse.unauthorized(
            message=result.message
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


# ============== CLASS GROUPS ==============

@admin_bp.get('/class-groups')
@admin_bp.input(ClassGroupQuerySchema, location='query')
@admin_bp.doc(tags=['Admin Class Groups'], summary='List class groups')
@require_admin
def list_class_groups(query_data):
    """Lista turmas do administrador."""
    result = ClassGroupService.list(
        admin_id=get_current_admin_id(),
        active=query_data.get('active'),
        search=query_data.get('search')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/class-groups/<class_group_id>')
@admin_bp.doc(tags=['Admin Class Groups'], summary='Get class group by ID')
@require_admin
def get_class_group(class_group_id):
    """Obtem uma turma pelo ID."""
    result = ClassGroupService.get(
        class_group_id=class_group_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/class-groups')
@admin_bp.input(ClassGroupCreateSchema)
@admin_bp.doc(tags=['Admin Class Groups'], summary='Create class group')
@require_admin
def create_class_group(json_data):
    """Cria uma nova turma."""
    result = ClassGroupService.create(
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/class-groups/<class_group_id>')
@admin_bp.input(ClassGroupUpdateSchema)
@admin_bp.doc(tags=['Admin Class Groups'], summary='Update class group')
@require_admin
def update_class_group(class_group_id, json_data):
    """Atualiza uma turma."""
    result = ClassGroupService.update(
        class_group_id=class_group_id,
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/class-groups/<class_group_id>')
@admin_bp.doc(tags=['Admin Class Groups'], summary='Delete class group')
@require_admin
def delete_class_group(class_group_id):
    """Remove uma turma."""
    result = ClassGroupService.delete(
        class_group_id=class_group_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


# ============== STUDENTS ==============

@admin_bp.get('/students')
@admin_bp.input(StudentQuerySchema, location='query')
@admin_bp.doc(tags=['Admin Students'], summary='List students')
@require_admin
def list_students(query_data):
    """Lista alunos das turmas do administrador."""
    result = StudentService.list(
        admin_id=get_current_admin_id(),
        class_group_id=query_data.get('class_group_id'),
        active=query_data.get('active'),
        search=query_data.get('search')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/students/<student_id>')
@admin_bp.doc(tags=['Admin Students'], summary='Get student by ID')
@require_admin
def get_student(student_id):
    """Obtem um aluno pelo ID."""
    result = StudentService.get(
        student_id=student_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/students')
@admin_bp.input(StudentCreateSchema)
@admin_bp.doc(tags=['Admin Students'], summary='Create student')
@require_admin
def create_student(json_data):
    """Cria um novo aluno."""
    result = StudentService.create(
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/students/<student_id>')
@admin_bp.input(StudentUpdateSchema)
@admin_bp.doc(tags=['Admin Students'], summary='Update student')
@require_admin
def update_student(student_id, json_data):
    """Atualiza um aluno."""
    result = StudentService.update(
        student_id=student_id,
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/students/<student_id>')
@admin_bp.doc(tags=['Admin Students'], summary='Delete student')
@require_admin
def delete_student(student_id):
    """Remove um aluno."""
    result = StudentService.delete(
        student_id=student_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


# ============== CONTENT NODES ==============

@admin_bp.get('/content-nodes')
@admin_bp.input(ContentNodeQuerySchema, location='query')
@admin_bp.doc(tags=['Admin Content'], summary='List content nodes')
@require_admin
def list_content_nodes(query_data):
    """Lista conteudos das turmas do administrador."""
    result = ContentNodeService.list(
        admin_id=get_current_admin_id(),
        class_group_id=query_data.get('class_group_id'),
        parent_id=query_data.get('parent_id'),
        content_type=query_data.get('type'),
        visibility=query_data.get('visibility'),
        search=query_data.get('search')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/content-nodes/<content_id>')
@admin_bp.doc(tags=['Admin Content'], summary='Get content node by ID')
@require_admin
def get_content_node(content_id):
    """Obtem um conteudo pelo ID."""
    result = ContentNodeService.get(
        content_id=content_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/content-nodes')
@admin_bp.input(ContentNodeCreateSchema)
@admin_bp.doc(tags=['Admin Content'], summary='Create content node')
@require_admin
def create_content_node(json_data):
    """Cria um novo conteudo."""
    result = ContentNodeService.create(
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/content-nodes/<content_id>')
@admin_bp.input(ContentNodeUpdateSchema)
@admin_bp.doc(tags=['Admin Content'], summary='Update content node')
@require_admin
def update_content_node(content_id, json_data):
    """Atualiza um conteudo."""
    result = ContentNodeService.update(
        content_id=content_id,
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/content-nodes/<content_id>')
@admin_bp.doc(tags=['Admin Content'], summary='Delete content node')
@require_admin
def delete_content_node(content_id):
    """Remove um conteudo."""
    result = ContentNodeService.delete(
        content_id=content_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


# ============== YOUTUBE ==============

@admin_bp.get('/youtube/video-info/<video_id>')
@admin_bp.doc(tags=['Admin YouTube'], summary='Get YouTube video info')
@require_admin
def get_youtube_video_info(video_id):
    """Obtem informacoes de um video do YouTube."""
    video_info = get_video_info(video_id)

    if not video_info:
        return ApiResponse.bad_request(
            message='Nao foi possivel obter informacoes do video. Verifique se o ID esta correto e se a API key do YouTube esta configurada.'
        ).to_tuple()

    return ApiResponse.ok(data={
        'video_id': video_info.video_id,
        'title': video_info.title,
        'duration': video_info.duration,
        'channel': video_info.channel,
        'thumbnail_url': video_info.thumbnail_url
    }).to_tuple()


# ============== MATH AREAS ==============

@admin_bp.get('/math-areas')
@admin_bp.doc(tags=['Admin Math Areas'], summary='List math areas')
@require_admin
def list_math_areas():
    """Lista todas as areas matematicas."""
    result = MathAreaService.list_areas(include_inactive=True)
    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/math-areas/<area_id>')
@admin_bp.doc(tags=['Admin Math Areas'], summary='Get math area by ID')
@require_admin
def get_math_area(area_id):
    """Obtem uma area matematica pelo ID."""
    result = MathAreaService.get_area(area_id)

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/math-areas')
@admin_bp.input(MathAreaCreateSchema)
@admin_bp.doc(tags=['Admin Math Areas'], summary='Create math area')
@require_admin
def create_math_area(json_data):
    """Cria uma nova area matematica."""
    result = MathAreaService.create_area(json_data)

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/math-areas/<area_id>')
@admin_bp.input(MathAreaUpdateSchema)
@admin_bp.doc(tags=['Admin Math Areas'], summary='Update math area')
@require_admin
def update_math_area(area_id, json_data):
    """Atualiza uma area matematica."""
    result = MathAreaService.update_area(area_id, json_data)

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/math-areas/<area_id>')
@admin_bp.doc(tags=['Admin Math Areas'], summary='Delete math area')
@require_admin
def delete_math_area(area_id):
    """Remove uma area matematica."""
    result = MathAreaService.delete_area(area_id)

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


# ============== MATH SUBAREAS ==============

@admin_bp.get('/math-areas/<area_id>/subareas')
@admin_bp.doc(tags=['Admin Math Areas'], summary='List subareas of a math area')
@require_admin
def list_math_subareas(area_id):
    """Lista subareas de uma area matematica."""
    result = MathAreaService.list_subareas(area_id, include_inactive=True)

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/math-subareas/<subarea_id>')
@admin_bp.doc(tags=['Admin Math Areas'], summary='Get subarea by ID')
@require_admin
def get_math_subarea(subarea_id):
    """Obtem uma subarea pelo ID."""
    result = MathAreaService.get_subarea(subarea_id)

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/math-areas/<area_id>/subareas')
@admin_bp.input(MathSubareaCreateSchema)
@admin_bp.doc(tags=['Admin Math Areas'], summary='Create subarea')
@require_admin
def create_math_subarea(area_id, json_data):
    """Cria uma nova subarea."""
    result = MathAreaService.create_subarea(area_id, json_data)

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/math-subareas/<subarea_id>')
@admin_bp.input(MathSubareaUpdateSchema)
@admin_bp.doc(tags=['Admin Math Areas'], summary='Update subarea')
@require_admin
def update_math_subarea(subarea_id, json_data):
    """Atualiza uma subarea."""
    result = MathAreaService.update_subarea(subarea_id, json_data)

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/math-subareas/<subarea_id>')
@admin_bp.doc(tags=['Admin Math Areas'], summary='Delete subarea')
@require_admin
def delete_math_subarea(subarea_id):
    """Remove uma subarea."""
    result = MathAreaService.delete_subarea(subarea_id)

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


# ============== QUESTIONS ==============

@admin_bp.get('/questions')
@admin_bp.input(QuestionQuerySchema, location='query')
@admin_bp.doc(tags=['Admin Questions'], summary='List questions')
@require_admin
def list_questions(query_data):
    """Lista questoes."""
    result = QuestionService.list(
        admin_id=get_current_admin_id(),
        math_area_id=query_data.get('math_area_id'),
        math_subarea_id=query_data.get('math_subarea_id'),
        difficulty=query_data.get('difficulty'),
        active=query_data.get('active'),
        search=query_data.get('search')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/questions/<question_id>')
@admin_bp.doc(tags=['Admin Questions'], summary='Get question by ID')
@require_admin
def get_question(question_id):
    """Obtem uma questao pelo ID."""
    result = QuestionService.get(
        question_id=question_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.post('/questions')
@admin_bp.input(QuestionCreateSchema)
@admin_bp.doc(tags=['Admin Questions'], summary='Create question')
@require_admin
def create_question(json_data):
    """Cria uma nova questao."""
    result = QuestionService.create(
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.created(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.put('/questions/<question_id>')
@admin_bp.input(QuestionUpdateSchema)
@admin_bp.doc(tags=['Admin Questions'], summary='Update question')
@require_admin
def update_question(question_id, json_data):
    """Atualiza uma questao."""
    result = QuestionService.update(
        question_id=question_id,
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(
            message=result.message,
            errors=[{'code': result.code, 'message': result.message, 'field': result.field}]
        ).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/questions/<question_id>')
@admin_bp.doc(tags=['Admin Questions'], summary='Delete question')
@require_admin
def delete_question(question_id):
    """Remove uma questao."""
    result = QuestionService.delete(
        question_id=question_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


class TextToLatexSchema(Schema):
    """Schema for text to latex conversion."""
    text = String(required=True)


@admin_bp.post('/questions/convert-latex')
@admin_bp.input(TextToLatexSchema)
@admin_bp.doc(tags=['Admin Questions'], summary='Convert text to LaTeX')
@require_admin
def convert_to_latex(json_data):
    """Converte texto para LaTeX."""
    result = QuestionService.convert_to_latex(json_data.get('text', ''))

    return ApiResponse.ok(data={'latex': result.value}).to_tuple()


# ============== ANSWERS ==============

@admin_bp.get('/answers')
@admin_bp.input(AnswerQuerySchema, location='query')
@admin_bp.doc(tags=['Admin Answers'], summary='List answers')
@require_admin
def list_answers(query_data):
    """Lista respostas dos alunos."""
    result = AnswerAdminService.list(
        admin_id=get_current_admin_id(),
        question_id=query_data.get('question_id'),
        student_id=query_data.get('student_id'),
        status=query_data.get('status')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/answers/<answer_id>')
@admin_bp.doc(tags=['Admin Answers'], summary='Get answer by ID')
@require_admin
def get_answer(answer_id):
    """Obtem uma resposta pelo ID."""
    result = AnswerAdminService.get(
        answer_id=answer_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.put('/answers/<answer_id>/review')
@admin_bp.input(AnswerReviewSchema)
@admin_bp.doc(tags=['Admin Answers'], summary='Review answer')
@require_admin
def review_answer(answer_id, json_data):
    """Avalia uma resposta (aprovar/rejeitar)."""
    result = AnswerAdminService.review(
        answer_id=answer_id,
        data=json_data,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@admin_bp.delete('/answers/<answer_id>')
@admin_bp.doc(tags=['Admin Answers'], summary='Delete answer')
@require_admin
def delete_answer(answer_id):
    """Remove uma resposta."""
    result = AnswerAdminService.delete(
        answer_id=answer_id,
        admin_id=get_current_admin_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(message=result.message).to_tuple()


@admin_bp.get('/questions/<question_id>/answers')
@admin_bp.doc(tags=['Admin Answers'], summary='List answers for a question')
@require_admin
def list_question_answers(question_id):
    """Lista respostas para uma questao especifica."""
    result = AnswerAdminService.list(
        admin_id=get_current_admin_id(),
        question_id=question_id
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@admin_bp.get('/questions/<question_id>/answers/stats')
@admin_bp.doc(tags=['Admin Answers'], summary='Get answer statistics for a question')
@require_admin
def get_question_answers_stats(question_id):
    """Obtem estatisticas de respostas para uma questao."""
    result = AnswerAdminService.get_question_answers_stats(question_id)

    return ApiResponse.ok(data=result.value).to_tuple()
