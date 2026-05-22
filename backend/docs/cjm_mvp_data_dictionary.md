# CJM MVP data dictionary

This dictionary explains the current CJM MVP entities in human terms. Manual
intake files must contain anonymized project and stakeholder codes only. Do not
store real project names, client names, personal names, phones, email addresses,
or other personal data in examples, fixtures, or imports.

## `projects`

- Purpose: one anonymized project that the CJM import belongs to.
- Stores: `project_code`, external source project ID, working source code,
  coarse project type/direction, lifecycle phase, and project status.
- Required for manual load: `Project ID`, `External project ID`.
- Optional in manual load: working project code, direction, scale, known
  regions, operational model, additional contours, lifecycle stage, status,
  start date, summary.
- Must be anonymized: `Project ID` must look like `project_001`. Do not add a
  real project or client name.
- Current storage note: the MVP importer stores scale, known regions,
  operational model, additional contours, start date, and short summary from
  the project passport.

## `lpr_profiles`

- Purpose: anonymized decision-maker or client-side stakeholder profiles.
- Stores: `lpr_code`, optional external source LPR ID aliases, stakeholder role,
  influence level, and activity/engagement note.
- Required for manual load: `LPR ID`, role.
- Optional in manual load: external LPR ID aliases from a source CSV, influence,
  activity status, inferred attitude, evidence, and manual clarification note.
- Must be anonymized: `LPR ID` must look like `lpr_001`; roles must not contain
  names.

## `lpr_importance_factors`

- Purpose: factors that matter to an LPR when they assess the service.
- Stores: factor type, factor text, importance/criticality level, and source.
- Required for manual load: `LPR ID`, importance text.
- Optional in manual load: criticality, source, evidence quote, period,
  confidence, follow-up notes.
- Must be anonymized: LPR references and evidence quotes must not identify a
  person or client.

## `survey_batches`

- Purpose: one historical survey batch attached to a project in the wider MVP
  schema.
- Stores: batch code, survey type, collection period, and import status.
- Required for manual load: not loaded by the structured CJM workbook.
- Optional in manual load: survey history belongs to a separate future import
  path.
- Must be anonymized: use an internal survey code, not a client name.

## `survey_questions`

- Purpose: survey questions for future survey-history ingestion.
- Stores: stable generated question code, question text, and question type.
- Required for manual load: not loaded by the structured CJM workbook.
- Optional in manual load: question history belongs to a separate future import
  path.
- Must be anonymized: question wording must not include names or contact data.

## `survey_responses`

- Purpose: a response row inside a survey batch.
- Stores: generated response code, optional LPR link, respondent role, and
  submission metadata when available.
- Required for manual load: not loaded by the structured CJM workbook.
- Optional in manual load: response history belongs to a separate future import
  path.
- Must be anonymized: use codes and roles only.

## `survey_answers`

- Purpose: answer value and already anonymized client comment in the wider MVP
  survey schema.
- Stores: score/value and `original_comment_text`.
- Required for manual load: not loaded by the structured CJM workbook.
- Optional in manual load: answer history belongs to a separate future import
  path.
- Must be anonymized: a filled client comment is stored as the already
  anonymized text available at the MVP upload boundary.

## `comment_analysis`

- Purpose: manual or later AI analysis attached to a survey answer.
- Stores: topic, sentiment, criticality, repeated-theme flag, summary, evidence
  quote, analysis source, and confidence.
- Required for manual load: not loaded by the structured CJM workbook.
- Optional in manual load: analysis belongs to a later manual/AI flow.
- Must be anonymized: summary and evidence must not restore personal or client
  identity.

## `project_goals`

- Purpose: project goals and success criteria.
- Stores: goal text, goal type, success criteria, and status.
- Required for manual load: `08_Цели проекта` rows require goal ID, project ID,
  goal type, and goal text. Goal ID is persisted as the stable manual source ID
  for repeated imports.
- Optional in manual load: source, linked KPI/criterion, owner, priority,
  actuality status, and comment.
- Must be anonymized: goal wording must not include real project or client
  names.

## `project_kpis`

- Purpose: KPI or success criteria observed for the project.
- Stores: KPI code, metric name, target/current values, unit, and tracking
  status.
- Required for manual load: `KPI ID`, KPI/success criterion name.
- Optional in manual load: KPI type, source, actuality status, related
  expectation, related barrier, criticality, comment, confirmation flag.
- Must be anonymized: KPI labels and notes must not include identifying client
  data.
- Current storage note: source, comment, confirmation flag, related
  expectation, and related barrier are kept as MVP text fields.

## `client_expectations`

- Purpose: explicit or inferred client expectations that affect project risk.
- Stores: expectation text, expectation type, explicitness, criticality, check
  method, and free-text linked KPI or success criteria restored from CJM.
- Required for manual load: `Expectation ID`, expectation text, expectation
  type, criticality.
- Optional in manual load: explicitness, linked LPR, external LPR ID,
  importance, KPI, source, evidence, actuality status, confidence.
- Must be anonymized: expectation text and evidence must avoid client and person
  identity.
- Current storage note: the Excel `Expectation ID` is stored as the stable
  manual source ID for repeated imports and readback.

## `project_barriers`

- Purpose: barriers or risks seen in CJM history.
- Stores: title, barrier type, time status, criticality, status, source type,
  source ID, and free-text linked KPI or success criteria restored from CJM.
- Required for manual load: `Barrier ID`, title, type, time status, criticality.
- Optional in manual load: description, linked LPR, external LPR ID, linked
  importance, linked KPI, source, evidence, first/last period, barrier status,
  actuality status, confidence.
- Must be anonymized: source and evidence content must not identify people or
  clients.
- Current storage note: `Barrier ID` is stored as the manual Excel source ID for
  repeated imports and readback.

## `barrier_mitigation_plans`

- Purpose: a wider MVP-schema table for later barrier action plans.
- Stores: barrier link, action type, action text, owner role, due period,
  status, check method, expected and actual effects.
- Required for manual load: not loaded by the current structured CJM workbook.
- Optional in manual load: action-plan intake is outside this CJM file path.
- Must be anonymized: any later owner value must be a role, not a person.

## `communication_points`

- Purpose: interaction points and communication risk signals in the CJM.
- Stores: point type/channel, summary, optional LPR link, stage, and outcome.
- Required for manual load: communication ID and interaction topic.
- Optional in manual load: client side as LPR ID or role, external LPR ID, OPEN
  role, channel, frequency, criticality, source, actuality status, comment.
- Must be anonymized: sides of communication should be roles or teams, never
  names.
- Current storage note: the current importer composes the interaction summary
  from the topic, roles, external LPR ID, frequency, criticality, and actuality
  status. Excel `Communication ID` is stored as the stable manual source ID for
  repeated imports.

## `ai_project_findings`

- Purpose: later project-level AI findings.
- Stores: finding type, title, summary, criticality, and evidence summary.
- Required for manual load: not loaded by the manual CJM intake layer.
- Optional in manual load: none at this stage.
- Must be anonymized: future finding text must stay anonymized.

## `ai_recommendations`

- Purpose: later recommendations connected to project findings.
- Stores: recommendation type, recommendation text, priority, status, and
  optional finding link.
- Required for manual load: not loaded by the manual CJM intake layer.
- Optional in manual load: none at this stage.
- Must be anonymized: future recommendation text must stay anonymized.
