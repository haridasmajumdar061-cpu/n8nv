import { create } from "zustand";

type AuthState = {
  token: string | null;
  setToken: (token: string | null) => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("ai_life_os_token"),
  setToken: (token) => {
    if (token) {
      localStorage.setItem("ai_life_os_token", token);
    } else {
      localStorage.removeItem("ai_life_os_token");
    }
    set({ token });
  }
}));
