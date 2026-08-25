import apiClient from "./client";

export interface Project {
  id: number;
  name: string;
  description: string | null;
  owner_id: number;
  status: "ACTIVE" | "ARCHIVED" | "DELETED";
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string | null;
}

export interface ProjectUpdate {
  name?: string;
  description?: string | null;
}

export const getProjects = async (): Promise<Project[]> => {
  const response = await apiClient.get<Project[]>("/projects");
  return response.data;
};

export const getProject = async (
  projectId: number
): Promise<Project> => {
  const response = await apiClient.get<Project>(
    `/projects/${projectId}`
  );

  return response.data;
};

export const createProject = async (
  data: ProjectCreate
): Promise<Project> => {
  const response = await apiClient.post<Project>(
    "/projects",
    data
  );

  return response.data;
};

export const updateProject = async (
  projectId: number,
  data: ProjectUpdate
): Promise<Project> => {
  const response = await apiClient.put<Project>(
    `/projects/${projectId}`,
    data
  );

  return response.data;
};

export const deleteProject = async (
  projectId: number
): Promise<void> => {
  await apiClient.delete(`/projects/${projectId}`);
};