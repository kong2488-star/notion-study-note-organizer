# Work Logging Rules

## Purpose

A work Log is a concise, reproducible record of how an approved Plan was implemented and validated. It is not an application request log, a user activity audit log, a transcript, or a record of an agent's private reasoning.

Keep only evidence that helps another contributor understand decisions, reproduce important steps, and audit completion.

## Creation and Naming

- Every repository-changing task requires a work Log, including documentation-only and behavior-neutral comment changes.
- A read-only task that does not require a Plan does not require a work Log.
- When an approved Plan becomes In Progress, create the Log immediately from `logs/TEMPLATE.md`.
- Use the same three-digit index and English kebab-case slug as the Plan: `plan/001-project-setup.md` corresponds to `logs/001-project-setup.md`.
- Use exactly one Log for each Plan. Keep completed Logs in `logs/`; do not move, delete, or replace them.

## Incremental Updates

Do not reconstruct the Log from memory at the end of the task. Update it promptly after:

- a decision that affects implementation direction;
- an important implementation detail selected within the approved scope;
- a meaningful code, configuration, test, documentation, or generated-file change;
- a test failure, repeated error, implementation change, or environment constraint;
- a lint, type check, build, test, or meaningful manual validation.

Before completion, reconcile the summary, changed files, validation results, and unresolved issues with the actual state of the work.

## Required Content

Every Log keeps these sections, even when the value is `None`:

- Plan number and path, Log status, start date, and completion date;
- work summary;
- key decisions and rationale;
- changed files;
- meaningful commands and concise result summaries;
- meaningful failures, causes, and resolutions;
- validation results;
- unresolved issues and follow-up work.

Record decisions and outcomes, not extended deliberation. For commands, retain only work that matters for reproduction, diagnosis, or validation, such as dependency installation, code generation, migrations, linting, type checking, builds, tests, and key error reproduction. Include the command, exit status, and essential result instead of copying full output. Omit routine file reads, repeated searches, directory listings, and trivial successful commands.

Record failures that affect reproducibility or future work, including test or build failures, repeated errors, direction-changing problems, environment constraints, and unresolved completion blockers. Trivial mistakes corrected immediately may be omitted.

## Security and Data Minimization

Never copy the following into a work Log:

- API keys, tokens, cookies, passwords, authentication headers, or actual environment-variable values;
- personal information or raw user input;
- request and response bodies or full database contents;
- private agent reasoning, full conversations, full terminal output, or full file contents.

When context is necessary, summarize it and replace any sensitive value with `[REDACTED]`.

## Status and Completion

Log status follows `In Progress` → `Completed`.

- Set the status to In Progress and record the start date when the Log is created.
- If the Plan returns to Draft for reapproval, record why work stopped and pause implementation entries. Continue in the same Log after reapproval.
- When implementation and validation finish, finalize all required sections, set the status to Completed, and record the completion date.
- A Plan cannot become Completed until its Log is complete. The Plan, Log, changed files, and validation evidence must agree.

Application HTTP logs, runtime monitoring, file rotation, retention, and external log collection are separate concerns and require their own requirements and Plan.
