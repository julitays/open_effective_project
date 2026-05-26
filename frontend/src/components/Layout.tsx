import { FolderKanban, PanelsTopLeft } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="min-h-screen bg-[#f3f6f9] text-slate-900">
      <div className="mx-auto flex min-h-screen max-w-[1680px] flex-col lg:flex-row">
        <aside className="border-b border-slate-200 bg-white px-4 py-4 lg:w-80 lg:shrink-0 lg:border-b-0 lg:border-r lg:px-5 lg:py-6">
          <div className="rounded-lg bg-slate-950 p-5 text-white shadow-sm">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase text-slate-400">
              <PanelsTopLeft aria-hidden="true" className="h-4 w-4" />
              OPEN Project Risk
            </div>
            <div className="mt-3 text-xl font-semibold">Контекст проекта</div>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Рабочая карта проекта, ролей, ожиданий, KPI и клиентских рисков.
            </p>
          </div>

          <nav className="mt-4 flex gap-2 lg:flex-col">
            <NavLink
              to="/projects"
              className={({ isActive }) =>
                `flex min-h-11 items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? "bg-slate-900 text-white shadow-sm"
                    : "text-slate-700 hover:bg-slate-100"
                }`
              }
            >
              <FolderKanban aria-hidden="true" className="h-4 w-4 shrink-0" />
              Проекты
            </NavLink>
          </nav>
        </aside>

        <main className="min-w-0 flex-1 px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
