import {
  ArrowLeft,
  ChevronDown,
  MessageSquareText,
  Target,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { Link, useOutletContext, useParams } from "react-router-dom";

import { getProjectCjm } from "../api/projects";
import type { LayoutOutletContext } from "../components/Layout";
import EmptyState from "../components/EmptyState";
import StatusBadge from "../components/StatusBadge";
import type {
  Barrier,
  CommunicationPoint,
  Expectation,
  Goal,
  Kpi,
  LprImportanceFactor,
  LprProfile,
  ProjectCjm,
  ProjectPassport,
} from "../types/cjm";
import {
  formatActivityStatus,
  formatBarrierStatus,
  formatBarrierTimeStatus,
  formatBarrierType,
  formatCode,
  formatCommunicationChannel,
  formatCommunicationFrequency,
  formatConfidenceLevel,
  formatCriticality,
  formatDirection,
  formatEntityCode,
  formatExpectationType,
  formatExplicitness,
  formatGoalType,
  formatImportanceFactor,
  formatInfluenceLevel,
  formatLifecycleStage,
  formatOperationalModel,
  formatProjectScale,
  formatProjectStatus,
  formatRelationshipStatus,
  formatRelevanceStatus,
  formatText,
  formatYesNo,
  isActual,
  isConfirmationRequired,
  isRepeated,
} from "../utils/labels";

type Formatter = (value: string | null | undefined) => string;
type RelationResolver = ReturnType<typeof buildRelationResolver>;

export default function ProjectCjmPage() {
  const { projectCode } = useParams();
  const { activeCjmTab: activeTab } = useOutletContext<LayoutOutletContext>();
  const [projectCjm, setProjectCjm] = useState<ProjectCjm | null>(null);
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
          description={error || "По проекту не удалось получить данные."}
        />
      </div>
    );
  }

  const relationResolver = buildRelationResolver(projectCjm);

  return (
    <section className="space-y-6">
      <BackLink />
      <ProjectHeader project={projectCjm.project} />

      <div className="min-w-0" role="tabpanel">
        {activeTab === "overview" ? (
          <OverviewPanel cjm={projectCjm} relationResolver={relationResolver} />
        ) : null}
        {activeTab === "passport" ? (
          <PassportPanel project={projectCjm.project} />
        ) : null}
        {activeTab === "goals" ? (
          <GoalsPanel goals={projectCjm.goals} relationResolver={relationResolver} />
        ) : null}
        {activeTab === "lprs" ? (
          <LprsPanel lprs={projectCjm.lprs} relationResolver={relationResolver} />
        ) : null}
        {activeTab === "barriers" ? (
            <BarriersPanel barriers={projectCjm.barriers} relationResolver={relationResolver} />
        ) : null}
        {activeTab === "expectations" ? (
            <ExpectationsPanel expectations={projectCjm.expectations} relationResolver={relationResolver} />
          ) : null}
        {activeTab === "kpis" ? (
          <KpisPanel kpis={projectCjm.kpis} relationResolver={relationResolver} />
        ) : null}
        {activeTab === "communications" ? (
          <CommunicationsPanel communications={projectCjm.communications} relationResolver={relationResolver} />
        ) : null}
      </div>
    </section>
  );
}

function BackLink() {
  return (
    <Link
      to="/projects"
      className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm shadow-slate-200/70 hover:bg-slate-50"
    >
      <ArrowLeft aria-hidden="true" className="h-4 w-4" />
      К списку проектов
    </Link>
  );
}

function ProjectHeader({ project }: { project: ProjectPassport }) {
  const displayCode = formatCode(project.working_project_code || project.external_project_id);

  return (
    <header className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm shadow-slate-200/80">
      <div className="flex flex-col gap-6 2xl:flex-row 2xl:items-start 2xl:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge value={formatDirection(project.direction)} />
            <StatusBadge value={formatProjectScale(project.project_scale)} />
            <StatusBadge value={formatProjectStatus(project.project_status)} />
          </div>
          <h1 className="mt-4 break-words text-3xl font-semibold text-slate-950">
            Проект {displayCode}
          </h1>
          {project.short_description ? (
            <p className="mt-3 max-w-5xl text-sm leading-6 text-slate-600">
              {project.short_description}
            </p>
          ) : null}
        </div>

        <div className="grid min-w-0 gap-3 sm:grid-cols-2 2xl:w-[520px] 2xl:shrink-0">
          <InfoField label="Внутренний код" value={project.project_code} />
          <InfoField label="Код проекта" value={displayCode} />
          <InfoField label="Этап" value={formatLifecycleStage(project.lifecycle_stage)} />
          <InfoField label="Статус" value={formatProjectStatus(project.project_status)} badge />
        </div>
      </div>
    </header>
  );
}

