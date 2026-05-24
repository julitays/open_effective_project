import {
  ArrowLeft,
  ChevronDown,
  MessageSquareText,
  Pencil,
  Target,
} from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { Link, useOutletContext, useParams } from "react-router-dom";

import {
  getProjectCjm,
  updateBarrier,
  updateCommunication,
  updateExpectation,
  updateGoal,
  updateKpi,
  updateLpr,
  updateProject,
  type PatchPayload,
} from "../api/projects";
import type { LayoutOutletContext } from "../components/Layout";
import EditEntityModal, {
  type EditOption,
  type EditField,
  type EditPayload,
  type EditValues,
} from "../components/EditEntityModal";
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
  formatKpiType,
  formatLifecycleStage,
  formatOperationalModel,
  formatPriority,
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
type EditTarget = {
  title: string;
  fields: EditField[];
  values: EditValues;
  save: (payload: PatchPayload) => Promise<unknown>;
};

const criticalityOptions = [
  option("high", formatCriticality),
  option("medium", formatCriticality),
  option("low", formatCriticality),
  option("unknown", formatCriticality),
];
const relevanceOptions = [
  option("actual", formatRelevanceStatus),
  option("current", formatRelevanceStatus),
  option("historical", formatRelevanceStatus),
  option("requires_confirmation", formatRelevanceStatus),
  option("not_actual", formatRelevanceStatus),
  option("unknown", formatRelevanceStatus),
];
const confidenceOptions = [
  option("high", formatConfidenceLevel),
  option("medium", formatConfidenceLevel),
  option("low", formatConfidenceLevel),
  option("unknown", formatConfidenceLevel),
];
const influenceOptions = [
  option("high", formatInfluenceLevel),
  option("medium", formatInfluenceLevel),
  option("low", formatInfluenceLevel),
  option("requires_confirmation", formatInfluenceLevel),
  option("unknown", formatInfluenceLevel),
];
const activityOptions = [
  option("active", formatActivityStatus),
  option("inactive", formatActivityStatus),
  option("requires_confirmation", formatActivityStatus),
  option("historical", formatActivityStatus),
  option("unknown", formatActivityStatus),
];
const barrierTypeOptions = [
  option("communication", formatBarrierType),
  option("execution_quality", formatBarrierType),
  option("reporting", formatBarrierType),
  option("timing", formatBarrierType),
  option("staff", formatBarrierType),
  option("kpi", formatBarrierType),
  option("cost", formatBarrierType),
  option("training", formatBarrierType),
  option("control", formatBarrierType),
  option("expectations", formatBarrierType),
  option("process_organization", formatBarrierType),
  option("other", formatBarrierType),
];
const barrierTimeOptions = [
  option("past", formatBarrierTimeStatus),
  option("current", formatBarrierTimeStatus),
  option("future", formatBarrierTimeStatus),
  option("repeated", formatBarrierTimeStatus),
];
const barrierStatusOptions = [
  option("open", formatBarrierStatus),
  option("in_progress", formatBarrierStatus),
  option("contained", formatBarrierStatus),
  option("resolved", formatBarrierStatus),
  option("monitoring", formatBarrierStatus),
  option("unknown", formatBarrierStatus),
];
const expectationTypeOptions = [
  option("speed", formatExpectationType),
  option("quality", formatExpectationType),
  option("reporting", formatExpectationType),
  option("initiative", formatExpectationType),
  option("transparency", formatExpectationType),
  option("cost", formatExpectationType),
  option("expertise", formatExpectationType),
  option("predictability", formatExpectationType),
  option("minimum_manual_control", formatExpectationType),
  option("flexibility", formatExpectationType),
  option("agreements_compliance", formatExpectationType),
  option("other", formatExpectationType),
];
const explicitnessOptions = [
  option("explicit", formatExplicitness),
  option("implicit", formatExplicitness),
  option("unknown", formatExplicitness),
];
const goalTypeOptions = [
  option("open_internal", formatGoalType),
  option("client_business", formatGoalType),
  option("joint_project", formatGoalType),
  option("service", formatGoalType),
  option("operational", formatGoalType),
  option("financial", formatGoalType),
  option("risk_control", formatGoalType),
  option("other", formatGoalType),
];
const prioritySelectOptions = [
  option("high", formatPriority),
  option("medium", formatPriority),
  option("low", formatPriority),
  option("unknown", formatPriority),
];
const relationshipOptions = [
  option("loyal", formatRelationshipStatus),
  option("neutral", formatRelationshipStatus),
  option("cautious", formatRelationshipStatus),
  option("critical", formatRelationshipStatus),
  option("unknown", formatRelationshipStatus),
];
const confirmationOptions = [
  option("yes", formatYesNo),
  option("no", formatYesNo),
  option("requires_confirmation", formatYesNo),
  option("unknown", formatYesNo),
];
const kpiTypeOptions = [
  option("service", formatKpiType),
  option("operational", formatKpiType),
  option("financial", formatKpiType),
  option("quality", formatKpiType),
  option("commercial", formatKpiType),
  option("other", formatKpiType),
];

