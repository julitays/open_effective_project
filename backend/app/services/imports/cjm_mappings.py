from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping
from enum import StrEnum

from app.core.enums import (
    ActionStatus,
    ActionType,
    BarrierStatus,
    BarrierTimeStatus,
    BarrierType,
    CommunicationChannel,
    CommunicationFrequency,
    Criticality,
    Direction,
    ExpectationType,
    Explicitness,
    ImportanceFactorType,
    LifecycleStage,
    OperationalModel,
    PlanConfirmationStatus,
    ProjectScale,
    ProjectStatus,
    Sentiment,
    SurveyType,
)


def normalize_label(value: object) -> str:
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKC", str(value)).strip().lower()
    normalized = normalized.replace("ё", "е")
    return re.sub(r"\s+", " ", normalized)


def _aliases(enum_type: type[StrEnum], extras: Mapping[str, str]) -> dict[str, str]:
    aliases = {normalize_label(item.value): item.value for item in enum_type}
    aliases.update({normalize_label(label): code for label, code in extras.items()})
    return aliases


def map_code(
    value: object,
    enum_type: type[StrEnum],
    aliases: Mapping[str, str],
) -> str | None:
    normalized = normalize_label(value)
    if not normalized:
        return None
    mapped = aliases.get(normalized)
    if mapped is None:
        return None
    allowed = {item.value for item in enum_type}
    return mapped if mapped in allowed else None


def _split_composite(value: object) -> list[str]:
    return [
        part.strip()
        for part in re.split(r"\s*(?:/|;|,)\s*", normalize_label(value))
        if part.strip()
    ]


