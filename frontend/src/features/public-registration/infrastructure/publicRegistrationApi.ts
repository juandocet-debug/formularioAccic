import { apiRequest } from "../../../shared/infrastructure/apiClient";
import type { Registration, RegistrationPayload, TrainingGroup } from "../../../shared/domain/types";

export function fetchPublicGroups() {
  return apiRequest<TrainingGroup[]>("/public/groups");
}

export function createPublicRegistration(payload: RegistrationPayload) {
  return apiRequest<Registration>("/public/registrations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
