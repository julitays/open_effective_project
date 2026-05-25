import { Navigate, Route, BrowserRouter, Routes } from "react-router-dom";

import EmptyState from "./components/EmptyState";
import Layout from "./components/Layout";
import ProjectEffectivenessScreenMockup from "./pages/ProjectEffectivenessScreenMockup";
import ProjectsPage from "./pages/ProjectsPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/projects/:projectCode"
          element={<ProjectEffectivenessScreenMockup />}
        />
        <Route
          path="/projects/:projectCode/context-mockup"
          element={<Navigate replace to=".." relative="path" />}
        />
        <Route element={<Layout />}>
          <Route index element={<Navigate replace to="/projects" />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route
            path="*"
            element={
              <EmptyState
                title="Страница не найдена"
                description="Проверьте адрес или вернитесь к списку проектов."
              />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
