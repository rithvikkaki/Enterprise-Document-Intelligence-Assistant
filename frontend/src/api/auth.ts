import { api } from '../lib/axios';
import { User, TokenResponse } from '../types';

export const authApi = {
  login: async (credentials: { email: string; password: string }): Promise<TokenResponse> => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },

  register: async (data: { email: string; password: string; full_name: string }): Promise<User> => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};
