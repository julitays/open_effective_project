import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Plus, X } from "lucide-react";

import EmptyState from "../components/EmptyState";
import ProjectCard from "../components/ProjectCard";
import { createContextBlock, createProject, getProjects } from "../api/projects";
import type { ProjectPassport } from "../types/cjm";

type NewProjectForm = {
  external_project_id: string;
  direction: string;
  project_scale: string;
  primary_operational_model: string;
  lifecycle_stage: string;
  project_status: string;
  start_date: string;
  known_regions: string;
  short_description: string;
  additional_operational_contours: string;
  team_headcount: string;
  gkam: string;
  kam: string;
  stores: string;
  open_team: string;
};

const initialNewProjectForm: NewProjectForm = {
  external_project_id: "",
  direction: "unknown",
  project_scale: "unknown",
  primary_operational_model: "other",
  lifecycle_stage: "unknown",
  project_status: "active",
  start_date: "",
  known_regions: "",
  short_description: "",
  additional_operational_contours: "",
  team_headcount: "",
  gkam: "",
  kam: "",
  stores: "",
  open_team: "",
};

const directionOptions = [
  { value: "fmcg", label: "FMCG" },
  { value: "electronics", label: "Электроника" },
  { value: "kaf", label: "КАФ" },
  { value: "promo", label: "Промо" },
  { value: "training", label: "Обучение" },
  { value: "audit", label: "Аудит" },
  { value: "mixed", label: "Смешанная модель" },
  { value: "other", label: "Другое" },
  { value: "unknown", label: "Не указано" },
];

const scaleOptions = [
  { value: "local", label: "Локальный" },
  { value: "regional", label: "Региональный" },
  { value: "federal", label: "Федеральный" },
  { value: "interregional", label: "Межрегиональный" },
  { value: "unknown", label: "Не указано" },
];

const modelOptions = [
  { value: "merchandising", label: "Мерчендайзинг" },
  { value: "combined_merchandising", label: "Совмещённый мерчендайзинг" },
  { value: "promo_consulting", label: "Промо / консультирование" },
  { value: "kaf", label: "КАФ / кадровое администрирование" },
  { value: "training", label: "Обучение" },
  { value: "audit_quality_control", label: "Аудит / контроль качества" },
  { value: "analytics_reporting", label: "Аналитика / отчётность" },
  { value: "mixed", label: "Смешанная модель" },
  { value: "other", label: "Другое" },
];

const lifecycleOptions = [
  { value: "launch", label: "Запуск" },
  { value: "stabilization", label: "Стабилизация" },
  { value: "development", label: "Развитие" },
  { value: "retention", label: "Удержание" },
  { value: "restart", label: "Перезапуск" },
  { value: "risk", label: "Риск" },
  { value: "closing", label: "Завершение" },
  { value: "unknown", label: "Не указано" },
];

const statusOptions = [
  { value: "active", label: "Активен" },
  { value: "completed", label: "Завершён" },
  { value: "pilot", label: "Пилот" },
  { value: "at_risk", label: "В зоне риска" },
  { value: "unknown", label: "Не указано" },
];

