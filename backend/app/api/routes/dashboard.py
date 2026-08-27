from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse
from app.services.dashboard_services import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


dashboard_service = DashboardService()


@router.get(
    "/stats",
    response_model=DashboardStatsResponse,
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return aggregated platform statistics
    for the authenticated user.
    """

    return dashboard_service.get_statistics(
        db=db,
        current_user=current_user,
    )