function OverviewPanel({
  cjm,
  relationResolver,
}: {
  cjm: ProjectCjm;
  relationResolver: RelationResolver;
}) {
  const highInfluenceLprs = cjm.lprs.filter((lpr) => hasHighInfluence(lpr.influence_level));
  const watchedBarriers = cjm.barriers.filter(
    (barrier) =>
      isActual(barrier.relevance_status) ||
      isRepeated(barrier.time_status) ||
      hasCurrentTimeStatus(barrier.time_status),
  );
  const actualExpectations = cjm.expectations.filter((expectation) =>
    isActual(expectation.relevance_status),
  );
  const linkedKpis = cjm.kpis.filter(
    (kpi) =>
      kpi.related_barrier_text ||
      kpi.related_expectation_text ||
      isConfirmationRequired(kpi.relevance_status) ||
      isConfirmationRequired(kpi.requires_confirmation),
  );
  const confirmationItems = buildConfirmationItems(cjm);

  return (
    <PanelIntro
      title="Обзор"
      description="Сжатая карта: кто влияет на проект, что болит, какие ожидания и KPI нужно держать в фокусе."
    >
      <div className="grid gap-4 2xl:grid-cols-[1fr_360px]">
        <section className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <OverviewList
              title="Ключевые ЛПР"
              emptyText="Высокое влияние пока не выделено."
              items={highInfluenceLprs.slice(0, 5)}
              renderItem={(lpr) => (
                <>
                  <div className="text-xs font-semibold uppercase text-slate-400">
                    {formatEntityCode(lpr.lpr_code)}
                  </div>
                  <div className="mt-1 font-medium text-slate-950">
                    {formatText(lpr.role_zone || lpr.role)}
                  </div>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <StatusBadge value={formatInfluenceLevel(lpr.influence_level)} />
                    <StatusBadge value={formatRelationshipStatus(lpr.relationship_status)} />
                  </div>
                </>
              )}
            />
            <OverviewList
              title="Барьеры на контроле"
              emptyText="Актуальных или повторяющихся барьеров не найдено."
              items={watchedBarriers.slice(0, 5)}
              renderItem={(barrier) => (
                <>
                  <div className="font-medium text-slate-950">{barrier.barrier_title}</div>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <StatusBadge value={formatCriticality(barrier.criticality)} />
                    <StatusBadge value={formatBarrierTimeStatus(barrier.time_status)} />
                  </div>
                </>
              )}
            />
          </div>

          <div className="grid gap-4 lg:grid-cols-2">
            <OverviewList
              title="Актуальные ожидания"
              emptyText="Актуальные ожидания пока не выделены."
              items={actualExpectations.slice(0, 5)}
              renderItem={(expectation) => (
                <>
                  <div className="font-medium text-slate-950">{expectation.expectation_text}</div>
                  <div className="mt-1 flex flex-wrap gap-2">
                    <StatusBadge value={formatExpectationType(expectation.expectation_type)} />
                    <StatusBadge value={formatCriticality(expectation.criticality)} />
                  </div>
                </>
              )}
            />
            <OverviewList
              title="Связанные KPI и критерии"
              emptyText="Связанные KPI пока не заполнены."
              items={linkedKpis.slice(0, 5)}
              renderItem={(kpi) => (
                <>
                  <div className="font-medium text-slate-950">{kpi.kpi_name}</div>
                  <div className="mt-1 text-xs leading-5 text-slate-500">
                    {relationResolver.format(kpi.related_expectation_text || kpi.related_barrier_text)}
                  </div>
                </>
              )}
            />
          </div>
        </section>

        <aside className="space-y-4">
          {confirmationItems.length > 0 ? (
            <SoftCard>
              <SectionEyebrow>Что требует подтверждения</SectionEyebrow>
              <ul className="mt-4 space-y-3">
                {confirmationItems.slice(0, 8).map((item) => (
                  <li key={`${item.kind}-${item.title}`} className="text-sm leading-6">
                    <div className="font-medium text-slate-950">{item.title}</div>
                    <div className="text-xs text-slate-500">{item.kind}</div>
                  </li>
                ))}
              </ul>
            </SoftCard>
          ) : null}
        </aside>
      </div>
    </PanelIntro>
  );
}

