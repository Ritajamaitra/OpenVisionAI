import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { login as loginApi } from "../api/auth";
import type {
  AuthContextType,
  User,
} from "../types/auth";


interface ExtendedAuthContextType
  extends AuthContextType {
  authLoading: boolean;
}


const AuthContext =
  createContext<
    ExtendedAuthContextType | undefined
  >(undefined);


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {

  const [user, setUser] =
    useState<User | null>(null);

  const [authLoading, setAuthLoading] =
    useState(true);


  /* ==========================================================
     RESTORE AUTHENTICATION
     ========================================================== */

  useEffect(() => {

    try {

      const storedUser =
        localStorage.getItem("user");

      const token =
        localStorage.getItem(
          "access_token"
        );


      if (
        storedUser &&
        token
      ) {

        try {

          const parsedUser =
            JSON.parse(
              storedUser
            );

          setUser(
            parsedUser
          );

        } catch {

          localStorage.removeItem(
            "user"
          );

          localStorage.removeItem(
            "access_token"
          );

        }

      }

    } finally {

      setAuthLoading(false);

    }

  }, []);


  /* ==========================================================
     LOGIN
     ========================================================== */

  const login = async (
    username: string,
    password: string
  ) => {

    const response =
      await loginApi({
        username,
        password,
      });


    localStorage.setItem(
      "access_token",
      response.access_token
    );


    /*
     * Decode JWT payload for UI state.
     *
     * Backend remains authoritative
     * for authorization.
     */

    const payload =
      JSON.parse(
        atob(
          response.access_token
            .split(".")[1]
        )
      );


    const authenticatedUser: User = {

      id: Number(
        payload.sub
      ),

      username:
        payload.username,

      role:
        payload.role,

    };


    localStorage.setItem(
      "user",
      JSON.stringify(
        authenticatedUser
      )
    );


    setUser(
      authenticatedUser
    );

  };


  /* ==========================================================
     LOGOUT
     ========================================================== */

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    localStorage.removeItem(
      "user"
    );

    setUser(null);

  };


  /* ==========================================================
     PROVIDER
     ========================================================== */

  return (

    <AuthContext.Provider
      value={{

        user,

        isAuthenticated:
          !!user,

        authLoading,

        login,

        logout,

      }}
    >

      {children}

    </AuthContext.Provider>

  );

}


/* ============================================================
   HOOK
   ============================================================ */

export function useAuth() {

  const context =
    useContext(
      AuthContext
    );


  if (!context) {

    throw new Error(
      "useAuth must be used within AuthProvider"
    );

  }


  return context;

}