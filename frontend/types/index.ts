export interface User {
  id: string;
  email: string;
  full_name: string | null;
  phone: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  avatar_url: string | null;
  career_readiness_score: number;
  subscription_tier: "free" | "pro";
  subscription_expires_at: string | null;
  credits_balance: number;
  onboarded: boolean;
  target_roles: string | null;
  preferred_locations: string | null;
  min_salary_lpa: number | null;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  company_logo_url: string | null;
  location: string | null;
  job_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  description: string | null;
  requirements: string | null;
  apply_url: string | null;
  source: string | null;
  posted_at: string | null;
  ghost_score: number;
  company_health_score: number;
  is_fresh: boolean;
  tags: string[] | null;
}

export interface JobMatch {
  id: string;
  job: Job;
  match_score: number;
  matching_skills: string[] | null;
  missing_skills: string[] | null;
  match_reasons: string[] | null;
  concerns: string[] | null;
  is_dismissed: boolean;
  is_saved: boolean;
  created_at: string;
}

export type ApplicationStatus =
  | "applied"
  | "viewed"
  | "interviewing"
  | "offer"
  | "hired"
  | "rejected"
  | "ghosted";

export interface Application {
  id: string;
  user_id: string;
  job: Job;
  status: ApplicationStatus;
  applied_via: string;
  cover_letter: string | null;
  notes: string | null;
  follow_up_count: number;
  interview_date: string | null;
  offer_amount: number | null;
  created_at: string;
  updated_at: string;
}

export interface KanbanBoard {
  applied: Application[];
  viewed: Application[];
  interviewing: Application[];
  offer: Application[];
  hired: Application[];
  rejected: Application[];
  ghosted: Application[];
}

export interface Resume {
  id: string;
  user_id: string;
  file_url: string | null;
  file_name: string | null;
  parsed_json: {
    skills?: Array<{ name: string; proficiency?: string; years_experience?: number }>;
    experience?: Array<{
      company: string;
      title: string;
      location?: string;
      start?: string;
      end?: string;
      bullets?: string[];
    }>;
    education?: Array<{ institution: string; degree?: string; field?: string; year?: string }>;
    projects?: Array<{ name: string; description?: string; tech_stack?: string[] }>;
    summary?: string;
  } | null;
  career_dna: {
    top_strengths?: string[];
    keywords?: string[];
    seniority_level?: string;
    domains?: string[];
    persona?: string;
  } | null;
  is_primary: boolean;
  version: number;
  tailored_for_job_id: string | null;
  created_at: string;
}

export interface CreditBalance {
  balance: number;
  subscription_tier: string;
  can_use_free_tailor: boolean;
  can_use_free_cover_letter: boolean;
  can_use_free_mock: boolean;
  free_tailors_used_this_month: number;
  free_cover_letters_used_this_month: number;
  free_mocks_used_this_week: number;
}

export interface CreditPack {
  id: string;
  credits: number;
  price_inr: number;
  label: string;
  bonus_pct: number;
}
