const emptyLabel = "Не указано";

const directionLabels = {
  fmcg: "FMCG",
  electronics: "Электроника",
  kaf: "КАФ",
  promo: "Промо",
  training: "Обучение",
  audit: "Аудит",
  mixed: "Смешанная модель",
  other: "Другое",
};

const projectScaleLabels = {
  local: "Локальный",
  regional: "Региональный",
  federal: "Федеральный",
  interregional: "Межрегиональный",
  unknown: emptyLabel,
};

const operationalModelLabels = {
  merchandising: "Мерчендайзинг",
  combined_merchandising: "Совмещённый мерчендайзинг",
  promo_consulting: "Промо / консультирование",
  kaf: "КАФ / кадровое администрирование",
  training: "Обучение",
  audit_quality_control: "Аудит / контроль качества",
  analytics_reporting: "Аналитика / отчётность",
  mixed: "Смешанная модель",
  other: "Другое",
};

const lifecycleStageLabels = {
  launch: "Запуск",
  stabilization: "Стабилизация",
  development: "Развитие",
  retention: "Удержание",
  restart: "Перезапуск",
  risk: "Риск",
  closing: "Завершение",
  unknown: emptyLabel,
};

const projectStatusLabels = {
  active: "Активен",
  completed: "Завершён",
  pilot: "Пилот",
  at_risk: "В зоне риска",
  unknown: emptyLabel,
};

const criticalityLabels = {
  high: "Высокая",
  medium: "Средняя",
  low: "Низкая",
  unknown: emptyLabel,
};

const influenceLevelLabels = {
  high: "Высокое влияние",
  medium: "Среднее влияние",
  low: "Низкое влияние",
  requires_confirmation: "Требует подтверждения",
  unknown: emptyLabel,
};

const relevanceStatusLabels = {
  actual: "Актуально",
  current: "Актуально",
  historical: "Историческое",
  requires_confirmation: "Требует подтверждения",
  not_actual: "Неактуально",
  unknown: emptyLabel,
};

const confidenceLevelLabels = {
  high: "Высокая уверенность",
  medium: "Средняя уверенность",
  low: "Низкая уверенность",
  unknown: emptyLabel,
};

const relationshipStatusLabels = {
  loyal: "Лоялен",
  neutral: "Нейтрален",
  cautious: "Осторожен",
  critical: "Критичен",
  unknown: emptyLabel,
};

const activityStatusLabels = {
  active: "Активен",
  inactive: "Неактивен",
  requires_confirmation: "Требует подтверждения",
  historical: "Исторический",
  unknown: emptyLabel,
};

const importanceFactorLabels = {
  response_speed: "Скорость реакции",
  execution_quality: "Качество исполнения",
  status_transparency: "Прозрачность статусов",
  reporting: "Отчётность",
  initiative: "Инициативность",
  cost: "Стоимость",
  agreements_compliance: "Соблюдение договорённостей",
  staff_stability: "Стабильность персонала",
  team_expertise: "Экспертность команды",
  minimum_manual_control: "Минимум ручного контроля",
  flexibility: "Гибкость",
  predictability: "Прогнозируемость",
  staff_training_level: "Обученность персонала",
  safety: "Безопасность",
  other: "Другое",
};

const barrierTypeLabels = {
  communication: "Коммуникация",
  execution_quality: "Качество исполнения",
  reporting: "Отчётность",
  timing: "Сроки",
  staff: "Персонал",
  kpi: "KPI",
  cost: "Стоимость",
  training: "Обучение",
  control: "Контроль",
  expectations: "Ожидания",
  process_organization: "Организация процесса",
  other: "Другое",
};

const barrierTimeStatusLabels = {
  past: "Было",
  current: "Есть сейчас",
  future: "Может возникнуть",
  repeated: "Повторяется",
};

const barrierStatusLabels = {
  open: "Открыт",
  in_progress: "В работе",
  contained: "Сдерживается",
  resolved: "Решён",
  monitoring: "На контроле",
  unknown: emptyLabel,
};

const expectationTypeLabels = {
  speed: "Скорость",
  quality: "Качество",
  reporting: "Отчётность",
  initiative: "Инициативность",
  transparency: "Прозрачность",
  cost: "Стоимость",
  expertise: "Экспертность",
  predictability: "Прогнозируемость",
  minimum_manual_control: "Минимум ручного контроля",
  flexibility: "Гибкость",
  agreements_compliance: "Соблюдение договорённостей",
  other: "Другое",
};

