import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { Menu, X } from "lucide-react";

import {
  archiveEntity,
  createBarrier,
  createCommunication,
  createContextBlock,
  createGoal,
  createKpi,
  createLpr,
  getProjectEffectiveness,
  updateBarrier,
  updateCommunication,
  updateContextBlock,
  updateGoal,
  updateKpi,
  updateLpr,
  updateProject,
  type PatchPayload,
} from "../../api/projects";
import EditEntityModal, {
  type EditField,
  type EditOption,
  type EditPayload,
  type EditValues,
} from "../../components/EditEntityModal";
import EditCollectionModal, {
  type CollectionField,
  type CollectionItemValues,
} from "../../components/EditCollectionModal";
import type {
  Barrier,
  CommunicationPoint,
  Goal,
  Kpi,
  LprProfile,
  ProjectContextBlock,
  ProjectEffectiveness,
} from "../../types/cjm";
import {
  formatActivityStatus,
  formatBarrierStatus,
  formatBarrierTimeStatus,
  formatBarrierType,
  formatConfidenceLevel,
  formatCriticality,
  formatDirection,
  formatEntityCode,
  formatGoalType,
  formatInfluenceLevel,
  formatKpiType,
  formatLifecycleStage,
  formatOperationalModel,
  formatPriority,
  formatProjectScale,
  formatProjectStatus,
  formatImportanceFactor,
  formatRelationshipStatus,
  formatRelevanceStatus,
  formatText,
  formatYesNo,
  sanitizeCjm,
} from "../../utils/labels";
import { contextBlockKeys, passportSections, productModules } from "./constants";
import { Badge, Card, SectionTitle, type BadgeTone } from "./components/ScreenPrimitives";

type FactItem = { label: string; value: string };
type VisionItem = { title: string; value: string; use: string };
type ContourItem = { contour: string; owner: string; text: string };
type HistoryItem = { year: string; title: string; text: string };
type NeedItem = { level: string; title: string; description: string };
type StructureItem = { role: string; person: string; zone: string };
type CompetitorItem = { name: string; strengths: string[]; weaknesses: string[] };
type SwotValue = { strengths: string[]; weaknesses: string[]; opportunities: string[]; threats: string[] };
type InterpretationRuleItem = { id: string; title: string; appliesTo: string; rule: string; example: string };
type CommunicationRow = {
  id: string;
  clientSide: string;
  openSide: string;
  topic: string;
  frequency: string;
  channel: string;
  criticality: string;
  comment: string;
  raw: CommunicationPoint;
};
type Formatter = (value: string | null | undefined) => string;
type EditTarget = {
  title: string;
  fields: EditField[];
  values: EditValues;
  save: (payload: PatchPayload) => Promise<unknown>;
};
type CollectionEditTarget = {
  title: string;
  description?: string;
  itemLabel: string;
  fields: CollectionField[];
  items: CollectionItemValues[];
  save: (items: Record<string, string | null>[]) => Promise<unknown>;
};

