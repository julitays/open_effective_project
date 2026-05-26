import { Plus, Save, Trash2, X } from "lucide-react";
import { useEffect, useMemo, useState, type FormEvent } from "react";

import type { EditOption } from "./EditEntityModal";

export interface CollectionField {
  name: string;
  label: string;
  input?: "text" | "textarea" | "select";
  options?: EditOption[];
  rows?: number;
}

export interface CollectionItemValues {
  [key: string]: string | null | undefined;
}

interface EditCollectionModalProps {
  title: string;
  description?: string;
  itemLabel: string;
  fields: CollectionField[];
  items: CollectionItemValues[];
  saving: boolean;
  error: string | null;
  onClose: () => void;
  onSave: (items: Record<string, string | null>[]) => void;
}

export default function EditCollectionModal({
  title,
  description,
  itemLabel,
  fields,
  items,
  saving,
  error,
  onClose,
  onSave,
}: EditCollectionModalProps) {
  const emptyItem = useMemo(
    () =>
      fields.reduce<Record<string, string>>((accumulator, field) => {
        accumulator[field.name] = "";
        return accumulator;
      }, {}),
    [fields],
  );
  const [draft, setDraft] = useState<Record<string, string>[]>([]);

  useEffect(() => {
    const nextDraft = (items.length ? items : [emptyItem]).map((item) =>
      fields.reduce<Record<string, string>>((accumulator, field) => {
        accumulator[field.name] = item[field.name]?.toString() ?? "";
        return accumulator;
      }, {}),
    );
    setDraft(nextDraft);
  }, [emptyItem, fields, items]);

  function updateItem(index: number, fieldName: string, value: string) {
    setDraft((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [fieldName]: value } : item,
      ),
    );
  }

  function addItem() {
    setDraft((current) => [...current, { ...emptyItem }]);
  }

  function removeItem(index: number) {
    setDraft((current) => {
      if (current.length === 1) {
        return [{ ...emptyItem }];
      }
      return current.filter((_, itemIndex) => itemIndex !== index);
    });
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = draft
      .map((item) =>
        Object.fromEntries(
          Object.entries(item).map(([key, value]) => {
            const trimmed = value.trim();
            return [key, trimmed || null];
          }),
        ),
      )
      .filter((item) => Object.values(item).some(Boolean));
    onSave(payload);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 px-4 py-8 backdrop-blur-sm">
      <form
        onSubmit={submit}
        className="max-h-[92vh] w-full max-w-5xl overflow-hidden rounded-2xl bg-white shadow-2xl shadow-slate-950/20"
      >
        <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-6 py-5">
          <div>
            <div className="text-xs font-semibold uppercase text-slate-400">Редактирование</div>
            <h2 className="mt-1 text-xl font-semibold text-slate-950">{title}</h2>
            {description ? (
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-500">{description}</p>
            ) : null}
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

        <div className="max-h-[66vh] space-y-4 overflow-y-auto px-6 py-5">
          {draft.map((item, index) => (
            <section
              key={`${itemLabel}-${index}`}
              className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
            >
              <div className="mb-4 flex items-center justify-between gap-3">
                <div className="text-sm font-semibold text-slate-900">
                  {itemLabel} {index + 1}
                </div>
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="inline-flex items-center gap-1 rounded-lg border border-amber-200 bg-white px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-50"
                >
                  <Trash2 aria-hidden="true" className="h-3.5 w-3.5" />
                  Убрать
                </button>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                {fields.map((field) => (
                  <label key={`${index}-${field.name}`} className="block">
                    <span className="text-xs font-semibold uppercase text-slate-500">
                      {field.label}
                    </span>
                    {field.input === "select" ? (
                      <select
                        value={item[field.name] ?? ""}
                        onChange={(event) => updateItem(index, field.name, event.target.value)}
                        className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400"
                      >
                        <option value="">Не указано</option>
                        {(field.options || []).map((option) => (
                          <option key={`${field.name}-${option.value}`} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    ) : field.input === "textarea" ? (
                      <textarea
                        value={item[field.name] ?? ""}
                        onChange={(event) => updateItem(index, field.name, event.target.value)}
                        rows={field.rows || 4}
                        className="mt-2 w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-400"
                      />
                    ) : (
                      <input
                        value={item[field.name] ?? ""}
                        onChange={(event) => updateItem(index, field.name, event.target.value)}
                        className="mt-2 min-h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-slate-400"
                      />
                    )}
                  </label>
                ))}
              </div>
            </section>
          ))}

          <button
            type="button"
            onClick={addItem}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-dashed border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <Plus aria-hidden="true" className="h-4 w-4" />
            Добавить
          </button>

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
