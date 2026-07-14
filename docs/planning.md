# Planning Rules

## Purpose

Every repository-changing task must have an approved Plan before implementation. The Plan records why the work is needed, fixes the approved scope, guides execution, and defines how completion will be verified.

Read-only investigation, explanation, and review tasks that do not change repository files do not require a Plan or work Log.

## Creating a Plan

1. Create the Plan before changing any other repository file.
2. Copy the structure from `plan/TEMPLATE.md`.
3. Save it as `plan/NNN-task-slug.md`, using a three-digit index and a concise English kebab-case slug.
4. Fill in every required section: Motivation, Goal, Scope, Steps, and Validation.
5. Keep the Plan in Draft until the user approves it or explicitly requests execution of the presented Plan.

Use `001` when there are no numbered Plans. Otherwise, ignore `TEMPLATE.md`, find the greatest existing index, and add one. Indexes increase across the project, including when an earlier Plan was deleted; never reuse or renumber an index.

Use one Plan for one user-requested task. Related changes within the same approved scope belong to that Plan.

## Plan Lifecycle

Plan status follows this sequence:

`Draft` → `In Progress` → `Completed`

- **Draft:** The Plan is being prepared or needs user reapproval. Do not implement the proposed repository changes.
- **In Progress:** The Plan is approved and implementation has started. Create the matching work Log immediately and keep it current.
- **Completed:** Every approved change and validation step is finished, the work Log is complete, and no unresolved failure blocks completion.

If implementation reveals a material scope or approach change, return the Plan to Draft, record the interruption in the existing Log, stop implementation, and request reapproval. After reapproval, continue with the same Plan number and Log file.

## Execution and Completion

- Execute the Steps in the approved Plan. Update the Plan before proceeding when its scope, steps, or validation requirements materially change.
- Keep the Plan, Log, actual changes, and validation results consistent.
- For changes to Python code, tests, dependencies, generated code, or configuration that affects runtime behavior, run `python -m pytest` after implementation.
- If a required test fails, diagnose and fix it, record the meaningful failure in the Log, and run the test again. Do not mark the task Completed while a required test is failing.
- Documentation-only or behavior-neutral comment changes do not require `pytest`; validate their Markdown structure, references, and changed content instead.
- Complete the Log first. Mark the Plan Completed only after all required validation succeeds and the Log is Completed.
