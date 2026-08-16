from sqlalchemy.orm import Session

from app.models.inference_runs import InferenceRun
from app.repositories.base_repository import BaseRepository


class InferenceRunRepository(BaseRepository[InferenceRun]):

    def __init__(self):
        super().__init__(InferenceRun)

    def find_by_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[InferenceRun]:

        return (
            db.query(InferenceRun)
            .filter(
                InferenceRun.user_id == user_id
            )
            .order_by(
                InferenceRun.created_at.desc()
            )
            .all()
        )

    def find_by_model(
        self,
        db: Session,
        model_registry_id: int,
    ) -> list[InferenceRun]:

        return (
            db.query(InferenceRun)
            .filter(
                InferenceRun.model_registry_id
                == model_registry_id
            )
            .order_by(
                InferenceRun.created_at.desc()
            )
            .all()
        )