const explicitnessLabels = {
  explicit: "Явное",
  implicit: "Неявное",
  unknown: emptyLabel,
};

const communicationChannelLabels = {
  meeting: "Встреча",
  call: "Звонок",
  email: "Email",
  messenger: "Мессенджер",
  report: "Отчёт",
  bi_dashboard: "BI-дашборд",
  other: "Другое",
  unknown: emptyLabel,
};

const communicationFrequencyLabels = {
  on_request: "По запросу",
  weekly: "Еженедельно",
  biweekly: "Раз в две недели",
  monthly: "Ежемесячно",
  quarterly: "Ежеквартально",
  rarely: "Редко",
  unknown: emptyLabel,
};

const yesNoLabels = {
  true: "Да",
  false: "Нет",
  yes: "Да",
  no: "Нет",
  requires_confirmation: "Требует подтверждения",
  unknown: emptyLabel,
};

type LabelDictionary = Record<string, string>;

function normalize(value: string | null | undefined) {
  return value?.trim().toLowerCase();
}

function hasCyrillic(value: string) {
  return /[а-яё]/i.test(value);
}

function labelFrom(
  value: string | null | undefined,
  labels: LabelDictionary,
  options: { allowRussianText?: boolean } = { allowRussianText: true },
) {
  const normalized = normalize(value);

  if (!normalized) {
    return emptyLabel;
  }

  if (labels[normalized]) {
    return labels[normalized];
  }

  const original = value?.trim() ?? "";
  if (options.allowRussianText && hasCyrillic(original)) {
    return original;
  }

  return emptyLabel;
}

export function formatText(value: string | null | undefined) {
  const trimmed = value?.trim();
  return trimmed || emptyLabel;
}

export function formatCode(value: string | null | undefined) {
  return value?.trim() || emptyLabel;
}

export const formatDirection = (value: string | null | undefined) =>
  labelFrom(value, directionLabels, { allowRussianText: false });

export const formatProjectScale = (value: string | null | undefined) =>
  labelFrom(value, projectScaleLabels);

export const formatOperationalModel = (value: string | null | undefined) =>
  labelFrom(value, operationalModelLabels);

export const formatLifecycleStage = (value: string | null | undefined) =>
  labelFrom(value, lifecycleStageLabels);

export const formatProjectStatus = (value: string | null | undefined) =>
  labelFrom(value, projectStatusLabels);

export const formatCriticality = (value: string | null | undefined) =>
  labelFrom(value, criticalityLabels);

export const formatInfluenceLevel = (value: string | null | undefined) =>
  labelFrom(value, influenceLevelLabels);

export const formatRelevanceStatus = (value: string | null | undefined) =>
  labelFrom(value, relevanceStatusLabels);

export const formatConfidenceLevel = (value: string | null | undefined) =>
  labelFrom(value, confidenceLevelLabels);

export const formatRelationshipStatus = (value: string | null | undefined) =>
  labelFrom(value, relationshipStatusLabels);

export const formatActivityStatus = (value: string | null | undefined) =>
  labelFrom(value, activityStatusLabels);

export const formatImportanceFactor = (value: string | null | undefined) =>
  labelFrom(value, importanceFactorLabels);

export const formatBarrierType = (value: string | null | undefined) =>
  labelFrom(value, barrierTypeLabels);

export const formatBarrierTimeStatus = (value: string | null | undefined) =>
  labelFrom(value, barrierTimeStatusLabels);

export const formatBarrierStatus = (value: string | null | undefined) =>
  labelFrom(value, barrierStatusLabels);

export const formatExpectationType = (value: string | null | undefined) =>
  labelFrom(value, expectationTypeLabels);

export const formatExplicitness = (value: string | null | undefined) =>
  labelFrom(value, explicitnessLabels);

export const formatCommunicationChannel = (value: string | null | undefined) =>
  labelFrom(value, communicationChannelLabels);

export const formatCommunicationFrequency = (value: string | null | undefined) =>
  labelFrom(value, communicationFrequencyLabels);

export const formatYesNo = (value: string | null | undefined) =>
  labelFrom(value, yesNoLabels);

export function isConfirmationRequired(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "requires_confirmation" || normalized === "требует подтверждения";
}

export function isActual(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "actual" || normalized === "current" || normalized === "актуально";
}

export function isRepeated(value: string | null | undefined) {
  const normalized = normalize(value);
  return normalized === "repeated" || normalized === "повторяется";
}
