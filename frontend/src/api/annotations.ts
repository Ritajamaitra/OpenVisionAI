import apiClient from "./client";

/* ============================================================
   TYPES
   ============================================================ */

export type AnnotationStatus =
  | "AUTO_GENERATED"
  | "APPROVED"
  | "REJECTED";

export interface Annotation {
  id: number;

  dataset_id: number;

  image_name: string;

  label: string;

  confidence: number;

  bbox_x: number;
  bbox_y: number;
  bbox_width: number;
  bbox_height: number;

  status: AnnotationStatus;

  reviewed_at?: string | null;
  reviewed_by?: number | null;
}

export interface AnnotationListResponse {
  annotations: Annotation[];
  total: number;
}

export interface AutoAnnotationRequest {
  model: string;
  prompt: string;
  confidence: number;
}

export interface AutoAnnotationResponse {
  image_name: string;
  model: string;
  detections: number;
  classes: string[];
  annotation_uri?: string | null;
  processing_time_ms: number;
}


/* ============================================================
   HELPERS
   ============================================================ */

function getErrorMessage(
  error: unknown,
  fallback: string
): string {
  const axiosError = error as any;

  return (
    axiosError?.response?.data?.detail ??
    axiosError?.response?.data?.message ??
    axiosError?.message ??
    fallback
  );
}


/* ============================================================
   DATASET IMAGES
   ============================================================ */

export async function listDatasetImages(
  datasetId: number
): Promise<string[]> {
  try {
    const response =
      await apiClient.get<string[]>(
        `/datasets/${datasetId}/images`
      );

    return Array.isArray(response.data)
      ? response.data
      : [];
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Could not load dataset images."
      )
    );
  }
}


/* ============================================================
   SINGLE IMAGE
   ============================================================ */

export async function getDatasetImage(
  datasetId: number,
  imageName: string
): Promise<Blob> {
  try {
    const response =
      await apiClient.get<Blob>(
        `/datasets/${datasetId}/images/${encodeURIComponent(
          imageName
        )}`,
        {
          responseType: "blob",
        }
      );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        `Could not load image "${imageName}".`
      )
    );
  }
}


/* ============================================================
   IMAGE ANNOTATIONS
   ============================================================ */

export async function getImageAnnotations(
  datasetId: number,
  imageName: string
): Promise<AnnotationListResponse> {
  try {
    const response =
      await apiClient.get<
        AnnotationListResponse | Annotation[]
      >(
        `/datasets/${datasetId}/images/${encodeURIComponent(
          imageName
        )}/annotations`
      );

    /*
     * Support both possible backend shapes:
     *
     * {
     *   annotations: [...],
     *   total: 4
     * }
     *
     * OR
     *
     * [...]
     */

    if (Array.isArray(response.data)) {
      return {
        annotations: response.data,
        total: response.data.length,
      };
    }

    return {
      annotations:
        response.data?.annotations ?? [],
      total:
        response.data?.total ??
        response.data?.annotations?.length ??
        0,
    };
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Could not load image annotations."
      )
    );
  }
}


/* ============================================================
   AUTO ANNOTATION
   ============================================================ */

export async function autoAnnotateImage(
  datasetId: number,
  imageName: string,
  request: AutoAnnotationRequest
): Promise<AutoAnnotationResponse> {
  try {
    const response =
      await apiClient.post<AutoAnnotationResponse>(
        `/datasets/${datasetId}/images/${encodeURIComponent(
          imageName
        )}/annotate`,
        request
      );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Auto-annotation failed."
      )
    );
  }
}


/* ============================================================
   REVIEW ANNOTATION
   ============================================================ */

export async function reviewAnnotation(
  annotationId: number,
  status: AnnotationStatus
): Promise<Annotation> {
  try {
    const response =
      await apiClient.put<Annotation>(
        `/annotations/${annotationId}/review`,
        {
          status,
        }
      );

    return response.data;
  } catch (error) {
    throw new Error(
      getErrorMessage(
        error,
        "Could not update annotation status."
      )
    );
  }
}