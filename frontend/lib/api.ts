import axios, { AxiosError } from "axios";
import type {
  Application,
  AuthResponse,
  CreditBalance,
  CreditPack,
  Job,
  JobMatch,
  KanbanBoard,
  Resume,
  User,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "pathai_token";

export const api = axios.create({ baseURL: `${API_URL}/api` });

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err: AxiosError) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY);
    }
    return Promise.reject(err);
  },
);

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export const auth = {
  register: (payload: { email: string; password: string; full_name?: string; phone?: string }) =>
    api.post<AuthResponse>("/auth/register", payload).then((r) => r.data),
  login: (payload: { email: string; password: string }) =>
    api.post<AuthResponse>("/auth/login", payload).then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};

export const users = {
  update: (payload: { target_roles?: string; preferred_locations?: string; min_salary_lpa?: number }) =>
    api.patch<User>("/users/me", payload).then((r) => r.data),
};

export const resumeApi = {
  upload: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api
      .post<{ resume: Resume; skills: string[]; readiness_score: number; career_dna: Record<string, unknown> }>(
        "/resume/upload",
        fd,
        { headers: { "Content-Type": "multipart/form-data" } },
      )
      .then((r) => r.data);
  },
  get: () => api.get<Resume | null>("/resume").then((r) => r.data),
  versions: () => api.get<Resume[]>("/resume/versions").then((r) => r.data),
  tailor: (jobId: string) =>
    api.post<Resume>("/resume/tailor", { job_id: jobId }).then((r) => r.data),
};

export const jobsApi = {
  list: (limit = 30) => api.get<Job[]>(`/jobs?limit=${limit}`).then((r) => r.data),
  matches: (params: { minScore?: number; includeDismissed?: boolean } = {}) =>
    api
      .get<JobMatch[]>("/jobs/matches", {
        params: { min_score: params.minScore ?? 0, include_dismissed: params.includeDismissed ?? false },
      })
      .then((r) => r.data),
  get: (id: string) => api.get<Job>(`/jobs/${id}`).then((r) => r.data),
  save: (id: string) => api.post<JobMatch>(`/jobs/${id}/save`).then((r) => r.data),
  dismiss: (id: string) => api.post<JobMatch>(`/jobs/${id}/dismiss`).then((r) => r.data),
};

export const applicationsApi = {
  list: () => api.get<Application[]>("/applications").then((r) => r.data),
  kanban: () => api.get<KanbanBoard>("/applications/kanban").then((r) => r.data),
  create: (payload: { job_id: string; cover_letter?: string; notes?: string }) =>
    api.post<Application>("/applications", payload).then((r) => r.data),
  updateStatus: (id: string, status: string) =>
    api.patch<Application>(`/applications/${id}/status`, { status }).then((r) => r.data),
  updateNotes: (id: string, notes: string) =>
    api.patch<Application>(`/applications/${id}/notes`, { notes }).then((r) => r.data),
};

export const creditsApi = {
  balance: () => api.get<CreditBalance>("/credits/balance").then((r) => r.data),
  packs: () => api.get<CreditPack[]>("/credits/packs").then((r) => r.data),
  costs: () => api.get<Record<string, number>>("/credits/costs").then((r) => r.data),
  ledger: () => api.get("/credits/ledger").then((r) => r.data),
  purchase: (packId: string) =>
    api.post<CreditBalance>("/credits/purchase", { pack_id: packId }).then((r) => r.data),
};
