"""Service for questions CRUD operations."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select

from app.extensions import db
from models import Question, MathArea, MathSubarea
from models.enums import QuestionDifficulty
from utils.response import Result


class QuestionService:
    """Service for managing questions."""

    @staticmethod
    def _serialize_question(question: Question) -> dict:
        """Serialize a question to dictionary."""
        return {
            'id': str(question.id),
            'math_area_id': str(question.math_area_id),
            'math_area_name': question.math_area.name if question.math_area else None,
            'math_subarea_id': str(question.math_subarea_id) if question.math_subarea_id else None,
            'math_subarea_name': question.math_subarea.name if question.math_subarea else None,
            'title': question.title,
            'content': question.content,
            'content_latex': question.content_latex,
            'answer': question.answer,
            'answer_latex': question.answer_latex,
            'explanation': question.explanation,
            'explanation_latex': question.explanation_latex,
            'difficulty': question.difficulty.value if question.difficulty else None,
            'tags': question.tags or [],
            'active': question.active,
            'created_by': str(question.created_by),
            'created_at': question.created_at.isoformat() if question.created_at else None,
            'updated_at': question.updated_at.isoformat() if question.updated_at else None,
        }

    @staticmethod
    def list(
        admin_id: str,
        math_area_id: Optional[str] = None,
        math_subarea_id: Optional[str] = None,
        difficulty: Optional[str] = None,
        active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Result[list]:
        """
        List questions with optional filters.

        Args:
            admin_id: ID of the admin
            math_area_id: Filter by math area
            math_subarea_id: Filter by math subarea
            difficulty: Filter by difficulty
            active: Filter by active status
            search: Search in title and content

        Returns:
            Result containing list of questions
        """
        stmt = select(Question)

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

        if active is not None:
            stmt = stmt.where(Question.active == active)

        if search:
            stmt = stmt.where(
                Question.title.ilike(f'%{search}%') |
                Question.content.ilike(f'%{search}%')
            )

        stmt = stmt.order_by(Question.created_at.desc())

        result = db.session.execute(stmt)
        questions = result.scalars().all()

        return Result.success(
            value=[QuestionService._serialize_question(q) for q in questions]
        )

    @staticmethod
    def get(question_id: str, admin_id: str) -> Result[dict]:
        """
        Get a question by ID.

        Args:
            question_id: ID of the question
            admin_id: ID of the admin

        Returns:
            Result containing question data
        """
        stmt = select(Question).where(Question.id == question_id)
        result = db.session.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return Result.fail(
                message="Questao nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(
            value=QuestionService._serialize_question(question)
        )

    @staticmethod
    def create(data: dict, admin_id: str) -> Result[dict]:
        """
        Create a new question.

        Args:
            data: Question data
            admin_id: ID of the admin creating the question

        Returns:
            Result containing created question data
        """
        # Verify math area exists
        stmt = select(MathArea).where(MathArea.id == data.get('math_area_id'))
        result = db.session.execute(stmt)
        math_area = result.scalar_one_or_none()

        if not math_area:
            return Result.fail(
                message="Area matematica nao encontrada",
                code="MATH_AREA_NOT_FOUND",
                field="math_area_id"
            )

        # Verify math subarea if provided
        if data.get('math_subarea_id'):
            stmt = select(MathSubarea).where(
                MathSubarea.id == data.get('math_subarea_id'),
                MathSubarea.math_area_id == data.get('math_area_id')
            )
            result = db.session.execute(stmt)
            math_subarea = result.scalar_one_or_none()

            if not math_subarea:
                return Result.fail(
                    message="Subarea matematica nao encontrada ou nao pertence a area selecionada",
                    code="MATH_SUBAREA_NOT_FOUND",
                    field="math_subarea_id"
                )

        # Map difficulty
        difficulty_map = {
            'facil': QuestionDifficulty.EASY,
            'medio': QuestionDifficulty.MEDIUM,
            'dificil': QuestionDifficulty.HARD,
            'especialista': QuestionDifficulty.EXPERT,
        }
        difficulty = difficulty_map.get(data.get('difficulty', 'medio'), QuestionDifficulty.MEDIUM)

        # Create question
        question = Question(
            math_area_id=data.get('math_area_id'),
            math_subarea_id=data.get('math_subarea_id'),
            title=data.get('title'),
            content=data.get('content'),
            content_latex=data.get('content_latex'),
            answer=data.get('answer'),
            answer_latex=data.get('answer_latex'),
            explanation=data.get('explanation'),
            explanation_latex=data.get('explanation_latex'),
            difficulty=difficulty,
            tags=data.get('tags', []),
            created_by=admin_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        # Auto-generate LaTeX if not provided
        question.ensure_latex()

        db.session.add(question)
        db.session.commit()

        return Result.success(
            value=QuestionService._serialize_question(question),
            message="Questao criada com sucesso"
        )

    @staticmethod
    def update(question_id: str, data: dict, admin_id: str) -> Result[dict]:
        """
        Update a question.

        Args:
            question_id: ID of the question
            data: Data to update
            admin_id: ID of the admin

        Returns:
            Result containing updated question data
        """
        stmt = select(Question).where(Question.id == question_id)
        result = db.session.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return Result.fail(
                message="Questao nao encontrada",
                code="NOT_FOUND"
            )

        # Verify math area if being updated
        if data.get('math_area_id'):
            stmt = select(MathArea).where(MathArea.id == data.get('math_area_id'))
            result = db.session.execute(stmt)
            math_area = result.scalar_one_or_none()

            if not math_area:
                return Result.fail(
                    message="Area matematica nao encontrada",
                    code="MATH_AREA_NOT_FOUND",
                    field="math_area_id"
                )

        # Verify math subarea if being updated
        if 'math_subarea_id' in data and data.get('math_subarea_id'):
            area_id = data.get('math_area_id') or str(question.math_area_id)
            stmt = select(MathSubarea).where(
                MathSubarea.id == data.get('math_subarea_id'),
                MathSubarea.math_area_id == area_id
            )
            result = db.session.execute(stmt)
            math_subarea = result.scalar_one_or_none()

            if not math_subarea:
                return Result.fail(
                    message="Subarea matematica nao encontrada ou nao pertence a area selecionada",
                    code="MATH_SUBAREA_NOT_FOUND",
                    field="math_subarea_id"
                )

        # Update fields
        if data.get('math_area_id'):
            question.math_area_id = data['math_area_id']
        if 'math_subarea_id' in data:
            question.math_subarea_id = data['math_subarea_id'] if data['math_subarea_id'] else None
        if data.get('title'):
            question.title = data['title']
        if data.get('content'):
            question.content = data['content']
            # Regenerate LaTeX if content changed and no explicit latex provided
            if not data.get('content_latex'):
                question.content_latex = Question.text_to_latex(data['content'])
        if 'content_latex' in data and data.get('content_latex'):
            question.content_latex = data['content_latex']
        if 'answer' in data:
            question.answer = data['answer']
            if data.get('answer') and not data.get('answer_latex'):
                question.answer_latex = Question.text_to_latex(data['answer'])
        if 'answer_latex' in data and data.get('answer_latex'):
            question.answer_latex = data['answer_latex']
        if 'explanation' in data:
            question.explanation = data['explanation']
            if data.get('explanation') and not data.get('explanation_latex'):
                question.explanation_latex = Question.text_to_latex(data['explanation'])
        if 'explanation_latex' in data and data.get('explanation_latex'):
            question.explanation_latex = data['explanation_latex']
        if data.get('difficulty'):
            difficulty_map = {
                'facil': QuestionDifficulty.EASY,
                'medio': QuestionDifficulty.MEDIUM,
                'dificil': QuestionDifficulty.HARD,
                'especialista': QuestionDifficulty.EXPERT,
            }
            if data['difficulty'] in difficulty_map:
                question.difficulty = difficulty_map[data['difficulty']]
        if data.get('tags') is not None:
            question.tags = data['tags']
        if data.get('active') is not None:
            question.active = data['active']

        question.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return Result.success(
            value=QuestionService._serialize_question(question),
            message="Questao atualizada com sucesso"
        )

    @staticmethod
    def delete(question_id: str, admin_id: str) -> Result[None]:
        """
        Delete a question.

        Args:
            question_id: ID of the question
            admin_id: ID of the admin

        Returns:
            Result indicating success or failure
        """
        stmt = select(Question).where(Question.id == question_id)
        result = db.session.execute(stmt)
        question = result.scalar_one_or_none()

        if not question:
            return Result.fail(
                message="Questao nao encontrada",
                code="NOT_FOUND"
            )

        db.session.delete(question)
        db.session.commit()

        return Result.success(
            value=None,
            message="Questao removida com sucesso"
        )

    @staticmethod
    def convert_to_latex(text: str) -> Result[str]:
        """
        Convert plain text to LaTeX.

        Args:
            text: Plain text to convert

        Returns:
            Result containing LaTeX text
        """
        latex_text = Question.text_to_latex(text)
        return Result.success(value=latex_text)
