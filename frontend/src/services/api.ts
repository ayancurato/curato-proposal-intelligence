/**
 * Curato Proposal Intelligence -- API Service Layer
 *
 * Centralized API client for all backend communication.
 * The frontend should never need to perform business logic.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ── Types ────────────────────────────────────────────────────────────

export interface UploadResponse {
  id: string;
  status: string;
  status_message: string | null;
  proposal_count: number;
  proposals: ProposalSummary[];
  created_at: string;
  updated_at: string;
}

export interface ProposalSummary {
  id: string;
  original_name: string;
  status: string;
  agency_name: string | null;
  total_cost: number | null;
  created_at: string;
}

export interface ContactInfo {
  name: string | null;
  email: string | null;
  phone: string | null;
  role: string | null;
}

export interface PricingItem {
  item: string;
  amount: number | null;
  description: string | null;
}

export interface Pricing {
  total_cost: number | null;
  currency: string;
  breakdown: PricingItem[];
  payment_terms: string | null;
  retainer_fee: number | null;
  setup_fee: number | null;
  pricing_model: string | null;
}

export interface Milestone {
  name: string;
  target_date: string | null;
  deliverables: string[];
}

export interface Timeline {
  start_date: string | null;
  end_date: string | null;
  duration: string | null;
  milestones: Milestone[];
}

export interface TeamMember {
  name: string | null;
  role: string;
  experience: string | null;
}

export interface Team {
  total_members: number | null;
  members: TeamMember[];
  structure: string | null;
}

export interface KPI {
  metric: string;
  target: string | null;
  measurement_method: string | null;
}

export interface Reporting {
  frequency: string | null;
  format: string | null;
  metrics_included: string[];
  tools: string[];
}

export interface Deliverable {
  name: string;
  description: string | null;
  timeline: string | null;
}

export interface ExtractedProposal {
  agency_name: string;
  contact_info: ContactInfo | null;
  executive_summary: string | null;
  pricing: Pricing;
  deliverables: Deliverable[];
  timeline: Timeline;
  team: Team;
  scope: string | null;
  kpis: KPI[];
  reporting: Reporting;
  ownership_terms: string | null;
  termination_clause: string | null;
  confidentiality_terms: string | null;
  additional_terms: string | null;
  unique_selling_points: string[];
  case_studies: string[];
}

export interface ProposalRead {
  id: string;
  filename: string;
  original_name: string;
  file_size: number;
  page_count: number | null;
  status: string;
  error_message: string | null;
  extracted_data: ExtractedProposal | null;
  session_id: string;
  created_at: string;
  updated_at: string;
}

export interface DimensionScore {
  dimension: string;
  scores: Record<string, number>;
  leader: string | null;
  analysis: string;
  key_differences: string[];
}

export interface PricingComparison {
  lowest_cost_agency: string | null;
  highest_cost_agency: string | null;
  price_range: string | null;
  best_value_agency: string | null;
  value_reasoning: string | null;
  pricing_breakdown: Record<string, number>;
}

export interface ComparisonResult {
  session_id: string;
  proposal_count: number;
  agency_names: string[];
  dimensions: DimensionScore[];
  pricing_comparison: PricingComparison;
  overall_summary: string;
  head_to_head: string[];
}

export interface Risk {
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  explanation: string;
  suggested_action: string;
  affected_section: string;
}

export interface ProposalRiskAnalysis {
  proposal_id: string;
  agency_name: string;
  risks: Risk[];
  risk_score: number;
  summary: string;
}

export interface RiskAnalysisResult {
  session_id: string;
  analyses: ProposalRiskAnalysis[];
  comparative_insights: string[];
}

export interface AgencyAssessment {
  agency_name: string;
  strengths: string[];
  weaknesses: string[];
  best_for: string | null;
  overall_score: number;
}

export interface TradeOff {
  description: string;
  agency_a: string;
  agency_b: string;
  consideration: string;
}

export interface QuestionToAsk {
  agency_name: string;
  question: string;
  why_it_matters: string;
}

export interface Recommendation {
  session_id: string;
  best_fit_agency: string;
  confidence_level: string;
  primary_reasoning: string;
  detailed_reasoning: string[];
  assessments: AgencyAssessment[];
  trade_offs: TradeOff[];
  questions_to_ask: QuestionToAsk[];
  choose_agency_a_if: string | null;
  choose_agency_b_if: string | null;
  executive_summary: string;
}

export interface QuickStats {
  total_proposals: number;
  price_range_min: number | null;
  price_range_max: number | null;
  avg_timeline_days: number | null;
  total_risks: number;
  critical_risks: number;
  high_risks: number;
  recommended_agency: string | null;
  confidence_level: string | null;
}

export interface DashboardResponse {
  session_id: string;
  status: string;
  status_message: string | null;
  proposals: ProposalRead[];
  proposal_count: number;
  comparison: ComparisonResult | null;
  risk_analysis: RiskAnalysisResult | null;
  recommendation: Recommendation | null;
  quick_stats: QuickStats | null;
}

// ── API Functions ────────────────────────────────────────────────────

export async function uploadProposals(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));

  const res = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(error.detail || 'Upload failed');
  }

  return res.json();
}

export async function startAnalysis(sessionId: string): Promise<UploadResponse> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${sessionId}/start`, {
    method: 'POST',
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to start analysis' }));
    throw new Error(error.detail || 'Failed to start analysis');
  }

  return res.json();
}

export async function getAnalysis(sessionId: string): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${sessionId}`);

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to get analysis' }));
    throw new Error(error.detail || 'Failed to get analysis');
  }

  return res.json();
}

export async function getSessionStatus(sessionId: string): Promise<UploadResponse> {
  const res = await fetch(`${API_BASE_URL}/api/analysis/${sessionId}/status`);

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to get status' }));
    throw new Error(error.detail || 'Failed to get status');
  }

  return res.json();
}
