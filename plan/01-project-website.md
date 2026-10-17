# Step 1: Build the VitaBite project website

## Goal

Create a polished, responsive public website that explains VitaBite AI to consumers, restaurants, food brands, and potential partners. This is the first implementation step and the product's public-facing foundation.

## Context

VitaBite AI combines longevity research, nutrition, food, and AI to help people make informed food choices. Its vision is: “Every meal becomes a step toward a longer, healthier life.” The initial market is Vienna, with Germany, Switzerland, and the Nordics as later expansion markets.

The concept includes personalized meal plans and habit support for consumers; menu planning and ingredient alternatives for restaurants; and formulation tools for food brands. The long-term concept includes biomarker-informed personalization, but the website must not imply that the product diagnoses, treats, or prevents disease, or guarantee biological-age changes.

## Agent instructions

Inspect the repository and the project brief at `docu/vitabite_prezi.pdf` before implementation. Build on any existing stack and conventions; if the repository has no application yet, choose a simple, maintainable web stack appropriate to the available environment and document any consequential choice in the implementation summary. Do not alter or remove the project brief.

Implement the website, not just a design proposal. Keep the scope to the public-facing website; do not build account flows, collect personal or health data, or represent unbuilt features as already available.

## Website content

- A distinctive, memorable landing page with clear VitaBite AI branding and the vision statement.
- A concise explanation of the nutrition and longevity problem, and VitaBite's proposed approach.
- Separate, understandable descriptions of the consumer, restaurant, and food-brand use cases.
- The Vienna-first launch focus and the intended expansion direction.
- A roadmap summary that distinguishes planned work from currently available functionality.
- A contact or interest call to action. If there is no working submission endpoint, use a clearly labeled email/contact link or non-submitting placeholder rather than pretending a request was sent.
- A brief, visible note that the concept is informational and is not medical advice.

## Quality requirements

- Responsive and accessible layout, semantic structure, keyboard-operable links, and legible color contrast.
- Professional visual design suited to a science-informed food and wellness startup; use real project copy rather than generic filler or fabricated testimonials.
- Do not claim clinical validation, proven outcomes, partnerships, or capabilities that have not been established.
- Preserve existing repository behavior and conventions.

## Acceptance criteria

- The site can be run using the repository's documented development command.
- The primary page renders all required content and adapts to mobile and desktop layouts.
- Links and calls to action behave honestly; there are no broken or fake submission flows.
- Relevant lint, build, and tests pass, or any pre-existing/environment blocker is reported precisely.
- The agent reports changed files, how to run the site, verification performed, and any remaining limitations.

## Handoff

Complete this step before starting [Step 2](./02-platform-foundation.md). Keep the website working as later steps add the product application.
