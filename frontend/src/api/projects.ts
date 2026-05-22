import { apiGet } from "./client";
import type { ProjectCjm, ProjectPassport } from "../types/cjm";

export function getProjects(signal?: AbortSignal) {
  return apiGet<ProjectPassport[]>("/projects", signal);
}

export function getProjectCjm(projectCode: string, signal?: AbortSignal) {
  return apiGet<ProjectCjm>(`/projects/${encodeURIComponent(projectCode)}/cjm`, signal);
}
