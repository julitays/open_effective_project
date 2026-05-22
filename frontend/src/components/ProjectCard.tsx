import { ArrowRight, MapPinned } from "lucide-react";
import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";
import type { ProjectPassport } from "../types/cjm";

interface ProjectCardProps {
  project: ProjectPassport;
}

function readable(value: string | null) {
  return value || "Не заполнено";
}

export default function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Link
      to={`/projects/${project.project_code}`}
      className="group block rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-xs font-semibold uppercase text-slate-500">
            {project.project_code}
          </div>
          <h2 className="mt-2 break-words text-xl font-semibold text-slate-950">
            {readable(project.external_project_id)}
          </h2>
        </div>
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700 transition group-hover:bg-slate-900 group-hover:text-white">
          <ArrowRight aria-hidden="true" className="h-4 w-4" />
        </span>
      </div>

      {project.short_description ? (
        <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
          {project.short_description}
        </p>
      ) : null}

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <ProjectMeta label="Направление" value={project.direction} />
        <ProjectMeta label="Масштаб" value={project.project_scale} />
        <ProjectMeta label="Этап" value={project.lifecycle_stage} />
        <ProjectMeta label="Display code" value={project.working_project_code} />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
        <StatusBadge value={project.project_status} />
        {project.known_regions ? (
          <span className="inline-flex min-w-0 items-center gap-1 text-xs text-slate-500">
            <MapPinned aria-hidden="true" className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{project.known_regions}</span>
          </span>
        ) : null}
      </div>
    </Link>
  );
}

function ProjectMeta({
  label,
  value,
}: {
  label: string;
  value: string | null;
}) {
  return (
    <div className="min-w-0">
      <div className="text-xs font-medium uppercase text-slate-400">{label}</div>
      <div className="mt-1 truncate text-sm text-slate-800">{readable(value)}</div>
    </div>
  );
}