DIRECTION_ALIASES = _aliases(
    Direction,
    {
        "FMCG": "fmcg",
        "Электроника": "electronics",
        "КАФ": "kaf",
        "Промо": "promo",
        "Обучение": "training",
        "Аудит": "audit",
        "Смешанное": "mixed",
        "Другое": "other",
    },
)
PROJECT_SCALE_ALIASES = _aliases(
    ProjectScale,
    {
        "Локальный": "local",
        "Региональный": "regional",
        "Федеральный": "federal",
        "Межрегиональный": "interregional",
        "Неизвестно": "unknown",
    },
)
OPERATIONAL_MODEL_ALIASES = _aliases(
    OperationalModel,
    {
        "Мерчендайзинг": "merchandising",
        "Совмещенный мерчендайзинг": "combined_merchandising",
        "Промо / консультирование": "promo_consulting",
        "КАФ / кадровое администрирование": "kaf",
        "Обучение": "training",
        "Аудит / контроль качества": "audit_quality_control",
        "Аналитика / отчетность": "analytics_reporting",
        "Смешанная": "mixed",
        "Другое": "other",
    },
)
LIFECYCLE_STAGE_ALIASES = _aliases(
    LifecycleStage,
    {
        "Запуск": "launch",
        "Стабилизация": "stabilization",
        "Развитие": "development",
        "Удержание": "retention",
        "Перезапуск": "restart",
        "Риск": "risk",
        "Закрытие": "closing",
        "Неизвестно": "unknown",
    },
)
PROJECT_STATUS_ALIASES = _aliases(
    ProjectStatus,
    {
        "Активный": "active",
        "Завершен": "completed",
        "Завершенный": "completed",
        "Пилот": "pilot",
        "Под риском": "at_risk",
        "Требует подтверждения": "unknown",
        "Неизвестно": "unknown",
    },
)
SURVEY_TYPE_ALIASES = _aliases(
    SurveyType,
    {
        "Блиц": "blitz",
        "Блиц-опрос": "blitz",
        "Блиц опрос": "blitz",
        "Операционный": "operational",
        "Операционный опрос": "operational",
    },
)
IMPORTANCE_FACTOR_TYPE_ALIASES = _aliases(
    ImportanceFactorType,
    {
        "Скорость ответа": "response_speed",
        "Качество исполнения": "execution_quality",
        "Прозрачность статуса": "status_transparency",
        "Отчетность": "reporting",
        "Инициативность": "initiative",
        "Стоимость": "cost",
        "Соблюдение договоренностей": "agreements_compliance",
        "Стабильность персонала": "staff_stability",
        "Экспертиза команды": "team_expertise",
        "Минимум ручного контроля": "minimum_manual_control",
        "Гибкость": "flexibility",
        "Предсказуемость": "predictability",
        "Уровень обучения персонала": "staff_training_level",
        "Другое": "other",
    },
)
CRITICALITY_ALIASES = _aliases(
    Criticality,
    {
        "Высокая": "high",
        "Высокий": "high",
        "Средняя": "medium",
        "Средний": "medium",
        "Средняя / высокая": "high",
        "Средний / высокий": "high",
        "Низкая": "low",
        "Низкий": "low",
        "Неизвестно": "unknown",
    },
)
BARRIER_TYPE_ALIASES = _aliases(
    BarrierType,
    {
        "Коммуникация": "communication",
        "Качество исполнения": "execution_quality",
        "Отчетность": "reporting",
        "Сроки": "timing",
        "Персонал": "staff",
        "KPI": "kpi",
        "Стоимость": "cost",
        "Обучение": "training",
        "Контроль": "control",
        "Ожидания": "expectations",
        "Организация процесса": "process_organization",
        "Другое": "other",
    },
)
BARRIER_TIME_STATUS_ALIASES = _aliases(
    BarrierTimeStatus,
    {
        "Было": "past",
        "Есть сейчас": "current",
        "Может возникнуть": "future",
        "Повторяется": "repeated",
    },
)
BARRIER_STATUS_ALIASES = _aliases(
    BarrierStatus,
    {
        "Открыт": "open",
        "В работе": "in_progress",
        "Сдержан": "contained",
        "Решен": "resolved",
        "Мониторинг": "monitoring",
        "Наблюдение": "monitoring",
        "Неизвестно": "unknown",
    },
)
EXPECTATION_TYPE_ALIASES = _aliases(
    ExpectationType,
    {
        "Скорость": "speed",
        "Качество": "quality",
        "Отчетность": "reporting",
        "Инициативность": "initiative",
        "Прозрачность": "transparency",
        "Стоимость": "cost",
        "Экспертиза": "expertise",
        "Экспертность": "expertise",
        "Предсказуемость": "predictability",
        "Минимум ручного контроля": "minimum_manual_control",
        "Гибкость": "flexibility",
        "Соблюдение договоренностей": "agreements_compliance",
        "Другое": "other",
    },
)
EXPLICITNESS_ALIASES = _aliases(
    Explicitness,
    {
        "Явное": "explicit",
        "Неявное": "implicit",
        "Неизвестно": "unknown",
    },
)
COMMUNICATION_CHANNEL_ALIASES = _aliases(
    CommunicationChannel,
    {
        "Встреча": "meeting",
        "Звонок": "call",
        "Почта": "email",
        "Email": "email",
        "Мессенджер": "messenger",
        "Отчет": "report",
        "BI-дашборд": "bi_dashboard",
        "Другое": "other",
        "Неизвестно": "unknown",
    },
)
COMMUNICATION_FREQUENCY_ALIASES = _aliases(
    CommunicationFrequency,
    {
        "По запросу": "on_request",
        "Еженедельно": "weekly",
        "Раз в две недели": "biweekly",
        "Ежемесячно": "monthly",
        "Ежеквартально": "quarterly",
        "Редко": "rarely",
        "Неизвестно": "unknown",
    },
)
ACTION_TYPE_ALIASES = _aliases(
    ActionType,
    {
        "Устранение": "elimination",
        "Сдерживание": "containment",
        "Профилактика": "prevention",
        "Эскалация": "escalation",
        "Коммуникационное действие": "communication_action",
        "Обучение": "training",
        "Контроль": "control",
        "Изменение процесса": "process_change",
        "Пересмотр KPI": "kpi_review",
        "Другое": "other",
    },
)
ACTION_STATUS_ALIASES = _aliases(
    ActionStatus,
    {
        "Сделать": "todo",
        "В работе": "in_progress",
        "Сделано": "done",
        "Неизвестно": "unknown",
    },
)
PLAN_CONFIRMATION_STATUS_ALIASES = _aliases(
    PlanConfirmationStatus,
    {
        "Подтвержденный план": "confirmed_plan",
        "Черновик": "draft",
        "AI-гипотеза": "ai_hypothesis",
        "AI гипотеза": "ai_hypothesis",
        "Требует согласования": "requires_approval",
    },
)
SENTIMENT_ALIASES = _aliases(
    Sentiment,
    {
        "Позитивная": "positive",
        "Положительная": "positive",
        "Нейтральная": "neutral",
        "Негативная": "negative",
        "Отрицательная": "negative",
        "Смешанная": "mixed",
        "Неизвестно": "unknown",
    },
)