function PassportPanel({ project }: { project: ProjectPassport }) {
  return (
    <PanelIntro title="Паспорт" description="Ключевой проектный контекст.">
      <div className="content-card overflow-hidden">
        <div className="grid lg:grid-cols-[minmax(0,1fr)_420px]">
          <div className="p-6">
            <SectionEyebrow>Основная информация</SectionEyebrow>
            <h3 className="mt-2 text-2xl font-semibold text-slate-950">
              Проект {formatCode(project.working_project_code || project.external_project_id)}
            </h3>
            <div className="mt-6 grid gap-x-8 gap-y-5 md:grid-cols-2">
              <PassportItem label="Внутренний код" value={project.project_code} />
              <PassportItem label="Код проекта" value={formatCode(project.external_project_id)} />
              <PassportItem label="Направление" value={formatDirection(project.direction)} />
              <PassportItem label="Масштаб" value={formatProjectScale(project.project_scale)} />
              <PassportItem label="Этап жизненного цикла" value={formatLifecycleStage(project.lifecycle_stage)} />
              <PassportItem label="Дата старта" value={formatText(project.start_date)} />
            </div>
          </div>

          <div className="bg-slate-950 p-6 text-white">
            <SectionEyebrow>Статус проекта</SectionEyebrow>
            <div className="mt-4">
              <StatusBadge value={formatProjectStatus(project.project_status)} />
            </div>
            <div className="mt-8 space-y-5">
              <PassportItem
                label="Основная операционная модель"
                value={formatOperationalModel(project.primary_operational_model)}
                inverted
              />
              <PassportItem
                label="Дополнительные контуры"
                value={formatText(project.additional_operational_contours)}
                inverted
              />
            </div>
          </div>
        </div>

        <div className="border-t border-slate-100 bg-white px-6 py-5">
          <PassportItem label="Известные регионы" value={formatText(project.known_regions)} />
        </div>
      </div>
    </PanelIntro>
  );
}