const projectEditFields: EditField[] = [
  { name: "short_description", label: "Краткое описание", input: "textarea" },
  { name: "known_regions", label: "Известные регионы", input: "textarea" },
  {
    name: "primary_operational_model",
    label: "Основная операционная модель",
    input: "select",
    options: [
      option("merchandising", formatOperationalModel),
      option("combined_merchandising", formatOperationalModel),
      option("promo_consulting", formatOperationalModel),
      option("kaf", formatOperationalModel),
      option("training", formatOperationalModel),
      option("audit_quality_control", formatOperationalModel),
      option("analytics_reporting", formatOperationalModel),
      option("mixed", formatOperationalModel),
      option("other", formatOperationalModel),
    ],
  },
  {
    name: "additional_operational_contours",
    label: "Дополнительные операционные контуры",
    input: "textarea",
  },
  {
    name: "lifecycle_stage",
    label: "Этап жизненного цикла",
    input: "select",
    options: [
      option("launch", formatLifecycleStage),
      option("stabilization", formatLifecycleStage),
      option("development", formatLifecycleStage),
      option("retention", formatLifecycleStage),
      option("restart", formatLifecycleStage),
      option("risk", formatLifecycleStage),
      option("closing", formatLifecycleStage),
      option("unknown", formatLifecycleStage),
    ],
  },
  {
    name: "project_status",
    label: "Статус проекта",
    input: "select",
    options: [
      option("active", formatProjectStatus),
      option("completed", formatProjectStatus),
      option("pilot", formatProjectStatus),
      option("at_risk", formatProjectStatus),
      option("unknown", formatProjectStatus),
    ],
  },
];

const lprEditFields: EditField[] = [
  { name: "role_zone", label: "Место в структуре / зона влияния", input: "textarea" },
  { name: "influence_level", label: "Уровень влияния", input: "select", options: influenceOptions },
  { name: "activity_status", label: "Статус активности", input: "select", options: activityOptions },
  { name: "relationship_status", label: "Отношение", input: "select", options: relationshipOptions },
  { name: "evidence_basis", label: "Основание вывода", input: "textarea" },
  { name: "manual_comment", label: "Комментарий для ручного уточнения", input: "textarea" },
];

function option(value: string, formatter: Formatter) {
  return { value, label: formatter(value) };
}

function pickValues(entity: object, fields: EditField[]): EditValues {
  const record = entity as Record<string, string | null | undefined>;
  return fields.reduce<EditValues>((values, field) => {
    values[field.name] = record[field.name] ?? "";
    return values;
  }, {});
}

function buildGoalEditFields(cjm: ProjectCjm): EditField[] {
  return [
    { name: "goal_owner", label: "Владелец цели" },
    { name: "goal_type", label: "Тип цели", input: "select", options: goalTypeOptions },
    { name: "goal_text", label: "Текст цели", input: "textarea" },
    { name: "priority", label: "Приоритет", input: "select", options: prioritySelectOptions },
    {
      name: "related_kpi_or_criterion_text",
      label: "Связанные KPI / критерии",
      input: "multiselect",
      options: buildKpiRelationOptions(cjm.kpis),
    },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

function buildBarrierEditFields(cjm: ProjectCjm): EditField[] {
  return [
    { name: "barrier_title", label: "Название барьера", input: "textarea" },
    { name: "barrier_type", label: "Тип барьера", input: "select", options: barrierTypeOptions },
    { name: "time_status", label: "Временной статус", input: "select", options: barrierTimeOptions },
    { name: "description", label: "Описание барьера", input: "textarea" },
    { name: "criticality", label: "Критичность", input: "select", options: criticalityOptions },
    {
      name: "related_importance_text",
      label: "Связанные важности",
      input: "multiselect",
      options: buildImportanceRelationOptions(cjm.lprs),
    },
    {
      name: "linked_kpi_text",
      label: "Связанные KPI",
      input: "multiselect",
      options: buildKpiRelationOptions(cjm.kpis),
    },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "evidence_quote", label: "Доказательство / короткая цитата", input: "textarea" },
    { name: "status", label: "Статус", input: "select", options: barrierStatusOptions },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "confidence_level", label: "Уверенность", input: "select", options: confidenceOptions },
  ];
}

function buildExpectationEditFields(cjm: ProjectCjm): EditField[] {
  return [
    { name: "expectation_text", label: "Ожидание клиента", input: "textarea" },
    { name: "expectation_type", label: "Тип ожидания", input: "select", options: expectationTypeOptions },
    { name: "explicitness", label: "Явное или неявное", input: "select", options: explicitnessOptions },
    { name: "criticality", label: "Критичность", input: "select", options: criticalityOptions },
    {
      name: "related_importance_text",
      label: "Связанные важности",
      input: "multiselect",
      options: buildImportanceRelationOptions(cjm.lprs),
    },
    {
      name: "linked_kpi_text",
      label: "Связанные KPI",
      input: "multiselect",
      options: buildKpiRelationOptions(cjm.kpis),
    },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "evidence_quote", label: "Доказательство / короткая цитата", input: "textarea" },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "confidence_level", label: "Уверенность", input: "select", options: confidenceOptions },
  ];
}

