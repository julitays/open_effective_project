import { apiGet, apiPatch, apiPost } from "./client";
import type {
  Barrier,
  CommunicationPoint,
  Expectation,
  Goal,
  Kpi,
  LprProfile,
  ProjectCjm,
  ProjectContextBlock,
  ProjectEffectiveness,
  ProjectPassport,
} from "../types/cjm";

export function getProjects(signal?: AbortSignal) {
  return apiGet<ProjectPassport[]>("/projects", signal);
}

export function getProjectCjm(projectCode: string, signal?: AbortSignal) {
  return apiGet<ProjectCjm>(`/projects/${encodeURIComponent(projectCode)}/cjm`, signal);
}

export function getProjectEffectiveness(projectCode: string, signal?: AbortSignal) {
  return apiGet<ProjectEffectiveness>(
    `/projects/${encodeURIComponent(projectCode)}/effectiveness`,
    signal,
  );
}

export type PatchPayload = Record<string, string | null>;
export type CreatePayload = Record<string, unknown>;

export function updateProject(projectCode: string, payload: PatchPayload) {
  return apiPatch<ProjectPassport>(`/projects/${encodeURIComponent(projectCode)}`, payload);
}

export function updateGoal(projectCode: string, goalCode: string, payload: PatchPayload) {
  return apiPatch<Goal>(
    `/projects/${encodeURIComponent(projectCode)}/goals/${encodeURIComponent(goalCode)}`,
    payload,
  );
}

export function updateLpr(projectCode: string, lprCode: string, payload: PatchPayload) {
  return apiPatch<LprProfile>(
    `/projects/${encodeURIComponent(projectCode)}/lprs/${encodeURIComponent(lprCode)}`,
    payload,
  );
}

export function updateBarrier(projectCode: string, barrierCode: string, payload: PatchPayload) {
  return apiPatch<Barrier>(
    `/projects/${encodeURIComponent(projectCode)}/barriers/${encodeURIComponent(barrierCode)}`,
    payload,
  );
}

export function updateExpectation(
  projectCode: string,
  expectationCode: string,
  payload: PatchPayload,
) {
  return apiPatch<Expectation>(
    `/projects/${encodeURIComponent(projectCode)}/expectations/${encodeURIComponent(expectationCode)}`,
    payload,
  );
}

export function updateKpi(projectCode: string, kpiCode: string, payload: PatchPayload) {
  return apiPatch<Kpi>(
    `/projects/${encodeURIComponent(projectCode)}/kpis/${encodeURIComponent(kpiCode)}`,
    payload,
  );
}

export function updateCommunication(
  projectCode: string,
  communicationCode: string,
  payload: PatchPayload,
) {
  return apiPatch<CommunicationPoint>(
    `/projects/${encodeURIComponent(projectCode)}/communications/${encodeURIComponent(communicationCode)}`,
    payload,
  );
}

export function createProject(payload: CreatePayload) {
  return apiPost<ProjectPassport>("/projects", payload);
}

export function createGoal(projectCode: string, payload: CreatePayload) {
  return apiPost<Goal>(`/projects/${encodeURIComponent(projectCode)}/goals`, payload);
}

export function createLpr(projectCode: string, payload: CreatePayload) {
  return apiPost<LprProfile>(`/projects/${encodeURIComponent(projectCode)}/lprs`, payload);
}

export function createBarrier(projectCode: string, payload: CreatePayload) {
  return apiPost<Barrier>(`/projects/${encodeURIComponent(projectCode)}/barriers`, payload);
}

export function createExpectation(projectCode: string, payload: CreatePayload) {
  return apiPost<Expectation>(`/projects/${encodeURIComponent(projectCode)}/expectations`, payload);
}

export function createKpi(projectCode: string, payload: CreatePayload) {
  return apiPost<Kpi>(`/projects/${encodeURIComponent(projectCode)}/kpis`, payload);
}

export function createCommunication(projectCode: string, payload: CreatePayload) {
  return apiPost<CommunicationPoint>(
    `/projects/${encodeURIComponent(projectCode)}/communications`,
    payload,
  );
}

export function createContextBlock(projectCode: string, payload: CreatePayload) {
  return apiPost<ProjectContextBlock>(
    `/projects/${encodeURIComponent(projectCode)}/context-blocks`,
    payload,
  );
}

export function updateContextBlock(
  projectCode: string,
  sectionKey: string,
  blockCode: string,
  payload: Record<string, unknown>,
) {
  return apiPatch<ProjectContextBlock>(
    `/projects/${encodeURIComponent(projectCode)}/context-blocks/${encodeURIComponent(sectionKey)}/${encodeURIComponent(blockCode)}`,
    payload,
  );
}

export function archiveEntity(
  projectCode: string,
  entity: "goals" | "lprs" | "barriers" | "expectations" | "kpis" | "communications",
  code: string,
  archiveReason?: string | null,
) {
  return apiPost<unknown>(
    `/projects/${encodeURIComponent(projectCode)}/${entity}/${encodeURIComponent(code)}/archive`,
    { archive_reason: archiveReason ?? null },
  );
}
