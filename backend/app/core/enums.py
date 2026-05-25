from enum import StrEnum


class MVPCodeEnum(StrEnum):
    @classmethod
    def values(cls) -> set[str]:
        return {item.value for item in cls}


class Direction(MVPCodeEnum):
    FMCG = "fmcg"
    ELECTRONICS = "electronics"
    KAF = "kaf"
    PROMO = "promo"
    TRAINING = "training"
    AUDIT = "audit"
    MIXED = "mixed"
    OTHER = "other"


class ProjectScale(MVPCodeEnum):
    LOCAL = "local"
    REGIONAL = "regional"
    FEDERAL = "federal"
    INTERREGIONAL = "interregional"
    UNKNOWN = "unknown"


class OperationalModel(MVPCodeEnum):
    MERCHANDISING = "merchandising"
    COMBINED_MERCHANDISING = "combined_merchandising"
    PROMO_CONSULTING = "promo_consulting"
    KAF = "kaf"
    TRAINING = "training"
    AUDIT_QUALITY_CONTROL = "audit_quality_control"
    ANALYTICS_REPORTING = "analytics_reporting"
    MIXED = "mixed"
    OTHER = "other"


class LifecycleStage(MVPCodeEnum):
    LAUNCH = "launch"
    STABILIZATION = "stabilization"
    DEVELOPMENT = "development"
    RETENTION = "retention"
    RESTART = "restart"
    RISK = "risk"
    CLOSING = "closing"
    UNKNOWN = "unknown"


class ProjectStatus(MVPCodeEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PILOT = "pilot"
    AT_RISK = "at_risk"
    UNKNOWN = "unknown"


class ImportanceFactorType(MVPCodeEnum):
    RESPONSE_SPEED = "response_speed"
    EXECUTION_QUALITY = "execution_quality"
    STATUS_TRANSPARENCY = "status_transparency"
    REPORTING = "reporting"
    INITIATIVE = "initiative"
    COST = "cost"
    AGREEMENTS_COMPLIANCE = "agreements_compliance"
    STAFF_STABILITY = "staff_stability"
    TEAM_EXPERTISE = "team_expertise"
    MINIMUM_MANUAL_CONTROL = "minimum_manual_control"
    FLEXIBILITY = "flexibility"
    PREDICTABILITY = "predictability"
    STAFF_TRAINING_LEVEL = "staff_training_level"
    SAFETY = "safety"
    OTHER = "other"


class Criticality(MVPCodeEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class BarrierType(MVPCodeEnum):
    COMMUNICATION = "communication"
    EXECUTION_QUALITY = "execution_quality"
    REPORTING = "reporting"
    TIMING = "timing"
    STAFF = "staff"
    KPI = "kpi"
    COST = "cost"
    TRAINING = "training"
    CONTROL = "control"
    EXPECTATIONS = "expectations"
    PROCESS_ORGANIZATION = "process_organization"
    OTHER = "other"


class BarrierTimeStatus(MVPCodeEnum):
    PAST = "past"
    CURRENT = "current"
    FUTURE = "future"
    REPEATED = "repeated"


class BarrierStatus(MVPCodeEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    MONITORING = "monitoring"
    UNKNOWN = "unknown"


class ExpectationType(MVPCodeEnum):
    SPEED = "speed"
    QUALITY = "quality"
    REPORTING = "reporting"
    INITIATIVE = "initiative"
    TRANSPARENCY = "transparency"
    COST = "cost"
    EXPERTISE = "expertise"
    PREDICTABILITY = "predictability"
    MINIMUM_MANUAL_CONTROL = "minimum_manual_control"
    FLEXIBILITY = "flexibility"
    AGREEMENTS_COMPLIANCE = "agreements_compliance"
    OTHER = "other"


class Explicitness(MVPCodeEnum):
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    UNKNOWN = "unknown"


class CommunicationChannel(MVPCodeEnum):
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    MESSENGER = "messenger"
    REPORT = "report"
    BI_DASHBOARD = "bi_dashboard"
    OTHER = "other"
    UNKNOWN = "unknown"


class CommunicationFrequency(MVPCodeEnum):
    ON_REQUEST = "on_request"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    RARELY = "rarely"
    UNKNOWN = "unknown"
