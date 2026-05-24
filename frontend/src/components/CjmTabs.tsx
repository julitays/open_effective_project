export type CjmTabId =
  | "overview"
  | "passport"
  | "goals"
  | "lprs"
  | "barriers"
  | "expectations"
  | "kpis"
  | "communications";

const tabs: Array<{ id: CjmTabId; label: string }> = [
  { id: "overview", label: "Обзор" },
  { id: "passport", label: "Паспорт" },
  { id: "goals", label: "Цели" },
  { id: "lprs", label: "ЛПР" },
  { id: "barriers", label: "Барьеры" },
  { id: "expectations", label: "Ожидания" },
  { id: "kpis", label: "KPI" },
  { id: "communications", label: "Коммуникации" },
];

interface CjmTabsProps {
  activeTab: CjmTabId;
  onChange: (tabId: CjmTabId) => void;
}

export default function CjmTabs({ activeTab, onChange }: CjmTabsProps) {
  return (
    <nav
      className="rounded-xl border border-slate-200/80 bg-white/90 p-2 shadow-sm shadow-slate-200/70"
      role="tablist"
      aria-label="Разделы CJM"
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.id}
          onClick={() => onChange(tab.id)}
          className={`mb-1 flex min-h-10 w-full items-center rounded-lg px-3 py-2 text-left text-sm font-medium transition last:mb-0 ${
            activeTab === tab.id
              ? "bg-slate-950 text-white shadow-sm"
              : "text-slate-600 hover:bg-slate-100 hover:text-slate-950"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
