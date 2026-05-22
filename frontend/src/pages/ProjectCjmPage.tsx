import { ArrowLeft, MessageSquareText, Target } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getProjectCjm } from "../api/projects";
import CjmTabs, { type CjmTabId } from "../components/CjmTabs";
import EmptyState from "../components/EmptyState";
import StatusBadge from "../components/StatusBadge";
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

export default function ProjectCjmPage() {
  const { projectCode } = useParams();
  const [projectCjm, setProjectCjm] = useState<ProjectCjm | null>(null);
  const [activeTab, setActiveTab] = useState<CjmTabId>("passport");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectCode) {
      setError("В адресе не найден код проекта.");
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    setLoading(true);
    getProjectCjm(projectCode, controller.signal)
      .then((payload) => {
        setProjectCjm(payload);
        setError(null);
      })
      .catch((cause: unknown) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "Не удалось загрузить CJM.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [projectCode]);

  if (loading) {
    return <ProjectLoading />;
  }

  if (error || !projectCjm) {
    return (
      <div className="space-y-4">
        <BackLink />
        <EmptyState
          title="CJM не загрузился"
          description={error || "API не вернул данные проекта."}
        />
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <BackLink />
      <ProjectHeader project={projectCjm.project} />
      <CjmTabs activeTab={activeTab} onChange={setActiveTab} />
      <div role="tabpanel">
        {activeTab === "passport" ? (
          <PassportPanel project={projectCjm.project} />
        ) : null}
        {activeTab === "goals" ? <GoalsPanel goals={projectCjm.goals} /> : null}
        {activeTab === "lprs" ? <LprsPanel lprs={projectCjm.lprs} /> : null}
        {activeTab === "importance" ? (
          <ImportancePanel lprs={projectCjm.lprs} />
        ) : null}
        {activeTab === "barriers" ? (
          <BarriersPanel barriers={projectCjm.barriers} />
        ) : null}
        {activeTab === "expectations" ? (
          <ExpectationsPanel expectations={projectCjm.expectations} />
        ) : null}
        {activeTab === "kpis" ? <KpisPanel kpis={projectCjm.kpis} /> : null}
        {activeTab === "communications" ? (
          <CommunicationsPanel communications={projectCjm.communications} />
        ) : null}
      </div>
    </section>
  );
}

function BackLink() {
  return (
    <Link
      to="/projects"
      className="inline-flex min-h-10 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
    >
      <ArrowLeft aria-hidden="true" className="h-4 w-4" />
      К списку проектов
    </Link>
  );
}

function ProjectHeader({ project }: { project: ProjectPassport }) {
  return (
    <header className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge value={project.project_code} />
            <StatusBadge value={project.project_status} />
            {project.direction ? <StatusBadge value={project.direction} /> : null}
          </div>
          <h1 className="mt-4 break-words text-3xl font-semibold text-slate-950">
            CJM проекта {filled(project.external_project_id)}
          </h1>
          {project.short_description ? (
            <p className="mt-3 max-w-5xl text-sm leading-6 text-slate-600">
              {project.short_description}
            </p>
          ) : null}
        </div>

        <div className="grid min-w-0 gap-3 sm:grid-cols-2 xl:w-[420px] xl:shrink-0">
          <InfoField label="Project ID" value={project.project_code} />
          <InfoField label="Display code" value={project.working_project_code} />
          <InfoField label="Масштаб" value={project.project_scale} />
          <InfoField label="Этап" value={project.lifecycle_stage} />
        </div>
      </div>
    </header>
  );
}

function PassportPanel({ project }: { project: ProjectPassport }) {
  return (
    <PanelIntro
      title="Паспорт"
      description="Проектный контекст из загруженного CJM-файла."
    >
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        <InfoField label="Project ID" value={project.project_code} />
        <InfoField label="External project ID" value={project.external_project_id} />
        <InfoField label="Рабочий код" value={project.working_project_code} />
        <InfoField label="Направление" value={project.direction} />
        <InfoField label="Масштаб" value={project.project_scale} />
        <InfoField label="Статус" value={project.project_status} badge />
        <InfoField label="Известные регионы" value={project.known_regions} />
        <InfoField
          label="Основная операционная модель"
          value={project.primary_operational_model}
        />
        <InfoField
          label="Дополнительные контуры"
          value={project.additional_operational_contours}
        />
        <InfoField label="Этап жизненного цикла" value={project.lifecycle_stage} />
        <InfoField label="Дата старта" value={project.start_date} />
        <InfoField label="Описание" value={project.short_description} />
      </div>
    </PanelIntro>
  );
}

function GoalsPanel({ goals }: { goals: Goal[] }) {
  if (goals.length === 0) {
    return <EmptyState title="Целей нет" description="API вернул пустой список целей." />;
  }

  return (
    <PanelIntro title="Цели" description="Цели и связанные критерии успеха проекта.">
      <div className="grid gap-4 xl:grid-cols-2">
        {goals.map((goal) => (
          <article
            key={goal.goal_code || goal.goal_text}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <StatusBadge value={goal.goal_code || "goal"} />
              {goal.relevance_status ? (
                <StatusBadge value={goal.relevance_status} />
              ) : null}
            </div>
            <h3 className="mt-4 text-lg font-semibold text-slate-950">
              {goal.goal_text}
            </h3>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Detail label="Владелец" value={goal.goal_owner} />
              <Detail label="Тип" value={goal.goal_type} />
              <Detail label="Приоритет" value={goal.priority} />
              <Detail label="KPI / критерий" value={goal.related_kpi_or_criterion_text} />
              <Detail label="Источник" value={goal.source_text} />
              <Detail label="Комментарий" value={goal.comment} />
            </div>
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function LprsPanel({ lprs }: { lprs: LprProfile[] }) {
  if (lprs.length === 0) {
    return <EmptyState title="ЛПР нет" description="API вернул пустой список ЛПР." />;
  }

  return (
    <PanelIntro title="ЛПР" description="Обезличенные клиентские роли и статусы.">
      <div className="grid gap-4 xl:grid-cols-2">
        {lprs.map((lpr) => (
          <article
            key={lpr.lpr_code}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="text-xs font-semibold uppercase text-slate-500">
                  {lpr.lpr_code}
                </div>
                <h3 className="mt-2 text-lg font-semibold text-slate-950">
                  {lpr.role_zone}
                </h3>
              </div>
              {lpr.influence_level ? <StatusBadge value={lpr.influence_level} /> : null}
            </div>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Detail label="External LPR ID" value={lpr.external_lpr_id} />
              <Detail label="Активность" value={lpr.activity_status} />
              <Detail label="Отношение" value={lpr.relationship_status} />
              <Detail label="Влияние" value={lpr.influence_level} />
            </div>
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function ImportancePanel({ lprs }: { lprs: LprProfile[] }) {
  const lprsWithFactors = lprs.filter((lpr) => lpr.importance_factors.length > 0);

  if (lprsWithFactors.length === 0) {
    return (
      <EmptyState
        title="Важностей ЛПР нет"
        description="API вернул ЛПР без заполненных importance factors."
      />
    );
  }

  return (
    <PanelIntro
      title="Важности ЛПР"
      description="Факторы важности сгруппированы по обезличенному LPR ID."
    >
      <div className="space-y-4">
        {lprsWithFactors.map((lpr) => (
          <article
            key={lpr.lpr_code}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-wrap items-center gap-3 border-b border-slate-100 pb-4">
              <StatusBadge value={lpr.lpr_code} />
              <h3 className="text-base font-semibold text-slate-950">{lpr.role_zone}</h3>
            </div>
            <div className="mt-4 grid gap-3 xl:grid-cols-2">
              {lpr.importance_factors.map((factor) => (
                <div
                  key={`${lpr.lpr_code}-${factor.factor_type}`}
                  className="rounded-md border border-slate-200 bg-slate-50 p-4"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <StatusBadge value={factor.factor_type} />
                    {factor.criticality ? <StatusBadge value={factor.criticality} /> : null}
                  </div>
                  <div className="mt-3 text-sm font-semibold text-slate-950">
                    {factor.factor_text}
                  </div>
                  <div className="mt-3 grid gap-2">
                    <Detail label="Источник" value={factor.source_text} />
                    <Detail label="Доказательство" value={factor.evidence_quote} />
                    <Detail label="Уверенность" value={factor.confidence_level} />
                  </div>
                </div>
              ))}
            </div>
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function BarriersPanel({ barriers }: { barriers: Barrier[] }) {
  if (barriers.length === 0) {
    return <EmptyState title="Барьеров нет" description="API вернул пустой список." />;
  }

  return (
    <PanelIntro title="Барьеры" description="Риски и барьеры CJM с текстовым evidence.">
      <div className="grid gap-4 2xl:grid-cols-2">
        {barriers.map((barrier) => (
          <article
            key={barrier.barrier_code || barrier.barrier_title}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge value={barrier.barrier_code || "barrier"} />
              <StatusBadge value={barrier.criticality} />
              <StatusBadge value={barrier.status} />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-slate-950">
              {barrier.barrier_title}
            </h3>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Detail label="Тип" value={barrier.barrier_type} />
              <Detail label="Временной статус" value={barrier.time_status} />
              <Detail label="Актуальность" value={barrier.relevance_status} />
              <Detail label="Уверенность" value={barrier.confidence_level} />
              <Detail label="Связанный KPI" value={barrier.linked_kpi_text} />
              <Detail label="Источник" value={barrier.source_text} />
            </div>
            <Evidence value={barrier.evidence_quote} />
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function ExpectationsPanel({ expectations }: { expectations: Expectation[] }) {
  if (expectations.length === 0) {
    return <EmptyState title="Ожиданий нет" description="API вернул пустой список." />;
  }

  return (
    <PanelIntro
      title="Ожидания клиента"
      description="Явные и неявные ожидания рядом с их источниками."
    >
      <div className="grid gap-4 2xl:grid-cols-2">
        {expectations.map((expectation) => (
          <article
            key={expectation.expectation_code || expectation.expectation_text}
            className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
          >
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge value={expectation.expectation_code || "expectation"} />
              <StatusBadge value={expectation.criticality} />
              <StatusBadge value={expectation.explicitness} />
            </div>
            <h3 className="mt-4 text-lg font-semibold text-slate-950">
              {expectation.expectation_text}
            </h3>
            <div className="mt-4 grid gap-3 sm:grid-cols-2">
              <Detail label="Тип" value={expectation.expectation_type} />
              <Detail label="Актуальность" value={expectation.relevance_status} />
              <Detail label="Уверенность" value={expectation.confidence_level} />
              <Detail label="Связанный KPI" value={expectation.linked_kpi_text} />
              <Detail label="Источник" value={expectation.source_text} />
            </div>
            <Evidence value={expectation.evidence_quote} />
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function KpisPanel({ kpis }: { kpis: Kpi[] }) {
  if (kpis.length === 0) {
    return <EmptyState title="KPI нет" description="API вернул пустой список KPI." />;
  }

  return (
    <PanelIntro title="KPI" description="KPI и критерии успеха проекта.">
      <DataTable
        headers={[
          "KPI",
          "Название",
          "Тип",
          "Источник",
          "Актуальность",
          "Ожидание",
          "Барьер",
          "Критичность",
          "Подтверждение",
          "Комментарий",
        ]}
      >
        {kpis.map((kpi) => (
          <tr key={kpi.kpi_code} className="align-top hover:bg-slate-50">
            <Cell value={kpi.kpi_code} strong />
            <Cell value={kpi.kpi_name} />
            <Cell value={kpi.kpi_type} />
            <Cell value={kpi.source_text} />
            <Cell value={kpi.relevance_status} badge />
            <Cell value={kpi.related_expectation_text} />
            <Cell value={kpi.related_barrier_text} />
            <Cell value={kpi.client_criticality} badge />
            <Cell value={kpi.requires_confirmation} />
            <Cell value={kpi.comment} />
          </tr>
        ))}
      </DataTable>
    </PanelIntro>
  );
}

function CommunicationsPanel({
  communications,
}: {
  communications: CommunicationPoint[];
}) {
  if (communications.length === 0) {
    return (
      <EmptyState
        title="Коммуникаций нет"
        description="API вернул пустой список коммуникационных точек."
      />
    );
  }

  return (
    <PanelIntro
      title="Коммуникации"
      description="Каналы и темы взаимодействия клиента с OPEN."
    >
      <DataTable
        headers={[
          "Communication",
          "Сторона клиента",
          "External LPR",
          "Сторона OPEN",
          "Тема",
          "Канал",
          "Частота",
          "Критичность",
          "Источник",
          "Актуальность",
          "Комментарий",
        ]}
      >
        {communications.map((point) => (
          <tr
            key={point.communication_code || point.summary}
            className="align-top hover:bg-slate-50"
          >
            <Cell value={point.communication_code} strong />
            <Cell value={point.client_side} />
            <Cell value={point.external_lpr_id} />
            <Cell value={point.open_side_role} />
            <Cell value={point.topic_text} />
            <Cell value={point.channel_text} />
            <Cell value={point.frequency} />
            <Cell value={point.criticality} badge />
            <Cell value={point.source_text} />
            <Cell value={point.relevance_status} badge />
            <Cell value={point.comment} />
          </tr>
        ))}
      </DataTable>
    </PanelIntro>
  );
}

function PanelIntro({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <div className="flex flex-wrap items-start justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-950">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function InfoField({
  label,
  value,
  badge = false,
}: {
  label: string;
  value: string | null;
  badge?: boolean;
}) {
  return (
    <div className="min-w-0 rounded-md border border-slate-200 bg-slate-50 p-4">
      <div className="text-xs font-semibold uppercase text-slate-400">{label}</div>
      <div className="mt-2 break-words text-sm text-slate-900">
        {badge && value ? <StatusBadge value={value} /> : filled(value)}
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="min-w-0">
      <div className="text-xs font-semibold uppercase text-slate-400">{label}</div>
      <div className="mt-1 break-words text-sm leading-6 text-slate-700">
        {filled(value)}
      </div>
    </div>
  );
}

function Evidence({ value }: { value: string | null }) {
  if (!value) {
    return null;
  }

  return (
    <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400">
        <MessageSquareText aria-hidden="true" className="h-3.5 w-3.5" />
        Доказательство
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-700">{value}</p>
    </div>
  );
}

function DataTable({
  headers,
  children,
}: {
  headers: string[];
  children: React.ReactNode;
}) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="min-w-[1120px] table-fixed text-left text-sm">
        <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-3 py-3">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">{children}</tbody>
      </table>
    </div>
  );
}

function Cell({
  value,
  strong = false,
  badge = false,
}: {
  value: string | null;
  strong?: boolean;
  badge?: boolean;
}) {
  return (
    <td className={`break-words px-3 py-4 leading-6 ${strong ? "font-medium" : ""}`}>
      {badge && value ? <StatusBadge value={value} /> : filled(value)}
    </td>
  );
}

function ProjectLoading() {
  return (
    <div className="space-y-4" aria-label="Загрузка CJM проекта">
      <div className="h-10 w-40 animate-pulse rounded-md bg-white shadow-sm" />
      <div className="h-72 animate-pulse rounded-lg border border-slate-200 bg-white shadow-sm" />
      <div className="h-12 animate-pulse rounded-lg border border-slate-200 bg-white shadow-sm" />
      <div className="flex h-72 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-400 shadow-sm">
        <Target aria-hidden="true" className="h-7 w-7 animate-pulse" />
      </div>
    </div>
  );
}

function filled(value: string | null) {
  return value || "Не заполнено";
}
