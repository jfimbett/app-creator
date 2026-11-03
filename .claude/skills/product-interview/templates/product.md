# Product: <name>

Status: draft | agreed on <YYYY-MM-DD>

## Problem and customers

- **Customer:** <who exactly; one sentence>
- **Problem today:** <what they do now and what it costs them: time, errors, money>
- **Success looks like:** <an observable result, e.g. "a weekly peer comparison in 2 minutes instead of 2 hours">

## Main user journey

1. <the user opens ... and sees ...>
2. <they enter / choose / upload ...>
3. <the app shows / computes / exports ...>
4. <they take away ...>

## Screens and visuals

Look: <a table of figures | a dashboard with summary cards and charts | forms and lists>. Used on a phone: <yes / no>.
Theme: <dark default, light secondary | light only | follows the system>. Density: <compact | comfortable>.
Visual references: <a site or app the owner likes, and what they like about it; or "none">.

| Screen | Purpose | The user sees first | Cards / charts / tables (unit, period) | The user can | States |
|---|---|---|---|---|---|
| | | | <e.g. card "Weekly distance, km, week 12, change vs week 11"; bars "Distance by week, km"> | <search, choose an item, switch period> | <loading / empty / error / offline / missing-data text> |

Agreed visuals (each one: the question it answers, chart type, series, how gaps and negatives are shown):
<list, or "table only, by the owner's choice">

## MVP features (must have)

| Id | Feature (what the user can do) | Why the customer needs it | Criteria |
|---|---|---|---|
| F1 | | | AC1 |
| F2 | | | |
| F3 | | | |

## Explicitly not in the MVP

- <feature or idea we will not build now, and why>

## Data and calculations

| Data | Source | Freshness | Offline demo data (fixtures) | Licence / terms checked? |
|---|---|---|---|---|
| | | | <recorded sample, its date and source / none> | [to confirm] |

| Number the app shows | Formula | Units | Source of inputs | Known-answer example |
|---|---|---|---|---|
| | | | | CALC1 |

## Capabilities

| Capability | Needed? | Notes |
|---|---|---|
| Accounts / sign-in | no | |
| Per-user saved data | no | |
| File uploads | no | |
| Payments | no | |
| Background jobs / scheduled refresh | no | |
| Works offline (`npm run demo`) | yes | recorded sample data, clearly labelled |
| Must be online for others | no | demo on a laptop is enough |

## Team and constraints

- Mode: <interactive | delegated by `<brief>` §n; decisions in `<decisions file>`>
- Experience: <e.g. first app for all members>
- Time available: <hours until the deadline>
- Budget: <per month; 0 is fine>
- Rules to respect: <course rules, data terms, client constraints>