def map_direction(value: object) -> str | None:
    return map_code(value, Direction, DIRECTION_ALIASES)


def map_project_scale(value: object) -> str | None:
    return map_code(value, ProjectScale, PROJECT_SCALE_ALIASES)


def map_operational_model(value: object) -> str | None:
    return map_code(value, OperationalModel, OPERATIONAL_MODEL_ALIASES)


def map_lifecycle_stage(value: object) -> str | None:
    return map_code(value, LifecycleStage, LIFECYCLE_STAGE_ALIASES)


def map_project_status(value: object) -> str | None:
    return map_code(value, ProjectStatus, PROJECT_STATUS_ALIASES)


def map_survey_type(value: object) -> str | None:
    return map_code(value, SurveyType, SURVEY_TYPE_ALIASES)


def map_importance_factor_type(value: object) -> str | None:
    return map_code(value, ImportanceFactorType, IMPORTANCE_FACTOR_TYPE_ALIASES)


def map_criticality(value: object) -> str | None:
    return map_code(value, Criticality, CRITICALITY_ALIASES)


def map_barrier_type(value: object) -> str | None:
    return map_code(value, BarrierType, BARRIER_TYPE_ALIASES)


def map_barrier_time_status(value: object) -> str | None:
    return map_code(value, BarrierTimeStatus, BARRIER_TIME_STATUS_ALIASES)


def map_barrier_status(value: object) -> str | None:
    return map_code(value, BarrierStatus, BARRIER_STATUS_ALIASES)


def map_expectation_type(value: object) -> str | None:
    return map_code(value, ExpectationType, EXPECTATION_TYPE_ALIASES)


def map_explicitness(value: object) -> str | None:
    return map_code(value, Explicitness, EXPLICITNESS_ALIASES)


def map_communication_channel(value: object) -> str | None:
    direct = map_code(value, CommunicationChannel, COMMUNICATION_CHANNEL_ALIASES)
    if direct is not None:
        return direct

    parts = [
        map_code(part, CommunicationChannel, COMMUNICATION_CHANNEL_ALIASES)
        for part in _split_composite(value)
    ]
    known = [part for part in parts if part is not None]
    return known[0] if known else "other" if normalize_label(value) else None


def map_communication_frequency(value: object) -> str | None:
    direct = map_code(value, CommunicationFrequency, COMMUNICATION_FREQUENCY_ALIASES)
    if direct is not None:
        return direct

    parts = [
        map_code(part, CommunicationFrequency, COMMUNICATION_FREQUENCY_ALIASES)
        for part in _split_composite(value)
    ]
    known = [part for part in parts if part is not None]
    return known[0] if known else "unknown" if normalize_label(value) else None


def map_action_type(value: object) -> str | None:
    return map_code(value, ActionType, ACTION_TYPE_ALIASES)


def map_action_status(value: object) -> str | None:
    return map_code(value, ActionStatus, ACTION_STATUS_ALIASES)


def map_plan_confirmation_status(value: object) -> str | None:
    return map_code(value, PlanConfirmationStatus, PLAN_CONFIRMATION_STATUS_ALIASES)


def map_sentiment(value: object) -> str | None:
    return map_code(value, Sentiment, SENTIMENT_ALIASES)
