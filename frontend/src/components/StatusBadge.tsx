interface StatusBadgeProps {
  value: string;
}

const toneRules = [
  {
    tokens: ["high", "высок", "risk", "at_risk", "open"],
    className: "border-rose-200 bg-rose-50 text-rose-800",
  },
  {
    tokens: ["medium", "сред", "current", "актуал", "monitor"],
    className: "border-amber-200 bg-amber-50 text-amber-900",
  },
  {
    tokens: ["active", "done", "resolved", "completed", "низк", "low"],
    className: "border-emerald-200 bg-emerald-50 text-emerald-800",
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
      className={`inline-flex max-w-full items-center rounded-md border px-2 py-1 text-xs font-medium leading-5 ${getTone(value)}`}
    >
      <span className="break-words">{value}</span>
    </span>
  );
}