const EffectivenessContext = createContext<ProjectEffectiveness | null>(null);
const ScreenActionsContext = createContext<{
  editProject: () => void;
  editPassportHeader: (items: FactItem[]) => void;
  editPassportOverview: (items: FactItem[]) => void;
  editPassportService: (items: FactItem[]) => void;
  editClientVision: (items: Array<{ title: string; value: string; use: string }>) => void;
  editWorkContours: (items: Array<{ contour: string; owner: string; text: string }>) => void;
  editProjectHistory: (items: Array<{ year: string; title: string; text: string }>) => void;
  editNeeds: (
    contour: "client" | "open",
    items: Array<{ level: string; title: string; description: string }>,
  ) => void;
  createGoal: () => void;
  editGoal: (goal: Goal) => void;
  archiveGoal: (goal: Goal) => void;
  editOpenStructure: (items: Array<{ role: string; person: string; zone: string }>) => void;
  editClientStructure: (items: Array<{ role: string; person: string; zone: string }>) => void;
  createLpr: () => void;
  editLpr: (lpr: LprProfile) => void;
  archiveLpr: (lpr: LprProfile) => void;
  editOpenCompetitors: (
    items: Array<{ name: string; strengths: string[]; weaknesses: string[] }>,
  ) => void;
  editClientCompetitors: (
    items: Array<{ name: string; strengths: string[]; weaknesses: string[] }>,
  ) => void;
  editSwot: (value: {
    strengths: string[];
    weaknesses: string[];
    opportunities: string[];
    threats: string[];
  }) => void;
  createCommunication: () => void;
  editCommunication: (communication: CommunicationPoint) => void;
  archiveCommunication: (communication: CommunicationPoint) => void;
  createKpi: () => void;
  editKpi: (kpi: Kpi) => void;
  archiveKpi: (kpi: Kpi) => void;
  editInterpretationRules: (
    items: Array<{ id: string; title: string; appliesTo: string; rule: string; example: string }>,
  ) => void;
  editRiskMap: (items: Array<Record<string, unknown>>) => void;
  editBarrier: (barrier: Barrier) => void;
  createBarrier: () => void;
  archiveBarrier: (barrier: Barrier) => void;
  moveBarrier: (barrier: Barrier, timeStatus: string) => Promise<void>;
  editSummary: () => void;
} | null>(null);

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
const influenceOptions = [
  option("high", formatInfluenceLevel),
  option("medium", formatInfluenceLevel),
  option("low", formatInfluenceLevel),
  option("requires_confirmation", formatInfluenceLevel),
  option("unknown", formatInfluenceLevel),
];
const confidenceOptions = [
  option("high", formatConfidenceLevel),
  option("medium", formatConfidenceLevel),
  option("low", formatConfidenceLevel),
  option("unknown", formatConfidenceLevel),
];
const activityOptions = [
  option("active", formatActivityStatus),
  option("inactive", formatActivityStatus),
  option("requires_confirmation", formatActivityStatus),
  option("historical", formatActivityStatus),
  option("unknown", formatActivityStatus),
];
const relationshipOptions = [
  option("loyal", formatRelationshipStatus),
  option("neutral", formatRelationshipStatus),
  option("cautious", formatRelationshipStatus),
  option("critical", formatRelationshipStatus),
  option("unknown", formatRelationshipStatus),
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
const priorityOptions = [
  option("high", formatPriority),
  option("medium", formatPriority),
  option("low", formatPriority),
  option("unknown", formatPriority),
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
const projectStatusOptions = [
  option("active", formatProjectStatus),
  option("completed", formatProjectStatus),
  option("pilot", formatProjectStatus),
  option("at_risk", formatProjectStatus),
  option("unknown", formatProjectStatus),
];
const lifecycleOptions = [
  option("launch", formatLifecycleStage),
  option("stabilization", formatLifecycleStage),
  option("development", formatLifecycleStage),
  option("retention", formatLifecycleStage),
  option("restart", formatLifecycleStage),
  option("risk", formatLifecycleStage),
  option("closing", formatLifecycleStage),
  option("unknown", formatLifecycleStage),
];
const operationalModelOptions = [
  option("merchandising", formatOperationalModel),
  option("combined_merchandising", formatOperationalModel),
  option("promo_consulting", formatOperationalModel),
  option("kaf", formatOperationalModel),
  option("training", formatOperationalModel),
  option("audit_quality_control", formatOperationalModel),
  option("analytics_reporting", formatOperationalModel),
  option("mixed", formatOperationalModel),
  option("other", formatOperationalModel),
];
const kpiTypeOptions = [
  option("service", formatKpiType),
  option("operational", formatKpiType),
  option("financial", formatKpiType),
  option("quality", formatKpiType),
  option("commercial", formatKpiType),
  option("other", formatKpiType),
];
const confirmationOptions = [
  option("yes", formatYesNo),
  option("no", formatYesNo),
  option("requires_confirmation", formatYesNo),
  option("unknown", formatYesNo),
];
const openContactOptions: EditOption[] = [
  { value: "GKAM", label: "GKAM" },
  { value: "KAM", label: "KAM" },
  { value: "RM", label: "RM" },
  { value: "TM", label: "TM" },
  { value: "SV", label: "SV" },
];

const project = {
  code: "project_002",
  externalId: "1991",
  clientName: "Проект 1991",
  project_status: "active",
  direction: "Электроника",
  serviceModel: "Поддержка продаж и реализация в рознице",
  operationalModel: "Промо / консультирование + обучение + аналитика / отчётность",
  scale: "Федеральный проект",
  lifecycle: "Развитие",
  strategicImportance: "Высокая",
  contractType: "Долгосрочное обслуживание",
  geography: "Москва; Новосибирск; регионы присутствия требуют подтверждения",
  headcount: "86 человек: 1 GKAM, 1 KAM, 3 РМ, 12 СВ, 69 полевых сотрудников",
  stores: "розничные сети и точки продаж электроники",
  openTeam: "GKAM, KAM, РМ, СВ, консультанты, обучение, аналитика / отчётность",
  gkam: "Не указано",
  kam: "Не указано",
  lastUpdated: "24.05.2026",
  completeness: 72,
};

const clientNeeds = [
  {
    level: "1. База",
    title: "Исполнение без провалов",
    description: "Визиты выполняются, отчётность приходит вовремя, критичные задачи не теряются.",
  },
  {
    level: "2. Контроль",
    title: "Прозрачность ситуации",
    description: "Клиент понимает, что происходит в поле, где есть отклонения и кто отвечает за исправление.",
  },
  {
    level: "3. Уверенность",
    title: "OPEN управляет рисками заранее",
    description: "Команда не ждёт жалоб, а сама показывает проблемные зоны и план действий.",
  },
  {
    level: "4. Развитие",
    title: "Проект становится эффективнее",
    description: "Снижаются ручные согласования, растёт качество, решения принимаются на данных.",
  },
];

const riskMap =   [
  {
    id: "R-01",
    zone: "Коммуникации с ЛПР",
    risk: "Критичный вопрос остаётся без владельца, срока или понятного статуса",
    probability: { score: 2, label: "Средняя", basis: "В профиле ЛПР 1 скорость реакции указана как высокий приоритет; в KPI срок реакции отмечен как зона внимания." },
    impact: { score: 3, label: "Высокое", basis: "Затрагивает коммерческого ЛПР и может быстро перейти в эскалацию по сервису." },
    linked: [
      { type: "ЛПР", value: "ЛПР 1" },
      { type: "KPI", value: "Срок реакции на запрос" },
      { type: "Раздел", value: "Матрица коммуникаций" },
    ],
    earlySignals: [
      { signal: "повторный запрос статуса", source: "история коммуникаций / письма" },
      { signal: "нет назначенного владельца вопроса", source: "action-план / протокол встречи" },
      { signal: "срок ответа не зафиксирован", source: "матрица коммуникаций / рабочий статус" },
    ],
    control: { action: "Фиксировать по каждому критичному вопросу: проблема → действие → владелец → срок.", owner: "КАМ", filledBy: "КАМ после встречи или эскалации", review: "еженедельно" },
    status: "В работе",
  },
  {
    id: "R-02",
    zone: "Передача проекта",
    risk: "При смене ответственного теряется история договорённостей и особенности ЛПР",
    probability: { score: 2, label: "Средняя", basis: "В проекте несколько контуров влияния; часть информации хранится в профилях ЛПР и коммуникациях." },
    impact: { score: 3, label: "Высокое", basis: "Потеря контекста влияет на коммерческий, операционный и финансовый контур одновременно." },
    linked: [
      { type: "Раздел", value: "Паспорт проекта" },
      { type: "Раздел", value: "Карта влияния и ЛПР" },
      { type: "Роль", value: "GKAM / КАМ" },
    ],
    earlySignals: [
      { signal: "новый ответственный уточняет базовые договорённости", source: "передача проекта" },
      { signal: "нет истории решений по спорным вопросам", source: "протоколы / переписка" },
      { signal: "профили ЛПР не обновлялись", source: "карта влияния и ЛПР" },
    ],
    control: { action: "Передавать проект через паспорт, профили ЛПР, матрицу коммуникаций и список открытых вопросов.", owner: "GKAM / КАМ", filledBy: "GKAM перед передачей проекта", review: "при смене ответственного" },
    status: "В работе",
  },
  {
    id: "R-03",
    zone: "Операционное исполнение",
    risk: "Повторяющиеся операционные вопросы не выделяются в отдельный контур контроля",
    probability: { score: 2, label: "Средняя", basis: "Операционный контакт ориентирован на факт исправления; в проекте есть KPI закрытия критичных замечаний." },
    impact: { score: 2, label: "Среднее", basis: "Влияет на операционное восприятие сервиса и может накапливаться до коммерческого риска." },
    linked: [
      { type: "ЛПР", value: "ЛПР 2" },
      { type: "KPI", value: "Закрытие критичных замечаний" },
      { type: "Роль", value: "РМ" },
    ],
    earlySignals: [
      { signal: "одинаковые вопросы возвращаются", source: "реестр обращений / операционные встречи" },
      { signal: "нет подтверждения исправления", source: "рабочий статус" },
      { signal: "проблема переходит между ролями", source: "коммуникации OPEN / клиента" },
    ],
    control: { action: "Разделять разовые и повторяющиеся вопросы; для повторяющихся фиксировать владельца, территорию и срок закрытия.", owner: "РМ", filledBy: "РМ после операционной встречи", review: "2 раза в месяц" },
    status: "Наблюдать",
  },
  {
    id: "R-04",
    zone: "Качество сервиса",
    risk: "Формальные KPI выглядят нормально, но клиенту не хватает прозрачности по ходу работ",
    probability: { score: 2, label: "Средняя", basis: "Качество сервиса в KPI отмечено как норма, но срок реакции и закрытие критичных замечаний находятся в зоне внимания." },
    impact: { score: 2, label: "Среднее", basis: "Влияет на ощущение управляемости сервиса у коммерческого и операционного контакта." },
    linked: [
      { type: "KPI", value: "Качество сервиса" },
      { type: "KPI", value: "Срок реакции" },
      { type: "ЛПР", value: "ЛПР 1 / ЛПР 2" },
    ],
    earlySignals: [
      { signal: "клиент повторно запрашивает детали", source: "переписка / встречи" },
      { signal: "не хватает статуса по проблемам", source: "рабочий статус" },
      { signal: "есть разрыв между отчётом и ощущением клиента", source: "опросы / комментарии / встречи" },
    ],
    control: { action: "Показывать не только факт выполнения, но и статус проблемных вопросов: что сделано, что в работе, когда будет закрыто.", owner: "КАМ / РМ", filledBy: "КАМ или РМ после получения сигнала от клиента", review: "ежемесячно" },
    status: "Наблюдать",
  },
  {
    id: "R-05",
    zone: "Данные проекта",
    risk: "Часть фактов проекта не подтверждена и не готова для дальнейшей аналитики",
    probability: { score: 3, label: "Высокая", basis: "В брифе проекта уже отмечены поля к проверке: регионы, численность, ЛПР, торговые сети, источники KPI и конкуренты." },
    impact: { score: 2, label: "Среднее", basis: "Без подтверждения фактов контекст нельзя безопасно использовать в расчётах и управленческих выводах." },
    linked: [
      { type: "Раздел", value: "Бриф проекта" },
      { type: "Раздел", value: "Паспорт проекта" },
      { type: "Данные", value: "KPI / регионы / численность" },
    ],
    earlySignals: [
      { signal: "регионы указаны частично", source: "паспорт проекта" },
      { signal: "ЛПР обезличены", source: "карта влияния и ЛПР" },
      { signal: "источники KPI описаны укрупнённо", source: "KPI проекта" },
    ],
    control: { action: "Закрыть список фактов к подтверждению перед использованием контекста в расчётах и управленческих выводах.", owner: "Аналитик / КАМ", filledBy: "аналитик вместе с КАМ", review: "перед расчётом эффективности" },
    status: "Актуализировать",
  },
  {
    id: "R-06",
    zone: "Конкурентный контур",
    risk: "Клиент сравнивает OPEN с другими промо-аутсорсерами только по цене",
    probability: { score: 1, label: "Низкая", basis: "В текущем контексте нет факта активного тендера, но конкурентный контур и финансовый контакт зафиксированы." },
    impact: { score: 2, label: "Среднее", basis: "Может повлиять на переговоры по стоимости и позиционирование ценности OPEN." },
    linked: [
      { type: "Раздел", value: "Конкуренты" },
      { type: "ЛПР", value: "ЛПР 3" },
      { type: "Роль", value: "GKAM" },
    ],
    earlySignals: [
      { signal: "запрос пересмотра стоимости", source: "переговоры / почта" },
      { signal: "вопросы о детализации затрат", source: "финансовое согласование" },
      { signal: "упоминание альтернативных подрядчиков", source: "встреча / тендерная коммуникация" },
    ],
    control: { action: "Готовить аргументацию не только по цене, но и по управляемости, покрытию, качеству сопровождения и аналитике.", owner: "GKAM", filledBy: "GKAM при подготовке к переговорам", review: "при коммерческих обсуждениях" },
    status: "Наблюдать",
  },
];

const dataModules = {
  people: {
    title: "Люди",
    description: "Слой данных о людях на проекте: аттестации, обучение, роли, стаж, текучесть, кадровый резерв, эффективность супервайзеров и мерчендайзеров. Паспорт проекта будет объяснять, почему одни и те же показатели на разных проектах нельзя трактовать одинаково.",
    cards: [
      { title: "Аттестации", text: "Оценки знаний, остаточные знания, динамика после обучения, слабые темы." },
      { title: "Обучение", text: "Посещение тренингов, обязательные курсы, связь обучения с качеством и KPI." },
      { title: "Роли и структура", text: "КАМ, РМ, ТМ, супервайзеры, мерчендайзеры, зоны ответственности и управленческая нагрузка." },
      { title: "Риски по людям", text: "Текучесть, перегруз, слабые зоны, кандидаты на развитие и замещение." },
    ],
  },
  assessment360: {
    title: "Оценка 360 структуры",
    description: "Слой восприятия управленческой структуры: как оценивают руководителей, коммуникации, поддержку, обратную связь и качество управления внутри проекта.",
    cards: [
      { title: "Руководители", text: "Оценка РМ, ТМ, супервайзеров по компетенциям и поведенческим индикаторам." },
      { title: "Командная среда", text: "Доверие, обратная связь, понятность целей, управленческая поддержка." },
      { title: "Риск структуры", text: "Где управленческая проблема может стать причиной просадки качества или ухода людей." },
      { title: "Связь с паспортом", text: "Если проект сложный по коммуникациям, требования к управлению выше. Это должно учитываться в интерпретации." },
    ],
  },
  surveys: {
    title: "Блиц- и операционные опросы",
    description: "Голос клиента: оценки, комментарии, eNPS, CSAT, исполнение, ожидания и повторяющиеся болевые темы. Здесь паспорт проекта задаёт контекст: кто ЛПР, что для него критично и какие исторические барьеры уже были.",
    cards: [
      { title: "Блиц-опросы", text: "Интервью с ЛПР, причины оценок, ожидания, качественные сигналы." },
      { title: "Операционные опросы", text: "Регулярные оценки сервиса, блоки вопросов, динамика по проектам и направлениям." },
      { title: "Комментарии", text: "Темы, тональность, повторяемость проблем, скрытые драйверы неудовлетворённости." },
      { title: "Сигналы риска", text: "Падение лояльности, рост негатива, расхождение между оценками и формальными KPI." },
    ],
  },
  operations: {
    title: "Операционные KPI",
    description: "Фактическое исполнение проекта: план/факт, соблюдение сроков, выполнение задач, стабильность отчётности, открытые проблемы и скорость закрытия отклонений.",
    cards: [
      { title: "План / факт", text: "Выполнение обязательств по проекту и отклонения от ожидаемого уровня." },
      { title: "Скорость реакции", text: "Сроки ответа, закрытие критичных вопросов, дисциплина коммуникаций." },
      { title: "Стабильность процесса", text: "Регулярность отчётов, повторяемость сбоев, зависимость от ручного контроля." },
      { title: "Связь с ожиданиями", text: "KPI может быть в норме, но клиент всё равно недоволен. Вот этот разрыв и надо ловить." },
    ],
  },
  serviceQuality: {
    title: "Качество сервиса",
    description: "Универсальный слой качества для разных типов проектов. Здесь не предполагаем наличие отдела контроля качества: источниками могут быть проверки визитов, клиентские опросы, BI-показатели, отчёты РМ, жалобы, комментарии и ручные сигналы по отклонениям.",
    cards: [
      { title: "Сигналы качества", text: "Отклонения из опросов, комментариев, BI, отчётов и ручных наблюдений команды." },
      { title: "Проблемные зоны", text: "Регионы, роли, торговые точки, сети или процессы, где повторяются сбои." },
      { title: "Влияние на сервис", text: "Как качество исполнения связано с удовлетворённостью клиента и выполнением ожиданий." },
      { title: "Ранние предупреждения", text: "Сигналы до того, как проблема станет конфликтом или попадёт в формальный опрос." },
    ],
  },
  finance: {
    title: "Финансы проекта",
    description: "Экономический слой: маржинальность, стоимость сопровождения, влияние ручного управления, потери от текучести, стоимость обучения и потенциальный ROI улучшений.",
    cards: [
      { title: "Маржинальность", text: "Финансовое здоровье проекта и динамика прибыльности." },
      { title: "Стоимость проблем", text: "Во что обходятся текучесть, ошибки, ручные эскалации и постоянное тушение пожаров." },
      { title: "ROI обучения", text: "Связь вложений в обучение с качеством, удержанием и операционными KPI." },
      { title: "Аргументы для развития", text: "Где можно обосновать расширение услуг или изменение модели сопровождения." },
    ],
  },
  effectiveness: {
    title: "Итоговая эффективность",
    description: "Финальный слой продукта: агрегированная оценка эффективности проекта, прогноз, объяснение причин и рекомендации. Его нельзя строить только на паспорте — паспорт лишь помогает правильно интерпретировать данные.",
    cards: [
      { title: "Индекс эффективности", text: "Не одна магическая цифра, а понятная модель из людей, качества, клиента, операций и экономики." },
      { title: "Прогноз", text: "Куда движется проект: стабилизация, рост, зона внимания или риск просадки." },
      { title: "Причины", text: "Почему система дала такую оценку: какие блоки тянут проект вверх или вниз." },
      { title: "Рекомендации", text: "Что делать управленчески: кого обучать, где усилить контроль, какие ожидания клиента закрывать." },
    ],
  },
};

function findBlock(
  blocks: ProjectContextBlock[],
  sectionKey: string,
  blockCode?: string,
) {
  return blocks.find((block) =>
    block.section_key === sectionKey && (!blockCode || block.block_code === blockCode),
  ) || null;
}

function asRecordArray(value: unknown) {
  return Array.isArray(value)
    ? value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    : [];
}

function asStringArray(value: unknown) {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === "string" && item.trim().length > 0)
    : [];
}

function useScreenData() {
  const data = useContext(EffectivenessContext);
  const cjm = data?.cjm;
  const contextBlocks = data?.context_blocks ?? [];
  const block = (sectionKey: string, blockCode?: string) =>
    findBlock(contextBlocks, sectionKey, blockCode);

  if (!cjm) {
    return {
      project,
      projectGoals: [],
      contacts: [],
      communications: [],
      kpis: [],
      barriers: [],
      swot: { strengths: [], weaknesses: [], opportunities: [], threats: [] },
      riskMap,
      dataModules,
      passportHeaderFacts: [],
      passportOverviewItems: [],
      passportServiceItems: [],
      clientVisionItems: [],
      workContourItems: [],
      historyItems: [],
      clientNeedsItems: [],
      openNeedsItems: [],
      openStructureItems: [],
      clientStructureItems: [],
      competitorsOpenItems: [],
      competitorsClientItems: [],
      interpretationRuleItems: [],
      summaryBlock: null,
      relationText: formatText,
      contextBlocks: [],
    };
  }

  const swotBlock = block(contextBlockKeys.swot.sectionKey, contextBlockKeys.swot.blockCode);
  const riskBlock = block(contextBlockKeys.riskMap.sectionKey, contextBlockKeys.riskMap.blockCode);
  const layersBlock = block("effectiveness_layers");
  const summaryBlock = block(contextBlockKeys.summary.sectionKey, contextBlockKeys.summary.blockCode);
  const passportHeaderBlock = block(
    contextBlockKeys.passportHeader.sectionKey,
    contextBlockKeys.passportHeader.blockCode,
  );
  const passportOverviewBlock = block(
    contextBlockKeys.passportOverview.sectionKey,
    contextBlockKeys.passportOverview.blockCode,
  );
  const passportServiceBlock = block(
    contextBlockKeys.passportService.sectionKey,
    contextBlockKeys.passportService.blockCode,
  );
  const clientVisionBlock = block(
    contextBlockKeys.clientVision.sectionKey,
    contextBlockKeys.clientVision.blockCode,
  );
  const workContoursBlock = block(
    contextBlockKeys.workContours.sectionKey,
    contextBlockKeys.workContours.blockCode,
  );
  const projectHistoryBlock = block(
    contextBlockKeys.projectHistory.sectionKey,
    contextBlockKeys.projectHistory.blockCode,
  );
  const clientNeedsBlock = block(
    contextBlockKeys.clientNeeds.sectionKey,
    contextBlockKeys.clientNeeds.blockCode,
  );
  const openNeedsBlock = block(
    contextBlockKeys.openNeeds.sectionKey,
    contextBlockKeys.openNeeds.blockCode,
  );
  const openStructureBlock = block(
    contextBlockKeys.openStructure.sectionKey,
    contextBlockKeys.openStructure.blockCode,
  );
  const clientStructureBlock = block(
    contextBlockKeys.clientStructure.sectionKey,
    contextBlockKeys.clientStructure.blockCode,
  );
  const competitorsOpenBlock = block(
    contextBlockKeys.competitorsOpen.sectionKey,
    contextBlockKeys.competitorsOpen.blockCode,
  );
  const competitorsClientBlock = block(
    contextBlockKeys.competitorsClient.sectionKey,
    contextBlockKeys.competitorsClient.blockCode,
  );
  const interpretationRulesBlock = block(
    contextBlockKeys.interpretationRules.sectionKey,
    contextBlockKeys.interpretationRules.blockCode,
  );
  const projectInfo = cjm.project;
  const relationTitles = new Map<string, string>();
  const rememberRelation = (code: string | null | undefined, title: string | null | undefined) => {
    const normalizedCode = code?.trim().toLowerCase();
    const normalizedTitle = title?.trim();
    if (!normalizedCode || !normalizedTitle) {
      return;
    }
    relationTitles.set(normalizedCode, normalizedTitle);
  };
  cjm.goals.forEach((goal) => rememberRelation(goal.goal_code, goal.goal_text));
  cjm.lprs.forEach((lpr) => rememberRelation(lpr.lpr_code, lpr.role_zone || lpr.role));
  cjm.barriers.forEach((barrier) => rememberRelation(barrier.barrier_code, barrier.barrier_title));
  cjm.expectations.forEach((expectation) =>
    rememberRelation(expectation.expectation_code, expectation.expectation_text),
  );
  cjm.kpis.forEach((kpi) => rememberRelation(kpi.kpi_code, kpi.kpi_name));
  cjm.communications.forEach((communication) =>
    rememberRelation(communication.communication_code, communication.topic_text || communication.summary),
  );
  const relationText = (value: string | null | undefined) => {
    const original = value?.trim();
    if (!original) {
      return formatText(value);
    }
    return original.replace(
      /\b(goal|lpr|barrier|expectation|expect|kpi|comm|communication)_0*\d+\b/gi,
      (match) => relationTitles.get(match.trim().toLowerCase()) || formatEntityCode(match),
    );
  };

  const headerContent = passportHeaderBlock?.content ?? {};
  const fallbackProject = {
    ...project,
    code: projectInfo.project_code,
    externalId: projectInfo.external_project_id || "Без кода",
    clientName: `Проект ${projectInfo.external_project_id || projectInfo.project_code}`,
    project_status: projectInfo.project_status,
    direction: formatDirection(projectInfo.direction),
    serviceModel: sanitizeCjm(projectInfo.short_description) || "Описание проекта нужно уточнить в паспорте.",
    operationalModel: formatOperationalModel(projectInfo.primary_operational_model),
    scale: formatProjectScale(projectInfo.project_scale),
    lifecycle: formatLifecycleStage(projectInfo.lifecycle_stage),
    contractType: String(headerContent.contractType || "Требует уточнения"),
    geography: projectInfo.known_regions || "Регионы требуют уточнения",
    headcount: String(headerContent.teamHeadcount || "Требует уточнения"),
    stores: String(headerContent.stores || "Требует уточнения"),
    openTeam: String(headerContent.openTeam || projectInfo.additional_operational_contours || "Требует уточнения"),
    gkam: String(headerContent.gkam || "Не указано"),
    kam: String(headerContent.kam || "Не указано"),
    lastUpdated: formatDateTime(
      maxDate([
        projectInfo.updated_at,
        passportHeaderBlock?.updated_at,
        passportOverviewBlock?.updated_at,
        passportServiceBlock?.updated_at,
        clientVisionBlock?.updated_at,
        workContoursBlock?.updated_at,
        projectHistoryBlock?.updated_at,
      ]),
    ),
    completeness: estimateCompleteness(cjm),
  };
  const realProject = fallbackProject;

  const realGoals = cjm.goals.map((goal, index) => ({
    id: goal.goal_code || `goal_${index + 1}`,
    entityCode: goal.goal_code || goal.goal_id || `goal_${index + 1}`,
    contour:
      goal.goal_type?.toLowerCase().includes("client")
      || goal.goal_owner?.toLowerCase().includes("клиент")
        ? "Клиент"
        : "OPEN",
    goal: goal.goal_text,
    type: formatGoalType(goal.goal_type),
    meaning: goal.comment || goal.success_criteria || "Смысл цели можно уточнить при редактировании.",
    evidence: relationText(goal.related_kpi_or_criterion_text),
    owner: goal.goal_owner || "Проектная команда",
    raw: goal,
  }));

  const realContacts = cjm.lprs.map((lpr) => ({
    id: lpr.lpr_code,
    entityCode: lpr.lpr_code,
    role: lpr.role_zone || lpr.role,
    decisionRole: lpr.evidence_basis || "Зона влияния уточняется в карточке ЛПР.",
    influence: formatInfluenceLevel(lpr.influence_level),
    attitude: formatRelationshipStatus(lpr.relationship_status),
    profileStatus: formatActivityStatus(lpr.activity_status),
    profileSource: lpr.evidence_basis || "Данные внесены в контекст проекта.",
    profileEvidence: lpr.importance_factors.map((factor) => ({
      source: humanizeSourceLabel(factor.source_text),
      detail: factor.evidence_quote || factor.factor_text,
      confirms: factor.factor_text,
    })),
    values: lpr.importance_factors.map((factor) => ({
      name: factor.factor_text || formatImportanceFactor(factor.factor_type),
      priority: formatCriticality(factor.criticality),
      description: factor.evidence_quote || factor.source_text || "Описание важности можно уточнить.",
    })),
    interaction: {
      preferredFormat: lpr.manual_comment || "Формат взаимодействия уточняется.",
      channel: "См. матрицу коммуникаций",
      frequency: "См. матрицу коммуникаций",
      owner: "Проектная команда",
    },
    doRules: ["фиксировать договорённости", "показывать статус и следующий шаг"],
    dontRules: ["оставлять вопрос без владельца", "терять контекст договорённостей"],
    notes: lpr.manual_comment || "Карточка редактируется в интерфейсе.",
    raw: lpr,
  }));

  const realCommunications: CommunicationRow[] = cjm.communications.map((row, index) => ({
    id: row.communication_code || row.communication_id || `communication_${index + 1}`,
    clientSide: row.client_side || "Клиентская сторона",
    openSide: row.open_side_role || "OPEN",
    topic: row.topic_text || row.summary,
    frequency: formatText(row.frequency),
    channel: row.channel_text || row.channel,
    criticality: formatCriticality(row.criticality),
    comment: row.comment || "",
    raw: row,
  }));

  const realKpis = cjm.kpis.map((kpi) => ({
    id: kpi.kpi_code,
    entityCode: kpi.kpi_code,
    name: kpi.kpi_name,
    sourceBlock: humanizeSourceLabel(kpi.source_text),
    stakeholder: "Клиент / OPEN",
    type: formatKpiType(kpi.kpi_type),
    purpose: kpi.comment || "Критерий успеха проекта.",
    measurement: [kpi.current_value, kpi.target_value, kpi.unit].filter(Boolean).join(" / ") || "Методика измерения уточняется.",
    dataSource: humanizeSourceLabel(kpi.source_text),
    clarify: formatYesNo(kpi.requires_confirmation),
    owner: "Проектная команда",
    priority: formatCriticality(kpi.client_criticality),
    linked: splitTextLinks(
      [relationText(kpi.related_expectation_text), relationText(kpi.related_barrier_text)]
        .filter(Boolean)
        .join("; "),
    ),
    goals: cjm.goals
      .filter((goal) => goal.related_kpi_or_criterion_text?.includes(kpi.kpi_code))
      .map((goal) => goal.goal_text),
    raw: kpi,
  }));

  const realBarriers = ["past", "current", "future"].map((timeStatus) => ({
    period: formatBarrierTimeStatus(timeStatus),
    color:
      timeStatus === "past"
        ? "border-slate-300 bg-slate-50"
        : timeStatus === "current"
          ? "border-amber-300 bg-amber-50"
          : "border-rose-300 bg-rose-50",
    items: cjm.barriers
      .filter((barrier) => barrier.time_status === timeStatus || (timeStatus === "current" && barrier.time_status === "repeated"))
      .map((barrier) => ({
        entityCode: barrier.barrier_code || barrier.barrier_id || barrier.barrier_title,
        title: barrier.barrier_title,
        level: formatCriticality(barrier.criticality),
        text: barrier.description || barrier.evidence_quote || "Описание барьера можно уточнить.",
        links: splitTextLinks(
          relationText(barrier.linked_kpi_text || barrier.related_importance_text || ""),
        ),
        raw: barrier,
      })),
  }));

  const realSwot = {
    strengths: asStringArray(swotBlock?.content.strengths).length
      ? asStringArray(swotBlock?.content.strengths)
      : [],
    weaknesses: asStringArray(swotBlock?.content.weaknesses).length
      ? asStringArray(swotBlock?.content.weaknesses)
      : [],
    opportunities: asStringArray(swotBlock?.content.opportunities).length
      ? asStringArray(swotBlock?.content.opportunities)
      : [],
    threats: asStringArray(swotBlock?.content.threats).length
      ? asStringArray(swotBlock?.content.threats)
      : [],
  };

  const riskItems = asRecordArray(riskBlock?.content.items);
  const realRiskMap = (riskItems.length > 0 ? riskItems : cjm.barriers).map((item, index) => {
    const source = item as Record<string, unknown>;
    const title = String(source.title || source.barrier_title || `Риск ${index + 1}`);
    const probabilityCode = String(source.probability_level || source.level || source.criticality || "unknown");
    const impactCode = String(source.impact_level || source.level || source.criticality || "unknown");
    return {
      id: String(source.id || source.barrier_code || `risk_${index + 1}`),
      entityCode: `Риск ${index + 1}`,
      zone: formatBarrierType(String(source.barrier_type || "other")),
      risk: title,
      probability: {
        score: probabilityScore(probabilityCode),
        label: formatCriticality(probabilityCode),
        basis: String(source.probability_basis || source.description || ""),
      },
      impact: {
        score: probabilityScore(impactCode),
        label: formatCriticality(impactCode),
        basis: String(source.impact_basis || source.linked_kpi_text || ""),
      },
      linked: splitTextLinks(relationText(String(source.linked_kpi_text || source.related_to || ""))).map((value) => ({ type: "Связь", value })),
      earlySignals: [
        {
          signal: String(source.early_signal || source.evidence_quote || source.description || title),
          source: humanizeSourceLabel(String(source.signal_source || source.source_text || "web")),
        },
      ],
      control: {
        action: String(source.control_action || "Назначить владельца контроля и период пересмотра."),
        owner: String(source.control_owner || "Проектная команда"),
        filledBy: String(source.filled_by || "Ответственный проекта"),
        review: String(source.review_period || "регулярно"),
      },
      status: formatBarrierStatus(String(source.status || "monitoring")),
      raw: source,
    };
  });

  const layers = asRecordArray(layersBlock?.content.layers);
  const realDataModules = {
    ...dataModules,
    effectiveness: {
      ...dataModules.effectiveness,
      cards: layers.length
        ? layers.map((item) => {
            const layer = item as Record<string, unknown>;
            return {
              title: String(layer.title || "Слой эффективности"),
              text: String(layer.status || "Данные уточняются."),
            };
          })
        : dataModules.effectiveness.cards,
    },
  };

  const passportHeaderFacts =
    asRecordArray(passportHeaderBlock?.content.items).map((item) => ({
      label: String(item.label || ""),
      value: formatText(String(item.value || "")),
    })) || [];
  const passportOverviewItems = asRecordArray(passportOverviewBlock?.content.items).length
    ? asRecordArray(passportOverviewBlock?.content.items).map((item) => ({
        label: String(item.label || ""),
        value: formatText(String(item.value || "")),
      }))
    : [
        { label: "Код проекта", value: formatText(projectInfo.external_project_id) },
        { label: "Статус", value: formatProjectStatus(projectInfo.project_status) },
        { label: "Этап жизненного цикла", value: formatLifecycleStage(projectInfo.lifecycle_stage) },
        { label: "Дата старта", value: formatText(projectInfo.start_date) },
      ];
  const passportServiceItems = asRecordArray(passportServiceBlock?.content.items).length
    ? asRecordArray(passportServiceBlock?.content.items).map((item) => ({
        label: String(item.label || ""),
        value: formatText(String(item.value || "")),
      }))
    : [
        { label: "Основная модель", value: formatOperationalModel(projectInfo.primary_operational_model) },
        { label: "Формат сервиса", value: formatText(sanitizeCjm(projectInfo.short_description)) },
        { label: "Дополнительные контуры", value: formatText(projectInfo.additional_operational_contours) },
        { label: "География", value: formatText(projectInfo.known_regions) },
      ];
  const clientVisionItems = asRecordArray(clientVisionBlock?.content.items).length
    ? asRecordArray(clientVisionBlock?.content.items).map((item) => ({
        title: String(item.title || ""),
        value: String(item.value || ""),
        use: String(item.use || ""),
      }))
    : [];
  const workContourItems = asRecordArray(workContoursBlock?.content.items).length
    ? asRecordArray(workContoursBlock?.content.items).map((item) => ({
        contour: String(item.contour || ""),
        owner: String(item.owner || ""),
        text: String(item.text || ""),
      }))
    : [];
  const historyItems = asRecordArray(projectHistoryBlock?.content.items).length
    ? asRecordArray(projectHistoryBlock?.content.items).map((item) => ({
        year: String(item.year || ""),
        title: String(item.title || ""),
        text: String(item.text || ""),
      }))
    : [];
  const clientNeedsItems = asRecordArray(clientNeedsBlock?.content.items).length
    ? asRecordArray(clientNeedsBlock?.content.items).map((item) => ({
        level: String(item.level || ""),
        title: String(item.title || ""),
        description: String(item.description || ""),
      }))
    : [];
  const openNeedsItems = asRecordArray(openNeedsBlock?.content.items).length
    ? asRecordArray(openNeedsBlock?.content.items).map((item) => ({
        level: String(item.level || ""),
        title: String(item.title || ""),
        description: String(item.description || ""),
      }))
    : [];
  const openStructureItems = asRecordArray(openStructureBlock?.content.items).length
    ? asRecordArray(openStructureBlock?.content.items).map((item) => ({
        role: String(item.role || ""),
        person: String(item.person || ""),
        zone: String(item.zone || ""),
      }))
    : [];
  const clientStructureItems = asRecordArray(clientStructureBlock?.content.items).length
    ? asRecordArray(clientStructureBlock?.content.items).map((item) => ({
        role: String(item.role || ""),
        person: String(item.person || ""),
        zone: String(item.zone || ""),
      }))
    : [];
  const competitorsOpenItems = asRecordArray(competitorsOpenBlock?.content.items).length
    ? asRecordArray(competitorsOpenBlock?.content.items).map((item) => ({
        name: String(item.name || ""),
        strengths: splitLines(String(item.strengths || "")),
        weaknesses: splitLines(String(item.weaknesses || "")),
      }))
    : [];
  const competitorsClientItems = asRecordArray(competitorsClientBlock?.content.items).length
    ? asRecordArray(competitorsClientBlock?.content.items).map((item) => ({
        name: String(item.name || ""),
        strengths: splitLines(String(item.strengths || "")),
        weaknesses: splitLines(String(item.weaknesses || "")),
      }))
    : [];
  const interpretationRuleItems = asStringArray(interpretationRulesBlock?.content.rules).length
    ? asStringArray(interpretationRulesBlock?.content.rules).map((text, index) => ({
        id: `Правило ${index + 1}`,
        title: `Правило ${index + 1}`,
        appliesTo: "Контекст проекта",
        rule: text,
        example: "Уточняется в ходе проектной работы.",
      }))
    : [];

  return {
    project: realProject,
    projectGoals: realGoals,
    contacts: realContacts,
    communications: realCommunications,
    kpis: realKpis,
    barriers: realBarriers,
    swot: realSwot,
    riskMap: realRiskMap,
    dataModules: realDataModules,
    passportHeaderFacts: passportHeaderFacts.length ? passportHeaderFacts : [
      { label: "Команда", value: realProject.headcount },
      { label: "GKAM", value: realProject.gkam },
      { label: "KAM", value: realProject.kam },
      { label: "Контуры", value: realProject.openTeam },
    ],
    passportOverviewItems,
    passportServiceItems,
    clientVisionItems,
    workContourItems,
    historyItems,
    clientNeedsItems,
    openNeedsItems,
    openStructureItems,
    clientStructureItems,
    competitorsOpenItems,
    competitorsClientItems,
    interpretationRuleItems,
    summaryBlock,
    relationText,
    contextBlocks,
  };
}

function useScreenActions() {
  const actions = useContext(ScreenActionsContext);
  if (!actions) {
    throw new Error("Screen actions are unavailable outside the project effectiveness screen.");
  }
  return actions;
}

function estimateCompleteness(cjm: ProjectEffectiveness["cjm"]) {
  const sections = [
    cjm.project.short_description,
    cjm.goals.length,
    cjm.lprs.length,
    cjm.barriers.length,
    cjm.expectations.length,
    cjm.kpis.length,
    cjm.communications.length,
  ];
  const filled = sections.filter(Boolean).length;
  return Math.round((filled / sections.length) * 100);
}

function splitTextLinks(value: string) {
  return value
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitLines(value: string | null | undefined) {
  return (value || "")
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function mergeOpenContacts(selected: string | null | undefined, custom: string | null | undefined) {
  const values = [
    ...splitTextLinks(selected || ""),
    ...splitTextLinks(custom || ""),
  ];
  return Array.from(new Set(values)).join("; ");
}

function buildCommunicationPayload(payload: PatchPayload): PatchPayload {
  const { open_side_role_custom, ...rest } = payload;
  const mergedOpen = mergeOpenContacts(payload.open_side_role, open_side_role_custom);
  return {
    ...rest,
    open_side_role: mergedOpen || null,
  };
}

function formatDateTime(value: string | null | undefined) {
  if (!value) {
    return "Не указано";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return formatText(value);
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(date);
}

function maxDate(values: Array<string | null | undefined>) {
  const timestamps = values
    .map((value) => (value ? new Date(value).getTime() : Number.NaN))
    .filter((value) => Number.isFinite(value));
  if (timestamps.length === 0) {
    return null;
  }
  return new Date(Math.max(...timestamps)).toISOString();
}

function probabilityScore(value: string | null | undefined) {
  const normalized = value?.trim().toLowerCase() || "";
  if (normalized.includes("high") || normalized.includes("высок")) {
    return 3;
  }
  if (normalized.includes("medium") || normalized.includes("средн")) {
    return 2;
  }
  return 1;
}

function humanizeSourceLabel(value: string | null | undefined) {
  const normalized = value?.trim().toLowerCase() || "";
  if (!normalized) {
    return "Контур проекта";
  }
  if (normalized === "web") {
    return "Веб-платформа";
  }
  if (normalized.includes("cjm")) {
    return "Исторический контекст проекта";
  }
  return formatText(value);
}

function option(value: string, formatter: Formatter): EditOption {
  return { value, label: formatter(value) };
}

function pickValues(entity: object, fields: EditField[]): EditValues {
  const record = entity as Record<string, string | null | undefined>;
  return fields.reduce<EditValues>((values, field) => {
    values[field.name] = record[field.name] ?? "";
    return values;
  }, {});
}

function mergeOptions(base: EditOption[], extra: EditOption[]) {
  const seen = new Set<string>();
  return [...base, ...extra].filter((option) => {
    const key = `${option.value}|${option.label}`;
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function buildRawOptions<T>(
  items: T[],
  selector: (item: T) => string | null | undefined,
  formatter: Formatter = formatText,
) {
  const seen = new Set<string>();
  return items.flatMap((item) => {
    const value = selector(item)?.trim();
    if (!value || seen.has(value)) {
      return [];
    }
    seen.add(value);
    return [{ value, label: formatter(value) }];
  });
}

function buildKpiRelationOptions(kpisList: Kpi[]) {
  return kpisList.map((kpi) => ({
    value: kpi.kpi_name,
    label: kpi.kpi_name,
  }));
}

function buildImportanceRelationOptions(lprsList: LprProfile[]) {
  const values = lprsList.flatMap((lpr) => lpr.importance_factors.map((factor) => factor.factor_text));
  return Array.from(new Set(values.filter(Boolean))).map((value) => ({
    value,
    label: value,
  }));
}

function criticalityTone(value: string | null | undefined): BadgeTone {
  const normalized = value?.toLowerCase() ?? "";
  if (normalized.includes("high") || normalized.includes("высок")) {
    return "danger";
  }
  if (normalized.includes("medium") || normalized.includes("средн")) {
    return "warn";
  }
  if (normalized.includes("low") || normalized.includes("низк")) {
    return "good";
  }
  return "neutral";
}

function priorityTone(value: string | null | undefined): BadgeTone {
  return criticalityTone(value);
}

const projectEditFields: EditField[] = [
  { name: "external_project_id", label: "Код проекта" },
  {
    name: "direction",
    label: "Направление",
    input: "select",
    options: [
      option("fmcg", formatDirection),
      option("electronics", formatDirection),
      option("kaf", formatDirection),
      option("promo", formatDirection),
      option("training", formatDirection),
      option("audit", formatDirection),
      option("mixed", formatDirection),
      option("other", formatDirection),
    ],
  },
  {
    name: "project_scale",
    label: "Масштаб проекта",
    input: "select",
    options: [
      option("local", formatProjectScale),
      option("regional", formatProjectScale),
      option("federal", formatProjectScale),
      option("interregional", formatProjectScale),
      option("unknown", formatProjectScale),
    ],
  },
  { name: "short_description", label: "Краткое описание", input: "textarea" },
  { name: "known_regions", label: "Известные регионы", input: "textarea" },
  {
    name: "primary_operational_model",
    label: "Основная операционная модель",
    input: "select",
    options: operationalModelOptions,
  },
  {
    name: "additional_operational_contours",
    label: "Дополнительные операционные контуры",
    input: "textarea",
  },
  { name: "start_date", label: "Дата старта" },
  { name: "lifecycle_stage", label: "Этап жизненного цикла", input: "select", options: lifecycleOptions },
  { name: "project_status", label: "Статус проекта", input: "select", options: projectStatusOptions },
];

const lprEditFields: EditField[] = [
  { name: "external_lpr_id", label: "ID в базе данных" },
  { name: "role_zone", label: "Место в структуре / зона влияния", input: "textarea" },
  { name: "influence_level", label: "Уровень влияния", input: "select", options: influenceOptions },
  { name: "activity_status", label: "Статус активности", input: "select", options: activityOptions },
  { name: "relationship_status", label: "Отношение", input: "select", options: relationshipOptions },
  { name: "evidence_basis", label: "Основание вывода", input: "textarea" },
  { name: "manual_comment", label: "Комментарий", input: "textarea" },
];

function buildGoalEditFields(effectiveness: ProjectEffectiveness): EditField[] {
  return [
    { name: "goal_owner", label: "Владелец цели" },
    { name: "goal_type", label: "Тип цели", input: "select", options: goalTypeOptions },
    { name: "goal_text", label: "Текст цели", input: "textarea" },
    { name: "priority", label: "Приоритет", input: "select", options: priorityOptions },
    {
      name: "related_kpi_or_criterion_text",
      label: "Связанные KPI / критерии",
      input: "multiselect",
      options: buildKpiRelationOptions(effectiveness.cjm.kpis),
    },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

function buildKpiEditFields(effectiveness: ProjectEffectiveness): EditField[] {
  return [
    { name: "kpi_name", label: "Название KPI / критерия", input: "textarea" },
    {
      name: "kpi_type",
      label: "Тип KPI",
      input: "select",
      options: mergeOptions(kpiTypeOptions, buildRawOptions(effectiveness.cjm.kpis, (kpi) => kpi.kpi_type, formatKpiType)),
    },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    {
      name: "related_expectation_text",
      label: "Связанные ожидания",
      input: "multiselect",
      options: effectiveness.cjm.expectations.map((item) => ({ value: item.expectation_text, label: item.expectation_text })),
    },
    {
      name: "related_barrier_text",
      label: "Связанные барьеры",
      input: "multiselect",
      options: effectiveness.cjm.barriers.map((item) => ({ value: item.barrier_title, label: item.barrier_title })),
    },
    { name: "client_criticality", label: "Критичность для клиента", input: "select", options: criticalityOptions },
    { name: "requires_confirmation", label: "Требует подтверждения", input: "select", options: confirmationOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

function buildBarrierEditFields(effectiveness: ProjectEffectiveness): EditField[] {
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
      options: buildImportanceRelationOptions(effectiveness.cjm.lprs),
    },
    {
      name: "linked_kpi_text",
      label: "Связанные KPI",
      input: "multiselect",
      options: buildKpiRelationOptions(effectiveness.cjm.kpis),
    },
    { name: "source_text", label: "Источник", input: "textarea" },
    { name: "evidence_quote", label: "Подтверждение / цитата", input: "textarea" },
    { name: "status", label: "Статус", input: "select", options: barrierStatusOptions },
    { name: "relevance_status", label: "Актуальность", input: "select", options: relevanceOptions },
    { name: "confidence_level", label: "Уверенность", input: "select", options: confidenceOptions },
  ];
}

function buildCommunicationEditFields(effectiveness: ProjectEffectiveness): EditField[] {
  const lprOptions = effectiveness.cjm.lprs.map((lpr) => ({
    value: lpr.external_lpr_id || lpr.lpr_code,
    label: `${lpr.role_zone || lpr.role} (${lpr.external_lpr_id || lpr.lpr_code})`,
  }));

  return [
    {
      name: "external_lpr_id",
      label: "Контакт клиента (выбрать ЛПР)",
      input: "select",
      options: lprOptions,
    },
    { name: "client_side", label: "Контакт клиента (описание / роль)" },
    {
      name: "open_side_role",
      label: "Контакт OPEN",
      input: "multiselect",
      options: openContactOptions,
    },
    { name: "open_side_role_custom", label: "Контакт OPEN (добавить свой)" },
    { name: "topic_text", label: "Тема", input: "textarea" },
    { name: "frequency", label: "Частота" },
    { name: "channel_text", label: "Канал" },
    { name: "criticality", label: "Критичность", input: "select", options: criticalityOptions },
    { name: "comment", label: "Комментарий", input: "textarea" },
  ];
}

const factCollectionFields: CollectionField[] = [
  { name: "label", label: "Название параметра" },
  { name: "value", label: "Значение", input: "textarea", rows: 3 },
];

const clientVisionFields: CollectionField[] = [
  { name: "title", label: "Блок" },
  { name: "value", label: "Что говорит клиент", input: "textarea", rows: 3 },
  { name: "use", label: "Как использовать в работе", input: "textarea", rows: 3 },
];

const contourFields: CollectionField[] = [
  { name: "contour", label: "Контур" },
  { name: "owner", label: "Ответственный" },
  { name: "text", label: "Описание", input: "textarea", rows: 3 },
];

const historyFields: CollectionField[] = [
  { name: "year", label: "Год / период" },
  { name: "title", label: "Событие" },
  { name: "text", label: "Что произошло", input: "textarea", rows: 3 },
];

const needFields: CollectionField[] = [
  { name: "level", label: "Уровень" },
  { name: "title", label: "Название" },
  { name: "description", label: "Описание", input: "textarea", rows: 3 },
];

const structureFields: CollectionField[] = [
  { name: "role", label: "Роль" },
  { name: "person", label: "Место в структуре / роль в базе" },
  { name: "zone", label: "Зона ответственности / влияния", input: "textarea", rows: 3 },
];

const competitorFields: CollectionField[] = [
  { name: "name", label: "Компания / игрок" },
  { name: "strengths", label: "Сильные стороны", input: "textarea", rows: 4 },
  { name: "weaknesses", label: "Слабые стороны", input: "textarea", rows: 4 },
];

const interpretationRuleFields: CollectionField[] = [
  { name: "rule", label: "Правило", input: "textarea", rows: 4 },
];

const riskFields: CollectionField[] = [
  { name: "title", label: "Риск", input: "textarea", rows: 2 },
  { name: "barrier_type", label: "Тип риска", input: "select", options: barrierTypeOptions },
  { name: "probability_level", label: "Вероятность", input: "select", options: criticalityOptions },
  { name: "probability_basis", label: "Основание вероятности", input: "textarea", rows: 3 },
  { name: "impact_level", label: "Влияние", input: "select", options: criticalityOptions },
  { name: "impact_basis", label: "Основание влияния", input: "textarea", rows: 3 },
  { name: "related_to", label: "Связано с", input: "textarea", rows: 2 },
  { name: "early_signal", label: "Ранние сигналы", input: "textarea", rows: 3 },
  { name: "control_action", label: "Контрольное действие", input: "textarea", rows: 3 },
  { name: "control_owner", label: "Владелец контроля" },
  { name: "review_period", label: "Период пересмотра" },
  { name: "source_text", label: "Источник", input: "textarea", rows: 2 },
];

function Passport() {
  const {
    project,
    passportHeaderFacts,
    passportOverviewItems,
    passportServiceItems,
    clientVisionItems,
    workContourItems,
    historyItems,
  } = useScreenData();
  const {
    editProject,
    editPassportHeader,
    editPassportOverview,
    editPassportService,
    editClientVision,
    editWorkContours,
    editProjectHistory,
  } = useScreenActions();

  const Section = ({
    eyebrow,
    title,
    description,
    children,
    action,
    onAction,
  }: {
    eyebrow: string;
    title: string;
    description?: string;
    children: ReactNode;
    action?: string;
    onAction?: () => void;
  }) => (
    <section className="grid grid-cols-1 gap-5 border-t border-slate-100 px-4 py-5 sm:px-5 sm:py-6 xl:grid-cols-[260px_1fr] xl:px-6">
      <div>
        <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-400">{eyebrow}</div>
        <h3 className="mt-2 text-lg font-semibold text-slate-950">{title}</h3>
        {description && <p className="mt-2 text-sm leading-6 text-slate-500">{description}</p>}
        {action ? (
          <button
            onClick={onAction}
            className="mt-4 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            {action}
          </button>
        ) : null}
      </div>
      <div className="min-w-0">{children}</div>
    </section>
  );

  const FieldSet = ({ items }: { items: FactItem[] }) => (
    <div className="grid grid-cols-1 overflow-hidden rounded-2xl border border-slate-200 bg-white md:grid-cols-2">
      {items.map((item) => (
        <div key={item.label} className="border-b border-slate-100 px-4 py-4 last:border-b-0 md:border-r md:last:border-r-0 md:[&:nth-last-child(-n+2)]:border-b-0 md:[&:nth-child(even)]:border-r-0">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">{item.label}</div>
          <div className="mt-2 text-sm font-medium leading-6 text-slate-900">{item.value}</div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-5">
      <div className="overflow-hidden rounded-[30px] bg-slate-950 shadow-sm">
        <div className="grid grid-cols-1 xl:grid-cols-[1fr_260px]">
          <div className="bg-white p-4 text-slate-950 sm:p-6 xl:p-7">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="good">{formatProjectStatus(project.project_status || "active")}</Badge>
              <Badge tone="blue">{project.direction}</Badge>
              <Badge tone="neutral">{project.scale}</Badge>
              <Badge tone="neutral">{project.lifecycle}</Badge>
            </div>
            <h2 className="mt-5 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">Паспорт проекта · {project.externalId}</h2>
            <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-500">{project.serviceModel}</p>
          </div>

          <div className="border-t border-white/10 bg-slate-950 p-4 text-white sm:p-6 xl:border-l xl:border-t-0">
            <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Последнее обновление</div>
            <div className="mt-2 text-lg font-semibold text-white">{project.lastUpdated}</div>
            <div className="mt-5 space-y-2">
              <button
                onClick={editProject}
                className="w-full rounded-xl bg-white px-4 py-2 text-sm font-medium text-slate-900 shadow-sm hover:bg-slate-100"
              >
                Редактировать шапку
              </button>
              <button
                onClick={() => editPassportHeader(passportHeaderFacts)}
                className="w-full rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium text-white hover:bg-white/15"
              >
                Редактировать факты
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 border-t border-white/10 bg-slate-950 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
          {passportHeaderFacts.map((item) => (
            <div key={item.label} className="min-w-0 border-t border-white/10 px-4 py-4 first:border-t-0 xl:border-l xl:border-t-0 xl:first:border-l-0 2xl:border-l">
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{item.label}</div>
              <div className="mt-2 text-sm font-semibold text-white break-words">{item.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-[30px] border border-slate-200 bg-white shadow-sm">
        <Section
          eyebrow="01"
          title="Основные параметры"
          description="Базовые реквизиты проекта: идентификаторы, статус, этап, договорной контур и стратегическая важность."
          action="Редактировать"
          onAction={() => editPassportOverview(passportOverviewItems)}
        >
          <FieldSet items={passportOverviewItems} />
        </Section>

        <Section
          eyebrow="02"
          title="Модель сервиса"
          description="Что OPEN фактически оказывает клиенту и в каком операционном формате работает проект."
          action="Редактировать"
          onAction={() => editPassportService(passportServiceItems)}
        >
          <FieldSet items={passportServiceItems} />
        </Section>

        <Section
          eyebrow="03"
          title="Видение клиента"
          description="Как клиент описывает ценную услугу и зрелого поставщика. Это контекст для будущих оценок и комментариев."
          action="Редактировать"
          onAction={() => editClientVision(clientVisionItems)}
        >
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            {clientVisionItems.map((item, index) => (
              <div key={item.title} className="grid grid-cols-1 gap-3 border-t border-slate-100 px-4 py-4 first:border-t-0 lg:grid-cols-[42px_1fr_1fr_1fr] lg:gap-5">
                <div className="hidden text-sm font-semibold text-slate-300 lg:block">{String(index + 1).padStart(2, "0")}</div>
                <div className="text-sm font-semibold leading-6 text-slate-950">{item.title}</div>
                <div className="text-sm leading-6 text-slate-700">{item.value}</div>
                <div className="text-sm leading-6 text-slate-500">{item.use}</div>
              </div>
            ))}
          </div>
        </Section>

        <Section
          eyebrow="04"
          title="Контуры работы"
          description="Рабочая схема проекта: кто отвечает за отношения, операционное исполнение, полевую команду и данные."
          action="Редактировать"
          onAction={() => editWorkContours(workContourItems)}
        >
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            {workContourItems.map((row, index) => (
              <div key={row.contour} className="grid grid-cols-1 gap-3 border-t border-slate-100 px-4 py-4 first:border-t-0 lg:grid-cols-[42px_1fr_1fr_1fr] lg:gap-5">
                <div className="hidden text-sm font-semibold text-slate-300 lg:block">{String(index + 1).padStart(2, "0")}</div>
                <div className="text-sm font-semibold leading-6 text-slate-950">{row.contour}</div>
                <div className="text-sm font-medium leading-6 text-slate-800">{row.owner}</div>
                <div className="text-sm leading-6 text-slate-600">{row.text}</div>
              </div>
            ))}
          </div>
        </Section>

        <Section
          eyebrow="05"
          title="История проекта"
          description="Ключевые этапы развития проекта и изменения, которые важны для передачи контекста."
          action="Редактировать"
          onAction={() => editProjectHistory(historyItems)}
        >
          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
            {historyItems.map((item) => (
              <div key={item.year} className="grid grid-cols-1 gap-2 border-t border-slate-100 px-4 py-4 first:border-t-0 md:grid-cols-[90px_260px_1fr] md:gap-5">
                <div className="text-sm font-semibold text-slate-950">{item.year}</div>
                <div className="text-sm font-medium leading-6 text-slate-900">{item.title}</div>
                <div className="text-sm leading-6 text-slate-600">{item.text}</div>
              </div>
            ))}
          </div>
        </Section>
      </div>
    </div>
  );
}

function Goals() {
  const { projectGoals, clientNeedsItems, openNeedsItems } = useScreenData();
  const { editGoal, editNeeds, createGoal, archiveGoal } = useScreenActions();
  const NeedPyramid = ({
    title,
    items,
    tone,
  }: {
    title: string;
    items: typeof clientNeeds;
    tone: "client" | "open";
  }) => (
    <Card>
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <div className="mt-5 flex flex-col-reverse gap-3">
        {items.map((item, index) => (
          <div
            key={item.title}
            className={`mx-auto rounded-2xl border p-4 text-center shadow-sm ${
              tone === "client" ? "border-sky-200 bg-sky-50" : "border-violet-200 bg-violet-50"
            }`}
            style={{ width: `${70 + index * 8}%` }}
          >
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{item.level}</div>
            <div className="mt-1 text-sm font-semibold text-slate-900">{item.title}</div>
            <p className="mt-2 text-xs leading-5 text-slate-600">{item.description}</p>
          </div>
        ))}
      </div>
    </Card>
  );

  const contourTone = (contour: string): BadgeTone => {
    if (contour === "Клиент") return "blue";
    if (contour === "ЛПР") return "warn";
    return "violet";
  };

  return (
    <div className="space-y-6">
      <SectionTitle
        title="Цели OPEN и клиента"
        description="Цели фиксируют желаемый результат проекта. KPI на отдельном листе показывают, какими показателями эти цели проверяются."
      />

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div>
          <div className="mb-3 flex justify-end">
            <button
              onClick={() => editNeeds("client", clientNeedsItems)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Редактировать пирамиду клиента
            </button>
          </div>
          <NeedPyramid title="Пирамида потребностей клиента" items={clientNeedsItems} tone="client" />
        </div>
        <div>
          <div className="mb-3 flex justify-end">
            <button
              onClick={() => editNeeds("open", openNeedsItems)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Редактировать пирамиду OPEN
            </button>
          </div>
          <NeedPyramid title="Пирамида потребностей OPEN" items={openNeedsItems} tone="open" />
        </div>
      </div>

      <div className="[overflow:clip] rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Реестр целей проекта</h3>
              <p className="mt-1 text-sm leading-6 text-slate-500">
                Здесь хранится управленческая рамка: какой результат нужен клиенту, ЛПР и OPEN.
              </p>
            </div>
            <button
              onClick={createGoal}
              className="shrink-0 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Добавить новую цель
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[860px] table-fixed text-left text-sm">
            <colgroup>
              <col className="w-[86px]" />
              <col className="w-[120px]" />
              <col className="w-[220px]" />
              <col className="w-[140px]" />
              <col className="w-[240px]" />
              <col className="w-[200px]" />
              <col className="w-[160px]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="whitespace-nowrap px-4 py-3">ID</th>
                <th className="whitespace-nowrap px-4 py-3">Контур</th>
                <th className="px-4 py-3">Цель</th>
                <th className="whitespace-nowrap px-4 py-3">Тип</th>
                <th className="px-4 py-3">Смысл для проекта</th>
                <th className="px-4 py-3">Связанные KPI / критерии</th>
                <th className="whitespace-nowrap px-4 py-3">Владелец</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {projectGoals.map((goal) => (
                <tr key={goal.id} className="align-top hover:bg-slate-50">
                  <td className="whitespace-nowrap px-4 py-4 font-semibold text-slate-900">
                    {formatEntityCode((goal as { entityCode?: string }).entityCode || goal.id)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-4"><Badge tone={contourTone(goal.contour)}>{goal.contour}</Badge></td>
                  <td className="px-4 py-4 font-medium leading-6 text-slate-900">{goal.goal}</td>
                  <td className="whitespace-nowrap px-4 py-4 text-slate-700">{goal.type}</td>
                  <td className="px-4 py-4 leading-6 text-slate-600">{goal.meaning}</td>
                  <td className="px-4 py-4 leading-6 text-slate-600">{goal.evidence}</td>
                  <td className="px-4 py-4 font-medium text-slate-900">
                    <div className="flex items-center justify-between gap-3">
                      <span>{goal.owner}</span>
                      {"raw" in goal ? (
                        <div className="flex flex-wrap gap-2">
                          <button
                            onClick={() => editGoal((goal as { raw: Goal }).raw)}
                            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                          >
                            Редактировать
                          </button>
                          <button
                            onClick={() => archiveGoal((goal as { raw: Goal }).raw)}
                            className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-100"
                          >
                            В архив
                          </button>
                        </div>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function ProjectMap() {
  const { contacts, openStructureItems, clientStructureItems } = useScreenData();
  const { editLpr, createLpr, archiveLpr, editOpenStructure, editClientStructure } = useScreenActions();
  const [expandedContact, setExpandedContact] = useState<string | null>("ЛПР 1");

  return (
    <div>
      <SectionTitle
        title="Карта влияния и ЛПР"
        description="Раздел фиксирует роли влияния, ожидания ЛПР и правила взаимодействия: кто влияет на решение, что для него важно, кто ведёт контакт со стороны OPEN и на чём основан профиль."
      />

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Card>
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold text-slate-900">Структура OPEN</h3>
            <button
              onClick={() => editOpenStructure(openStructureItems)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Редактировать
            </button>
          </div>
          <div className="mt-4 space-y-3">
            {openStructureItems.map((item) => (
              <div key={item.role} className="rounded-2xl bg-slate-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{item.role}</div>
                    <div className="mt-1 text-sm text-slate-500">{item.person}</div>
                  </div>
                  <Badge tone="neutral">OPEN</Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">{item.zone}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold text-slate-900">Структура клиента</h3>
            <button
              onClick={() => editClientStructure(clientStructureItems)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Редактировать
            </button>
          </div>
          <div className="mt-4 space-y-3">
            {clientStructureItems.map((item) => (
              <div key={item.role} className="rounded-2xl bg-slate-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">{item.role}</div>
                    <div className="mt-1 text-sm text-slate-500">{item.person}</div>
                  </div>
                  <Badge tone="blue">клиент</Badge>
                </div>
                <p className="mt-2 text-sm leading-6 text-slate-600">{item.zone}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-5">
        <div className="mb-4 flex items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Профили ЛПР</h3>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              Карточка раскрывается, чтобы видеть роль ЛПР, его ожидания, удобный формат коммуникации и подтверждающие факты.
            </p>
          </div>
          <button
            onClick={createLpr}
            className="shrink-0 rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Добавить профиль роли
          </button>
        </div>

        <div className="space-y-4">
          {contacts.map((contact) => {
            const isOpen = expandedContact === contact.id;

            return (
              <Card key={contact.id} className={isOpen ? "border-slate-900" : ""}>
                <button
                  onClick={() => setExpandedContact(isOpen ? null : contact.id)}
                  className="flex w-full items-start justify-between gap-4 text-left"
                >
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        {formatEntityCode((contact as { entityCode?: string }).entityCode || contact.id)}
                      </div>
                      <Badge tone={criticalityTone(contact.influence)}>влияние: {contact.influence}</Badge>
                      <Badge tone="neutral">{contact.attitude}</Badge>
                    </div>
                    <h3 className="mt-2 text-lg font-semibold text-slate-900">{contact.role}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{contact.decisionRole}</p>
                  </div>
                  <span className="shrink-0 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-medium text-slate-600">
                    {isOpen ? "свернуть" : "раскрыть"}
                  </span>
                </button>

                {isOpen && (
                  <div className="mt-5 space-y-4 border-t border-slate-100 pt-5">
                    {"raw" in contact ? (
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => editLpr((contact as { raw: LprProfile }).raw)}
                          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Редактировать
                        </button>
                        <button
                          onClick={() => archiveLpr((contact as { raw: LprProfile }).raw)}
                          className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-800 hover:bg-amber-100"
                        >
                          В архив
                        </button>
                      </div>
                    ) : null}
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Зона влияния</div>
                        <div className="mt-2 text-sm font-medium leading-6 text-slate-900">{contact.decisionRole}</div>
                      </div>
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Ответственный OPEN</div>
                        <div className="mt-2 text-sm font-medium leading-6 text-slate-900">{contact.interaction.owner}</div>
                      </div>
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">ID в базе данных</div>
                        <div className="mt-2 text-sm font-medium leading-6 text-slate-900">{formatText(("raw" in contact ? (contact as { raw: LprProfile }).raw.external_lpr_id : "") || "")}</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
                      <div className="rounded-2xl bg-sky-50 p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-sky-700">Что важно для ЛПР</div>
                        <div className="mt-3 space-y-3">
                          {contact.values.map((item) => (
                            <div key={item.name} className="rounded-2xl bg-white/80 p-3">
                              <div className="flex items-start justify-between gap-3">
                                <div className="text-sm font-semibold text-slate-900">{item.name}</div>
                                <Badge tone={priorityTone(item.priority)}>{item.priority}</Badge>
                              </div>
                              <p className="mt-2 text-sm leading-5 text-slate-600">{item.description}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="rounded-2xl bg-emerald-50 p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-emerald-700">Как взаимодействовать</div>
                        <div className="mt-3 rounded-2xl bg-white/80 p-3 text-sm font-medium leading-6 text-slate-900">
                          {contact.interaction.preferredFormat}
                        </div>
                        <ul className="mt-3 space-y-2 text-sm leading-5 text-slate-600">
                          {contact.doRules.map((item) => (
                            <li key={item}>• {item}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="rounded-2xl bg-rose-50 p-4">
                        <div className="text-xs font-semibold uppercase tracking-wide text-rose-700">Чего избегать</div>
                        <ul className="mt-3 space-y-2 text-sm leading-5 text-slate-600">
                          {contact.dontRules.map((item) => (
                            <li key={item}>• {item}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                      <div>
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Основание профиля</div>
                            <p className="mt-2 text-sm leading-6 text-slate-700">{contact.profileSource}</p>
                          </div>
                          <Badge tone="neutral">подтверждающие факты</Badge>
                        </div>

                        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
                          {contact.profileEvidence.map((item) => (
                            <div key={`${contact.id}-${item.source}-${item.confirms}`} className="rounded-2xl bg-white p-4">
                              <div className="text-sm font-semibold text-slate-900">{item.source}</div>
                              <p className="mt-2 text-sm leading-5 text-slate-600">{item.detail}</p>
                              <div className="mt-3 border-t border-slate-100 pt-3 text-xs leading-5 text-slate-500">
                                Подтверждает: {item.confirms}
                              </div>
                            </div>
                          ))}
                        </div>

                        <p className="mt-4 text-sm leading-6 text-slate-500">{contact.notes}</p>
                      </div>
                    </div>
                  </div>
                )}
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function Competitors() {
  const { competitorsOpenItems, competitorsClientItems } = useScreenData();
  const { editOpenCompetitors, editClientCompetitors } = useScreenActions();
  const Block = ({
    title,
    items,
    tone,
    onEdit,
  }: {
    title: string;
    items: Array<{ name: string; strengths: string[]; weaknesses: string[] }>;
    tone: BadgeTone;
    onEdit: () => void;
  }) => (
    <Card>
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        <button
          onClick={onEdit}
          className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          Редактировать
        </button>
      </div>
      <div className="mt-4 space-y-4">
        {items.map((item) => (
          <div key={item.name} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-start justify-between gap-3">
              <h4 className="text-sm font-semibold text-slate-900">{item.name}</h4>
              <Badge tone={tone}>{title.includes("OPEN") ? "для OPEN" : "для клиента"}</Badge>
            </div>
            <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-emerald-700">Сильные стороны</div>
                <ul className="mt-2 space-y-1 text-sm text-slate-600">
                  {item.strengths.map((text) => <li key={text}>• {text}</li>)}
                </ul>
              </div>
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-rose-700">Слабые стороны</div>
                <ul className="mt-2 space-y-1 text-sm text-slate-600">
                  {item.weaknesses.map((text) => <li key={text}>• {text}</li>)}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );

  return (
    <div>
      <SectionTitle
        title="Конкурентный контур проекта"
        description="Внешний контекст проекта: какие промо-, BTL-, field marketing- и аутсорсинговые компании могут конкурировать с OPEN за проект, а какие бренды давят на клиента в рознице."
      />
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <Block
          title="Конкуренты OPEN"
          items={competitorsOpenItems}
          tone="violet"
          onEdit={() => editOpenCompetitors(competitorsOpenItems)}
        />
        <Block
          title="Конкуренты клиента"
          items={competitorsClientItems}
          tone="blue"
          onEdit={() => editClientCompetitors(competitorsClientItems)}
        />
      </div>
    </div>
  );
}

function Swot() {
  const { swot } = useScreenData();
  const { editSwot } = useScreenActions();
  const blocks: Array<{ title: string; items: string[]; className: string }> = [
    { title: "Сильные стороны", items: swot.strengths, className: "bg-emerald-50 border-emerald-200" },
    { title: "Слабые стороны", items: swot.weaknesses, className: "bg-amber-50 border-amber-200" },
    { title: "Возможности", items: swot.opportunities, className: "bg-sky-50 border-sky-200" },
    { title: "Угрозы", items: swot.threats, className: "bg-rose-50 border-rose-200" },
  ];

  return (
    <div>
      <SectionTitle
        title="SWOT-анализ проекта"
        description="Короткий управленческий разбор проекта: что усиливает позицию OPEN, что ослабляет, где есть точки роста и что может ударить по проекту."
        action="Редактировать"
        onAction={() => editSwot(swot)}
      />
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        {blocks.map(({ title, items, className }) => (
          <div key={title} className={`rounded-3xl border p-5 shadow-sm ${className}`}>
            <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
              {items.map((item) => (
                <li key={item} className="rounded-2xl bg-white/70 p-3">• {item}</li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function Communications() {
  const { communications } = useScreenData();
  const { createCommunication, editCommunication, archiveCommunication } = useScreenActions();
  const [selectedId, setSelectedId] = useState<string>(communications[0]?.id || "");
  const selected = communications.find((item) => item.id === selectedId) || communications[0];

  useEffect(() => {
    if (!selectedId && communications[0]?.id) {
      setSelectedId(communications[0].id);
    }
  }, [communications, selectedId]);

  return (
    <div>
      <SectionTitle
        title="Матрица коммуникаций"
        description="Кто с кем общается, по каким темам, с какой частотой, через какой канал и где критичность коммуникации высокая."
        action="Добавить контакт"
        onAction={createCommunication}
      />
      <div className="[overflow:clip] rounded-3xl border border-slate-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
        <table className="w-full min-w-[980px] text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              {["Контакт клиента", "Контакт OPEN", "Тема", "Частота", "Канал", "Критичность", "Комментарий"].map((h) => (
                <th key={h} className="px-4 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {communications.map((row) => (
              <tr
                key={row.id}
                onClick={() => setSelectedId(row.id)}
                className={`cursor-pointer hover:bg-slate-50 ${selected?.id === row.id ? "bg-slate-50" : ""}`}
              >
                <td className="px-4 py-4 text-slate-700">{row.clientSide}</td>
                <td className="px-4 py-4 text-slate-700">{row.openSide}</td>
                <td className="px-4 py-4 text-slate-700">{row.topic}</td>
                <td className="px-4 py-4 text-slate-700">{row.frequency}</td>
                <td className="px-4 py-4 text-slate-700">{row.channel}</td>
                <td className="px-4 py-4 text-slate-700"><Badge tone={criticalityTone(row.criticality)}>{row.criticality}</Badge></td>
                <td className="px-4 py-4 text-slate-700">{row.comment || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        </div>
      </div>
      {selected ? (
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            onClick={() => editCommunication(selected.raw)}
            className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Редактировать запись
          </button>
          <button
            onClick={() => archiveCommunication(selected.raw)}
            className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-800 shadow-sm hover:bg-amber-100"
          >
            В архив
          </button>
        </div>
      ) : null}
    </div>
  );
}

function InterpretationRules() {
  const { interpretationRuleItems } = useScreenData();
  const { editInterpretationRules } = useScreenActions();
  return (
    <div className="space-y-5">
      <SectionTitle
        title="Правила интерпретации проекта"
        description="Методические правила чтения будущих данных по проекту: опросов, 360, ОЭД, KPI, финансов и проектных исключений."
        action="Редактировать"
        onAction={() => editInterpretationRules(interpretationRuleItems)}
      />

      <div className="[overflow:clip] rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <h3 className="text-lg font-semibold text-slate-950">Реестр правил</h3>
          <p className="mt-1 text-sm leading-6 text-slate-500">
            Правила задают корректную трактовку данных: фактическое исполнение, восприятие клиента, управленческая среда и экономика проекта читаются в связке с контекстом.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] table-fixed text-left text-sm">
            <colgroup>
              <col className="w-[88px]" />
              <col className="w-[220px]" />
              <col className="w-[220px]" />
              <col className="w-[330px]" />
              <col className="w-[300px]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="whitespace-nowrap px-4 py-3">ID</th>
                <th className="px-4 py-3">Правило</th>
                <th className="px-4 py-3">Где применяется</th>
                <th className="px-4 py-3">Как использовать</th>
                <th className="px-4 py-3">Пример</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {interpretationRuleItems.map((item) => (
                <tr key={item.id} className="align-top hover:bg-slate-50">
                  <td className="whitespace-nowrap px-4 py-4 font-semibold text-slate-900">{item.id}</td>
                  <td className="px-4 py-4 font-medium leading-6 text-slate-900">{item.title}</td>
                  <td className="px-4 py-4 leading-6 text-slate-600">{item.appliesTo}</td>
                  <td className="px-4 py-4 leading-6 text-slate-700">{item.rule}</td>
                  <td className="px-4 py-4 leading-6 text-slate-600">{item.example}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function Kpi() {
  const { kpis, relationText } = useScreenData();
  const { editKpi, createKpi, archiveKpi } = useScreenActions();
  const [selectedKpiId, setSelectedKpiId] = useState("KPI-01");
  const selectedKpi = kpis.find((item) => item.id === selectedKpiId) || kpis[0];

  const kpiGroups = Array.from(new Set(kpis.map((item) => item.sourceBlock))).map((group) => ({
    group,
    count: kpis.filter((item) => item.sourceBlock === group).length,
  }));

  return (
    <div className="space-y-5">
      <SectionTitle
        title="KPI проекта"
        description="Критерии, по которым проект оценивается клиентом, ЛПР и OPEN: коммерческие цели, качество услуги, полевое исполнение, риски и экономика."
        action="Добавить KPI"
        onAction={createKpi}
      />

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {kpiGroups.map((item) => (
          <div key={item.group} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Контур</div>
            <div className="mt-2 text-sm font-semibold leading-5 text-slate-900">{item.group}</div>
            <div className="mt-3 text-2xl font-semibold text-slate-950">{item.count}</div>
            <div className="mt-1 text-xs text-slate-500">KPI / критерия</div>
          </div>
        ))}
      </div>

      <div className="[overflow:clip] rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-100 px-5 py-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Реестр KPI</h3>
              <p className="mt-1 text-sm leading-6 text-slate-500">
                В таблице хранятся сами критерии проекта. Подробности по выбранному KPI открываются ниже.
              </p>
            </div>
            <div className="text-right text-xs leading-5 text-slate-500">
              <div>Всего: <span className="font-semibold text-slate-900">{kpis.length}</span></div>
              <div>Высокий приоритет: <span className="font-semibold text-slate-900">{kpis.filter((item) => item.priority.includes("Высок")).length}</span></div>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[1040px] table-fixed text-left text-sm">
            <colgroup>
              <col className="w-[88px]" />
              <col className="w-[300px]" />
              <col className="w-[210px]" />
              <col className="w-[210px]" />
              <col className="w-[150px]" />
              <col className="w-[132px]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="whitespace-nowrap px-4 py-3">ID</th>
                <th className="px-4 py-3">KPI / критерий</th>
                <th className="whitespace-nowrap px-4 py-3">Контур</th>
                <th className="whitespace-nowrap px-4 py-3">Связанные цели</th>
                <th className="whitespace-nowrap px-4 py-3">Тип</th>
                <th className="whitespace-nowrap px-4 py-3">Приоритет</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {kpis.map((kpi) => {
                const isActive = selectedKpiId === kpi.id;
                return (
                  <tr
                    key={kpi.id}
                    onClick={() => setSelectedKpiId(kpi.id)}
                    className={`cursor-pointer align-top hover:bg-slate-50 ${isActive ? "bg-slate-50" : ""}`}
                  >
                    <td className="whitespace-nowrap px-4 py-4 font-semibold text-slate-900">
                      {formatEntityCode((kpi as { entityCode?: string }).entityCode || kpi.id)}
                    </td>
                    <td className="px-4 py-4">
                      <div className="font-medium leading-5 text-slate-900">{kpi.name}</div>
                      <div className="mt-1 line-clamp-2 text-xs leading-5 text-slate-500">{kpi.purpose}</div>
                    </td>
                    <td className="px-4 py-4 text-slate-700">{kpi.sourceBlock}</td>
                    <td className="px-4 py-4">
                      <div className="flex flex-wrap gap-2">
                        {kpi.goals.map((goalName) => (
                          <Badge key={`${kpi.id}-${goalName}`} tone="neutral">{goalName}</Badge>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-4 text-slate-700">{kpi.type}</td>
                    <td className="whitespace-nowrap px-4 py-4"><Badge tone={priorityTone(kpi.priority)}>{kpi.priority}</Badge></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="whitespace-nowrap text-sm font-semibold text-slate-900">
                {formatEntityCode((selectedKpi as { entityCode?: string }).entityCode || selectedKpi.id)}
              </span>
              <Badge tone="neutral">{selectedKpi.sourceBlock}</Badge>
              <Badge tone={priorityTone(selectedKpi.priority)}>приоритет: {selectedKpi.priority}</Badge>
              <Badge tone="blue">{selectedKpi.type}</Badge>
            </div>
            <h3 className="mt-3 text-lg font-semibold leading-7 text-slate-950">{selectedKpi.name}</h3>
            <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-600">{selectedKpi.purpose}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => "raw" in selectedKpi && editKpi((selectedKpi as { raw: Kpi }).raw)}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              Редактировать KPI
            </button>
            {"raw" in selectedKpi ? (
              <button
                onClick={() => archiveKpi((selectedKpi as { raw: Kpi }).raw)}
                className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-2 text-sm font-medium text-amber-800 shadow-sm hover:bg-amber-100"
              >
                В архив
              </button>
            ) : null}
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 xl:grid-cols-12">
          <div className="rounded-2xl bg-slate-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Как измерять</div>
            <p className="mt-2 text-sm leading-6 text-slate-700">{selectedKpi.measurement}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Источник данных</div>
            <p className="mt-2 text-sm leading-6 text-slate-700">{selectedKpi.dataSource}</p>
            <div className="mt-3 text-xs leading-5 text-slate-500">Владелец: {selectedKpi.owner}</div>
          </div>
          <div className="rounded-2xl bg-amber-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-amber-700">Что уточнить</div>
            <p className="mt-2 text-sm leading-6 text-slate-700">{selectedKpi.clarify}</p>
          </div>
        </div>

        <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
          <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Связанные объекты контекста</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {selectedKpi.linked.map((item) => (
              <Badge key={`${selectedKpi.id}-${item}`} tone="blue">{relationText(item)}</Badge>
              ))}
            </div>
          <p className="mt-3 text-xs leading-5 text-slate-500">
            Здесь полезно видеть, к каким целям относится KPI: один показатель может подтверждать несколько целей клиента, ЛПР или OPEN.
          </p>
        </div>
      </div>
    </div>
  );
}

function RiskMap() {
  const { riskMap } = useScreenData();
  const { editBarrier, editRiskMap } = useScreenActions();
  const [expandedRisk, setExpandedRisk] = useState("R-01");

  type RiskItem = (typeof riskMap)[number];
  const riskScore = (item: RiskItem) => item.probability.score * item.impact.score;
  const riskLevel = (item: RiskItem) => {
    const score = riskScore(item);
    if (score >= 6) return "Высокий";
    if (score >= 3) return "Средний";
    return "Низкий";
  };
  const riskTone = (level: string): BadgeTone => {
    if (level === "Высокий") return "danger";
    if (level === "Средний") return "warn";
    return "good";
  };

  const riskStats = [
    { label: "Высокие", value: riskMap.filter((item) => riskLevel(item) === "Высокий").length },
    { label: "Средние", value: riskMap.filter((item) => riskLevel(item) === "Средний").length },
    { label: "Низкие", value: riskMap.filter((item) => riskLevel(item) === "Низкий").length },
    { label: "Всего", value: riskMap.length },
  ];

  const rules = [
    {
      title: "Кто добавляет риск",
      text: "В MVP риск создаёт человек: КАМ, GKAM, РМ или аналитик. Система не должна сама записывать риск в реестр без подтверждения.",
    },
    {
      title: "Как может помогать система",
      text: "Позже система может подсвечивать кандидатов в риски из KPI, опросов, комментариев и коммуникаций, но только как черновик на проверку.",
    },
    {
      title: "Как считается уровень",
      text: "Уровень = вероятность × влияние. Вероятность и влияние выставляются вручную по шкале 1–3 с обязательным основанием.",
    },
    {
      title: "Что обязательно заполнить",
      text: "Риск, связь с объектами проекта, основание, владелец, контрольное действие и срок пересмотра.",
    },
  ];

  const selectedRisk = riskMap.find((item) => item.id === expandedRisk) || riskMap[0];
  const selectedLevel = riskLevel(selectedRisk);

  return (
    <div className="space-y-5">
      <SectionTitle
        title="Карта рисков"
        description="Рабочий реестр рисков проекта. В MVP риски добавляются вручную проектной командой; автоматические сигналы могут быть только подсказками на проверку."
        action="Редактировать карту"
        onAction={() =>
          editRiskMap(
            riskMap.map((item) =>
              ("raw" in item ? (item.raw as Record<string, unknown>) : {}) as Record<string, unknown>,
            ),
          )
        }
      />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <Card className="xl:col-span-8">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-950">Правила работы</h3>
              <p className="mt-1 text-sm leading-6 text-slate-500">
                Лист фиксирует управляемый контроль рисков: каждый риск имеет основание, владельца, контрольное действие и срок пересмотра.
              </p>
            </div>
            <Badge tone="dark">ручной реестр</Badge>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {rules.map((rule) => (
              <div key={rule.title} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                <div className="text-sm font-semibold leading-5 text-slate-900">{rule.title}</div>
                <p className="mt-2 text-xs leading-5 text-slate-600">{rule.text}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card className="xl:col-span-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-lg font-semibold text-slate-950">Сводка</h3>
            <Badge tone="neutral">P × I</Badge>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-4">
            {riskStats.map((item) => (
              <div key={item.label} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-center">
                <div className="text-2xl font-semibold text-slate-950">{item.value}</div>
                <div className="mt-1 text-xs font-medium text-slate-500">{item.label}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 rounded-2xl bg-slate-50 p-3 text-xs leading-5 text-slate-600">
            P = вероятность, I = влияние. 1–2 низкий, 3–5 средний, 6–9 высокий.
          </div>
        </Card>
      </div>

      <div className="[overflow:clip] rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-950">Реестр рисков</h3>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              На небольшом экране таблица показывает только ключевые поля. Подробности открываются в карточке выбранного риска ниже.
            </p>
          </div>
          <Badge tone="dark">компактный вид</Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[1040px] table-fixed text-left text-sm">
            <colgroup>
              <col className="w-[72px]" />
              <col className="w-[360px]" />
              <col className="w-[150px]" />
              <col className="w-[150px]" />
              <col className="w-[160px]" />
              <col className="w-[148px]" />
            </colgroup>
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="whitespace-nowrap px-4 py-3">ID</th>
                <th className="px-4 py-3">Зона / риск</th>
                <th className="whitespace-nowrap px-4 py-3">Оценка</th>
                <th className="whitespace-nowrap px-4 py-3">Уровень</th>
                <th className="whitespace-nowrap px-4 py-3">Владелец</th>
                <th className="whitespace-nowrap px-4 py-3">Статус</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {riskMap.map((item) => {
                const level = riskLevel(item);
                const isActive = expandedRisk === item.id;

                return (
                  <tr
                    key={item.id}
                    onClick={() => setExpandedRisk(item.id)}
                    className={`cursor-pointer align-top hover:bg-slate-50 ${isActive ? "bg-slate-50" : ""}`}
                  >
                    <td className="whitespace-nowrap px-4 py-4 font-semibold text-slate-900">{item.id}</td>
                    <td className="px-4 py-4">
                      <div className="truncate text-xs font-medium uppercase tracking-wide text-slate-400">{item.zone}</div>
                      <div className="mt-1 line-clamp-2 font-medium leading-5 text-slate-900">{item.risk}</div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-4 text-slate-700">
                      P{item.probability.score} × I{item.impact.score} = {riskScore(item)}
                    </td>
                    <td className="whitespace-nowrap px-4 py-4"><Badge tone={riskTone(level)}>{level}</Badge></td>
                    <td className="whitespace-nowrap px-4 py-4 font-medium text-slate-900">{item.control.owner}</td>
                    <td className="whitespace-nowrap px-4 py-4"><Badge tone={item.status === "В работе" ? "danger" : "warn"}>{item.status}</Badge></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="whitespace-nowrap text-sm font-semibold text-slate-900">
                {formatEntityCode((selectedRisk as { entityCode?: string }).entityCode || selectedRisk.id)}
              </span>
              <Badge tone={riskTone(selectedLevel)}>{riskScore(selectedRisk)} · {selectedLevel}</Badge>
              <Badge tone="neutral">{selectedRisk.zone}</Badge>
            </div>
            <h3 className="mt-3 text-lg font-semibold leading-7 text-slate-950">{selectedRisk.risk}</h3>
          </div>
          <button
            onClick={() => {
              if ("raw" in selectedRisk && (selectedRisk as { raw?: Barrier }).raw) {
                editBarrier((selectedRisk as { raw: Barrier }).raw);
              }
            }}
            className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            Редактировать риск
          </button>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 xl:grid-cols-12">
          <div className="rounded-2xl bg-slate-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Вероятность</div>
            <div className="mt-2 text-sm font-semibold text-slate-900">{selectedRisk.probability.score} · {selectedRisk.probability.label}</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">{selectedRisk.probability.basis}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Влияние</div>
            <div className="mt-2 text-sm font-semibold text-slate-900">{selectedRisk.impact.score} · {selectedRisk.impact.label}</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">{selectedRisk.impact.basis}</p>
          </div>
          <div className="rounded-2xl bg-slate-50 p-4 xl:col-span-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Контроль</div>
            <div className="mt-2 text-sm font-semibold text-slate-900">{selectedRisk.control.owner}</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">{selectedRisk.control.action}</p>
            <div className="mt-3 text-xs leading-5 text-slate-500">Заполняет: {selectedRisk.control.filledBy}</div>
            <div className="text-xs leading-5 text-slate-500">Пересмотр: {selectedRisk.control.review}</div>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Связано с</div>
            <div className="mt-3 flex flex-wrap gap-2">
              {selectedRisk.linked.map((link) => (
                <Badge key={`${selectedRisk.id}-${link.type}-${link.value}`} tone="blue">{link.type}: {link.value}</Badge>
              ))}
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-500">
              Связи выбираются вручную из объектов проекта: ЛПР, KPI, роли, разделы паспорта, данные или коммуникации.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">Ранние сигналы</div>
            <div className="mt-3 space-y-2">
              {selectedRisk.earlySignals.map((signal) => (
                <div key={`${selectedRisk.id}-${signal.signal}`} className="rounded-xl bg-slate-50 px-3 py-2">
                  <div className="text-sm font-medium text-slate-800">{signal.signal}</div>
                  <div className="mt-1 text-xs text-slate-500">источник: {signal.source}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Barriers() {
  const { barriers } = useScreenData();
  const { createBarrier, editBarrier, archiveBarrier, moveBarrier } = useScreenActions();
  return (
    <div>
      <SectionTitle
        title="Барьеры: было / есть сейчас / будет"
        description="История и прогноз проблем проекта с привязкой к контактам, KPI, коммуникациям и правилам работы."
        action="Добавить барьер"
        onAction={createBarrier}
      />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {barriers.map((group) => (
          <div
            key={group.period}
            className={`min-h-[520px] rounded-3xl border p-4 ${group.color}`}
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              const rawCode = event.dataTransfer.getData("text/barrier-code");
              const barrierItem = barriers
                .flatMap((item) => item.items)
                .find((item) => "raw" in item && (item.raw as Barrier)?.barrier_code === rawCode);
              const nextStatus = group.period === "Было" ? "past" : group.period === "Есть сейчас" ? "current" : "future";
              if (barrierItem && "raw" in barrierItem) {
                void moveBarrier(barrierItem.raw as Barrier, nextStatus);
              }
            }}
          >
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">{group.period}</h3>
            </div>
            <div className="space-y-3">
              {group.items.map((item) => (
                <div
                  key={item.title}
                  draggable={"raw" in item && Boolean(item.raw?.barrier_code)}
                  onDragStart={(event) => {
                    if ("raw" in item && (item.raw as Barrier)?.barrier_code) {
                      event.dataTransfer.setData("text/barrier-code", (item.raw as Barrier).barrier_code || "");
                    }
                  }}
                  className="rounded-2xl border border-white/80 bg-white p-4 shadow-sm"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="text-sm font-semibold text-slate-900">{item.title}</div>
                    <Badge tone={criticalityTone(item.level)}>{item.level}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{item.text}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {item.links.map((link) => (
                      <Badge key={link} tone="neutral">{link}</Badge>
                    ))}
                  </div>
                  {"raw" in item ? (
                    <div className="mt-4 flex flex-wrap gap-2">
                      <button
                        onClick={() => editBarrier(item.raw)}
                        className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                      >
                        Редактировать
                      </button>
                      <button
                        onClick={() => archiveBarrier(item.raw)}
                        className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-100"
                      >
                        В архив
                      </button>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Summary() {
  const { project } = useScreenData();
  const { editSummary } = useScreenActions();
  const confirmedFacts = [
    { label: "Код проекта", value: project.externalId },
    { label: "Направление", value: project.direction },
    { label: "Статус", value: formatProjectStatus(project.project_status) },
    { label: "Этап", value: project.lifecycle },
    { label: "Масштаб", value: project.scale },
    { label: "Команда", value: project.headcount },
  ];

  const handoverBlocks = [
    {
      title: "Кто ведёт проект",
      items: [
        { name: "GKAM", value: project.gkam, status: "указан" },
        { name: "KAM", value: project.kam, status: "указан" },
        { name: "Коммерческий ЛПР", value: "ЛПР 1", status: "обезличен" },
        { name: "Операционный контакт", value: "ЛПР 2", status: "обезличен" },
      ],
    },
    {
      title: "Как устроен сервис",
      items: [
        { name: "Основная модель", value: project.operationalModel, status: "указано" },
        { name: "Дополнительные контуры", value: project.openTeam, status: "указано" },
        { name: "Формат сервиса", value: project.serviceModel, status: "указано" },
        { name: "Полевой контур", value: "консультанты / мерчендайзеры", status: "указано" },
      ],
    },
    {
      title: "Где работает проект",
      items: [
        { name: "Известные регионы", value: project.geography, status: "частично" },
        { name: "Остальные регионы", value: "требуют подтверждения", status: "проверить" },
        { name: "Торговые сети", value: project.stores, status: "обобщено" },
        { name: "Каналы продаж", value: "требуют уточнения", status: "проверить" },
      ],
    },
  ];

  const dataReadiness = [
    { section: "Паспорт проекта", status: "Заполнено", content: "код, статус, направление, масштаб, этап, модель, команда" },
    { section: "Хронология", status: "Заполнено", content: "2019–2022: ключевые изменения проекта" },
    { section: "KPI проекта", status: "Заполнено как пример", content: "покрытие, продажи, доля рынка, качественные критерии ЛПР, экономика проекта" },
    { section: "Правила интерпретации", status: "Как методика", content: "как читать KPI, опросы, 360, ОЭД и проектные исключения" },
    { section: "Карта влияния и ЛПР", status: "Частично", content: "структура OPEN, структура клиента и обезличенные карточки ЛПР" },
    { section: "Коммуникации", status: "Частично", content: "контакты, темы, частота, канал, критичность" },
    { section: "Конкуренты", status: "Как пример", content: "конкуренты OPEN и конкуренты клиента по проектному сегменту" },
    { section: "SWOT", status: "Как гипотеза", content: "сильные стороны, слабые стороны, возможности, угрозы" },
    { section: "Барьеры", status: "Как пример", content: "было / есть сейчас / будет" },
  ];

  const nextToFill = [
    { field: "Регионы", current: "Москва; Новосибирск", needed: "полный список регионов присутствия" },
    { field: "Численность", current: "86 человек", needed: "подтверждение по ролям и территориям" },
    { field: "ЛПР", current: "ЛПР 1 / ЛПР 2 / ЛПР 3", needed: "реальные роли или согласованное обезличивание" },
    { field: "Торговые сети", current: "общее описание", needed: "список сетей / каналов продаж" },
    { field: "KPI", current: "примерная структура", needed: "фактические источники расчёта" },
    { field: "Конкуренты", current: "рыночные примеры", needed: "кто реально пересекался с OPEN по клиенту" },
  ];

  const statusTone = (status: string): BadgeTone => {
    if (["Заполнено", "указан", "указано"].includes(status)) return "good";
    if (["проверить", "Частично", "частично"].includes(status)) return "warn";
    return "neutral";
  };

  return (
    <div className="space-y-6">
      <SectionTitle
        title="Бриф проекта"
        description="Один лист для быстрой передачи проекта: что уже известно, что заполнено частично и какие факты нужно подтвердить перед использованием контекста в аналитике."
        action="Обновить бриф"
        onAction={editSummary}
      />

      <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
        <div className="grid grid-cols-1 xl:grid-cols-12">
          <div className="p-4 sm:p-6 xl:col-span-8">
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="blue">передача проекта</Badge>
              <Badge tone="neutral">фактологический бриф</Badge>
              <Badge tone="warn">есть поля к проверке</Badge>
            </div>
            <h3 className="mt-4 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
              {project.clientName}: короткая сводка для входа в контекст
            </h3>
            <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-600">
              Стартовая карточка для КАМ, руководителя или аналитика: базовые факты проекта, готовность разделов и список данных, требующих подтверждения.
            </p>
          </div>

          <div className="border-t border-slate-200 bg-slate-950 p-4 text-white sm:p-6 xl:col-span-4 xl:border-l xl:border-t-0">
            <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Готовность контекста</div>
            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
                <div className="text-2xl font-semibold text-white">3</div>
                <div className="mt-1 text-xs leading-4 text-slate-400">раздела заполнены</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
                <div className="text-2xl font-semibold text-white">3</div>
                <div className="mt-1 text-xs leading-4 text-slate-400">частично</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-center">
                <div className="text-2xl font-semibold text-white">6</div>
                <div className="mt-1 text-xs leading-4 text-slate-400">фактов к проверке</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 border-t border-slate-200 bg-slate-50 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
          {confirmedFacts.map((fact) => (
            <div key={fact.label} className="px-4 py-4 xl:border-r xl:border-slate-200 xl:last:border-r-0">
              <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{fact.label}</div>
              <div className="mt-2 break-words text-sm font-semibold leading-5 text-slate-900">{fact.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        {handoverBlocks.map((block) => (
          <Card key={block.title}>
            <h3 className="text-base font-semibold text-slate-900">{block.title}</h3>
            <div className="mt-4 space-y-3">
              {block.items.map((item) => (
                <div key={`${block.title}-${item.name}`} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="text-xs font-medium uppercase tracking-wide text-slate-400">{item.name}</div>
                    <Badge tone={statusTone(item.status)}>{item.status}</Badge>
                  </div>
                  <div className="mt-2 text-sm font-medium leading-6 text-slate-900">{item.value}</div>
                </div>
              ))}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-12">
        <Card className="xl:col-span-7">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-base font-semibold text-slate-900">Что уже есть в контексте</h3>
            <Badge tone="dark">разделы</Badge>
          </div>
          <div className="mt-4 [overflow:clip] rounded-2xl border border-slate-200">
            <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3">Раздел</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Что содержит</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {dataReadiness.map((row) => (
                  <tr key={row.section}>
                    <td className="px-4 py-4 font-medium text-slate-900">{row.section}</td>
                    <td className="px-4 py-4"><Badge tone={statusTone(row.status)}>{row.status}</Badge></td>
                    <td className="px-4 py-4 text-slate-600">{row.content}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
        </Card>

        <Card className="border-amber-200 bg-amber-50 xl:col-span-5">
          <h3 className="text-base font-semibold text-slate-900">Что мешает считать контекст полным</h3>
          <div className="mt-4 space-y-3">
            {nextToFill.map((item) => (
              <div key={item.field} className="rounded-2xl bg-white/75 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="text-sm font-semibold text-slate-900">{item.field}</div>
                  <Badge tone="warn">уточнить</Badge>
                </div>
                <div className="mt-3 grid grid-cols-1 gap-3 text-sm leading-5 md:grid-cols-2">
                  <div>
                    <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Сейчас</div>
                    <div className="mt-1 text-slate-700">{item.current}</div>
                  </div>
                  <div>
                    <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Нужно</div>
                    <div className="mt-1 text-slate-700">{item.needed}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}

type DataModuleId = keyof typeof dataModules;

function DataModule({ moduleId }: { moduleId: DataModuleId }) {
  const { dataModules } = useScreenData();
  const module = dataModules[moduleId] || dataModules.people;

  return (
    <div>
      <SectionTitle
        title={module.title}
        description={module.description}
      />
      <div className="mb-5 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="dark">слой расчёта эффективности</Badge>
          <Badge tone="warn">нужны источники данных</Badge>
          <Badge tone="neutral">паспорт = контекст интерпретации</Badge>
        </div>
        <p className="mt-4 text-sm leading-6 text-slate-600">
          Этот слой использует паспорт как справочник условий: масштаб, модель работы, ЛПР, ожидания, барьеры и коммуникации. Дальше данные из блока идут в общую оценку эффективности проекта.
        </p>
      </div>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {module.cards.map((card) => (
          <Card key={card.title}>
            <h3 className="text-base font-semibold text-slate-900">{card.title}</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{card.text}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default function ProjectContextPage() {
  const { projectCode } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const sectionFromQuery = searchParams.get("section");
  const allSectionIds = useMemo(
    () => new Set<string>([...passportSections.map((section) => section.id), ...productModules.map((module) => module.id)]),
    [],
  );
  const [effectiveness, setEffectiveness] = useState<ProjectEffectiveness | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [active, setActive] = useState<string>(
    sectionFromQuery && allSectionIds.has(sectionFromQuery) ? sectionFromQuery : "passport",
  );
  const [passportOpen, setPassportOpen] = useState(true);
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<EditTarget | null>(null);
  const [collectionEditTarget, setCollectionEditTarget] = useState<CollectionEditTarget | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const loadEffectiveness = useCallback(
    async (signal?: AbortSignal) => {
      if (!projectCode) {
        setLoadError("Код проекта не указан.");
        setLoading(false);
        return;
      }

      const payload = await getProjectEffectiveness(projectCode, signal);
      setEffectiveness(payload);
      setLoadError(null);
    },
    [projectCode],
  );

  useEffect(() => {
    if (!projectCode) {
      setLoadError("Код проекта не указан.");
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);
    setLoadError(null);

    loadEffectiveness(controller.signal)
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setLoadError(error instanceof Error ? error.message : "Не удалось загрузить проект.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, [loadEffectiveness, projectCode]);

  useEffect(() => {
    setIsNavOpen(false);
  }, [active]);

  useEffect(() => {
    if (!sectionFromQuery || !allSectionIds.has(sectionFromQuery)) {
      return;
    }
    if (sectionFromQuery !== active) {
      setActive(sectionFromQuery);
    }
  }, [active, allSectionIds, sectionFromQuery]);

  const setActiveSection = useCallback(
    (sectionId: string) => {
      setActive(sectionId);
      const next = new URLSearchParams(searchParams);
      next.set("section", sectionId);
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  async function refreshEffectiveness() {
    setLoading(true);
    try {
      await loadEffectiveness();
    } catch (error: unknown) {
      setLoadError(error instanceof Error ? error.message : "Не удалось загрузить проект.");
    } finally {
      setLoading(false);
    }
  }

  function openCreate(title: string, fields: EditField[], save: EditTarget["save"]) {
    const values = fields.reduce<EditValues>((draft, field) => {
      draft[field.name] = "";
      return draft;
    }, {});
    setSaveError(null);
    setEditTarget({ title, fields, values, save });
  }

  function openCollectionEditor(target: CollectionEditTarget) {
    setSaveError(null);
    setCollectionEditTarget(target);
  }

  async function archiveAndRefresh(
    entity: "goals" | "lprs" | "barriers" | "expectations" | "kpis" | "communications",
    code: string | null | undefined,
  ) {
    if (!projectCode || !code) {
      return;
    }
    const confirmed = window.confirm("Перенести запись в архив? Она исчезнет из рабочего контура, но останется в базе.");
    if (!confirmed) {
      return;
    }
    await archiveEntity(projectCode, entity, code, "Archived from web interface");
    await refreshEffectiveness();
  }

  async function saveContextBlock(
    sectionKey: string,
    blockCode: string,
    blockType: string,
    title: string | null,
    content: Record<string, unknown>,
    displayOrder: number,
  ) {
    if (!projectCode || !effectiveness) {
      return;
    }

    const existing = findBlock(effectiveness.context_blocks, sectionKey, blockCode);
    if (existing) {
      await updateContextBlock(projectCode, sectionKey, blockCode, { title, content, display_order: displayOrder });
      return;
    }

    await createContextBlock(projectCode, {
      section_key: sectionKey,
      block_code: blockCode,
      block_type: blockType,
      title,
      content,
      display_order: displayOrder,
    });
  }

  async function saveEdit(payload: EditPayload) {
    if (!editTarget) {
      return;
    }

    setSaving(true);
    setSaveError(null);
    try {
      await editTarget.save(payload);
      setEditTarget(null);
      await refreshEffectiveness();
    } catch (error: unknown) {
      setSaveError(error instanceof Error ? error.message : "Не удалось сохранить изменения.");
    } finally {
      setSaving(false);
    }
  }

  async function saveCollectionEdit(items: Record<string, string | null>[]) {
    if (!collectionEditTarget) {
      return;
    }

    setSaving(true);
    setSaveError(null);
    try {
      await collectionEditTarget.save(items);
      setCollectionEditTarget(null);
      await refreshEffectiveness();
    } catch (error: unknown) {
      setSaveError(error instanceof Error ? error.message : "Не удалось сохранить изменения.");
    } finally {
      setSaving(false);
    }
  }

  const content = useMemo(() => {
    const map: Record<string, ReactNode> = {
      passport: <Passport />,
      goals: <Goals />,
      "project-map": <ProjectMap />,
      competitors: <Competitors />,
      swot: <Swot />,
      communications: <Communications />,
      kpi: <Kpi />,
      "interpretation-rules": <InterpretationRules />,
      "risk-map": <RiskMap />,
      barriers: <Barriers />,
      summary: <Summary />,
      people: <DataModule moduleId="people" />,
      assessment360: <DataModule moduleId="assessment360" />,
      surveys: <DataModule moduleId="surveys" />,
      operations: <DataModule moduleId="operations" />,
      serviceQuality: <DataModule moduleId="serviceQuality" />,
      finance: <DataModule moduleId="finance" />,
      effectiveness: <DataModule moduleId="effectiveness" />,
    };

    return map[active] || <Passport />;
  }, [active]);

  const allSections = useMemo(
    () => [
      ...passportSections.map((section) => ({ id: section.id, label: section.label })),
      ...productModules.map((module) => ({ id: module.id, label: module.label })),
    ],
    [],
  );

  const currentSectionIndex = allSections.findIndex((section) => section.id === active);
  const nextSection =
    currentSectionIndex >= 0 && currentSectionIndex < allSections.length - 1
      ? allSections[currentSectionIndex + 1]
      : null;

  const hideBigHeaderOnPassport = active === "passport";
  const screenData = effectiveness ? buildHeaderProject(effectiveness) : project;
  const actions = useMemo(() => {
    if (!effectiveness || !projectCode) {
      return null;
    }

    const summaryBlock = findBlock(
      effectiveness.context_blocks,
      contextBlockKeys.summary.sectionKey,
      contextBlockKeys.summary.blockCode,
    );

    return {
      editProject: () => {
        setSaveError(null);
        setEditTarget({
          title: `Редактирование проекта ${effectiveness.cjm.project.external_project_id || effectiveness.cjm.project.project_code}`,
          fields: projectEditFields,
          values: pickValues(effectiveness.cjm.project, projectEditFields),
          save: (payload) => updateProject(projectCode, payload),
        });
      },
      editPassportHeader: (items: FactItem[]) => {
        openCollectionEditor({
          title: "Шапка паспорта проекта",
          description: "Здесь редактируются только данные внутри фактов проекта: команда, GKAM, KAM и другие служебные параметры.",
          itemLabel: "Параметр",
          fields: factCollectionFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.passportHeader.sectionKey,
              contextBlockKeys.passportHeader.blockCode,
              contextBlockKeys.passportHeader.blockType,
              "Шапка паспорта",
              { items: records },
              10,
            ),
        });
      },
      editPassportOverview: (items: FactItem[]) => {
        openCollectionEditor({
          title: "Основные параметры проекта",
          itemLabel: "Параметр",
          fields: factCollectionFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.passportOverview.sectionKey,
              contextBlockKeys.passportOverview.blockCode,
              contextBlockKeys.passportOverview.blockType,
              "Основные параметры",
              { items: records },
              20,
            ),
        });
      },
      editPassportService: (items: FactItem[]) => {
        openCollectionEditor({
          title: "Модель сервиса",
          itemLabel: "Параметр",
          fields: factCollectionFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.passportService.sectionKey,
              contextBlockKeys.passportService.blockCode,
              contextBlockKeys.passportService.blockType,
              "Модель сервиса",
              { items: records },
              30,
            ),
        });
      },
      editClientVision: (items: VisionItem[]) => {
        openCollectionEditor({
          title: "Видение клиента",
          itemLabel: "Блок",
          fields: clientVisionFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.clientVision.sectionKey,
              contextBlockKeys.clientVision.blockCode,
              contextBlockKeys.clientVision.blockType,
              "Видение клиента",
              { items: records },
              40,
            ),
        });
      },
      editWorkContours: (items: ContourItem[]) => {
        openCollectionEditor({
          title: "Контуры работы",
          itemLabel: "Контур",
          fields: contourFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.workContours.sectionKey,
              contextBlockKeys.workContours.blockCode,
              contextBlockKeys.workContours.blockType,
              "Контуры работы",
              { items: records },
              50,
            ),
        });
      },
      editProjectHistory: (items: HistoryItem[]) => {
        openCollectionEditor({
          title: "История проекта",
          itemLabel: "Этап истории",
          fields: historyFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.projectHistory.sectionKey,
              contextBlockKeys.projectHistory.blockCode,
              contextBlockKeys.projectHistory.blockType,
              "История проекта",
              { items: records },
              60,
            ),
        });
      },
      editNeeds: (contour: "client" | "open", items: NeedItem[]) => {
        const blockKey = contour === "client" ? contextBlockKeys.clientNeeds : contextBlockKeys.openNeeds;
        openCollectionEditor({
          title: contour === "client" ? "Пирамида потребностей клиента" : "Пирамида потребностей OPEN",
          itemLabel: "Уровень",
          fields: needFields,
          items,
          save: (records) =>
            saveContextBlock(
              blockKey.sectionKey,
              blockKey.blockCode,
              blockKey.blockType,
              contour === "client" ? "Пирамида клиента" : "Пирамида OPEN",
              { items: records },
              contour === "client" ? 70 : 80,
            ),
        });
      },
      editGoal: (goal: Goal) => {
        const fields = buildGoalEditFields(effectiveness);
        setSaveError(null);
        setEditTarget({
          title: goal.goal_text,
          fields,
          values: pickValues(goal, fields),
            save: (payload) => updateGoal(projectCode, goal.goal_code || goal.goal_id || "", payload),
        });
      },
      createGoal: () => {
        openCreate("Новая цель", buildGoalEditFields(effectiveness), (payload) =>
          createGoal(projectCode, payload),
        );
      },
      archiveGoal: (goal: Goal) => archiveAndRefresh("goals", goal.goal_code || goal.goal_id),
      editOpenStructure: (items: StructureItem[]) => {
        openCollectionEditor({
          title: "Структура OPEN",
          itemLabel: "Роль",
          fields: structureFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.openStructure.sectionKey,
              contextBlockKeys.openStructure.blockCode,
              contextBlockKeys.openStructure.blockType,
              "Структура OPEN",
              { items: records },
              90,
            ),
        });
      },
      editClientStructure: (items: StructureItem[]) => {
        openCollectionEditor({
          title: "Структура клиента",
          itemLabel: "Роль",
          fields: structureFields,
          items,
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.clientStructure.sectionKey,
              contextBlockKeys.clientStructure.blockCode,
              contextBlockKeys.clientStructure.blockType,
              "Структура клиента",
              { items: records },
              100,
            ),
        });
      },
      createLpr: () => {
        openCreate("Новый профиль роли", lprEditFields, (payload) => createLpr(projectCode, payload));
      },
      editLpr: (lpr: LprProfile) => {
        setSaveError(null);
        setEditTarget({
          title: lpr.role_zone || lpr.role,
          fields: lprEditFields,
          values: pickValues(lpr, lprEditFields),
          save: (payload) => updateLpr(projectCode, lpr.lpr_code, payload),
        });
      },
      archiveLpr: (lpr: LprProfile) => archiveAndRefresh("lprs", lpr.lpr_code),
      editOpenCompetitors: (items: CompetitorItem[]) => {
        openCollectionEditor({
          title: "Конкуренты OPEN",
          itemLabel: "Игрок",
          fields: competitorFields,
          items: items.map((item) => ({
            name: item.name,
            strengths: item.strengths.join("\n"),
            weaknesses: item.weaknesses.join("\n"),
          })),
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.competitorsOpen.sectionKey,
              contextBlockKeys.competitorsOpen.blockCode,
              contextBlockKeys.competitorsOpen.blockType,
              "Конкуренты OPEN",
              { items: records },
              110,
            ),
        });
      },
      editClientCompetitors: (items: CompetitorItem[]) => {
        openCollectionEditor({
          title: "Конкуренты клиента",
          itemLabel: "Игрок",
          fields: competitorFields,
          items: items.map((item) => ({
            name: item.name,
            strengths: item.strengths.join("\n"),
            weaknesses: item.weaknesses.join("\n"),
          })),
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.competitorsClient.sectionKey,
              contextBlockKeys.competitorsClient.blockCode,
              contextBlockKeys.competitorsClient.blockType,
              "Конкуренты клиента",
              { items: records },
              120,
            ),
        });
      },
      editSwot: (value: SwotValue) => {
        openCollectionEditor({
          title: "SWOT-анализ проекта",
          itemLabel: "Блок SWOT",
          fields: [
            { name: "strengths", label: "Сильные стороны", input: "textarea", rows: 4 },
            { name: "weaknesses", label: "Слабые стороны", input: "textarea", rows: 4 },
            { name: "opportunities", label: "Возможности", input: "textarea", rows: 4 },
            { name: "threats", label: "Угрозы", input: "textarea", rows: 4 },
          ],
          items: [{
            strengths: value.strengths.join("\n"),
            weaknesses: value.weaknesses.join("\n"),
            opportunities: value.opportunities.join("\n"),
            threats: value.threats.join("\n"),
          }],
          save: async ([record]) =>
            saveContextBlock(
              contextBlockKeys.swot.sectionKey,
              contextBlockKeys.swot.blockCode,
              contextBlockKeys.swot.blockType,
              "SWOT-анализ проекта",
              {
                strengths: splitLines(record?.strengths),
                weaknesses: splitLines(record?.weaknesses),
                opportunities: splitLines(record?.opportunities),
                threats: splitLines(record?.threats),
              },
              130,
            ),
        });
      },
      createCommunication: () => {
        openCreate(
          "Новая коммуникация",
          buildCommunicationEditFields(effectiveness),
          (payload) => createCommunication(projectCode, buildCommunicationPayload(payload)),
        );
      },
      editCommunication: (communication: CommunicationPoint) => {
        const fields = buildCommunicationEditFields(effectiveness);
        setSaveError(null);
        setEditTarget({
          title: communication.topic_text || communication.summary || "Коммуникация",
          fields,
          values: {
            ...pickValues(communication, fields),
            open_side_role_custom: "",
          },
          save: (payload) =>
            updateCommunication(
              projectCode,
              communication.communication_code || communication.communication_id || "",
              buildCommunicationPayload(payload),
            ),
        });
      },
      archiveCommunication: (communication: CommunicationPoint) =>
        archiveAndRefresh(
          "communications",
          communication.communication_code || communication.communication_id,
        ),
      createKpi: () => {
        openCreate("Новый KPI", buildKpiEditFields(effectiveness), (payload) => createKpi(projectCode, payload));
      },
      editKpi: (kpi: Kpi) => {
        const fields = buildKpiEditFields(effectiveness);
        setSaveError(null);
        setEditTarget({
          title: kpi.kpi_name,
          fields,
          values: pickValues(kpi, fields),
          save: (payload) => updateKpi(projectCode, kpi.kpi_code, payload),
        });
      },
      archiveKpi: (kpi: Kpi) => archiveAndRefresh("kpis", kpi.kpi_code),
      editInterpretationRules: (items: InterpretationRuleItem[]) => {
        openCollectionEditor({
          title: "Правила интерпретации",
          itemLabel: "Правило",
          fields: interpretationRuleFields,
          items: items.map((item) => ({ rule: item.rule || item.title })),
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.interpretationRules.sectionKey,
              contextBlockKeys.interpretationRules.blockCode,
              contextBlockKeys.interpretationRules.blockType,
              "Правила интерпретации",
              { rules: records.map((record) => record.rule).filter(Boolean) },
              140,
            ),
        });
      },
      editRiskMap: (items: Array<Record<string, unknown>>) => {
        openCollectionEditor({
          title: "Карта рисков",
          itemLabel: "Риск",
          fields: riskFields,
          items: items.map((item) => ({
            title: String(item.title || item.risk || ""),
            barrier_type: String(item.barrier_type || item.zone || ""),
            probability_level: String(item.probability_level || item.level || ""),
            probability_basis: String(item.probability_basis || ""),
            impact_level: String(item.impact_level || item.level || ""),
            impact_basis: String(item.impact_basis || ""),
            related_to: String(item.related_to || item.linked_kpi_text || ""),
            early_signal: String(item.early_signal || item.evidence_quote || ""),
            control_action: String(item.control_action || ""),
            control_owner: String(item.control_owner || ""),
            review_period: String(item.review_period || ""),
            source_text: String(item.source_text || ""),
          })),
          save: (records) =>
            saveContextBlock(
              contextBlockKeys.riskMap.sectionKey,
              contextBlockKeys.riskMap.blockCode,
              contextBlockKeys.riskMap.blockType,
              "Карта рисков",
              { items: records },
              150,
            ),
        });
      },
      editBarrier: (barrier: Barrier) => {
        const fields = buildBarrierEditFields(effectiveness);
        setSaveError(null);
        setEditTarget({
          title: barrier.barrier_title,
          fields,
          values: pickValues(barrier, fields),
          save: (payload) =>
            updateBarrier(projectCode, barrier.barrier_code || barrier.barrier_id || "", payload),
        });
      },
      createBarrier: () => {
        openCreate("Новый барьер", buildBarrierEditFields(effectiveness), (payload) =>
          createBarrier(projectCode, payload),
        );
      },
      archiveBarrier: (barrier: Barrier) =>
        archiveAndRefresh("barriers", barrier.barrier_code || barrier.barrier_id),
      moveBarrier: async (barrier: Barrier, timeStatus: string) => {
        await updateBarrier(projectCode, barrier.barrier_code || barrier.barrier_id || "", {
          time_status: timeStatus,
        });
        await refreshEffectiveness();
      },
      editSummary: () => {
        const values: EditValues = {
          title: summaryBlock?.title ?? "Бриф проекта",
          critical_to_client: asStringArray(summaryBlock?.content.critical_to_client).join("\n"),
          main_risks: asStringArray(summaryBlock?.content.main_risks).join("\n"),
          note: String(summaryBlock?.content.note || ""),
        };

        setSaveError(null);
        setEditTarget({
          title: summaryBlock?.title || "Бриф проекта",
          fields: [
            { name: "title", label: "Заголовок" },
            { name: "critical_to_client", label: "Что критично клиенту", input: "textarea" },
            { name: "main_risks", label: "Где основной риск", input: "textarea" },
            { name: "note", label: "Комментарий", input: "textarea" },
          ],
          values,
          save: (payload) =>
            saveContextBlock(
              contextBlockKeys.summary.sectionKey,
              contextBlockKeys.summary.blockCode,
              contextBlockKeys.summary.blockType,
              payload.title,
              {
                critical_to_client: splitLines(payload.critical_to_client),
                main_risks: splitLines(payload.main_risks),
                note: payload.note,
              },
              160,
            ),
        });
      },
    };
  }, [effectiveness, projectCode]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6 text-slate-700">
        Загружаем карту проекта...
      </div>
    );
  }

  if (loadError || !effectiveness) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
        <div className="max-w-lg rounded-3xl border border-rose-200 bg-white p-6 text-sm leading-6 text-rose-700 shadow-sm">
          {loadError || "Проект не найден."}
        </div>
      </div>
    );
  }

  return (
    <EffectivenessContext.Provider value={effectiveness}>
    <ScreenActionsContext.Provider value={actions}>
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="flex min-h-screen flex-col xl:flex-row">
        {isNavOpen && (
          <div onClick={() => setIsNavOpen(false)} className="fixed inset-0 z-30 bg-slate-950/40 xl:hidden" />
        )}

        <aside className={`${isNavOpen ? "fixed left-3 right-3 top-16 z-40 max-h-[78vh] overflow-y-auto rounded-2xl shadow-2xl" : "hidden"} shrink-0 border border-slate-200 bg-white p-4 sm:p-5 xl:relative xl:block xl:inset-auto xl:right-auto xl:top-auto xl:z-auto xl:w-80 xl:max-h-none xl:overflow-visible xl:rounded-none xl:border-b-0 xl:border-l-0 xl:border-r xl:border-t-0 xl:shadow-none`}>
          <button
            onClick={() => setIsNavOpen(false)}
            className="mb-4 inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 xl:hidden"
          >
            <X aria-hidden="true" className="h-4 w-4" />
            Закрыть
          </button>

          <div className="rounded-3xl bg-slate-950 p-5 text-white shadow-sm">
            <div className="text-xs uppercase tracking-[0.2em] text-slate-400">OPEN Intelligence</div>
            <div className="mt-2 text-xl font-semibold">Эффективность проекта</div>
            <div className="mt-3 text-sm leading-6 text-slate-300">
              Финальный продукт объединяет контекст проекта, клиентские сигналы, операционные показатели, людей, качество сервиса и экономику.
            </div>
          </div>

          <nav className="mt-5 space-y-2">
            <button
              onClick={() => setPassportOpen((value) => !value)}
              className="flex w-full items-center justify-between rounded-2xl bg-slate-900 px-4 py-3 text-left text-sm font-semibold text-white shadow-sm"
            >
              <span>КОНТЕКСТ ПРОЕКТА</span>
              <span className="text-xs text-slate-300">{passportOpen ? "свернуть" : "раскрыть"}</span>
            </button>

            {passportOpen && (
              <div className="space-y-1 pl-0 sm:pl-3">
                {passportSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id)}
                    className={`w-full rounded-2xl px-4 py-3 text-left text-sm font-medium transition break-words ${
                      active === section.id ? "bg-slate-900 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    {section.label}
                  </button>
                ))}
              </div>
            )}
                      <div className="pt-3">
              <div className="px-4 pb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Слои эффективности</div>
              <div className="space-y-1">
                {productModules.map((module) => (
                  <button
                    key={module.id}
                    onClick={() => setActiveSection(module.id)}
                    className={`w-full rounded-2xl px-4 py-3 text-left transition ${
                      active === module.id ? "bg-slate-900 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
                    }`}
                  >
                    <div className="text-sm font-medium break-words">{module.label}</div>
                    <div className={`mt-1 text-xs ${active === module.id ? "text-slate-300" : "text-slate-400"}`}>{module.status}</div>
                  </button>
                ))}
              </div>
            </div>
          </nav>
        </aside>

        <main className="min-w-0 flex-1 p-3 sm:p-4 lg:p-5 xl:p-6">
          <div className="mb-4 flex items-center justify-between gap-3">
            <Link
              to="/projects"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
            >
              К выбору проектов
            </Link>
          </div>

          {!hideBigHeaderOnPassport && (
            <header className="mb-6 overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
              <div className="grid grid-cols-1 lg:grid-cols-12">
                <div className="p-4 sm:p-5 lg:col-span-8">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge tone="good">Активен</Badge>
                    <Badge tone="blue">{screenData.direction}</Badge>
                    <Badge tone="neutral">{screenData.scale}</Badge>
                    <Badge tone="neutral">{screenData.lifecycle}</Badge>
                  </div>

                  <h1 className="mt-4 break-words text-xl font-semibold tracking-tight text-slate-950 sm:text-2xl lg:text-3xl">{screenData.clientName}</h1>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
                    {screenData.serviceModel}.
                  </p>
                </div>

                <div className="border-t border-slate-200 bg-slate-50 p-4 sm:p-5 lg:col-span-4 lg:border-l lg:border-t-0">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Код проекта</div>
                      <div className="mt-2 break-words text-sm font-semibold text-slate-900">{screenData.externalId}</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">Команда</div>
                      <div className="mt-2 break-words text-sm font-semibold text-slate-900">{screenData.headcount}</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">GKAM</div>
                      <div className="mt-2 break-words text-sm font-semibold text-slate-900">{screenData.gkam}</div>
                    </div>
                    <div>
                      <div className="text-xs font-medium uppercase tracking-wide text-slate-400">KAM</div>
                      <div className="mt-2 break-words text-sm font-semibold text-slate-900">{screenData.kam}</div>
                    </div>
                  </div>
                </div>
              </div>
            </header>
          )}

          {content}
          {nextSection ? (
            <div className="mt-6">
              <button
                type="button"
                onClick={() => setActiveSection(nextSection.id)}
                className="w-full rounded-2xl border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-800 shadow-sm transition hover:bg-slate-50 sm:w-auto"
              >
                Перейти в раздел «{nextSection.label}»
              </button>
            </div>
          ) : null}
        </main>
      </div>
      <button
        onClick={() => setIsNavOpen((value) => !value)}
        className="fixed bottom-4 right-4 z-30 inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 shadow-lg hover:bg-slate-50 xl:hidden"
      >
        {isNavOpen ? <X aria-hidden="true" className="h-4 w-4" /> : <Menu aria-hidden="true" className="h-4 w-4" />}
        {isNavOpen ? "Закрыть" : "Разделы"}
      </button>
    </div>
    {editTarget ? (
      <EditEntityModal
        title={editTarget.title}
        fields={editTarget.fields}
        values={editTarget.values}
        saving={saving}
        error={saveError}
        onClose={() => {
          if (!saving) {
            setEditTarget(null);
            setSaveError(null);
          }
        }}
        onSave={saveEdit}
      />
    ) : null}
    {collectionEditTarget ? (
      <EditCollectionModal
        title={collectionEditTarget.title}
        description={collectionEditTarget.description}
        itemLabel={collectionEditTarget.itemLabel}
        fields={collectionEditTarget.fields}
        items={collectionEditTarget.items}
        saving={saving}
        error={saveError}
        onClose={() => {
          if (!saving) {
            setCollectionEditTarget(null);
            setSaveError(null);
          }
        }}
        onSave={saveCollectionEdit}
      />
    ) : null}
    </ScreenActionsContext.Provider>
    </EffectivenessContext.Provider>
  );
}

function buildHeaderProject(effectiveness: ProjectEffectiveness) {
  const projectInfo = effectiveness.cjm.project;
  const headerBlock = findBlock(
    effectiveness.context_blocks,
    contextBlockKeys.passportHeader.sectionKey,
    contextBlockKeys.passportHeader.blockCode,
  );
  const headerItems = asRecordArray(headerBlock?.content.items);
  const headerValue = (label: string) =>
    String(
      headerItems.find((item) => String(item.label || "").trim().toLowerCase() === label.trim().toLowerCase())
        ?.value || "",
    );
  return {
    ...project,
    externalId: projectInfo.external_project_id || projectInfo.project_code,
    clientName: `Проект ${projectInfo.external_project_id || projectInfo.project_code}`,
    direction: formatDirection(projectInfo.direction),
    serviceModel: sanitizeCjm(projectInfo.short_description) || "Описание проекта нужно уточнить в паспорте",
    scale: formatProjectScale(projectInfo.project_scale),
    lifecycle: formatLifecycleStage(projectInfo.lifecycle_stage),
    headcount: headerValue("Команда") || project.headcount,
    gkam: headerValue("GKAM") || project.gkam,
    kam: headerValue("KAM") || project.kam,
  };
}
