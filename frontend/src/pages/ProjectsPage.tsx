import { useEffect, useState } from "react";

import EmptyState from "../components/EmptyState";
import ProjectCard from "../components/ProjectCard";
import { getProjects } from "../api/projects";
import type { ProjectPassport } from "../types/cjm";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectPassport[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    setLoading(true);
    getProjects(controller.signal)
      .then((items) => {
        setProjects(items);
        setError(null);
      })
      .catch((cause: unknown) => {
        if (!controller.signal.aborted) {
          setError(cause instanceof Error ? cause.message : "Не удалось загрузить проекты.");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      });

    return () => controller.abort();
  }, []);

  return (
    <section className="space-y-5">
      <header className="border-b border-slate-200 pb-5">
        <p className="text-sm font-semibold text-sky-800">Проекты</p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-950">
          Карты CJM
        </h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Выберите обезличенный проект, чтобы открыть паспорт и CJM-разделы.
        </p>
      </header>

      {loading ? (
        <LoadingGrid />
      ) : error ? (
        <EmptyState title="Не удалось загрузить проекты" description={error} />
      ) : projects.length === 0 ? (
        <EmptyState
          title="Проектов пока нет"
          description="Read-only API вернул пустой список проектов."
        />
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          {projects.map((project) => (
            <ProjectCard key={project.project_code} project={project} />
          ))}
        </div>
      )}
    </section>
  );
}

function LoadingGrid() {
  return (
    <div className="grid gap-4 xl:grid-cols-2" aria-label="Загрузка проектов">
      {["one", "two"].map((item) => (
        <div
          key={item}
          className="h-72 animate-pulse rounded-lg border border-slate-200 bg-white shadow-sm"
        />
      ))}
    </div>
  );
}
