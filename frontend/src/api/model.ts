import apiClient from "./client";

export type ModelManagementRecord = {
  id: number;
  name: string;
  version: string;
  dataset_id: number;
  dataset_name: string;
  training_run_id: string | null;
  precision: number | null;
  recall: number | null;
  map50: number | null;
  map50_95: number | null;
  training_time: number | null;
  azure_model_reference: string;
  artifact_uri: string | null;
  status: string;
  created_at: string;
};

export async function listManagedModels(): Promise<ModelManagementRecord[]> {
  const response = await apiClient.get<ModelManagementRecord[]>(
    "/models/management"
  );

  return response.data;
}


export async function registerTrainingModel(
  azureRunId: string
): Promise<void> {
  await apiClient.post(
    `/training/jobs/${encodeURIComponent(
      azureRunId
    )}/register-model`
  );
}
