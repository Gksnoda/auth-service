export interface LoginCredentials {
  email: string;
}

export interface LoginResponse {
  message: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  name: string | null;
}

export interface RegisterResponse {
  message: string;
}
