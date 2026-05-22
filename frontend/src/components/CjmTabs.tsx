export type CjmTabId =
  | "passport"
  | "goals"
  | "lprs"
  | "importance"
  | "barriers"
  | "expectations"
  | "kpis"
  | "communications";

const tabs: Array<{ id: CjmTabId; label: string }> = [
  { id: "passport", label: "Паспорт" },
  { id: "goals", label: "Цели" },
  { id: "lprs", label: "ЛПР" },
  { id: "importance", label: "Важности ЛПР" },
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
    <div className="flex flex-wrap gap-2" role="tablist" aria-label="Разделы CJM">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          role="tab"
          aria-selected={activeTab === tab.id}
          onClick={() => onChange(tab.id)}
          className={`min-h-10 rounded-md border px-3 py-2 text-sm font-medium transition ${
            activeTab === tab.id
              ? "border-slate-900 bg-slate-900 text-white shadow-sm"
              : "border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}
