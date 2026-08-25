export interface User {
  id: number;
  username: string;
  role: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (
    username: string,
    password: string
  ) => Promise<void>;
  logout: () => void;
}