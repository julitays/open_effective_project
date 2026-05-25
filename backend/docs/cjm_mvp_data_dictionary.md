# CJM MVP data dictionary

Supabase is the source of truth for MVP CJM data. New projects and records are
created through the web/API flow. Workbook import is not part of the active MVP
workflow.

All project and stakeholder data must stay anonymized: use `project_001`,
`lpr_001`, role names, and neutral project descriptions. Do not store real
client names, brand names, personal names, phone numbers, emails, or other
personal data in source files, examples, fixtures, or API payloads.

## `projects`

- Purpose: project passport and top-level project state.
- Stores: project code, external source ID, working code, direction, scale,
  regions, operational model, lifecycle stage, status, start date, and short
  description.
- Web editing: passport fields are updated with `PATCH /api/v1/projects/{code}`.
- Archive: `POST /api/v1/projects/{code}/archive`.

## `lpr_profiles`

- Purpose: client-side decision-maker or stakeholder roles.
- Stores: `lpr_code`, optional external LPR ID aliases, role/zone, influence,
  activity, relationship status, evidence basis, and manual comment.
- Web creation: `POST /api/v1/projects/{code}/lprs`.
- Archive: `POST /api/v1/projects/{code}/lprs/{lpr_code}/archive`.

## `lpr_importance_factors`

- Purpose: what matters to each LPR when they assess the service.
- Stores: factor type/text, criticality, source, evidence, period/source, and
  confidence.
- Current MVP note: these records are read in the LPR section. Creation from UI
  can be added as a focused next step if users need separate management of LPR
  importance factors.

## `project_goals`

- Purpose: goals of OPEN, the client, or the joint project.
- Stores: goal code, owner, type, text, priority, related KPI/criterion,
  source, relevance, comment, success criteria, and status.
- Web creation: `POST /api/v1/projects/{code}/goals`.
- Archive: `POST /api/v1/projects/{code}/goals/{goal_code}/archive`.

## `project_kpis`

- Purpose: KPI and success criteria used to assess the project.
- Stores: KPI code, name, type, source, relevance, related expectation/barrier,
  client criticality, confirmation flag, target/current values, unit, and
  status.
- Web creation: `POST /api/v1/projects/{code}/kpis`.
- Archive: `POST /api/v1/projects/{code}/kpis/{kpi_code}/archive`.

## `client_expectations`

- Purpose: explicit or inferred client expectations that affect project risk.
- Stores: expectation code, text, type, explicitness, criticality, linked LPR,
  linked KPI text, source, evidence, relevance, and confidence.
- Web creation: `POST /api/v1/projects/{code}/expectations`.
- Archive: `POST /api/v1/projects/{code}/expectations/{expectation_code}/archive`.

## `project_barriers`

- Purpose: barriers and risk signals across past, current, repeated, and future
  project context.
- Stores: barrier code, title, type, time status, description, criticality,
  linked LPR, linked importance/KPI text, source, evidence, first/last seen
  periods, status, relevance, and confidence.
- Web creation: `POST /api/v1/projects/{code}/barriers`.
- Archive: `POST /api/v1/projects/{code}/barriers/{barrier_code}/archive`.

## `communication_points`

- Purpose: communication matrix between client-side roles and OPEN roles.
- Stores: communication code, client side, external LPR ID, OPEN role, topic,
  channel, frequency, criticality, source, relevance, comment, and summary.
- Web creation: `POST /api/v1/projects/{code}/communications`.
- Archive: `POST /api/v1/projects/{code}/communications/{communication_code}/archive`.

## `project_context_blocks`

- Purpose: flexible web-first storage for extended project-effectiveness
  sections that are useful in the full screen but are not core CJM entities.
- Stores: section key, block code, block type, title, JSON content, and display
  order.
- Intended sections: summary, SWOT, risk map, interpretation rules,
  effectiveness layers, competitors, and other future contextual blocks.
- Web creation: `POST /api/v1/projects/{code}/context-blocks`.

## Archive Fields

Main MVP tables include:

- `archived_at`
- `archived_by`
- `archive_reason`

Read endpoints hide archived records by default. This keeps the workspace clean
without losing audit history.
