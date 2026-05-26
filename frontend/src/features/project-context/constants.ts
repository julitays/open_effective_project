export const passportSections = [
  { id: "passport", label: "Паспорт проекта" },
  { id: "goals", label: "Цели OPEN и клиента" },
  { id: "project-map", label: "Карта влияния и ЛПР" },
  { id: "competitors", label: "Конкуренты" },
  { id: "swot", label: "SWOT-анализ проекта" },
  { id: "communications", label: "Матрица коммуникаций" },
  { id: "kpi", label: "KPI проекта" },
  { id: "interpretation-rules", label: "Правила интерпретации" },
  { id: "risk-map", label: "Карта рисков" },
  { id: "barriers", label: "Барьеры: было / есть / будет" },
  { id: "summary", label: "Бриф проекта" },
] as const;

export const productModules = [
  { id: "people", label: "Люди", status: "аттестации, обучение, роли" },
  { id: "assessment360", label: "Оценка 360 структуры", status: "управленческая среда" },
  { id: "surveys", label: "Блиц- и операционные опросы", status: "голос клиента" },
  { id: "operations", label: "Операционные показатели", status: "факты исполнения" },
  { id: "serviceQuality", label: "Качество сервиса", status: "отклонения и сигналы" },
  { id: "finance", label: "Финансы проекта", status: "экономика" },
  { id: "effectiveness", label: "Итоговая эффективность", status: "финальный расчёт" },
] as const;

export const contextBlockKeys = {
  passportHeader: { sectionKey: "passport_header", blockCode: "passport_header_001", blockType: "facts" },
  passportOverview: { sectionKey: "passport_overview", blockCode: "passport_overview_001", blockType: "facts" },
  passportService: { sectionKey: "passport_service", blockCode: "passport_service_001", blockType: "facts" },
  clientVision: { sectionKey: "client_vision", blockCode: "client_vision_001", blockType: "records" },
  workContours: { sectionKey: "work_contours", blockCode: "work_contours_001", blockType: "records" },
  projectHistory: { sectionKey: "project_history", blockCode: "project_history_001", blockType: "timeline" },
  clientNeeds: { sectionKey: "client_needs", blockCode: "client_needs_001", blockType: "pyramid" },
  openNeeds: { sectionKey: "open_needs", blockCode: "open_needs_001", blockType: "pyramid" },
  openStructure: { sectionKey: "open_structure", blockCode: "open_structure_001", blockType: "records" },
  clientStructure: { sectionKey: "client_structure", blockCode: "client_structure_001", blockType: "records" },
  competitorsOpen: { sectionKey: "competitors_open", blockCode: "competitors_open_001", blockType: "records" },
  competitorsClient: { sectionKey: "competitors_client", blockCode: "competitors_client_001", blockType: "records" },
  swot: { sectionKey: "swot", blockCode: "swot_001", blockType: "swot" },
  interpretationRules: { sectionKey: "interpretation_rules", blockCode: "interpretation_rules_001", blockType: "rules" },
  riskMap: { sectionKey: "risk_map", blockCode: "risk_map_001", blockType: "risk_list" },
  summary: { sectionKey: "summary", blockCode: "summary_001", blockType: "management_summary" },
} as const;
