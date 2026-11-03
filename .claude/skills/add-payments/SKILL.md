---
name: add-payments
description: Use when the app must charge customers, sell subscriptions or credits, show a checkout, unlock paid features, or handle payment confirmations, webhooks, refunds or failed payments. Test mode only; off by default.
---

# Payments (optional capability, test mode only)

Only when `<docs>/product.md` says someone pays. Payments need accounts (`add-accounts`) so the app knows who
paid. During a course or demo project, **use the provider's test mode only**: no live keys, no real cards, no real
money. Payments involve money: in delegated mode (`docs/TOOLKIT.md` §4) they are never a routine decision.

Paths: `<backend>`, `<frontend>`, `<docs>` come from `app-creator.config.json`. Settings names go in the root
`.env.example`.

## Inputs

- `<docs>/product.md` (what is sold, price, one-off or subscription), `<docs>/architecture.md`,
  `<docs>/acceptance.md`.
- The payment provider's **official documentation** for hosted checkout, webhooks, signature verification and test
  mode, and its official Python library if it has one. Read it before writing code; if it cannot be read, stop.
- The owner's explicit agreement on the provider (they create the account; never create it for them).

## Actions

1. **Design the flow** in `<docs>/architecture.md`: what is bought, price and currency (integer minor units), what
   the customer gets after paying (a flag, credits, a subscription status), and what happens on failure,
   cancellation and refund. Add acceptance criteria for: successful payment, cancelled checkout, failed payment,
   a user without payment trying a paid feature, and a repeated confirmation.
2. **Use the provider's hosted checkout page.** The app never receives, stores or logs card numbers. A FastAPI
   endpoint (`POST /api/checkout`, signed-in users only) creates the checkout session with the price defined on
   the server (a price id or amount from settings or the database, never from the browser) and returns the
   provider's URL; the Next.js page redirects to it.
3. **Grant access only from a verified confirmation:** a webhook endpoint (`POST /api/payments/webhook`) reads the
   **raw** request body (`await request.body()`, before any JSON parsing), verifies the provider's signature with
   the webhook secret using the provider's library, then records the payment against the user. The "success"
   page the browser returns to is not proof of payment. Store each event id with a unique constraint so the same
   event arriving twice grants once. The webhook is excluded from the CSRF origin check (`add-accounts`) because
   its signature is the check; it is the only such route.
4. **Settings:** test keys and the webhook secret as setting names in `.env.example` (placeholders only); values
   only in the person's `.env`. The backend refuses to start with a live key (by its documented prefix) unless an
   explicit production setting is on, and course projects never turn it on. The publishable key, if the frontend
   needs one, is the only payment value allowed in `NEXT_PUBLIC_*`.
5. **Paid features check payment status on the server**, like any permission (`add-accounts`): a dependency such
   as `require_paid(user)` on each paid endpoint.
6. **Tests** (`test-and-check`): granting access from a verified event, rejecting a bad or missing signature (400),
   ignoring a duplicate event id, blocking unpaid users (402 or 403), and a price sent by the browser being ignored.
   Use recorded test-mode events (secrets removed) or synthetic events labelled as such, signed in the test with a
   throw-away test secret. Mock the provider's API with `respx` when the server calls it.

## Outputs

Checkout endpoint and page, webhook handler with signature verification, payment records with unique event ids,
paid-feature checks, tests, updated documents, a change report that lists every test-mode scenario checked.

## Verification

- `npm run verify` passes, including success, bad signature, duplicate and unpaid cases.
- With the owner's test keys, the owner completes a test-mode checkout with the provider's documented test card
  and the paid feature unlocks; a cancelled checkout leaves it locked. If the webhook cannot reach the laptop, use
  the provider's documented local forwarding tool or state the gap.
- The security reviewer has reviewed the change (`review-changes`).

## Stop when

- All payment scenarios pass in test mode.
- **Stop and ask** before anything involving live keys, real money, storing card data, tax or invoicing rules, or
  refunds that move real funds. These are outside a course MVP unless the instructor approves them.

## Common mistakes

- Unlocking features on the success redirect instead of the verified webhook.
- Parsing the webhook body as JSON before verifying the signature (the signature covers the raw bytes).
- Price or product id taken from the browser.
- Test and live keys mixed in one `.env`; a secret key in a `NEXT_PUBLIC_` variable.
- Logging the whole webhook event (it can contain customer names and addresses).

## Example

"Unlock the export feature for a one-off payment of 5.00 EUR." Settings: `PAYMENT_SECRET_KEY`,
`PAYMENT_WEBHOOK_SECRET`, `EXPORT_PRICE_ID` (placeholders). `POST /api/checkout` → provider session for
`EXPORT_PRICE_ID`, `client_reference_id` = the signed-in user's id, return URL `/export?checkout=done`. Webhook
verifies the signature, then on the "checkout completed" event inserts `payments(event_id UNIQUE, user_id,
amount_minor=500, currency='EUR')` and sets `users.export_unlocked = 1`. The export page shows "Waiting for
confirmation…" until `GET /api/me` says unlocked. Tests: signed event unlocks; same event twice → one payment
row; wrong signature → 400 and nothing changes; unpaid user → 403 on `GET /api/export`.
