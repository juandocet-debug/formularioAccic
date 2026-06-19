import { useEffect, useState } from "react";
import type { RegistrationPayload, TrainingGroup } from "../../../shared/domain/types";
import { createPublicRegistration, fetchPublicGroups } from "../infrastructure/publicRegistrationApi";

export function usePublicRegistration() {
  const [groups, setGroups] = useState<TrainingGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadGroups() {
    setLoading(true);
    setError(null);
    try {
      setGroups(await fetchPublicGroups());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "No fue posible cargar los grupos.");
    } finally {
      setLoading(false);
    }
  }

  async function submit(payload: RegistrationPayload) {
    setMessage(null);
    setError(null);
    try {
      await createPublicRegistration(payload);
      setMessage("Registro exitoso. Tu seleccion quedo guardada.");
      await loadGroups();
      return true;
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "No fue posible guardar el registro.");
      return false;
    }
  }

  useEffect(() => {
    void loadGroups();
  }, []);

  return { groups, loading, message, error, submit };
}
