import { Save, X } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";

export interface EditOption {
  value: string;
  label: string;
}

export interface EditField {
  name: string;
  label: string;
  input?: "text" | "textarea" | "select" | "multiselect";
  options?: EditOption[];
}

export type EditValues = Record<string, string | null | undefined>;
export type EditPayload = Record<string, string | null>;

interface EditEntityModalProps {
  title: string;
  fields: EditField[];
  values: EditValues;
  saving: boolean;
  error: string | null;
  onClose: () => void;
  onSave: (payload: EditPayload) => void;
}

export default function EditEntityModal({
  title,
  fields,
  values,
  saving,
  error,
  onClose,
  onSave,
}: EditEntityModalProps) {
  const [draft, setDraft] = useState<Record<string, string>>({});

  useEffect(() => {
    const nextDraft: Record<string, string> = {};
    fields.forEach((field) => {
      nextDraft[field.name] = values[field.name] ?? "";
    });
    setDraft(nextDraft);
  }, [fields, values]);

  function setValue(name: string, value: string) {
    setDraft((current) => ({ ...current, [name]: value }));
  }

  function toggleMultiValue(name: string, value: string) {
    setDraft((current) => {
      const values = splitMultiValue(current[name] ?? "");
      const nextValues = values.includes(value)
        ? values.filter((item) => item !== value)
        : [...values, value];

      return { ...current, [name]: nextValues.join("; ") };
    });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload: EditPayload = {};
    fields.forEach((field) => {
      const trimmed = (draft[field.name] ?? "").trim();
      payload[field.name] = trimmed || null;
    });
    onSave(payload);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-8 backdrop-blur-sm">
      <form
        onSubmit={submit}
        className="max-h-[90vh] w-full max-w-3xl overflow-hidden rounded-2xl bg-white shadow-2xl shadow-slate-950/20"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
          <div>
            <div className="text-xs font-semibold uppercase text-slate-400">Редактирование</div>
            <h2 className="mt-1 text-xl font-semibold text-slate-950">{title}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition-all duration-200 ease-out hover:bg-slate-100"
            aria-label="Закрыть"
          >
            <X aria-hidden="true" className="h-5 w-5" />
          </button>
        </div>

        <div className="max-h-[62vh] space-y-4 overflow-y-auto px-6 py-5">
          {fields.map((field) => {
            const options = visibleOptions(field.options || [], draft[field.name] ?? "");
            const showEmptyOption = !options.some((option) => option.label === "Не указано");
            return (
            <label key={field.name} className="block">
              <span className="text-xs font-semibold uppercase text-slate-500">{field.label}</span>
              {field.input === "select" ? (
                <select
                  value={draft[field.name] ?? ""}
                  onChange={(event) => setValue(field.name, event.target.value)}
                  className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
                >
                  {showEmptyOption ? <option value="">Не указано</option> : null}
                  {options.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : field.input === "multiselect" ? (
                <div className="mt-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
                  {options.length > 0 ? (
                    <div className="max-h-52 space-y-2 overflow-y-auto pr-1">
                      {options.map((option) => {
                        const checked = splitMultiValue(draft[field.name] ?? "").includes(option.value);
                        return (
                          <label
                            key={option.value}
                            className="flex cursor-pointer items-start gap-2 rounded-md px-2 py-1.5 text-sm text-slate-800 hover:bg-white"
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={() => toggleMultiValue(field.name, option.value)}
                              className="mt-1 h-4 w-4 rounded border-slate-300 text-slate-950 focus:ring-slate-400"
                            />
                            <span className="leading-5">{option.label}</span>
                          </label>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500">Нет доступных вариантов.</div>
                  )}
                  {draft[field.name] && !hasSelectedKnownOption(options, draft[field.name] ?? "") ? (
                    <div className="mt-3 rounded-md bg-white px-3 py-2 text-xs leading-5 text-slate-500 ring-1 ring-slate-200">
                      Текущее значение: {draft[field.name]}
                    </div>
                  ) : null}
                </div>
              ) : field.input === "textarea" ? (
                <textarea
                  value={draft[field.name] ?? ""}
                  onChange={(event) => setValue(field.name, event.target.value)}
                  rows={4}
                  className="mt-2 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
                />
              ) : (
                <input
                  value={draft[field.name] ?? ""}
                  onChange={(event) => setValue(field.name, event.target.value)}
                  className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400 focus:bg-white"
                />
              )}
            </label>
          )})}

          {error ? (
            <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              {error}
            </div>
          ) : null}
        </div>

        <div className="flex flex-col-reverse gap-3 border-t border-slate-100 bg-slate-50 px-6 py-4 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="min-h-11 rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 shadow-sm transition-all duration-200 ease-out hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Отмена
          </button>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex min-h-11 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 text-sm font-semibold text-white shadow-sm transition-all duration-200 ease-out hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Save aria-hidden="true" className="h-4 w-4" />
            {saving ? "Сохраняем..." : "Сохранить"}
          </button>
        </div>
      </form>
    </div>
  );
}

function visibleOptions(options: EditOption[], currentValue: string) {
  const seenLabels = new Set<string>();
  const result: EditOption[] = [];
  const currentOption = options.find((option) => option.value === currentValue);
  const orderedOptions = currentOption
    ? [currentOption, ...options.filter((option) => option.value !== currentValue)]
    : options;

  orderedOptions.forEach((option) => {
    if (option.label === "Не указано" && option.value !== currentValue) {
      return;
    }

    if (seenLabels.has(option.label)) {
      return;
    }

    seenLabels.add(option.label);
    result.push(option);
  });

  if (
    currentOption &&
    !result.some((option) => option.value === currentValue)
  ) {
    return [
      currentOption,
      ...result.filter((option) => option.label !== currentOption.label),
    ];
  }

  if (currentValue && !result.some((option) => option.value === currentValue)) {
    return [{ value: currentValue, label: currentValue }, ...result];
  }

  return result;
}

function splitMultiValue(value: string) {
  return value
    .split(";")
    .map((item) => item.trim())
    .filter(Boolean);
}

function hasSelectedKnownOption(options: EditOption[], value: string) {
  const selected = splitMultiValue(value);
  return selected.length > 0 && selected.every((item) => options.some((option) => option.value === item));
}
