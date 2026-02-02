"""Service for answers CRUD operations (admin)."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select

from app.extensions import db
from models import Answer, Question, Student
from models.enums import AnswerStatus
from utils.response import Result


class AnswerAdminService:
    """Service for managing answers (admin side)."""

    @staticmethod
    def _serialize_answer(answer: Answer) -> dict:
        """Serialize an answer to dictionary."""
        return {
            'id': str(answer.id),
            'student_id': str(answer.student_id),
            'student_name': answer.student.name if answer.student else None,
            'student_email': answer.student.email if answer.student else None,
            'question_id': str(answer.question_id),
            'question_title': answer.question.title if answer.question else None,
            'content': answer.content,
            'content_latex': answer.content_latex,
            'status': answer.status.value if answer.status else None,
            'is_correct': answer.is_correct,
            'feedback': answer.feedback,
            'score': answer.score,
            'reviewed_by': str(answer.reviewed_by) if answer.reviewed_by else None,
            'reviewed_at': answer.reviewed_at.isoformat() if answer.reviewed_at else None,
            'created_at': answer.created_at.isoformat() if answer.created_at else None,
            'updated_at': answer.updated_at.isoformat() if answer.updated_at else None,
        }

    @staticmethod
    def list(
        admin_id: str,
        question_id: Optional[str] = None,
        student_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Result[list]:
        """
        List answers with optional filters.

        Args:
            admin_id: ID of the admin
            question_id: Filter by question
            student_id: Filter by student
            status: Filter by status

        Returns:
            Result containing list of answers
        """
        stmt = select(Answer)

        if question_id:
            stmt = stmt.where(Answer.question_id == question_id)

        if student_id:
            stmt = stmt.where(Answer.student_id == student_id)

        if status:
            status_map = {
                'pendente': AnswerStatus.PENDING,
                'aprovado': AnswerStatus.APPROVED,
                'rejeitado': AnswerStatus.REJECTED,
            }
            if status in status_map:
                stmt = stmt.where(Answer.status == status_map[status])

        stmt = stmt.order_by(Answer.created_at.desc())

        result = db.session.execute(stmt)
        answers = result.scalars().all()

        return Result.success(
            value=[AnswerAdminService._serialize_answer(a) for a in answers]
        )

    @staticmethod
    def get(answer_id: str, admin_id: str) -> Result[dict]:
        """
        Get an answer by ID.

        Args:
            answer_id: ID of the answer
            admin_id: ID of the admin

        Returns:
            Result containing answer data
        """
        stmt = select(Answer).where(Answer.id == answer_id)
        result = db.session.execute(stmt)
        answer = result.scalar_one_or_none()

        if not answer:
            return Result.fail(
                message="Resposta nao encontrada",
                code="NOT_FOUND"
            )

        return Result.success(
            value=AnswerAdminService._serialize_answer(answer)
        )

    @staticmethod
    def review(answer_id: str, data: dict, admin_id: str) -> Result[dict]:
        """
        Review an answer (approve/reject).

        Args:
            answer_id: ID of the answer
            data: Review data (status, is_correct, feedback, score)
            admin_id: ID of the admin reviewing

        Returns:
            Result containing updated answer data
        """
        stmt = select(Answer).where(Answer.id == answer_id)
        result = db.session.execute(stmt)
        answer = result.scalar_one_or_none()

        if not answer:
            return Result.fail(
                message="Resposta nao encontrada",
                code="NOT_FOUND"
            )

        # Update status
        status_map = {
            'aprovado': AnswerStatus.APPROVED,
            'rejeitado': AnswerStatus.REJECTED,
        }
        if data.get('status') in status_map:
            answer.status = status_map[data['status']]

        # Update review fields
        if data.get('is_correct') is not None:
            answer.is_correct = data['is_correct']
        if 'feedback' in data:
            answer.feedback = data['feedback']
        if data.get('score') is not None:
            answer.score = data['score']

        answer.reviewed_by = admin_id
        answer.reviewed_at = datetime.now(timezone.utc)
        answer.updated_at = datetime.now(timezone.utc)

        db.session.commit()

        return Result.success(
            value=AnswerAdminService._serialize_answer(answer),
            message="Resposta avaliada com sucesso"
        )

    @staticmethod
    def delete(answer_id: str, admin_id: str) -> Result[None]:
        """
        Delete an answer.

        Args:
            answer_id: ID of the answer
            admin_id: ID of the admin

        Returns:
            Result indicating success or failure
        """
        stmt = select(Answer).where(Answer.id == answer_id)
        result = db.session.execute(stmt)
        answer = result.scalar_one_or_none()

        if not answer:
            return Result.fail(
                message="Resposta nao encontrada",
                code="NOT_FOUND"
            )

        db.session.delete(answer)
        db.session.commit()

        return Result.success(
            value=None,
            message="Resposta removida com sucesso"
        )

    @staticmethod
    def get_question_answers_stats(question_id: str) -> Result[dict]:
        """Get statistics for answers to a question."""
        stmt = select(Answer).where(Answer.question_id == question_id)
        result = db.session.execute(stmt)
        answers = result.scalars().all()

        total = len(answers)
        pending = sum(1 for a in answers if a.status == AnswerStatus.PENDING)
        approved = sum(1 for a in answers if a.status == AnswerStatus.APPROVED)
        rejected = sum(1 for a in answers if a.status == AnswerStatus.REJECTED)
        correct = sum(1 for a in answers if a.is_correct is True)

        return Result.success(value={
            'total': total,
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'correct': correct,
        })
