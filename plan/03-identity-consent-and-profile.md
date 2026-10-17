# Step 3: Add identity, consent, and user profiles

## Goal

Provide a secure, privacy-conscious account and profile foundation before introducing personalization or health-related inputs.

## Prerequisite

Complete [Step 2](./02-platform-foundation.md). Follow its architecture, data model, and security conventions.

## Agent instructions

Implement the smallest complete identity and profile flow supported by the project's chosen stack. Select established authentication mechanisms or providers rather than inventing password/security primitives. Make consent specific, understandable, revocable, and separate from account creation where applicable. Do not collect biomarker readings in this step.

## Scope

- Implement registration, sign-in, sign-out, and session handling, including safe error and expired-session states.
- Add a consumer profile with only necessary fields. Clearly distinguish optional preferences from sensitive health information.
- Add an explicit privacy/consent record with purpose, status, and timestamp; allow users to view and withdraw applicable consent.
- Enforce server-side authorization for profile access and changes; users must not be able to access another user's data by changing an identifier.
- Provide account deletion or a clearly implemented deletion-request flow consistent with the chosen storage model.
- Add tests for authentication, consent state, access control, and invalid input; document configuration and data-handling limitations.

## Safety and privacy

- Minimize collection and retention. Do not log credentials, tokens, or sensitive profile values.
- Do not treat consent to basic service operation as consent to research or marketing.
- Avoid making claims of legal or regulatory compliance without an implemented basis and qualified review.

## Acceptance criteria

- User identity and profile access are protected server-side, with tests for cross-user access denial.
- Consent state is explicit, inspectable, changeable, and cannot be silently inferred.
- No biomarker or clinical data is collected yet.
- Existing public-site and foundation tests continue to pass.
- The agent reports security-relevant choices, verification, changed files, and known limitations.

## Handoff

Finish before [Step 4](./04-nutrition-data-catalog.md), which will introduce the food and nutrient data used by recommendations.
