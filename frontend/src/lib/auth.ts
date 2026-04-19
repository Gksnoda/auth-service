import { apiClient } from './apiClient';
import type {
  LoginCredentials,
  LoginResponse,
  RegisterPayload,
  RegisterResponse,
} from '../types/auth';

export function login(credentials: LoginCredentials): Promise<LoginResponse> {
  return apiClient.post<LoginResponse, LoginCredentials>('/auth/login', credentials);
}

export function register(payload: RegisterPayload): Promise<RegisterResponse> {
  return apiClient.post<RegisterResponse, RegisterPayload>('/auth/register', payload);
}
