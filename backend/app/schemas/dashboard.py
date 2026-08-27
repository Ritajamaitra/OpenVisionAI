from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    projects: int
    datasets: int
    models: int
    inference_runs: int