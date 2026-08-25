import apiClient from "./client";


/* ============================================================
   TYPES
   ============================================================ */

export interface Dataset {
  id: number;
  name: string;
  description: string | null;
  project_id: number;
  storage_path: string;
  dataset_version: string;
  total_images: number;
  total_annotations: number;
  annotated_images?: number;
  total_classes?: number;
  status: "ACTIVE" | "ARCHIVED" | "DELETED";
  created_at: string;
  updated_at: string;
  last_updated?: string | null;
}

export interface DatasetInput {
  name: string;
  description?: string | null;
  storage_path: string;
  dataset_version: string;
}

export interface DatasetStatistics {
  dataset_id?: number;
  total_images?: number;
  annotated_images?: number;
  total_annotations?: number;
  total_classes?: number;
  last_updated?: string | null;
  image_count?: number;
  annotated_image_count?: number;
  annotation_count?: number;
  class_count?: number;

  // Allow backend naming variations without
  // breaking the frontend.
  images?: number;
  annotated?: number;
  annotations?: number;
  classes?: number;

  [key: string]: unknown;
}


export interface DatasetImageUploadResult {
  filename?: string;
  name?: string;
  status?: string;
  message?: string;

  [key: string]: unknown;
}


/* ============================================================
   GET DATASET STATISTICS
   ============================================================ */

/*
 * IMPORTANT:
 *
 * Swagger exposes this endpoint as:
 *
 * GET /{dataset_id}/statistics
 *
 * NOT:
 *
 * GET /datasets/{dataset_id}/statistics
 */

export async function getDatasetStatistics(
  datasetId: number
): Promise<DatasetStatistics> {

  const response =
    await apiClient.get<DatasetStatistics>(
      `/${datasetId}/statistics`
    );

  return response.data;
}


/* ============================================================
   LIST DATASET IMAGES
   ============================================================ */

export async function listDatasetImages(
  datasetId: number
): Promise<string[]> {

  const response =
    await apiClient.get<
      string[] | {
        images?: string[];
      }
    >(
      `/datasets/${datasetId}/images`
    );


  /*
   * Backend may return either:
   *
   * [
   *   "image1.jpg",
   *   "image2.jpg"
   * ]
   *
   * or:
   *
   * {
   *   images: [...]
   * }
   */

  if (
    Array.isArray(response.data)
  ) {
    return response.data;
  }


  if (
    response.data &&
    Array.isArray(
      response.data.images
    )
  ) {
    return response.data.images;
  }


  return [];
}


/* ============================================================
   UPLOAD DATASET IMAGE
   ============================================================ */

/*
 * Swagger:
 *
 * POST /datasets/{dataset_id}/images
 *
 * This endpoint is "Upload Image", singular.
 *
 * Therefore we upload files individually rather than
 * assuming a multi-file "files" field.
 */

export async function uploadDatasetImages(
  datasetId: number,
  files: File[],
  onProgress?: (
    percentage: number
  ) => void
): Promise<
  DatasetImageUploadResult[]
> {

  const results:
    DatasetImageUploadResult[] = [];


  for (
    let index = 0;
    index < files.length;
    index++
  ) {

    const file =
      files[index];


    const formData =
      new FormData();


    /*
     * IMPORTANT:
     *
     * The backend upload endpoint is singular:
     * "Upload Image"
     *
     * The FastAPI parameter is expected to be
     * a single uploaded file.
     */

    formData.append(
      "file",
      file
    );


    const response =
      await apiClient.post<
        DatasetImageUploadResult
      >(
        `/datasets/${datasetId}/images`,
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },

          onUploadProgress:
            (event) => {

              if (
                !onProgress ||
                !event.total
              ) {
                return;
              }


              /*
               * Progress across the entire
               * batch rather than just the
               * current file.
               */

              const currentFileProgress =
                event.loaded /
                event.total;


              const completedFiles =
                index;


              const totalProgress =
                (
                  (
                    completedFiles +
                    currentFileProgress
                  ) /
                  files.length
                ) *
                100;


              onProgress(
                Math.round(
                  totalProgress
                )
              );
            },
        }
      );


    results.push(
      response.data
    );
  }


  if (onProgress) {
    onProgress(100);
  }


  return results;
}


/* ============================================================
   GET SINGLE DATASET IMAGE
   ============================================================ */

export async function getDatasetImage(
  datasetId: number,
  imageName: string
): Promise<Blob> {

  const response =
    await apiClient.get(
      `/datasets/${datasetId}/images/${encodeURIComponent(
        imageName
      )}`,
      {
        responseType:
          "blob",
      }
    );


  return response.data;
}


export async function getProjectDatasets(
  projectId: number
): Promise<Dataset[]> {
  const response = await apiClient.get<Dataset[]>(
    `/projects/${projectId}/datasets`
  );

  return response.data;
}


export async function createDataset(
  projectId: number,
  data: DatasetInput
): Promise<Dataset> {
  const response = await apiClient.post<Dataset>(
    `/projects/${projectId}/datasets`,
    data
  );

  return response.data;
}


export async function updateDataset(
  datasetId: number,
  data: Partial<DatasetInput>
): Promise<Dataset> {
  const response = await apiClient.put<Dataset>(
    `/datasets/${datasetId}`,
    data
  );

  return response.data;
}


export async function deleteDataset(
  datasetId: number
): Promise<void> {
  await apiClient.delete(`/datasets/${datasetId}`);
}