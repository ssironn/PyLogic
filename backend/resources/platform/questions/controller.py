"""Controller para endpoints de questoes na plataforma."""
from apiflask import APIBlueprint, Schema
from apiflask.fields import String

from resources.platform.questions.service import QuestionPlatformService
from resources.platform.questions.schemas import QuestionQuerySchema, AnswerSubmitSchema
from utils.response import ApiResponse
# from utils.auth import require_student, get_current_student_id


questions_bp = APIBlueprint('platform_questions', __name__, url_prefix='/api/questions')


@questions_bp.get('')
@questions_bp.input(QuestionQuerySchema, location='query')
@questions_bp.doc(tags=['Platform Questions'], summary='List questions')
# #@required_student
def list_questions(query_data):
    """Lista questoes disponiveis."""
    result = QuestionPlatformService.list_questions(
        student_id=get_current_student_id(),
        math_area_id=query_data.get('math_area_id'),
        math_subarea_id=query_data.get('math_subarea_id'),
        difficulty=query_data.get('difficulty'),
        search=query_data.get('search')
    )

    return ApiResponse.ok(data=result.value).to_tuple()


@questions_bp.get('/<question_id>')
@questions_bp.doc(tags=['Platform Questions'], summary='Get question by ID')
# #@required_student
def get_question(question_id):
    """Obtem uma questao pelo ID."""
    result = QuestionPlatformService.get_question(
        question_id=question_id,
        student_id=get_current_student_id()
    )

    if result.is_failure:
        return ApiResponse.not_found(message=result.message).to_tuple()

    return ApiResponse.ok(data=result.value).to_tuple()


@questions_bp.post('/<question_id>/answer')
@questions_bp.input(AnswerSubmitSchema)
@questions_bp.doc(tags=['Platform Questions'], summary='Submit answer to question')
#@required_student
def submit_answer(question_id, json_data):
    """Envia resposta para uma questao."""
    result = QuestionPlatformService.submit_answer(
        question_id=question_id,
        data=json_data,
        student_id=get_current_student_id()
    )

    if result.is_failure:
        if result.code == 'NOT_FOUND':
            return ApiResponse.not_found(message=result.message).to_tuple()
        return ApiResponse.bad_request(message=result.message).to_tuple()

    return ApiResponse.ok(
        data=result.value,
        message=result.message
    ).to_tuple()


@questions_bp.get('/<question_id>/approved-answers')
@questions_bp.doc(tags=['Platform Questions'], summary='Get approved answers for question')
#@required_student
def get_approved_answers(question_id):
    """Obtem respostas aprovadas para uma questao."""
    result = QuestionPlatformService.get_approved_answers(question_id)

    return ApiResponse.ok(data=result.value).to_tuple()


@questions_bp.get('/math-areas')
@questions_bp.doc(tags=['Platform Questions'], summary='List math areas')
#@required_student
def list_math_areas():
    """Lista areas matematicas para filtro."""
    result = QuestionPlatformService.list_math_areas()

    return ApiResponse.ok(data=result.value).to_tuple()


@questions_bp.get('/math-areas/<area_id>/subareas')
@questions_bp.doc(tags=['Platform Questions'], summary='List subareas')
#@required_student
def list_subareas(area_id):
    """Lista subareas de uma area matematica."""
    result = QuestionPlatformService.list_subareas(area_id)

    return ApiResponse.ok(data=result.value).to_tuple()


class TextToLatexSchema(Schema):
    """Schema for text to latex conversion."""
    text = String(required=True)


@questions_bp.post('/convert-latex')
@questions_bp.input(TextToLatexSchema)
@questions_bp.doc(tags=['Platform Questions'], summary='Convert text to LaTeX')
#@required_student
def convert_to_latex(json_data):
    """Converte texto para LaTeX."""
    result = QuestionPlatformService.convert_to_latex(json_data.get('text', ''))

    return ApiResponse.ok(data={'latex': result.value}).to_tuple()
