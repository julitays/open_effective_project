# CJM MVP data dictionary

This dictionary explains the current CJM MVP entities in human terms. Manual
intake files must contain anonymized project and stakeholder codes only. Do not
store real project names, client names, personal names, phones, email addresses,
or other personal data in examples, fixtures, or imports.

## `projects`

- Purpose: one anonymized project that the CJM import belongs to.
- Stores: `project_code`, coarse project type/direction, lifecycle phase, and
  project status.
- Required for manual load: `Project ID`.
- Optional in manual load: direction, scale, operational model, additional
  contours, lifecycle stage, status, start date, summary, follow-up notes.
- Must be anonymized: `Project ID` must look like `project_001`. Do not add a
  real project or client name.
- Current storage note: scale, operational model, additional contours, start
  date, summary, and follow-up notes remain in the Excel intake file until the
  domain model is expanded.

## `lpr_profiles`

- Purpose: anonymized decision-maker or client-side stakeholder profiles.
- Stores: `lpr_code`, stakeholder role, influence level, and engagement note.
- Required for manual load: `LPR ID`, role.
- Optional in manual load: influence, survey participation notes, periods,
  inferred attitude, evidence, follow-up notes.
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

- Purpose: one historical survey batch attached to a project.
- Stores: batch code, survey type, collection period, and import status.
- Required for manual load: `Survey ID`, `Project ID`, survey type.
- Optional in manual load: year and period/date.
- Must be anonymized: use an internal survey code, not a client name.

## `survey_questions`

- Purpose: survey questions represented in the manual history sheet.
- Stores: stable generated question code, question text, and question type.
- Required for manual load: question text on the survey history row.
- Optional in manual load: no separate question fields are required beyond the
  row context.
- Must be anonymized: question wording must not include names or contact data.

## `survey_responses`

- Purpose: a response row inside a survey batch.
- Stores: generated response code, optional LPR link, respondent role, and
  submission metadata when available.
- Required for manual load: the surrounding survey row context.
- Optional in manual load: `LPR ID`; rows may be loaded without a stakeholder
  link.
- Must be anonymized: use codes and roles only.

## `survey_answers`

- Purpose: answer value and client comment captured from survey history.
- Stores: score/value and `original_comment_text`.
- Required for manual load: survey and question context.
- Optional in manual load: score and client comment can be blank.
- Must be anonymized: a filled client comment is stored as the already
  anonymized text available at the MVP upload boundary.

## `comment_analysis`

- Purpose: manual or later AI analysis attached to a survey answer.
- Stores: topic, sentiment, criticality, repeated-theme flag, summary, evidence
  quote, analysis source, and confidence.
- Required for manual load: created only when a survey row has analysis context
  such as topic, useful/not-useful reason, or comment evidence.
- Optional in manual load: evidence quote and confidence.
- Must be anonymized: summary and evidence must not restore personal or client
  identity.

## `project_goals`

- Purpose: project goals and success criteria.
- Stores: goal text, goal type, success criteria, and status.
- Required for manual load: not loaded by the current Excel intake sheets.
- Optional in manual load: goal data can be added in a later intake extension.
- Must be anonymized: goal wording must not include real project or client
  names.

## `project_kpis`

- Purpose: KPI or success criteria observed for the project.
- Stores: KPI code, metric name, target/current values, unit, and tracking
  status.
- Required for manual load: `KPI ID`, KPI/success criterion name.
- Optional in manual load: KPI type, source, normal/alarm/critical notes,
  related expectation, related barrier, follow-up notes.
- Must be anonymized: KPI labels and notes must not include identifying client
  data.
- Current storage note: normal threshold is stored as a target value; the alarm
  and critical deviation notes stay in the Excel intake file for now.

## `client_expectations`

- Purpose: explicit or inferred client expectations that affect project risk.
- Stores: expectation text, expectation type, explicitness, criticality, and
  check method.
- Required for manual load: `Expectation ID`, expectation text, expectation
  type, criticality.
- Optional in manual load: explicitness, linked LPR, importance, KPI, source,
  evidence, check method, follow-up notes.
- Must be anonymized: expectation text and evidence must avoid client and person
  identity.
- Current storage note: the Excel `Expectation ID` is used in reports; current
  MVP persistence matches expectations by text and type.

## `project_barriers`

- Purpose: barriers or risks seen in CJM history.
- Stores: title, barrier type, time status, criticality, status, source type,
  and source ID.
- Required for manual load: `Barrier ID`, title, type, time status, criticality.
- Optional in manual load: description, linked LPR, linked importance, linked
  KPI, source, evidence, first/last period, status, follow-up notes.
- Must be anonymized: source and evidence content must not identify people or
  clients.
- Current storage note: `Barrier ID` is stored as the manual Excel source ID and
  is used for plan links.

## `barrier_mitigation_plans`

- Purpose: action plans used to remove, contain, or prevent barriers.
- Stores: barrier link, action type, action text, owner role, due period,
  status, check method, expected and actual effects.
- Required for manual load: plan ID, linked `Barrier ID`, action type, action
  text, owner role.
- Optional in manual load: related expectation, due period, status, check
  method, expected effect, follow-up notes.
- Must be anonymized: owner must be a role, not a person.

## `communication_points`

- Purpose: interaction points and communication risk signals in the CJM.
- Stores: point type/channel, summary, optional LPR link, stage, and outcome.
- Required for manual load: communication ID and interaction topic.
- Optional in manual load: client/open sides, channel, frequency, criticality,
  break-risk flag, evidence, follow-up notes.
- Must be anonymized: sides of communication should be roles or teams, never
  names.
- Current storage note: the current importer composes the interaction summary
  from the topic, roles, frequency, criticality, and break-risk flag.

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
