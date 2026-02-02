"""Service for platform questions operations (student side)."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select

from app.extensions import db
from models import Question, MathArea, MathSubarea, Answer
from models.enums import QuestionDifficulty, AnswerStatus
from utils.response import Result


class QuestionPlatformService:
    """Service for students to view questions and submit answers."""

    @staticmethod
    def _serialize_question(question: Question, student_id: Optional[str] = None) -> dict:
        """Serialize a question to dictionary."""
        data = {
            'id': str(question.id),
            'math_area_id': str(question.math_area_id),
            'math_area_name': question.math_area.name if question.math_area else None,
            'math_subarea_id': str(question.math_subarea_id) if question.math_subarea_id else None,
            'math_subarea_name': question.math_subarea.name if question.math_subarea else None,
            'title': question.title,
            'content': question.content,
            'content_latex': question.content_latex,
            'difficulty': question.difficulty.value if question.difficulty else None,
            'tags': question.tags or [],
            'created_at': question.created_at.isoformat() if question.created_at else None,
        }

        # Check if student has answered this question
        if student_id:
            stmt = select(Answer).where(
                Answer.question_id == question.id,
                Answer.student_id == student_id
            )
            result = db.session.execute(stmt)
            answer = result.scalar_one_or_none()
            if answer:
                data['my_answer'] = {
                    'id': str(answer.id),
                    'content': answer.content,
                    'content_latex': answer.content_latex,
                    'status': answer.status.value if answer.status else None,
                    'is_correct': answer.is_correct,
                    'feedback': answer.feedback,
                    'score': answer.score,
                    'created_at': answer.created_at.isoformat() if answer.created_at else None,
                }
            else:
                data['my_answer'] = None

        # Get count of approved answers
        stmt = select(Answer).where(
            Answer.question_id == question.id,
            Answer.status == AnswerStatus.APPROVED
        )
        result = db.session.execute(stmt)
        approved_answers = result.scalars().all()
        data['approved_answers_count'] = len(approved_answers)

        return data

    @staticmethod
    def _serialize_answer(answer: Answer) -> dict:
        """Serialize an approved answer for public view."""
        return {
            'id': str(answer.id),
            'student_name': answer.student.name if answer.student else 'Anonimo',
            'content': answer.content,
            'content_latex': answer.content_latex,
            'is_correct': answer.is_correct,
            'score': answer.score,
            'created_at': answer.created_at.isoformat() if answer.created_at else None,
        }

    @staticmethod
    def list_questions(
        student_id: str,
        math_area_id: Optional[str] = None,
        math_subarea_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None
    ) -> Result[list]:
        """
        List active questions for students.

        Args:
            student_id: ID of the student
            math_area_id: Filter by math area
            math_subarea_id: Filter by math subarea
            difficulty: Filter by difficulty
            search: Search in title and content

        Returns:
            Result containing list of questions
        """
        stmt = select(Question).where(Question.active == True)

        if math_area_id:
            stmt = stmt.where(Question.math_area_id == math_area_id)

        if math_subarea_id:
            stmt = stmt.where(Question.math_subarea_id == math_subarea_id)

        if difficulty:
            difficulty_map = {
                'facil': QuestionDifficulty.EASY,
                'medio': QuestionDifficulty.MEDIUM,
                'dificil': QuestionDifficulty.HARD,
                'especialista': QuestionDifficulty.EXPERT,
            }
            if difficulty in difficulty_map:
                stmt = stmt.where(Question.difficulty == difficulty_map[difficulty])

        if search:
            stmt = stmt.where(
                Question.title.ilike(f'%{search}%') |
                Question.content.ilike(f'%{search}%')
            )

        stmt = stmt.order_by(Question.created_at.desc())

        result = db.session.execute(stmt)
        questions = result.scalars().all()

        return Result.success(
            value=[QuestionPlatformService._serialize_question(q, student_id) for q in questions]
        )

    @staticmethod
    def get_question(question_id: str, student_id: str) -> Result[dict]:
        """
        Get a question by ID.

        Args:
            question_id: ID of the question
            student_id: ID of the student

        Returns:
            Result containing question data
        """
        stmt = select(Question).where(
            Question.id == question_id,
            Question.active == True
        )
        result = db.session.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return Result.fail(
                message="Questao nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(
            value=QuestionPlatformService._serialize_question(question, student_id)
        )

    @staticmethod
    def submit_answer(question_id: str, data: dict, student_id: str) -> Result[dict]:
        """
        Submit or update an answer to a question.

        Args:
            question_id: ID of the question
            data: Answer data (content, content_latex)
            student_id: ID of the student

        Returns:
            Result containing answer data
        """
        # Verify question exists and is active
        stmt = select(Question).where(
            Question.id == question_id,
            Question.active == True
        )
        result = db.session.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return Result.fail(
                message="Questao nao encontrada",
                code="NOT_FOUND"
            )

        # Check if student already answered
        stmt = select(Answer).where(
            Answer.question_id == question_id,
            Answer.student_id == student_id
        )
        result = db.session.execute(stmt)
        existing_answer = result.scalar_one_or_none()

        if existing_answer:
            # Update existing answer
            existing_answer.content = data.get('content')
            existing_answer.content_latex = data.get('content_latex')
            existing_answer.ensure_latex()
            existing_answer.status = AnswerStatus.PENDING  # Reset to pending
            existing_answer.is_correct = None
            existing_answer.feedback = None
            existing_answer.score = None
            existing_answer.reviewed_by = None
            existing_answer.reviewed_at = None
            existing_answer.updated_at = datetime.now(timezone.utc)

            db.session.commit()

            return Result.success(
                value={
                    'id': str(existing_answer.id),
                    'content': existing_answer.content,
                    'content_latex': existing_answer.content_latex,
                    'status': existing_answer.status.value,
                    'created_at': existing_answer.created_at.isoformat() if existing_answer.created_at else None,
                    'updated_at': existing_answer.updated_at.isoformat() if existing_answer.updated_at else None,
                },
                message="Resposta atualizada com sucesso"
            )
        else:
            # Create new answer
            answer = Answer(
                student_id=student_id,
                question_id=question_id,
                content=data.get('content'),
                content_latex=data.get('content_latex'),
                status=AnswerStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            answer.ensure_latex()

            db.session.add(answer)
            db.session.commit()

            return Result.success(
                value={
                    'id': str(answer.id),
                    'content': answer.content,
                    'content_latex': answer.content_latex,
                    'status': answer.status.value,
                    'created_at': answer.created_at.isoformat() if answer.created_at else None,
                },
                message="Resposta enviada com sucesso"
            )

    @staticmethod
    def get_approved_answers(question_id: str) -> Result[list]:
        """
        Get approved answers for a question.

        Args:
            question_id: ID of the question

        Returns:
            Result containing list of approved answers
        """
        stmt = select(Answer).where(
            Answer.question_id == question_id,
            Answer.status == AnswerStatus.APPROVED
        ).order_by(Answer.created_at.desc())

        result = db.session.execute(stmt)
        answers = result.scalars().all()

        return Result.success(
            value=[QuestionPlatformService._serialize_answer(a) for a in answers]
        )

    @staticmethod
    def list_math_areas() -> Result[list]:
        """List active math areas for filtering."""
        stmt = select(MathArea).where(MathArea.active == True).order_by(MathArea.order)
        result = db.session.execute(stmt)
        areas = result.scalars().all()

        data = [{
            'id': str(area.id),
            'name': area.name,
            'icon': area.icon,
            'color': area.color,
        } for area in areas]

        return Result.success(value=data)

    @staticmethod
    def list_subareas(area_id: str) -> Result[list]:
        """List active subareas for a math area."""
        stmt = select(MathSubarea).where(
            MathSubarea.math_area_id == area_id,
            MathSubarea.active == True
        ).order_by(MathSubarea.order)
        result = db.session.execute(stmt)
        subareas = result.scalars().all()

        data = [{
            'id': str(subarea.id),
            'name': subarea.name,
        } for subarea in subareas]

        return Result.success(value=data)

    @staticmethod
    def convert_to_latex(text: str) -> Result[str]:
        """Convert plain text to LaTeX."""
        latex_text = Answer.text_to_latex(text)
        return Result.success(value=latex_text)
