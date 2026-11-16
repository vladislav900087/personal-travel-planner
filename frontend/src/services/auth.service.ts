import { api } from "@/lib/api";
import { AuthTokens, LoginPayload, RegisterPayload, User } from "@/types/auth";

// api calls for authentication
export const authService = {
  async register(payload: RegisterPayload): Promise<User> {
    const { data } = await api.post<User>("/auth/register", payload);
    return data;
  },

  async login(payload: LoginPayload): Promise<AuthTokens> {
    const { data } = await api.post<AuthTokens>("/auth/login", payload);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data;
  },

  async logout(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        await api.post("/auth/logout", { refresh_token: refreshToken });
      }
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  async getMe(): Promise<User> {
    const { data } = await api.get<User>("/auth/me");
    return data;
  },
};
