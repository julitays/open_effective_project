export interface ProjectPassport {
  project_code: string;
  external_project_id: string;
  direction: string | null;
  project_scale: string | null;
  known_regions: string | null;
  primary_operational_model: string | null;
  additional_operational_contours: string | null;
  lifecycle_stage: string | null;
  project_status: string;
  start_date: string | null;
  short_description: string | null;
  updated_at: string;
}

export interface LprImportanceFactor {
  factor_type: string;
  factor_text: string;
  criticality: string | null;
  source_type: string | null;
  source_text: string | null;
  evidence_quote: string | null;
  period_or_source: string | null;
  confidence_level: string | null;
}

export interface LprProfile {
  lpr_code: string;
  external_lpr_id: string | null;
  role: string;
  role_zone: string;
  influence_level: string | null;
  activity_status: string | null;
  relationship_status: string | null;
  evidence_basis: string | null;
  manual_comment: string | null;
  importance_factors: LprImportanceFactor[];
}

export interface Barrier {
  barrier_id: string | null;
  barrier_code: string | null;
  barrier_title: string;
  barrier_type: string;
  time_status: string;
  criticality: string;
  status: string;
  description: string | null;
  relevance_status: string | null;
  confidence_level: string | null;
  linked_kpi_text: string | null;
  related_lpr_code: string | null;
  external_lpr_id: string | null;
  related_importance_text: string | null;
  source_type: string | null;
  source_id: string | null;
  source_text: string | null;
  evidence_quote: string | null;
  first_seen_period: string | null;
  last_seen_period: string | null;
}

export interface Expectation {
  expectation_id: string | null;
  expectation_code: string | null;
  expectation_text: string;
  expectation_type: string;
  explicitness: string;
  criticality: string;
  relevance_status: string | null;
  confidence_level: string | null;
  linked_kpi_text: string | null;
  related_lpr_code: string | null;
  external_lpr_id: string | null;
  related_importance_text: string | null;
  source: string | null;
  source_text: string | null;
  evidence_quote: string | null;
}

export interface Kpi {
  kpi_id: string;
  kpi_code: string;
  kpi_name: string;
  metric_name: string;
  kpi_type: string | null;
  source_text: string | null;
  relevance_status: string | null;
  related_expectation_text: string | null;
  related_barrier_text: string | null;
  client_criticality: string | null;
  comment: string | null;
  requires_confirmation: string | null;
  target_value: string | null;
  current_value: string | null;
  unit: string | null;
  status: string;
}

export interface CommunicationPoint {
  communication_id: string | null;
  communication_code: string | null;
  client_side: string | null;
  external_lpr_id: string | null;
  open_side_role: string | null;
  topic_type: string | null;
  topic_text: string | null;
  channel: string;
  channel_type: string;
  channel_text: string | null;
  frequency: string | null;
  criticality: string | null;
  source_text: string | null;
  relevance_status: string | null;
  comment: string | null;
  summary: string;
  outcome: string | null;
  cjm_stage: string | null;
}

export interface Goal {
  goal_id: string | null;
  goal_code: string | null;
  goal_owner: string | null;
  goal_contour: string | null;
  goal_text: string;
  goal_type: string | null;
  priority: string | null;
  related_kpi_or_criterion_text: string | null;
  source_text: string | null;
  relevance_status: string | null;
  comment: string | null;
  success_criteria: string | null;
  status: string;
}

export interface ProjectCjm {
  project: ProjectPassport;
  goals: Goal[];
  lprs: LprProfile[];
  barriers: Barrier[];
  expectations: Expectation[];
  kpis: Kpi[];
  communications: CommunicationPoint[];
}

export interface ProjectContextBlock {
  section_key: string;
  block_code: string;
  block_type: string | null;
  title: string | null;
  content: Record<string, unknown>;
  display_order: number;
  updated_at: string;
}

export interface ProjectEffectiveness {
  cjm: ProjectCjm;
  context_blocks: ProjectContextBlock[];
}
