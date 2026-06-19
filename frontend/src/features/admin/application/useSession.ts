import { useState } from "react";
import { login } from "../infrastructure/adminApi";

const TOKEN_KEY = "formulario_asic_admin_token";

export function useSession() {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [error, setError] = useState<string | null>(null);

  async function signIn(username: string, password: string) {
    setError(null);
    try {
      const response = await login(username, password);
      sessionStorage.setItem(TOKEN_KEY, response.access_token);
      setToken(response.access_token);
      return true;
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "No fue posible iniciar sesion.");
      return false;
    }
  }

  function signOut() {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
  }

  return { token, error, signIn, signOut };
}