export default function ProjectsPage() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<ProjectPassport[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);
  const [form, setForm] = useState<NewProjectForm>(initialNewProjectForm);

  function loadProjects(signal?: AbortSignal) {
    return getProjects(signal)
      .then((items) => {
        setProjects(items);
        setError(null);
      })
      .catch((cause: unknown) => {
        if (!signal?.aborted) {
          setError(cause instanceof Error ? cause.message : "Не удалось загрузить проекты.");
        }
      })
      .finally(() => {
        if (!signal?.aborted) {
          setLoading(false);
        }
      });
  }

  useEffect(() => {
    const controller = new AbortController();

    setLoading(true);
    loadProjects(controller.signal);

    return () => controller.abort();
  }, []);

  function updateForm<K extends keyof NewProjectForm>(field: K, value: NewProjectForm[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submitCreateProject() {
    const externalId = form.external_project_id.trim();
    const description = form.short_description.trim();

    if (!externalId) {
      setCreateError("Укажите код проекта.");
      return;
    }
    if (!description) {
      setCreateError("Добавьте краткое описание проекта.");
      return;
    }

    setCreating(true);
    setCreateError(null);
    try {
      const created = await createProject({
        external_project_id: externalId,
        direction: form.direction,
        project_scale: form.project_scale,
        primary_operational_model: form.primary_operational_model,
        lifecycle_stage: form.lifecycle_stage,
        project_status: form.project_status,
        start_date: trimToNull(form.start_date),
        known_regions: trimToNull(form.known_regions),
        short_description: description,
        additional_operational_contours: trimToNull(form.additional_operational_contours),
      });

      await createContextBlock(created.project_code, {
        section_key: "passport_header",
        block_code: "passport_header_001",
        block_type: "facts",
        title: "Шапка проекта",
        display_order: 10,
        content: {
          items: [
            { label: "Команда", value: form.team_headcount.trim() || "Требует уточнения" },
            { label: "GKAM", value: form.gkam.trim() || "Не указано" },
            { label: "KAM", value: form.kam.trim() || "Не указано" },
            { label: "Торговые сети", value: form.stores.trim() || "Требует уточнения" },
            { label: "Контуры", value: form.open_team.trim() || "Требует уточнения" },
          ],
        },
      });

      await createContextBlock(created.project_code, {
        section_key: "passport_overview",
        block_code: "passport_overview_001",
        block_type: "facts",
        title: "Основные параметры",
        display_order: 20,
        content: {
          items: [
            { label: "Код проекта", value: externalId },
            { label: "Статус", value: optionLabel(statusOptions, form.project_status) },
            { label: "Этап жизненного цикла", value: optionLabel(lifecycleOptions, form.lifecycle_stage) },
            { label: "Дата старта", value: form.start_date.trim() || "Не указано" },
          ],
        },
      });

      await createContextBlock(created.project_code, {
        section_key: "passport_service",
        block_code: "passport_service_001",
        block_type: "facts",
        title: "Модель сервиса",
        display_order: 30,
        content: {
          items: [
            { label: "Основная модель", value: optionLabel(modelOptions, form.primary_operational_model) },
            { label: "Формат сервиса", value: description },
            {
              label: "Дополнительные контуры",
              value: form.additional_operational_contours.trim() || "Не указано",
            },
            { label: "География", value: form.known_regions.trim() || "Не указано" },
          ],
        },
      });

      setCreateModalOpen(false);
      setForm(initialNewProjectForm);
      setProjects((current) => [created, ...current]);
      navigate(`/projects/${created.project_code}?section=passport`);
    } catch (cause: unknown) {
      setCreateError(cause instanceof Error ? cause.message : "Не удалось создать проект.");
    } finally {
      setCreating(false);
    }
  }

  return (
    <section className="space-y-5">
      <header className="border-b border-slate-200 pb-5">
        <p className="text-sm font-semibold text-sky-800">Проекты</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Контекст проектов
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Выберите проект, чтобы открыть паспорт, цели, роли, риски, KPI и рабочий контекст.
        </p>
        <button
          type="button"
          onClick={() => {
            setCreateModalOpen(true);
            setCreateError(null);
          }}
          className="mt-4 inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-slate-800"
        >
          <Plus aria-hidden="true" className="h-4 w-4" />
          Новый проект
        </button>
      </header>

      {loading ? (
        <LoadingGrid />
      ) : error ? (
        <EmptyState title="Не удалось загрузить проекты" description={error} />
      ) : projects.length === 0 ? (
        <EmptyState
          title="Проектов пока нет"
          description="Список проектов пока пуст."
        />
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          {projects.map((project) => (
            <ProjectCard key={project.project_code} project={project} />
          ))}
        </div>
      )}

      {createModalOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 p-4">
          <div className="max-h-[92vh] w-full max-w-5xl overflow-hidden rounded-2xl bg-white shadow-2xl">
            <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
              <div>
                <div className="text-xs font-semibold uppercase text-slate-400">Создание проекта</div>
                <h2 className="mt-1 text-xl font-semibold text-slate-950">Новый проект с нуля</h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                  Заполните базовый контекст паспорта. После сохранения откроется страница проекта для дальнейшего редактирования.
                </p>
              </div>
              <button
                type="button"
                onClick={() => !creating && setCreateModalOpen(false)}
                className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100"
                aria-label="Закрыть"
              >
                <X aria-hidden="true" className="h-5 w-5" />
              </button>
            </div>

            <div className="max-h-[68vh] space-y-5 overflow-y-auto px-6 py-5">
              <div className="grid gap-4 md:grid-cols-2">
                <Input label="Код проекта (обязательно)" value={form.external_project_id} onChange={(value) => updateForm("external_project_id", value)} />
                <Select label="Направление" value={form.direction} onChange={(value) => updateForm("direction", value)} options={directionOptions} />
                <Select label="Масштаб" value={form.project_scale} onChange={(value) => updateForm("project_scale", value)} options={scaleOptions} />
                <Select label="Основная операционная модель" value={form.primary_operational_model} onChange={(value) => updateForm("primary_operational_model", value)} options={modelOptions} />
                <Select label="Этап жизненного цикла" value={form.lifecycle_stage} onChange={(value) => updateForm("lifecycle_stage", value)} options={lifecycleOptions} />
                <Select label="Статус проекта" value={form.project_status} onChange={(value) => updateForm("project_status", value)} options={statusOptions} />
                <Input label="Дата старта" value={form.start_date} onChange={(value) => updateForm("start_date", value)} />
                <TextArea label="Краткое описание (обязательно)" value={form.short_description} onChange={(value) => updateForm("short_description", value)} />
                <TextArea label="Известные регионы" value={form.known_regions} onChange={(value) => updateForm("known_regions", value)} />
                <TextArea label="Дополнительные контуры" value={form.additional_operational_contours} onChange={(value) => updateForm("additional_operational_contours", value)} />
                <TextArea label="Контуры OPEN (для шапки)" value={form.open_team} onChange={(value) => updateForm("open_team", value)} />
                <Input label="Команда (для шапки)" value={form.team_headcount} onChange={(value) => updateForm("team_headcount", value)} />
                <Input label="GKAM (для шапки)" value={form.gkam} onChange={(value) => updateForm("gkam", value)} />
                <Input label="KAM (для шапки)" value={form.kam} onChange={(value) => updateForm("kam", value)} />
                <Input label="Торговые сети (для шапки)" value={form.stores} onChange={(value) => updateForm("stores", value)} />
              </div>
              {createError ? (
                <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
                  {createError}
                </div>
              ) : null}
            </div>

            <div className="flex flex-col-reverse gap-3 border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex-row sm:justify-end">
              <button
                type="button"
                onClick={() => setCreateModalOpen(false)}
                disabled={creating}
                className="min-h-11 rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={submitCreateProject}
                disabled={creating}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 text-sm font-semibold text-white shadow-sm hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {creating ? "Создаём..." : "Создать проект"}
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function LoadingGrid() {
  return (
    <div className="grid gap-4 xl:grid-cols-2" aria-label="Загрузка проектов">
      {["one", "two"].map((item) => (
        <div
          key={item}
          className="h-72 animate-pulse rounded-lg border border-slate-200 bg-white shadow-sm"
        />
      ))}
    </div>
  );
}

function Input({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase text-slate-500">{label}</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
      />
    </label>
  );
}

function TextArea({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase text-slate-500">{label}</span>
      <textarea
        value={value}
        rows={4}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
      />
    </label>
  );
}

function Select({
  label,
  value,
  onChange,
  options,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase text-slate-500">{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function trimToNull(value: string) {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function optionLabel(options: Array<{ value: string; label: string }>, value: string) {
  return options.find((option) => option.value === value)?.label || value;
}