function GoalsPanel({
  goals,
  relationResolver,
}: {
  goals: Goal[];
  relationResolver: RelationResolver;
}) {
  const [relevance, setRelevance] = useState("");
  const [goalType, setGoalType] = useState("");
  const [priority, setPriority] = useState("");
  const priorityOptions = buildOptions(goals, (goal) => goal.priority, formatLooseText);
  const filteredGoals = goals.filter(
    (goal) =>
      matches(goal.relevance_status, relevance) &&
      matches(goal.goal_type, goalType) &&
      matches(goal.priority, priority),
  );

  if (goals.length === 0) {
    return <EmptyState title="Целей нет" description="В разделе пока нет целей проекта." />;
  }

  return (
    <PanelIntro title="Цели" description="Цели проекта и связанные критерии успеха.">
      <FilterBar>
        <SelectFilter
          label="Актуальность"
          value={relevance}
          onChange={setRelevance}
          options={buildOptions(goals, (goal) => goal.relevance_status, formatRelevanceStatus)}
        />
        <SelectFilter
          label="Тип цели"
          value={goalType}
          onChange={setGoalType}
          options={buildOptions(goals, (goal) => goal.goal_type, formatGoalType)}
        />
        {priorityOptions.length > 0 ? (
          <SelectFilter
            label="Приоритет"
            value={priority}
            onChange={setPriority}
            options={priorityOptions}
          />
        ) : null}
      </FilterBar>

      <div className="space-y-3">
        {filteredGoals.map((goal) => (
          <article key={goal.goal_code || goal.goal_text} className="content-card p-5">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div className="min-w-0">
                <div className="text-xs font-medium text-slate-400">
                  {formatEntityCode(goal.goal_code)}
                </div>
                <h3 className="mt-1 text-lg font-semibold leading-7 text-slate-950">
                  {goal.goal_text}
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                <StatusBadge value={formatRelevanceStatus(goal.relevance_status)} />
                {goal.priority ? <StatusBadge value={formatLooseText(goal.priority)} /> : null}
              </div>
            </div>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <Detail label="Тип" value={formatGoalType(goal.goal_type)} />
              <Detail label="KPI / критерий" value={relationResolver.format(goal.related_kpi_or_criterion_text)} />
              {goal.comment ? <Detail label="Комментарий" value={goal.comment} /> : null}
            </div>
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function LprsPanel({
  lprs,
  relationResolver,
}: {
  lprs: LprProfile[];
  relationResolver: RelationResolver;
}) {
  const [expandedCodes, setExpandedCodes] = useState<Set<string>>(new Set());

  if (lprs.length === 0) {
    return <EmptyState title="ЛПР нет" description="В разделе пока нет клиентских ролей." />;
  }

  function toggle(lprCode: string) {
    setExpandedCodes((current) => {
      const next = new Set(current);
      if (next.has(lprCode)) {
        next.delete(lprCode);
      } else {
        next.add(lprCode);
      }
      return next;
    });
  }

  return (
    <PanelIntro title="ЛПР" description="Ключевые клиентские роли и зоны влияния.">
      <InfluenceLegend />
      <div className="grid gap-4 xl:grid-cols-2">
        {lprs.map((lpr) => {
          const isExpanded = expandedCodes.has(lpr.lpr_code);
          return (
            <article key={lpr.lpr_code} className="content-card overflow-hidden">
              <button
                type="button"
                onClick={() => toggle(lpr.lpr_code)}
                className="flex w-full flex-col gap-4 p-5 text-left"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-slate-400">
                      {formatEntityCode(lpr.lpr_code)}
                    </div>
                    <h3 className="mt-1 text-lg font-semibold leading-7 text-slate-950">
                      Зона ответственности / влияния
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      {formatText(lpr.role_zone || lpr.role)}
                    </p>
                    {lpr.external_lpr_id ? (
                      <p className="mt-1 text-xs text-slate-500">
                        ID в базе данных: {lpr.external_lpr_id}
                      </p>
                    ) : null}
                  </div>
                  <ChevronDown
                    aria-hidden="true"
                    className={`mt-1 h-5 w-5 shrink-0 text-slate-400 transition ${
                      isExpanded ? "rotate-180" : ""
                    }`}
                  />
                </div>
                <div className="flex flex-wrap gap-2">
                  <StatusBadge value={formatInfluenceLevel(lpr.influence_level)} />
                  <StatusBadge value={formatActivityStatus(lpr.activity_status)} />
                  <StatusBadge value={formatRelationshipStatus(lpr.relationship_status)} />
                </div>
              </button>

              {isExpanded ? (
                <div className="border-t border-slate-100 bg-slate-50/80 p-5">
                  <div className="grid gap-3 md:grid-cols-2">
                    <Detail label="ЛПР" value={formatEntityCode(lpr.lpr_code)} />
                    <Detail label="Зона ответственности / влияния" value={formatText(lpr.role_zone || lpr.role)} />
                    <Detail label="ID в базе данных" value={formatText(lpr.external_lpr_id)} />
                    <Detail label="Уровень влияния" value={formatInfluenceLevel(lpr.influence_level)} />
                    <Detail label="Активность" value={formatActivityStatus(lpr.activity_status)} />
                    <Detail label="Отношение" value={formatRelationshipStatus(lpr.relationship_status)} />
                    <Detail label="Основание вывода" value={relationResolver.format(lpr.evidence_basis)} />
                  </div>
                  <ImportanceList factors={lpr.importance_factors} />
                </div>
              ) : null}
            </article>
          );
        })}
      </div>
    </PanelIntro>
  );
}

function BarriersPanel({
  barriers,
  relationResolver,
}: {
  barriers: Barrier[];
  relationResolver: RelationResolver;
}) {
  const [timeStatus, setTimeStatus] = useState("");
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confidence, setConfidence] = useState("");
  const filteredBarriers = barriers.filter(
    (barrier) =>
      matches(barrier.time_status, timeStatus) &&
      matches(barrier.relevance_status, relevance) &&
      matches(barrier.criticality, criticality) &&
      matches(barrier.confidence_level, confidence),
  );

  if (barriers.length === 0) {
    return <EmptyState title="Барьеров нет" description="В разделе пока нет барьеров." />;
  }

  return (
    <PanelIntro title="Барьеры" description="Барьеры, которые влияют на восприятие и устойчивость проекта.">
      <FilterBar>
        <SelectFilter
          label="Временной статус"
          value={timeStatus}
          onChange={setTimeStatus}
          options={buildOptions(barriers, (barrier) => barrier.time_status, formatBarrierTimeStatus)}
        />
        <SelectFilter
          label="Актуальность"
          value={relevance}
          onChange={setRelevance}
          options={buildOptions(barriers, (barrier) => barrier.relevance_status, formatRelevanceStatus)}
        />
        <SelectFilter
          label="Критичность"
          value={criticality}
          onChange={setCriticality}
          options={buildOptions(barriers, (barrier) => barrier.criticality, formatCriticality)}
        />
        <SelectFilter
          label="Уверенность"
          value={confidence}
          onChange={setConfidence}
          options={buildOptions(barriers, (barrier) => barrier.confidence_level, formatConfidenceLevel)}
        />
      </FilterBar>

      <div className="grid gap-4 2xl:grid-cols-2">
        {filteredBarriers.map((barrier) => (
          <article key={barrier.barrier_code || barrier.barrier_title} className="content-card p-5">
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge value={formatCriticality(barrier.criticality)} />
              <StatusBadge value={formatBarrierTimeStatus(barrier.time_status)} />
              <StatusBadge value={formatRelevanceStatus(barrier.relevance_status)} />
            </div>
            <h3 className="mt-4 text-lg font-semibold leading-7 text-slate-950">
              {barrier.barrier_title}
            </h3>
            {barrier.description ? (
              <p className="mt-2 text-sm leading-6 text-slate-600">{barrier.description}</p>
            ) : null}
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <Detail label="Тип" value={formatBarrierType(barrier.barrier_type)} />
              <Detail label="Статус" value={formatBarrierStatus(barrier.status)} />
              <Detail label="Уверенность" value={formatConfidenceLevel(barrier.confidence_level)} />
              <Detail label="Связанный KPI" value={relationResolver.format(barrier.linked_kpi_text)} />
            </div>
            <Evidence value={barrier.evidence_quote} />
            <SecondaryDetails sourceText={barrier.source_text} code={barrier.barrier_code} />
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function ExpectationsPanel({
  expectations,
  relationResolver,
}: {
  expectations: Expectation[];
  relationResolver: RelationResolver;
}) {
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confidence, setConfidence] = useState("");
  const filteredExpectations = expectations.filter(
    (expectation) =>
      matches(expectation.relevance_status, relevance) &&
      matches(expectation.criticality, criticality) &&
      matches(expectation.confidence_level, confidence),
  );

  if (expectations.length === 0) {
    return <EmptyState title="Ожиданий нет" description="В разделе пока нет ожиданий клиента." />;
  }

  return (
    <PanelIntro
      title="Ожидания клиента"
      description="То, по чему клиент оценивает пользу и качество проекта."
    >
      <FilterBar>
        <SelectFilter
          label="Актуальность"
          value={relevance}
          onChange={setRelevance}
          options={buildOptions(expectations, (item) => item.relevance_status, formatRelevanceStatus)}
        />
        <SelectFilter
          label="Критичность"
          value={criticality}
          onChange={setCriticality}
          options={buildOptions(expectations, (item) => item.criticality, formatCriticality)}
        />
        <SelectFilter
          label="Уверенность"
          value={confidence}
          onChange={setConfidence}
          options={buildOptions(expectations, (item) => item.confidence_level, formatConfidenceLevel)}
        />
      </FilterBar>

      <div className="grid gap-4 2xl:grid-cols-2">
        {filteredExpectations.map((expectation) => (
          <article
            key={expectation.expectation_code || expectation.expectation_text}
            className="content-card p-5"
          >
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge value={formatCriticality(expectation.criticality)} />
              <StatusBadge value={formatExplicitness(expectation.explicitness)} />
              <StatusBadge value={formatRelevanceStatus(expectation.relevance_status)} />
            </div>
            <h3 className="mt-4 text-lg font-semibold leading-7 text-slate-950">
              {expectation.expectation_text}
            </h3>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              <Detail label="Тип" value={formatExpectationType(expectation.expectation_type)} />
              <Detail label="Уверенность" value={formatConfidenceLevel(expectation.confidence_level)} />
              <Detail label="Связанный KPI" value={relationResolver.format(expectation.linked_kpi_text)} />
              <Detail label="Связанная важность" value={formatDisplayText(expectation.related_importance_text)} />
            </div>
            <Evidence value={expectation.evidence_quote} />
            <SecondaryDetails sourceText={expectation.source_text} code={expectation.expectation_code} />
          </article>
        ))}
      </div>
    </PanelIntro>
  );
}

function KpisPanel({
  kpis,
  relationResolver,
}: {
  kpis: Kpi[];
  relationResolver: RelationResolver;
}) {
  const [kpiType, setKpiType] = useState("");
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const filteredKpis = kpis.filter(
    (kpi) =>
      matches(kpi.kpi_type, kpiType) &&
      matches(kpi.relevance_status, relevance) &&
      matches(kpi.client_criticality, criticality) &&
      matches(kpi.requires_confirmation, confirmation),
  );

  if (kpis.length === 0) {
    return <EmptyState title="KPI нет" description="В разделе пока нет KPI и критериев." />;
  }

  return (
    <PanelIntro title="KPI" description="KPI и критерии успеха, связанные с ожиданиями и барьерами.">
      <FilterBar>
        <SelectFilter
          label="Тип KPI"
          value={kpiType}
          onChange={setKpiType}
          options={buildOptions(kpis, (kpi) => kpi.kpi_type, formatLooseText)}
        />
        <SelectFilter
          label="Актуальность"
          value={relevance}
          onChange={setRelevance}
          options={buildOptions(kpis, (kpi) => kpi.relevance_status, formatRelevanceStatus)}
        />
        <SelectFilter
          label="Критичность"
          value={criticality}
          onChange={setCriticality}
          options={buildOptions(kpis, (kpi) => kpi.client_criticality, formatCriticality)}
        />
        <SelectFilter
          label="Подтверждение"
          value={confirmation}
          onChange={setConfirmation}
          options={buildOptions(kpis, (kpi) => kpi.requires_confirmation, formatYesNo)}
        />
      </FilterBar>

      <DataTable
        headers={[
          "KPI / критерий",
          "Тип",
          "Актуальность",
          "Критичность",
          "Ожидание",
          "Барьер",
          "Комментарий",
        ]}
      >
        {filteredKpis.map((kpi) => (
          <tr key={kpi.kpi_code} className="align-top hover:bg-slate-50">
            <Cell
              value={
                <div>
                  <div className="font-medium text-slate-950">{kpi.kpi_name}</div>
                  <div className="mt-1 text-xs text-slate-400">{formatEntityCode(kpi.kpi_code)}</div>
                </div>
              }
            />
            <Cell value={formatLooseText(kpi.kpi_type)} />
            <Cell value={<StatusBadge value={formatRelevanceStatus(kpi.relevance_status)} />} />
            <Cell value={<StatusBadge value={formatCriticality(kpi.client_criticality)} />} />
            <Cell value={relationResolver.format(kpi.related_expectation_text)} />
            <Cell value={relationResolver.format(kpi.related_barrier_text)} />
            <Cell value={formatText(kpi.comment)} />
          </tr>
        ))}
      </DataTable>
    </PanelIntro>
  );
}

function CommunicationsPanel({
  communications,
  relationResolver,
}: {
  communications: CommunicationPoint[];
  relationResolver: RelationResolver;
}) {
  if (communications.length === 0) {
    return <EmptyState title="Коммуникаций нет" description="В разделе пока нет каналов взаимодействия." />;
  }

  return (
    <PanelIntro title="Коммуникации" description="Каналы, темы и частота взаимодействия.">
      <DataTable
        headers={[
          "Сторона клиента",
          "Сторона OPEN",
          "Тема",
          "Канал",
          "Частота",
          "Критичность",
          "Актуальность",
          "Комментарий",
        ]}
      >
        {communications.map((point) => (
          <tr key={point.communication_code || point.summary} className="align-top hover:bg-slate-50">
            <Cell
              value={
                <div>
                  <div className="font-medium text-slate-950">
                    {relationResolver.format(point.client_side)}
                  </div>
                  {point.external_lpr_id ? (
                    <div className="mt-1 text-xs text-slate-400">{point.external_lpr_id}</div>
                  ) : null}
                </div>
              }
            />
            <Cell value={formatText(point.open_side_role)} />
            <Cell value={formatText(point.topic_text || point.topic_type)} />
            <Cell value={formatCommunicationChannel(point.channel_text || point.channel_type || point.channel)} />
            <Cell value={formatCommunicationFrequency(point.frequency)} />
            <Cell value={<StatusBadge value={formatCriticality(point.criticality)} />} />
            <Cell value={<StatusBadge value={formatRelevanceStatus(point.relevance_status)} />} />
            <Cell value={formatText(point.comment)} />
          </tr>
        ))}
      </DataTable>
    </PanelIntro>
  );
}

function InfluenceLegend() {
  const items = [
    ["Высокое влияние", "Влияет на решение, бюджет, оценку проекта или ключевые условия."],
    ["Среднее влияние", "Отвечает за отдельные зоны и может влиять на операционную оценку."],
    ["Низкое влияние", "Участвует в коммуникации, но не определяет ключевые решения."],
    ["Требует подтверждения", "Нужно уточнить роль, активность или степень влияния в проекте."],
  ];

  return (
    <div className="content-card p-5">
      <SectionEyebrow>Как читать уровень влияния</SectionEyebrow>
      <div className="mt-4 grid gap-3 lg:grid-cols-4">
        {items.map(([title, description]) => (
          <div key={title} className="rounded-xl bg-slate-50 p-4 text-sm leading-6">
            <div className="font-semibold text-slate-950">{title}</div>
            <p className="mt-2 text-slate-600">{description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function ImportanceList({ factors }: { factors: LprImportanceFactor[] }) {
  if (factors.length === 0) {
    return (
      <div className="mt-5 rounded-xl bg-white p-4 text-sm text-slate-500">
        Что важно этому ЛПР пока не заполнено.
      </div>
    );
  }

  return (
    <div className="mt-5 space-y-3">
      <SectionEyebrow>Что важно этому ЛПР</SectionEyebrow>
      <div className="grid gap-3">
        {factors.map((factor) => (
          <div key={`${factor.factor_type}-${factor.factor_text}`} className="rounded-xl bg-white p-4">
            <div className="flex flex-wrap items-center gap-2">
              <StatusBadge value={factorTitle(factor)} />
              <StatusBadge value={formatCriticality(factor.criticality)} />
              <StatusBadge value={formatConfidenceLevel(factor.confidence_level)} />
            </div>
            {factor.evidence_quote ? (
              <p className="mt-3 text-sm leading-6 text-slate-600">{factor.evidence_quote}</p>
            ) : null}
          </div>
        ))}
      </div>
    </div>
  );
}

function PanelIntro({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  return (
    <section className="space-y-5">
      <div className="border-b border-slate-200 pb-4">
        <h2 className="text-2xl font-semibold text-slate-950">{title}</h2>
        <p className="mt-1 text-sm leading-6 text-slate-600">{description}</p>
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
  const displayValue = formatText(value);
  return (
    <div className="min-w-0 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200/80">
      <div className="text-xs font-semibold uppercase text-slate-400">{label}</div>
      <div className="mt-2 break-words text-sm text-slate-900">
        {badge ? <StatusBadge value={displayValue} /> : displayValue}
      </div>
    </div>
  );
}

function PassportItem({
  label,
  value,
  inverted = false,
}: {
  label: string;
  value: string | null;
  inverted?: boolean;
}) {
  return (
    <div className="min-w-0">
      <div className={`text-xs font-semibold uppercase ${inverted ? "text-slate-400" : "text-slate-400"}`}>
        {label}
      </div>
      <div
        className={`mt-1 break-words text-sm leading-6 ${
          inverted ? "text-white" : "text-slate-900"
        }`}
      >
        {formatText(value)}
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="min-w-0">
      <div className="text-xs font-semibold uppercase text-slate-400">{label}</div>
      <div className="mt-1 break-words text-sm leading-6 text-slate-700">
        {formatText(value)}
      </div>
    </div>
  );
}

function Evidence({ value }: { value: string | null }) {
  if (!value) {
    return null;
  }

  return (
    <div className="mt-4 rounded-xl bg-slate-50 p-4 ring-1 ring-slate-200/80">
      <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400">
        <MessageSquareText aria-hidden="true" className="h-3.5 w-3.5" />
        Доказательство / короткая цитата
      </div>
      <p className="mt-2 text-sm leading-6 text-slate-700">{value}</p>
    </div>
  );
}

function SecondaryDetails({ sourceText, code }: { sourceText: string | null; code: string | null }) {
  if (!sourceText && !code) {
    return null;
  }

  return (
    <details className="mt-4 rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-600 ring-1 ring-slate-200/80">
      <summary className="cursor-pointer font-medium text-slate-700">Дополнительно</summary>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        {code ? <Detail label="Код" value={formatEntityCode(code)} /> : null}
        {sourceText ? <Detail label="Источник" value={sourceText} /> : null}
      </div>
    </details>
  );
}

function FilterBar({ children }: { children: ReactNode }) {
  return (
    <div className="grid gap-3 rounded-xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/60 md:grid-cols-2 2xl:grid-cols-4">
      {children}
    </div>
  );
}

function SelectFilter({
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
    <label className="min-w-0 text-xs font-semibold uppercase text-slate-400">
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="mt-2 min-h-10 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm font-medium normal-case text-slate-800 outline-none transition focus:border-slate-400 focus:bg-white"
      >
        <option value="">Все</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function DataTable({ headers, children }: { headers: string[]; children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200/80 bg-white shadow-sm shadow-slate-200/70">
      <table className="min-w-[1040px] table-fixed text-left text-sm">
        <thead className="bg-slate-50 text-xs font-semibold uppercase text-slate-500">
          <tr>
            {headers.map((header) => (
              <th key={header} className="px-4 py-3">
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

function Cell({ value }: { value: ReactNode }) {
  return <td className="break-words px-4 py-4 leading-6 text-slate-700">{value}</td>;
}

function OverviewList<T>({
  title,
  items,
  emptyText,
  renderItem,
}: {
  title: string;
  items: T[];
  emptyText: string;
  renderItem: (item: T) => ReactNode;
}) {
  return (
    <SoftCard>
      <SectionEyebrow>{title}</SectionEyebrow>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">{emptyText}</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {items.map((item, index) => (
            <li key={index} className="rounded-xl bg-slate-50 p-3 text-sm leading-6">
              {renderItem(item)}
            </li>
          ))}
        </ul>
      )}
    </SoftCard>
  );
}

function SoftCard({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm shadow-slate-200/70">
      {children}
    </div>
  );
}

function SectionEyebrow({ children }: { children: ReactNode }) {
  return <div className="text-xs font-semibold uppercase text-slate-400">{children}</div>;
}

function ProjectLoading() {
  return (
    <div className="space-y-4" aria-label="Загрузка CJM проекта">
      <div className="h-10 w-40 animate-pulse rounded-lg bg-white shadow-sm" />
      <div className="h-72 animate-pulse rounded-2xl border border-slate-200 bg-white shadow-sm" />
      <div className="flex h-80 items-center justify-center rounded-2xl border border-slate-200 bg-white text-slate-400 shadow-sm">
        <Target aria-hidden="true" className="h-7 w-7 animate-pulse" />
      </div>
    </div>
  );
}

function buildRelationResolver(cjm: ProjectCjm) {
  const titles = new Map<string, string>();

  function remember(code: string | null | undefined, title: string | null | undefined) {
    const normalizedCode = normalize(code);
    const normalizedTitle = title?.trim();

    if (!normalizedCode || !normalizedTitle) {
      return;
    }

    titles.set(normalizedCode, normalizedTitle);

    const suffix = normalizedCode.match(/_0*(\d+)$/)?.[1];
    if (!suffix) {
      return;
    }

    if (normalizedCode.startsWith("expectation_")) {
      titles.set(`expect_${suffix.padStart(3, "0")}`, normalizedTitle);
    }
    if (normalizedCode.startsWith("expect_")) {
      titles.set(`expectation_${suffix.padStart(3, "0")}`, normalizedTitle);
    }
  }

  cjm.expectations.forEach((expectation) => {
    remember(expectation.expectation_code, expectation.expectation_text);
    remember(expectation.expectation_id, expectation.expectation_text);
  });
  cjm.barriers.forEach((barrier) => {
    remember(barrier.barrier_code, barrier.barrier_title);
    remember(barrier.barrier_id, barrier.barrier_title);
  });
  cjm.kpis.forEach((kpi) => {
    remember(kpi.kpi_code, kpi.kpi_name);
    remember(kpi.kpi_id, kpi.kpi_name);
  });

  function resolve(code: string) {
    const normalizedCode = normalize(code);
    return titles.get(normalizedCode) || formatEntityCode(code);
  }

  function format(value: string | null | undefined) {
    const original = value?.trim();
    if (!original) {
      return formatText(value);
    }

    return original.replace(
      /\b(goal|lpr|barrier|expectation|expect|kpi|comm|communication)_0*\d+\b/gi,
      (match) => resolve(match),
    );
  }

  return { format, resolve };
}

function buildConfirmationItems(cjm: ProjectCjm) {
  const items: Array<{ kind: string; title: string }> = [];

  cjm.goals.forEach((goal) => {
    if (isConfirmationRequired(goal.relevance_status)) {
      items.push({ kind: "Цель", title: goal.goal_text });
    }
  });
  cjm.barriers.forEach((barrier) => {
    if (isConfirmationRequired(barrier.relevance_status)) {
      items.push({ kind: "Барьер", title: barrier.barrier_title });
    }
  });
  cjm.expectations.forEach((expectation) => {
    if (isConfirmationRequired(expectation.relevance_status)) {
      items.push({ kind: "Ожидание", title: expectation.expectation_text });
    }
  });
  cjm.kpis.forEach((kpi) => {
    if (isConfirmationRequired(kpi.relevance_status) || isConfirmationRequired(kpi.requires_confirmation)) {
      items.push({ kind: "KPI", title: kpi.kpi_name });
    }
  });
  cjm.communications.forEach((point) => {
    if (isConfirmationRequired(point.relevance_status)) {
      items.push({ kind: "Коммуникация", title: formatText(point.topic_text || point.summary) });
    }
  });

  return items;
}

function buildOptions<T>(
  items: T[],
  accessor: (item: T) => string | null,
  formatter: Formatter,
) {
  const seen = new Set<string>();
  return items
    .map(accessor)
    .filter((value): value is string => Boolean(value?.trim()))
    .filter((value) => {
      if (seen.has(value)) {
        return false;
      }
      seen.add(value);
      return true;
    })
    .map((value) => ({ value, label: formatter(value) }))
    .sort((left, right) => left.label.localeCompare(right.label, "ru"));
}

function matches(value: string | null, selected: string) {
  return !selected || value === selected;
}

function factorTitle(factor: LprImportanceFactor) {
  const mappedFactor = formatImportanceFactor(factor.factor_type);
  if (mappedFactor !== "Другое" && mappedFactor !== "Не указано") {
    return mappedFactor;
  }

  return formatDisplayText(factor.factor_text);
}

function normalize(value: string | null | undefined) {
  return value?.trim().toLowerCase() || "";
}

function hasHighInfluence(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "high" || normalized.includes("высок");
}

function hasCurrentTimeStatus(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "current" || normalized.includes("сейчас");
}

function formatLooseText(value: string | null | undefined) {
  const text = formatDisplayText(value);
  if (/^[a-z]+(?:_[a-z]+)*$/.test(text)) {
    return "Не указано";
  }
  return text;
}

function formatDisplayText(value: string | null | undefined) {
  const text = formatText(value);
  if (text === "Не указано" || /^[A-ZА-ЯЁ0-9/.\-\s]+$/.test(text)) {
    return text;
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
}
