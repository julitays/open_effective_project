import { ArrowRight, ChevronDown, ChevronUp, MapPinned } from "lucide-react";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import StatusBadge from "./StatusBadge";
import type { ProjectPassport } from "../types/cjm";
import {
  formatCode,
  formatDirection,
  formatLifecycleStage,
  formatProjectScale,
  formatProjectStatus,
  sanitizeCjm,
} from "../utils/labels";

interface ProjectCardProps {
  project: ProjectPassport;
}

export default function ProjectCard({ project }: ProjectCardProps) {
  const [expanded, setExpanded] = useState(false);
  const completeness = useMemo(() => buildPassportCompleteness(project), [project]);

  return (
    <article className="rounded-xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/70 transition hover:border-slate-300 hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-xs font-semibold uppercase text-slate-400">Код проекта</div>
          <h2 className="mt-2 break-words text-xl font-semibold text-slate-950">
            {formatCode(project.external_project_id)}
          </h2>
        </div>
        <Link
          to={`/projects/${project.project_code}`}
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700 transition hover:bg-slate-900 hover:text-white"
          aria-label="Открыть проект"
        >
          <ArrowRight aria-hidden="true" className="h-4 w-4" />
        </Link>
      </div>

      {project.short_description ? (
        <p className="mt-4 line-clamp-3 text-sm leading-6 text-slate-600">
          {sanitizeCjm(project.short_description)}
        </p>
      ) : null}

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <ProjectMeta label="Направление" value={formatDirection(project.direction)} />
        <ProjectMeta label="Масштаб" value={formatProjectScale(project.project_scale)} />
        <ProjectMeta label="Этап" value={formatLifecycleStage(project.lifecycle_stage)} />
        <ProjectMeta label="Статус" value={formatProjectStatus(project.project_status)} />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4">
        <StatusBadge value={formatProjectStatus(project.project_status)} />
        {project.known_regions ? (
          <span className="inline-flex min-w-0 items-center gap-1 text-xs text-slate-500">
            <MapPinned aria-hidden="true" className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{project.known_regions}</span>
          </span>
        ) : null}
      </div>

      <div className="mt-4 border-t border-slate-100 pt-4">
        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-700 hover:text-slate-950"
        >
          {expanded ? <ChevronUp aria-hidden="true" className="h-4 w-4" /> : <ChevronDown aria-hidden="true" className="h-4 w-4" />}
          {expanded ? "Скрыть полноту паспорта" : "Показать полноту паспорта"}
        </button>

        {expanded ? (
          <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-slate-900">Паспорт проекта</div>
              <div className="text-sm font-semibold text-slate-900">{completeness.percent}%</div>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
              <div className="h-full rounded-full bg-slate-900" style={{ width: `${completeness.percent}%` }} />
            </div>
            <div className="mt-4 space-y-2">
              {completeness.items.map((item) => (
                <div key={item.label} className="flex items-center justify-between gap-3 text-sm">
                  <span className="text-slate-600">{item.label}</span>
                  <span className={item.filled ? "font-medium text-emerald-700" : "font-medium text-amber-700"}>
                    {item.filled ? "Заполнено" : "Пусто"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </article>
  );
}

function ProjectMeta({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="min-w-0">
      <div className="text-xs font-medium uppercase text-slate-400">{label}</div>
      <div className="mt-1 truncate text-sm text-slate-800">{value}</div>
    </div>
  );
}

function buildPassportCompleteness(project: ProjectPassport) {
  const items = [
    { label: "Код проекта", filled: Boolean(project.external_project_id) },
    { label: "Направление", filled: Boolean(project.direction) },
    { label: "Масштаб", filled: Boolean(project.project_scale) },
    { label: "Регионы", filled: Boolean(project.known_regions) },
    { label: "Модель", filled: Boolean(project.primary_operational_model) },
    { label: "Контуры", filled: Boolean(project.additional_operational_contours) },
    { label: "Этап", filled: Boolean(project.lifecycle_stage) },
    { label: "Статус", filled: Boolean(project.project_status) },
    { label: "Дата старта", filled: Boolean(project.start_date) },
    { label: "Описание", filled: Boolean(project.short_description) },
  ];

  const percent = Math.round((items.filter((item) => item.filled).length / items.length) * 100);
  return { items, percent };
}
