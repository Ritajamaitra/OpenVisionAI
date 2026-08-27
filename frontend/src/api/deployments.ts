import apiClient from "./client";

export type DeploymentRecord = {
  model_id: number;
  model_name: string;
  model_version: string;
  dataset_name: string | null;
  endpoint_name: string;
  deployment_name: string;
  deployment_status: string;
  endpoint_status: string;
  endpoint_url: string | null;
  instance_type: string | null;
  instance_count: number | null;
  azure_model_reference: string;
  created_at: string | null;
};

export type DeploymentOptions = {
  endpoint_name?: string;
  deployment_name?: string;
  instance_type?: string;
  instance_count?: number;
};

export async function listDeployments(): Promise<
  DeploymentRecord[]
> {
  const response =
    await apiClient.get<DeploymentRecord[]>(
      "/deployments/management"
    );

  return response.data;
}

export async function deployModel(
  modelId: number,
  options: DeploymentOptions = {}
): Promise<DeploymentRecord> {
  const response =
    await apiClient.post<DeploymentRecord>(
      `/deployments/models/${modelId}`,
      options
    );

  return response.data;
}

export async function stopDeployment(
  endpointName: string
): Promise<void> {
  await apiClient.delete(
    `/deployments/${encodeURIComponent(endpointName)}`
  );
}
