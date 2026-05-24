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
  high: "Высокая критичность",
  "высокая": "Высокая критичность",
  "высокий": "Высокая критичность",
  medium: "Средняя критичность",
  "средняя": "Средняя критичность",
  "средний": "Средняя критичность",
  low: "Низкая критичность",
  "низкая": "Низкая критичность",
  "низкий": "Низкая критичность",
  unknown: emptyLabel,
};

const influenceLevelLabels = {
  high: "Высокое влияние",
  "высокий": "Высокое влияние",
  "высокое": "Высокое влияние",
  medium: "Среднее влияние",
  "средний": "Среднее влияние",
  "среднее": "Среднее влияние",
  low: "Низкое влияние",
  "низкий": "Низкое влияние",
  "низкое": "Низкое влияние",
  requires_confirmation: "Требует подтверждения",
  "требует подтверждения": "Требует подтверждения",
  unknown: emptyLabel,
};

const relevanceStatusLabels = {
  actual: "Актуально",
  "актуально": "Актуально",
  current: "Актуально",
  historical: "Историческое",
  "историческое": "Историческое",
  requires_confirmation: "Требует подтверждения",
  "требует подтверждения": "Требует подтверждения",
  not_actual: "Неактуально",
  "неактуально": "Неактуально",
  unknown: emptyLabel,
};

const confidenceLevelLabels = {
  high: "Высокая уверенность",
  "высокая": "Высокая уверенность",
  "высокий": "Высокая уверенность",
  medium: "Средняя уверенность",
  "средняя": "Средняя уверенность",
  "средний": "Средняя уверенность",
  low: "Низкая уверенность",
  "низкая": "Низкая уверенность",
  "низкий": "Низкая уверенность",
  unknown: emptyLabel,
};

const relationshipStatusLabels = {
  loyal: "Лоялен",
  "лоялен": "Лоялен",
  neutral: "Нейтрален",
  "нейтрален": "Нейтрален",
  cautious: "Осторожен",
  "осторожен": "Осторожен",
  critical: "Критичен",
  "критичен": "Критичен",
  unknown: emptyLabel,
};

const activityStatusLabels = {
  active: "Активен",
  "активен": "Активен",
  inactive: "Неактивен",
  "неактивен": "Неактивен",
  requires_confirmation: "Требует подтверждения",
  "требует подтверждения": "Требует подтверждения",
  historical: "Исторический",
  "исторический": "Исторический",
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
  "было": "Было",
  current: "Есть сейчас",
  "есть сейчас": "Есть сейчас",
  future: "Может возникнуть",
  "может возникнуть": "Может возникнуть",
  repeated: "Повторяется",
  "повторяется": "Повторяется",
};

const barrierStatusLabels = {
  open: "Открыт",
  "открыт": "Открыт",
  in_progress: "В работе",
  "в работе": "В работе",
  contained: "Сдерживается",
  "сдерживается": "Сдерживается",
  resolved: "Решён",
  "решён": "Решён",
  "решен": "Решён",
  monitoring: "На контроле",
  "на контроле": "На контроле",
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
  "явное": "Явное",
  implicit: "Неявное",
  "неявное": "Неявное",
  unknown: emptyLabel,
};

const communicationChannelLabels = {
  meeting: "Встреча",
  "встреча": "Встреча",
  call: "Звонок",
  "звонок": "Звонок",
  email: "Email",
  "почта": "Email",
  messenger: "Мессенджер",
  "мессенджер": "Мессенджер",
  report: "Отчёт",
  "отчёт": "Отчёт",
  "отчет": "Отчёт",
  bi_dashboard: "BI-дашборд",
  other: "Другое",
  unknown: emptyLabel,
};

const communicationFrequencyLabels = {
  on_request: "По запросу",
  "по запросу": "По запросу",
  weekly: "Еженедельно",
  "еженедельно": "Еженедельно",
  biweekly: "Раз в две недели",
  monthly: "Ежемесячно",
  "ежемесячно": "Ежемесячно",
  quarterly: "Ежеквартально",
  "ежеквартально": "Ежеквартально",
  rarely: "Редко",
  "редко": "Редко",
  unknown: emptyLabel,
};

const yesNoLabels = {
  true: "Да",
  false: "Нет",
  yes: "Да",
  no: "Нет",
  "да": "Да",
  "нет": "Нет",
  requires_confirmation: "Требует подтверждения",
  unknown: emptyLabel,
};

const goalTypeLabels = {
  "финансовая": "Финансовый результат",
  "финансовый": "Финансовый результат",
  "клиентская": "Клиентский результат",
  "клиентский": "Клиентский результат",
  "бизнес клиента": "Бизнес-результат клиента",
  "операционная": "Операционный результат",
  "операционный": "Операционный результат",
};

type LabelDictionary = Record<string, string>;

function normalize(value: string | null | undefined) {
  return value?.trim().toLowerCase();
}

function hasCyrillic(value: string) {
  return /[а-яё]/i.test(value);
}

function sentenceCase(value: string) {
  const trimmed = value.trim();
  if (!trimmed) {
    return emptyLabel;
  }

  if (/^[A-ZА-ЯЁ0-9/.\-\s]+$/.test(trimmed)) {
    return trimmed;
  }

  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
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
    return sentenceCase(original);
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

export function formatEntityCode(value: string | null | undefined) {
  const normalized = normalize(value);
  const match = normalized?.match(/^(goal|lpr|barrier|expectation|expect|kpi|comm|communication)_0*(\d+)$/);

  if (!match) {
    return formatCode(value);
  }

  const [, entity, number] = match;
  const labels: Record<string, string> = {
    goal: "Цель",
    lpr: "ЛПР",
    barrier: "Барьер",
    expectation: "Ожидание",
    expect: "Ожидание",
    kpi: "KPI",
    comm: "Коммуникация",
    communication: "Коммуникация",
  };

  return `${labels[entity]} ${Number(number)}`;
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

export const formatGoalType = (value: string | null | undefined) =>
  labelFrom(value, goalTypeLabels);

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
