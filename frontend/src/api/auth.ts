import apiClient from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export const login = async (
  credentials: LoginRequest
): Promise<LoginResponse> => {
  const formData = new URLSearchParams();

  formData.append("username", credentials.username);
  formData.append("password", credentials.password);

  const response = await apiClient.post<LoginResponse>(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
};