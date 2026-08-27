import apiClient from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  full_name: string;
  password: string;
}

export interface ResetCaptchaResponse {
  message: string;
  captcha: string;
  expires_in_seconds: number;
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

export const register = async (
  request: RegisterRequest
): Promise<void> => {
  await apiClient.post("/auth/register", request);
};

export const generateResetCaptcha = async (
  email: string
): Promise<ResetCaptchaResponse> => {
  const response = await apiClient.post<ResetCaptchaResponse>(
    "/auth/forgot-password/captcha",
    null,
    {
      params: { email },
    }
  );

  return response.data;
};

export const resetPassword = async (
  email: string,
  captcha: string,
  newPassword: string
): Promise<void> => {
  await apiClient.post(
    "/auth/forgot-password/reset",
    null,
    {
      params: {
        email,
        captcha,
        new_password: newPassword,
      },
    }
  );
};
