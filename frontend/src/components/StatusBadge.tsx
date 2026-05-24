interface StatusBadgeProps {
  value: string;
}

const tones = {
  danger: "border-rose-200 bg-rose-50 text-rose-800 ring-1 ring-rose-100",
  warning: "border-amber-200 bg-amber-50 text-amber-900 ring-1 ring-amber-100",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800 ring-1 ring-emerald-100",
  neutral: "border-slate-200 bg-slate-50 text-slate-600 ring-1 ring-slate-100",
  info: "border-sky-200 bg-sky-50 text-sky-800 ring-1 ring-sky-100",
};

function getTone(value: string) {
  const normalized = value.toLowerCase();

  if (
    normalized.includes("требует подтверждения") ||
    normalized.includes("не указано") ||
    normalized.includes("unknown") ||
    normalized.includes("истор")
  ) {
    return tones.neutral;
  }

  if (
    normalized === "актуально" ||
    normalized === "активен" ||
    normalized.includes("лоялен") ||
    normalized.includes("реш")
  ) {
    return tones.success;
  }

  if (
    normalized.includes("высок") ||
    normalized.includes("критичен") ||
    normalized.includes("в зоне риска") ||
    normalized.includes("открыт")
  ) {
    return tones.danger;
  }

  if (
    normalized.includes("сред") ||
    normalized.includes("осторож") ||
    normalized.includes("контрол")
  ) {
    return tones.warning;
  }

  if (
    normalized.includes("низк") ||
    normalized.includes("неактуально") ||
    normalized.includes("неактив")
  ) {
    return tones.neutral;
  }

  return tones.info;
}

export default function StatusBadge({ value }: StatusBadgeProps) {
  const displayValue = formatBadgeText(value);

  return (
    <span
      className={`inline-flex max-w-full items-center whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-medium leading-5 ${getTone(value)}`}
    >
      <span>{displayValue}</span>
    </span>
  );
}

function formatBadgeText(value: string) {
  const trimmed = value.trim();

  if (/^[A-ZА-ЯЁ0-9/.\-\s]+$/.test(trimmed)) {
    return trimmed;
  }

  return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
}
