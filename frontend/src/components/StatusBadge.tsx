interface StatusBadgeProps {
  value: string;
}

const toneRules = [
  {
    tokens: ["high", "высок", "risk", "риск", "критич", "открыт"],
    className: "border-rose-200 bg-rose-50 text-rose-800 ring-1 ring-rose-100",
  },
  {
    tokens: ["medium", "сред", "актуал", "контрол", "подтверж", "осторож"],
    className: "border-amber-200 bg-amber-50 text-amber-900 ring-1 ring-amber-100",
  },
  {
    tokens: ["active", "актив", "done", "resolved", "заверш", "реш", "низк", "low", "лоялен"],
    className: "border-emerald-200 bg-emerald-50 text-emerald-800 ring-1 ring-emerald-100",
  },
  {
    tokens: ["не указано", "unknown", "истор"],
    className: "border-slate-200 bg-slate-50 text-slate-600 ring-1 ring-slate-100",
  },
];

function getTone(value: string) {
  const normalized = value.toLowerCase();
  return (
    toneRules.find((rule) =>
      rule.tokens.some((token) => normalized.includes(token)),
    )?.className ?? "border-sky-200 bg-sky-50 text-sky-800"
  );
}

export default function StatusBadge({ value }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex max-w-full items-center rounded-full border px-2.5 py-1 text-xs font-medium leading-5 ${getTone(value)}`}
    >
      <span className="break-words">{value}</span>
    </span>
  );
}
