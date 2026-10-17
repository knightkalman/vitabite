# Step 2: Establish the application foundation

## Goal

Turn the website codebase into a maintainable product foundation that can support the VitaBite consumer and business experiences without disrupting the public website.

## Prerequisite

Complete [Step 1](./01-project-website.md). Inspect its implementation and keep its stack, design conventions, and working website unless there is a concrete compatibility issue.

## Agent instructions

Inspect the current repository, existing tests, and available runtime before changing architecture. Implement only the shared foundation needed by the subsequent steps; avoid speculative services or unnecessary infrastructure. Do not create unprotected health-data features in this step.

## Scope

- Establish a clear separation between the public site and product application routes/layouts.
- Set up the repository's standard development, test, lint, and production-build workflows where missing and appropriate to its existing stack.
- Define the initial application domain boundaries and persistence approach for users, consumer profiles, organizations, and products. Prefer explicit migrations/schema definitions over undocumented database assumptions.
- Add environment configuration examples without secrets, and fail clearly when required configuration is missing.
- Add a small, useful automated test baseline and document local setup in the existing project documentation.
- Keep future authentication and authorization extension points explicit; do not claim secure authentication until it is implemented and tested.

## Acceptance criteria

- The public website still builds and behaves as before.
- The application has a clear route/layout boundary and a tested foundation for future product work.
- Setup, test, lint, and build commands are discoverable and work in the available environment.
- No credentials, real user health information, or production-only assumptions are introduced.
- The agent reports architectural choices, changed files, verification, and any limitations.

## Handoff

Finish before [Step 3](./03-identity-consent-and-profile.md). Step 3 must use the selected persistence and application conventions.
