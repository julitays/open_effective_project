import { CircleAlert } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description: string;
}

export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-5 py-8 shadow-sm">
      <div className="mx-auto flex max-w-xl flex-col items-center text-center">
        <span className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-100 text-slate-600">
          <CircleAlert aria-hidden="true" className="h-5 w-5" />
        </span>
        <h2 className="mt-4 text-lg font-semibold text-slate-950">{title}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
      </div>
    </div>
  );
}
