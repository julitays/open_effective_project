export type CjmTabId =
  | "overview"
  | "passport"
  | "goals"
  | "lprs"
  | "barriers"
  | "expectations"
  | "kpis"
  | "communications";

export const cjmTabs: Array<{ id: CjmTabId; label: string }> = [
  { id: "overview", label: "Обзор" },
  { id: "passport", label: "Паспорт" },
  { id: "goals", label: "Цели" },
  { id: "lprs", label: "ЛПР" },
  { id: "barriers", label: "Барьеры" },
  { id: "expectations", label: "Ожидания" },
  { id: "kpis", label: "KPI" },
  { id: "communications", label: "Коммуникации" },
];

export function isCjmTabId(value: string | null): value is CjmTabId {
  return cjmTabs.some((tab) => tab.id === value);
}

interface CjmTabsProps {
  activeTab: CjmTabId;
  onChange: (tabId: CjmTabId) => void;
}

export default function CjmTabs({ activeTab, onChange }: CjmTabsProps) {
  return (
    <nav
      className="space-y-1"
      role="tablist"
      aria-label="Разделы CJM"
    >
      {cjmTabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.id}
          onClick={() => onChange(tab.id)}
          className={`flex min-h-10 w-full items-center rounded-lg px-3 py-2 text-left text-sm font-medium transition ${
            activeTab === tab.id
              ? "bg-slate-950 text-white shadow-sm"
              : "text-slate-700 hover:bg-slate-100 hover:text-slate-950"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
