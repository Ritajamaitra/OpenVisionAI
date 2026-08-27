import apiClient from "./client";

export interface TrainingRunSummary {
  azure_run_id: string;
  project_id: number;
  experiment_name?: string | null;
  model_name?: string | null;
  status: string;

  precision?: number | null;
  recall?: number | null;
  map50?: number | null;
  map50_95?: number | null;

  training_time?: number | null;
  started_at?: string | null;
}

export interface TrainingRun {
  id: number;

  project_id: number;
  dataset_id: number;
  submitted_by: number;

  azure_run_id: string;

  experiment_name?: string | null;
  model_name?: string | null;

  status: string;

  precision?: number | null;
  recall?: number | null;
  map50?: number | null;
  map50_95?: number | null;

  training_time?: number | null;

  registered_model_name?: string | null;
  registered_model_version?: string | null;

  endpoint_name?: string | null;

  started_at?: string | null;
  completed_at?: string | null;

  created_at: string;
  updated_at: string;
}

export interface TrainingJobRequest {
  project_id: number;
  dataset_id: number;
  model_name: string;
  epochs: number;
  imgsz: number;
  batch: number;
}

export async function listTrainingRuns(): Promise<
  TrainingRunSummary[]
> {
  const response = await apiClient.get("/training/jobs");
  return response.data;
}

export async function listProjectTrainingRuns(
  projectId: number
): Promise<TrainingRunSummary[]> {
  const response = await apiClient.get(
    `/training/jobs/project/${projectId}`
  );

  return response.data;
}

export async function getTrainingRun(
  azureRunId: string
): Promise<TrainingRun> {
  const response = await apiClient.get(
    `/training/jobs/${encodeURIComponent(azureRunId)}`
  );

  return response.data;
}

export async function createTrainingJob(
  request: TrainingJobRequest
): Promise<TrainingRun> {
  const response = await apiClient.post(
    "/training/jobs",
    request
  );

  return response.data;
}

export async function syncTrainingRun(
  azureRunId: string
): Promise<TrainingRun> {
  const response = await apiClient.post(
    `/training/jobs/${encodeURIComponent(
      azureRunId
    )}/sync`
  );

  return response.data;
}

export async function cancelTrainingRun(
  azureRunId: string
): Promise<TrainingRun> {
  const response = await apiClient.post(
    `/training/jobs/${encodeURIComponent(
      azureRunId
    )}/cancel`
  );

  return response.data;
}

export async function deleteTrainingRun(
  azureRunId: string
): Promise<void> {
  await apiClient.delete(
    `/training/jobs/${encodeURIComponent(
      azureRunId
    )}`
  );
}