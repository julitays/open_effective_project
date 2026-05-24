import { apiGet, apiPatch } from "./client";
import type {
  Barrier,
  CommunicationPoint,
  Expectation,
  Goal,
  Kpi,
  LprProfile,
  ProjectCjm,
  ProjectPassport,
} from "../types/cjm";

export function getProjects(signal?: AbortSignal) {
  return apiGet<ProjectPassport[]>("/projects", signal);
}

export function getProjectCjm(projectCode: string, signal?: AbortSignal) {
  return apiGet<ProjectCjm>(`/projects/${encodeURIComponent(projectCode)}/cjm`, signal);
}

export type PatchPayload = Record<string, string | null>;

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
