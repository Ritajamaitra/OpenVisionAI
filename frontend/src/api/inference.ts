import apiClient from "./client";

export type InferencePrediction = {
  bbox?: [number, number, number, number];
  label?: string;
  confidence?: number;
  class_id?: number;
  [key: string]: unknown;
};

export type InferenceResponse = {
  inference_id: number;
  model_id: number;
  model_name: string;
  model_version: string;
  predictions: InferencePrediction[];
};

export type InferenceRun = {
  id: number;
  model_id: number;
  model_name: string;
  model_version: string;
  status: string;
  confidence_threshold: number;
  prediction_count: number;
  predictions: InferencePrediction[];
  inference_latency_ms: number | null;
  input_filename: string | null;
  input_content_type: string | null;
  error_message: string | null;
  created_at: string;
};

export async function runInference(
  modelId: number,
  image: File,
  confidence: number
): Promise<InferenceResponse> {
  const formData = new FormData();

  formData.append("image", image, image.name);
  formData.append("confidence", String(confidence));

  const response = await apiClient.post<InferenceResponse>(
    `/models/${modelId}/infer`,
    formData
  );

  return response.data;
}

export async function listInferenceRuns(): Promise<InferenceRun[]> {
  const response = await apiClient.get<InferenceRun[]>("/inference/runs");
  return response.data;
}
