export type TrainingGroup = {
  group_id: number;
  group_name: string;
  place: string;
  days: string;
  schedule: string;
  registered_count: number;
  capacity: number;
  available: number;
  is_full: boolean;
};

export type RegistrationPayload = {
  first_name: string;
  second_name?: string | null;
  first_last_name: string;
  second_last_name?: string | null;
  document_number: string;
  phone: string;
  group_id: number;
  interested_courses: string[];
};

export type Registration = RegistrationPayload & {
  id: number;
  group_name: string;
  place: string;
  days: string;
  schedule: string;
  created_at: string;
  updated_at: string;
};

export type RegistrationFilters = {
  group_id?: string;
  place?: string;
  date?: string;
  name?: string;
  document?: string;
  capacity_status?: string;
};
