export type UserRole = "candidate" | "recruiter" | "admin";

export interface UserOut {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface JobOut {
  id: string;
  title: string;
  description: string;
  responsibilities: string;
  location: string;
  employment_type: string;
  status: string;
  company_id: string;
  company_name: string | null;
  must_have_skills: string[];
  preferred_skills: string[];
}

export interface MatchBreakdown {
  skills_match: number;
  experience_relevance: number;
  project_relevance: number;
  assessment_readiness: number;
}

export interface MatchResult {
  job_id: string;
  candidate_id: string;
  overall_score: number;
  breakdown: MatchBreakdown;
  matched_skills: string[];
  missing_must_have: string[];
  missing_preferred: string[];
  explanation: string;
  disclaimer: string;
}

export interface GrowthPathStep {
  order: number;
  action: string;
  related_skill: string | null;
}

export interface GrowthPathOut {
  candidate_id: string;
  target_job_id: string;
  current_match: number;
  previous_match: number | null;
  strengths: string[];
  skills_to_improve: string[];
  steps: GrowthPathStep[];
  progress: number;
}

export interface CandidateDashboard {
  welcome_name: string;
  profile_completion: number;
  career_overview: {
    applications: number;
    interviews_scheduled: number;
    average_match_score: number;
  };
  applications: Array<{
    id: string;
    job_id: string;
    job_title: string;
    status: string;
    match_score: number;
  }>;
}

export interface ParsedResumeOut {
  id: string;
  file_name: string;
  parsed_status: string;
  detected_name: string | null;
  detected_skills: string[];
  detected_education: string[];
  detected_experience: string[];
}
