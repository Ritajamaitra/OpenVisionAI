import apiClient from "./client";

export interface DashboardStats {
  projects: number;
  datasets: number;
  models: number;
  inference_runs: number;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const response = await apiClient.get<DashboardStats>(
    "/dashboard/stats"
  );

  return response.data;
}