function buildKpiEditFields(cjm: ProjectCjm): EditField[] {
  return [
    { name: "kpi_name", label: "Название KPI / критерия", input: "textarea" },
    {
      name: "kpi_type",
      label: "Тип KPI",
      input: "select",
      options: mergeOptions(kpiTypeOptions, buildRawOptions(cjm.kpis, (kpi) => kpi.kpi_type, formatKpiType)),
    },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    {
      name: "related_expectation_text",
      label: "Связанные ожидания",
      input: "multiselect",
      options: buildExpectationRelationOptions(cjm.expectations),
    },
    {
      name: "related_barrier_text",
      label: "Связанные барьеры",
      input: "multiselect",
      options: buildBarrierRelationOptions(cjm.barriers),
    },
    { name: "client_criticality", label: "Критичность для клиента", input: "select", options: criticalityOptions },
    { name: "requires_confirmation", label: "Требует подтверждения", input: "select", options: confirmationOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

function buildCommunicationEditFields(cjm: ProjectCjm): EditField[] {
  return [
    {
      name: "client_side",
      label: "Сторона клиента",
      input: "select",
      options: buildLprRelationOptions(cjm.lprs),
    },
    { name: "external_lpr_id", label: "ID в базе данных" },
    { name: "open_side_role", label: "Сторона OPEN: роль", input: "textarea" },
    { name: "topic_text", label: "Тема взаимодействия", input: "textarea" },
    { name: "channel_text", label: "Канал" },
    { name: "frequency", label: "Частота" },
    { name: "criticality", label: "Критичность", input: "select", options: criticalityOptions },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

function buildKpiRelationOptions(kpis: Kpi[]) {
  return uniqueOptions(
    kpis.map((kpi) => ({
      value: kpi.kpi_code || kpi.kpi_name,
      label: kpi.kpi_name,
    })),
  );
}

function buildImportanceRelationOptions(lprs: LprProfile[]) {
  return uniqueOptions(
    lprs.flatMap((lpr) =>
      lpr.importance_factors.map((factor) => {
        const title = factorTitle(factor);
        return {
          value: title,
          label: `${title} · ${formatEntityCode(lpr.lpr_code)}`,
        };
      }),
    ),
  );
}

function buildExpectationRelationOptions(expectations: Expectation[]) {
  return uniqueOptions(
    expectations.map((expectation) => ({
      value: expectation.expectation_code || expectation.expectation_text,
      label: expectation.expectation_text,
    })),
  );
}

function buildBarrierRelationOptions(barriers: Barrier[]) {
  return uniqueOptions(
    barriers.map((barrier) => ({
      value: barrier.barrier_code || barrier.barrier_title,
      label: barrier.barrier_title,
    })),
  );
}

function buildLprRelationOptions(lprs: LprProfile[]) {
  return uniqueOptions(
    lprs.map((lpr) => ({
      value: lpr.lpr_code,
      label: `${formatText(lpr.role_zone || lpr.role)} · ${formatEntityCode(lpr.lpr_code)}`,
    })),
  );
}

function mergeOptions(...groups: EditOption[][]) {
  return uniqueOptions(groups.flat());
}

function uniqueOptions(options: EditOption[]) {
  const seen = new Set<string>();
  return options.filter((option) => {
    const key = normalize(option.value);
    if (!option.value || !option.label || seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function buildRawOptions<T>(
  items: T[],
  accessor: (item: T) => string | null,
  formatter: Formatter,
) {
  const seenLabels = new Set<string>();
  return items
    .map(accessor)
    .filter((value): value is string => Boolean(value?.trim()))
    .map((value) => ({ value, label: formatter(value) }))
    .filter((option) => {
      const normalizedLabel = normalize(option.label);
      if (!normalizedLabel || seenLabels.has(normalizedLabel)) {
        return false;
      }
      seenLabels.add(normalizedLabel);
      return true;
    });
}

export default function ProjectCjmPage() {
  const { projectCode } = useParams();
  const { activeCjmTab: activeTab } = useOutletContext<LayoutOutletContext>();
  const [projectCjm, setProjectCjm] = useState<ProjectCjm | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [editTarget, setEditTarget] = useState<EditTarget | null>(null);
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);

  async function loadCjm(signal?: AbortSignal) {
    if (!projectCode) {
      setError("В адресе не найден код проекта.");
      setLoading(false);
      return;
    }

    setLoading(true);
    getProjectCjm(projectCode, signal)
      .then((payload) => {
        setProjectCjm(payload);
        setError(null);
      })
      .catch((cause: unknown) => {
        if (!signal?.aborted) {
          setError(cause instanceof Error ? cause.message : "Не удалось загрузить CJM.");
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

    void loadCjm(controller.signal);

    return () => controller.abort();
  }, [projectCode]);

  function openEdit(target: EditTarget) {
    setEditTarget(target);
    setEditError(null);
  }

  async function saveEdit(payload: EditPayload) {
    if (!editTarget || !projectCode) {
      return;
    }

    setEditSaving(true);
    setEditError(null);
    try {
      await editTarget.save(payload);
      const refreshed = await getProjectCjm(projectCode);
      setProjectCjm(refreshed);
      setEditTarget(null);
    } catch (cause) {
      setEditError(cause instanceof Error ? cause.message : "Не удалось сохранить правку.");
    } finally {
      setEditSaving(false);
    }
  }

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
          <PassportPanel
            project={projectCjm.project}
            onEdit={() =>
              openEdit({
                title: "Паспорт проекта",
                fields: projectEditFields,
                values: pickValues(projectCjm.project, projectEditFields),
                save: (payload) => updateProject(projectCjm.project.project_code, payload),
              })
            }
          />
        ) : null}
        {activeTab === "goals" ? (
          <GoalsPanel
            goals={projectCjm.goals}
            relationResolver={relationResolver}
            onEdit={(goal) =>
              openEdit({
                title: formatEntityCode(goal.goal_code),
                fields: buildGoalEditFields(projectCjm),
                values: pickValues(goal, buildGoalEditFields(projectCjm)),
                save: (payload) =>
                  updateGoal(projectCjm.project.project_code, goal.goal_code || "", payload),
              })
            }
          />
        ) : null}
        {activeTab === "lprs" ? (
          <LprsPanel
            lprs={projectCjm.lprs}
            relationResolver={relationResolver}
            onEdit={(lpr) =>
              openEdit({
                title: formatEntityCode(lpr.lpr_code),
                fields: lprEditFields,
                values: pickValues(lpr, lprEditFields),
                save: (payload) => updateLpr(projectCjm.project.project_code, lpr.lpr_code, payload),
              })
            }
          />
        ) : null}
        {activeTab === "barriers" ? (
            <BarriersPanel
              barriers={projectCjm.barriers}
              relationResolver={relationResolver}
              onEdit={(barrier) =>
                openEdit({
                  title: barrier.barrier_title,
                  fields: buildBarrierEditFields(projectCjm),
                  values: pickValues(barrier, buildBarrierEditFields(projectCjm)),
                  save: (payload) =>
                    updateBarrier(projectCjm.project.project_code, barrier.barrier_code || "", payload),
                })
              }
            />
        ) : null}
        {activeTab === "expectations" ? (
            <ExpectationsPanel
              expectations={projectCjm.expectations}
              relationResolver={relationResolver}
              onEdit={(expectation) =>
                openEdit({
                  title: expectation.expectation_text,
                  fields: buildExpectationEditFields(projectCjm),
                  values: pickValues(expectation, buildExpectationEditFields(projectCjm)),
                  save: (payload) =>
                    updateExpectation(
                      projectCjm.project.project_code,
                      expectation.expectation_code || "",
                      payload,
                    ),
                })
              }
            />
          ) : null}
        {activeTab === "kpis" ? (
          <KpisPanel
            kpis={projectCjm.kpis}
            relationResolver={relationResolver}
            onEdit={(kpi) =>
              openEdit({
                title: kpi.kpi_name,
                fields: buildKpiEditFields(projectCjm),
                values: pickValues(kpi, buildKpiEditFields(projectCjm)),
                save: (payload) => updateKpi(projectCjm.project.project_code, kpi.kpi_code, payload),
              })
            }
          />
        ) : null}
        {activeTab === "communications" ? (
          <CommunicationsPanel
            communications={projectCjm.communications}
            relationResolver={relationResolver}
            onEdit={(point) =>
              openEdit({
                title: formatText(point.topic_text || point.summary),
                fields: buildCommunicationEditFields(projectCjm),
                values: pickValues(point, buildCommunicationEditFields(projectCjm)),
                save: (payload) =>
                  updateCommunication(
                    projectCjm.project.project_code,
                    point.communication_code || "",
                    payload,
                  ),
              })
            }
          />
        ) : null}
      </div>

      {editTarget ? (
        <EditEntityModal
          title={editTarget.title}
          fields={editTarget.fields}
          values={editTarget.values}
          saving={editSaving}
          error={editError}
          onClose={() => {
            if (!editSaving) {
              setEditTarget(null);
            }
          }}
          onSave={saveEdit}
        />
      ) : null}
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

function EditButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium leading-5 text-slate-700 ring-1 ring-slate-100 hover:bg-slate-50"
    >
      <Pencil aria-hidden="true" className="h-3.5 w-3.5" />
      Редактировать
    </button>
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
  const criticalClientItems = buildCriticalClientItems(cjm);
  const mainRiskItems = buildMainRiskItems(cjm);
  const barrierGroups = groupBarriersByTime(cjm.barriers);
  const completenessItems = buildCompletenessItems(cjm);

  return (
    <PanelIntro
      title="CJM проекта: рабочий обзор"
      description="Сжатая управленческая карта клиента: что важно, где болит, кто влияет на решение и какие барьеры надо держать под контролем."
    >
      <div className="grid gap-4 lg:grid-cols-3">
        <OverviewMetric label="Направление" value={formatDirection(cjm.project.direction)} />
        <OverviewMetric label="Этап жизненного цикла" value={formatLifecycleStage(cjm.project.lifecycle_stage)} />
        <OverviewMetric label="Статус проекта" value={formatProjectStatus(cjm.project.project_status)} />
      </div>

      <div className="grid gap-4 2xl:grid-cols-[minmax(0,1fr)_380px]">
        <MainFindingsCard
          criticalClientItems={criticalClientItems}
          mainRiskItems={mainRiskItems}
        />

        <CompletenessCard items={completenessItems} />

        <div className="2xl:col-span-2">
          <BarrierTimelineCard groups={barrierGroups} relationResolver={relationResolver} />
        </div>
      </div>
    </PanelIntro>
  );
}

function OverviewMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="content-card p-5">
      <SectionEyebrow>{label}</SectionEyebrow>
      <div className="mt-2 text-base font-medium text-slate-950">{value}</div>
    </div>
  );
}

function MainFindingsCard({
  criticalClientItems,
  mainRiskItems,
}: {
  criticalClientItems: string[];
  mainRiskItems: string[];
}) {
  return (
    <SoftCard>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-base font-semibold text-slate-950">Главные выводы по CJM</h3>
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <FindingColumn title="Что критично клиенту" items={criticalClientItems} />
        <FindingColumn title="Где основной риск" items={mainRiskItems} />
      </div>
    </SoftCard>
  );
}

function FindingColumn({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-xl bg-slate-50 p-4">
      <div className="text-sm font-semibold text-slate-950">{title}</div>
      {items.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
          {items.slice(0, 5).map((item) => (
            <li key={item}>• {item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-3 text-sm leading-6 text-slate-500">Данных для вывода пока недостаточно.</p>
      )}
    </div>
  );
}

function BarrierTimelineCard({
  groups,
  relationResolver,
}: {
  groups: ReturnType<typeof groupBarriersByTime>;
  relationResolver: RelationResolver;
}) {
  return (
    <SoftCard>
      <h3 className="text-base font-semibold text-slate-950">Барьеры: было / есть / будет</h3>
      <div className="mt-5 grid gap-4 xl:grid-cols-3">
        <BarrierTimelineColumn
          title="Было"
          tone="past"
          barriers={groups.past}
          relationResolver={relationResolver}
        />
        <BarrierTimelineColumn
          title="Есть сейчас"
          tone="current"
          barriers={groups.current}
          relationResolver={relationResolver}
        />
        <BarrierTimelineColumn
          title="Будет"
          tone="future"
          barriers={groups.future}
          relationResolver={relationResolver}
        />
      </div>
    </SoftCard>
  );
}

function BarrierTimelineColumn({
  title,
  tone,
  barriers,
  relationResolver,
}: {
  title: string;
  tone: "past" | "current" | "future";
  barriers: Barrier[];
  relationResolver: RelationResolver;
}) {
  const toneClass = {
    past: "border-slate-200 bg-slate-50",
    current: "border-amber-200 bg-amber-50/70",
    future: "border-rose-200 bg-rose-50/70",
  }[tone];

  return (
    <section className={`rounded-xl border p-4 ${toneClass}`}>
      <h4 className="text-sm font-semibold text-slate-950">{title}</h4>
      {barriers.length > 0 ? (
        <div className="mt-3 space-y-3">
          {barriers.slice(0, 3).map((barrier) => (
            <article key={barrier.barrier_code || barrier.barrier_title} className="rounded-xl bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <h5 className="min-w-0 text-sm font-semibold leading-6 text-slate-950">
                  {barrier.barrier_title}
                </h5>
                <StatusBadge value={formatCriticality(barrier.criticality)} />
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-600">
                {formatText(barrier.description || relationResolver.format(barrier.linked_kpi_text))}
              </p>
            </article>
          ))}
        </div>
      ) : (
        <p className="mt-3 rounded-xl bg-white p-4 text-sm leading-6 text-slate-500">
          В этом временном контуре барьеры не выделены.
        </p>
      )}
    </section>
  );
}

function CompletenessCard({ items }: { items: Array<{ label: string; percent: number }> }) {
  return (
    <SoftCard>
      <h3 className="text-base font-semibold text-slate-950">Полнота CJM</h3>
      <div className="mt-5 space-y-4">
        {items.map((item) => (
          <div key={item.label}>
            <div className="flex items-center justify-between gap-3 text-xs text-slate-600">
              <span>{item.label}</span>
              <span>{item.percent}%</span>
            </div>
            <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-slate-900"
                style={{ width: `${item.percent}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </SoftCard>
  );
}

function PassportPanel({
  project,
  onEdit,
}: {
  project: ProjectPassport;
  onEdit: () => void;
}) {
  return (
    <PanelIntro title="Паспорт" description="Ключевой проектный контекст.">
      <div className="content-card overflow-hidden">
        <div className="grid lg:grid-cols-[minmax(0,1fr)_420px]">
          <div className="p-6">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <SectionEyebrow>Основная информация</SectionEyebrow>
              <EditButton onClick={onEdit} />
            </div>
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
  onEdit,
}: {
  goals: Goal[];
  relationResolver: RelationResolver;
  onEdit: (goal: Goal) => void;
}) {
  const [relevance, setRelevance] = useState("");
  const [goalType, setGoalType] = useState("");
  const [priority, setPriority] = useState("");
  const priorityOptions = buildOptions(goals, (goal) => goal.priority, formatPriority);
  const filteredGoals = goals.filter(
    (goal) =>
      matchesByLabel(goal.relevance_status, relevance, formatRelevanceStatus) &&
      matchesByLabel(goal.goal_type, goalType, formatGoalType) &&
      matchesByLabel(goal.priority, priority, formatPriority),
  );
  const openGoals = filteredGoals.filter((goal) => !isClientGoal(goal));
  const clientGoals = filteredGoals.filter(isClientGoal);

  if (goals.length === 0) {
    return <EmptyState title="Целей нет" description="В разделе пока нет целей проекта." />;
  }

  return (
    <PanelIntro
      title="Цели OPEN и клиента"
      description="Слева — цели OPEN и проектной команды, справа — цели клиента."
    >
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

      <div className="grid gap-4 xl:grid-cols-2">
        <GoalColumn
          title="Цели OPEN"
          emptyText="Цели OPEN пока не заполнены."
          goals={openGoals}
          relationResolver={relationResolver}
          onEdit={onEdit}
        />
        <GoalColumn
          title="Цели клиента"
          emptyText="Цели клиента пока не заполнены."
          goals={clientGoals}
          relationResolver={relationResolver}
          onEdit={onEdit}
        />
      </div>
    </PanelIntro>
  );
}

function GoalColumn({
  title,
  emptyText,
  goals,
  relationResolver,
  onEdit,
}: {
  title: string;
  emptyText: string;
  goals: Goal[];
  relationResolver: RelationResolver;
  onEdit: (goal: Goal) => void;
}) {
  return (
    <section className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm shadow-slate-200/70">
      <h3 className="text-base font-semibold text-slate-950">{title}</h3>
      {goals.length > 0 ? (
        <div className="mt-4 space-y-3">
          {goals.map((goal) => (
            <GoalCard
              key={goal.goal_code || goal.goal_text}
              goal={goal}
              relationResolver={relationResolver}
              onEdit={onEdit}
            />
          ))}
        </div>
      ) : (
        <p className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">{emptyText}</p>
      )}
    </section>
  );
}

function GoalCard({
  goal,
  relationResolver,
  onEdit,
}: {
  goal: Goal;
  relationResolver: RelationResolver;
  onEdit: (goal: Goal) => void;
}) {
  return (
    <article className="rounded-xl border border-slate-200/80 bg-slate-50/70 p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="text-xs font-medium text-slate-400">
            {formatEntityCode(goal.goal_code)}
          </div>
          <h4 className="mt-1 text-base font-semibold leading-7 text-slate-950">
            {goal.goal_text}
          </h4>
        </div>
        <div className="flex flex-wrap gap-2">
          <StatusBadge value={formatRelevanceStatus(goal.relevance_status)} />
          {goal.priority ? <StatusBadge value={formatPriority(goal.priority)} /> : null}
          {goal.goal_code ? <EditButton onClick={() => onEdit(goal)} /> : null}
        </div>
      </div>
      <div className="mt-4 grid gap-3">
        <Detail label="Тип" value={formatGoalType(goal.goal_type)} />
        <Detail label="KPI / критерий" value={relationResolver.format(goal.related_kpi_or_criterion_text)} />
        {goal.comment ? <Detail label="Комментарий" value={goal.comment} /> : null}
      </div>
    </article>
  );
}

function LprsPanel({
  lprs,
  relationResolver,
  onEdit,
}: {
  lprs: LprProfile[];
  relationResolver: RelationResolver;
  onEdit: (lpr: LprProfile) => void;
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
                      {formatText(lpr.role_zone || lpr.role)}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      Место в структуре и зона влияния
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
                  <span
                    role="button"
                    tabIndex={0}
                    onClick={(event) => {
                      event.stopPropagation();
                      onEdit(lpr);
                    }}
                    onKeyDown={(event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        event.stopPropagation();
                        onEdit(lpr);
                      }
                    }}
                    className="inline-flex min-h-8 items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-medium leading-5 text-slate-700 ring-1 ring-slate-100 hover:bg-slate-50"
                  >
                    <Pencil aria-hidden="true" className="h-3.5 w-3.5" />
                    Редактировать
                  </span>
                </div>
              </button>

              {isExpanded ? (
                <div className="border-t border-slate-100 bg-slate-50/80 p-5">
                  <div className="grid gap-3 md:grid-cols-2">
                    <Detail label="ЛПР" value={formatEntityCode(lpr.lpr_code)} />
                    <Detail label="Место в структуре / зона влияния" value={formatText(lpr.role_zone || lpr.role)} />
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
  onEdit,
}: {
  barriers: Barrier[];
  relationResolver: RelationResolver;
  onEdit: (barrier: Barrier) => void;
}) {
  const [timeStatus, setTimeStatus] = useState("");
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confidence, setConfidence] = useState("");
  const filteredBarriers = barriers.filter(
    (barrier) =>
      matchesByLabel(barrier.time_status, timeStatus, formatBarrierTimeStatus) &&
      matchesByLabel(barrier.relevance_status, relevance, formatRelevanceStatus) &&
      matchesByLabel(barrier.criticality, criticality, formatCriticality) &&
      matchesByLabel(barrier.confidence_level, confidence, formatConfidenceLevel),
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
              {barrier.barrier_code ? <EditButton onClick={() => onEdit(barrier)} /> : null}
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
  onEdit,
}: {
  expectations: Expectation[];
  relationResolver: RelationResolver;
  onEdit: (expectation: Expectation) => void;
}) {
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confidence, setConfidence] = useState("");
  const filteredExpectations = expectations.filter(
    (expectation) =>
      matchesByLabel(expectation.relevance_status, relevance, formatRelevanceStatus) &&
      matchesByLabel(expectation.criticality, criticality, formatCriticality) &&
      matchesByLabel(expectation.confidence_level, confidence, formatConfidenceLevel),
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
              {expectation.expectation_code ? (
                <EditButton onClick={() => onEdit(expectation)} />
              ) : null}
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
  onEdit,
}: {
  kpis: Kpi[];
  relationResolver: RelationResolver;
  onEdit: (kpi: Kpi) => void;
}) {
  const [kpiType, setKpiType] = useState("");
  const [relevance, setRelevance] = useState("");
  const [criticality, setCriticality] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const filteredKpis = kpis.filter(
    (kpi) =>
      matchesByLabel(kpi.kpi_type, kpiType, formatKpiType) &&
      matchesByLabel(kpi.relevance_status, relevance, formatRelevanceStatus) &&
      matchesByLabel(kpi.client_criticality, criticality, formatCriticality) &&
      matchesByLabel(kpi.requires_confirmation, confirmation, formatYesNo),
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
          options={buildOptions(kpis, (kpi) => kpi.kpi_type, formatKpiType)}
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
          "",
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
            <Cell value={formatKpiType(kpi.kpi_type)} />
            <Cell value={<StatusBadge value={formatRelevanceStatus(kpi.relevance_status)} />} />
            <Cell value={<StatusBadge value={formatCriticality(kpi.client_criticality)} />} />
            <Cell value={relationResolver.format(kpi.related_expectation_text)} />
            <Cell value={relationResolver.format(kpi.related_barrier_text)} />
            <Cell value={formatText(kpi.comment)} />
            <Cell value={<EditButton onClick={() => onEdit(kpi)} />} />
          </tr>
        ))}
      </DataTable>
    </PanelIntro>
  );
}

function CommunicationsPanel({
  communications,
  relationResolver,
  onEdit,
}: {
  communications: CommunicationPoint[];
  relationResolver: RelationResolver;
  onEdit: (point: CommunicationPoint) => void;
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
          "",
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
            <Cell
              value={
                point.communication_code ? <EditButton onClick={() => onEdit(point)} /> : null
              }
            />
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

function buildCriticalClientItems(cjm: ProjectCjm) {
  const items = [
    ...cjm.expectations
      .filter((expectation) => isHighCriticality(expectation.criticality))
      .map((expectation) => expectation.expectation_text),
    ...cjm.lprs.flatMap((lpr) =>
      lpr.importance_factors
        .filter((factor) => isHighCriticality(factor.criticality))
        .map((factor) => factorTitle(factor)),
    ),
  ];

  return uniqueFilled(items).slice(0, 5);
}

function buildMainRiskItems(cjm: ProjectCjm) {
  const currentBarriers = cjm.barriers.filter(
    (barrier) =>
      isHighCriticality(barrier.criticality) ||
      isRepeated(barrier.time_status) ||
      hasCurrentTimeStatus(barrier.time_status),
  );

  return uniqueFilled(currentBarriers.map((barrier) => barrier.barrier_title)).slice(0, 5);
}

function groupBarriersByTime(barriers: Barrier[]) {
  const past = barriers.filter(
    (barrier) =>
      normalize(barrier.time_status) === "past" ||
      normalize(barrier.time_status).includes("было") ||
      normalize(barrier.relevance_status).includes("истор"),
  );
  const future = barriers.filter(
    (barrier) =>
      normalize(barrier.time_status) === "future" ||
      normalize(barrier.time_status).includes("может") ||
      normalize(barrier.time_status).includes("буд"),
  );
  const current = barriers.filter((barrier) => {
    if (past.includes(barrier) || future.includes(barrier)) {
      return false;
    }

    return (
      hasCurrentTimeStatus(barrier.time_status) ||
      isRepeated(barrier.time_status) ||
      isActual(barrier.relevance_status)
    );
  });

  return { past, current, future };
}

function buildCompletenessItems(cjm: ProjectCjm) {
  const lprProfilePercent = collectionPercent(cjm.lprs, [
    "external_lpr_id",
    "role_zone",
    "influence_level",
    "activity_status",
    "relationship_status",
    "evidence_basis",
  ]);
  const lprImportancePercent = collectionPercent(
    cjm.lprs.flatMap((lpr) => lpr.importance_factors),
    ["factor_type", "criticality", "source_text", "evidence_quote", "period_or_source", "confidence_level"],
  );

  return [
    {
      label: "Паспорт",
      percent: filledPercent(cjm.project, [
        "project_code",
        "external_project_id",
        "working_project_code",
        "direction",
        "project_scale",
        "known_regions",
        "primary_operational_model",
        "additional_operational_contours",
        "lifecycle_stage",
        "project_status",
        "start_date",
        "short_description",
      ]),
    },
    {
      label: "Цели",
      percent: collectionPercent(cjm.goals, [
        "goal_owner",
        "goal_type",
        "goal_text",
        "priority",
        "related_kpi_or_criterion_text",
        "source_text",
        "relevance_status",
        "comment",
      ]),
    },
    {
      label: "ЛПР",
      percent: weightedPercent([
        [lprProfilePercent, 0.6],
        [lprImportancePercent, 0.4],
      ]),
    },
    {
      label: "Коммуникации",
      percent: collectionPercent(cjm.communications, [
        "client_side",
        "external_lpr_id",
        "open_side_role",
        "topic_text",
        "channel_text",
        "frequency",
        "criticality",
        "source_text",
        "relevance_status",
        "comment",
      ]),
    },
    {
      label: "Барьеры",
      percent: collectionPercent(cjm.barriers, [
        "barrier_code",
        "barrier_title",
        "barrier_type",
        "time_status",
        "description",
        "criticality",
        "related_lpr_code",
        "external_lpr_id",
        "related_importance_text",
        "linked_kpi_text",
        "source_text",
        "relevance_status",
        "evidence_quote",
        "first_seen_period",
        "last_seen_period",
        "status",
        "confidence_level",
      ]),
    },
    {
      label: "Ожидания",
      percent: collectionPercent(cjm.expectations, [
        "expectation_code",
        "expectation_text",
        "expectation_type",
        "explicitness",
        "criticality",
        "related_lpr_code",
        "external_lpr_id",
        "related_importance_text",
        "relevance_status",
        "linked_kpi_text",
        "source_text",
        "evidence_quote",
        "confidence_level",
      ]),
    },
    {
      label: "KPI",
      percent: collectionPercent(cjm.kpis, [
        "kpi_code",
        "kpi_name",
        "kpi_type",
        "source_text",
        "relevance_status",
        "related_expectation_text",
        "related_barrier_text",
        "client_criticality",
        "requires_confirmation",
        "comment",
      ]),
    },
  ];
}

function collectionPercent<T extends object>(items: T[], keys: Array<keyof T>) {
  if (items.length === 0) {
    return 0;
  }

  const total = items.reduce((sum, item) => sum + filledPercent(item, keys), 0);
  return Math.round(total / items.length);
}

function filledPercent<T extends object>(item: T, keys: Array<keyof T>) {
  const filled = keys.reduce((sum, key) => sum + fieldScore(item[key]), 0);

  return Math.round((filled / keys.length) * 100);
}

function fieldScore(value: unknown): number {
  if (Array.isArray(value)) {
    return value.length > 0 ? 1 : 0;
  }

  if (typeof value === "string") {
    const normalized = normalize(value);

    if (
      !normalized ||
      normalized === "unknown" ||
      normalized === "не указано" ||
      normalized === "nan"
    ) {
      return 0;
    }

    if (isConfirmationRequired(value)) {
      return 0.45;
    }

    if (normalized === "other" || normalized === "другое") {
      return 0.7;
    }

    return 1;
  }

  if (value === null || value === undefined) {
    return 0;
  }

  return 1;
}

function weightedPercent(parts: Array<[number, number]>) {
  const totalWeight = parts.reduce((sum, [, weight]) => sum + weight, 0);
  if (totalWeight === 0) {
    return 0;
  }

  const total = parts.reduce((sum, [percent, weight]) => sum + percent * weight, 0);
  return Math.round(total / totalWeight);
}

function buildOptions<T>(
  items: T[],
  accessor: (item: T) => string | null,
  formatter: Formatter,
) {
  const seenLabels = new Set<string>();
  return items
    .map(accessor)
    .filter((value): value is string => Boolean(value?.trim()))
    .map((value) => {
      const label = formatter(value);
      return { value: label, label };
    })
    .filter((option) => {
      const normalizedLabel = normalize(option.label);
      if (!normalizedLabel || seenLabels.has(normalizedLabel)) {
        return false;
      }
      seenLabels.add(normalizedLabel);
      return true;
    })
    .sort((left, right) => left.label.localeCompare(right.label, "ru"));
}

function matchesByLabel(value: string | null, selectedLabel: string, formatter: Formatter) {
  return !selectedLabel || formatter(value) === selectedLabel;
}

function factorTitle(factor: LprImportanceFactor) {
  const mappedFactor = formatImportanceFactor(factor.factor_type);
  if (mappedFactor !== "Другое" && mappedFactor !== "Не указано") {
    return mappedFactor;
  }

  return formatDisplayText(factor.factor_text);
}

function isClientGoal(goal: Goal) {
  const marker = normalize(`${goal.goal_type || ""} ${goal.goal_owner || ""}`);
  return marker.includes("client") || marker.includes("клиент") || marker.includes("бизнес клиента");
}

function normalize(value: string | null | undefined) {
  return value?.trim().toLowerCase() || "";
}

function isHighCriticality(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "high" || normalized.includes("высок");
}

function uniqueFilled(values: Array<string | null | undefined>) {
  const seen = new Set<string>();
  const result: string[] = [];

  values.forEach((value) => {
    const formatted = formatDisplayText(value);
    const normalized = normalize(formatted);
    if (!normalized || formatted === "Не указано" || seen.has(normalized)) {
      return;
    }

    seen.add(normalized);
    result.push(formatted);
  });

  return result;
}

function hasCurrentTimeStatus(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "current" || normalized.includes("сейчас");
}

function formatDisplayText(value: string | null | undefined) {
  const text = formatText(value);
  if (text === "Не указано" || /^[A-ZА-ЯЁ0-9/.\-\s]+$/.test(text)) {
    return text;
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
}
