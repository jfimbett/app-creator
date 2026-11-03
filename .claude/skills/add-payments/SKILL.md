---
name: add-payments
description: Use when the application must charge customers, sell subscriptions or credits, show a checkout, unlock paid features, or handle payment confirmations, refunds or failed payments.
---

# Payments (optional capability, test mode)

Only when `docs/product.md` says someone pays. Payments need accounts (`add-accounts`) so the app knows who paid.
During a course project, **use the provider's test mode only**: no live keys, no real cards, no real money.

## Inputs

- `docs/product.md` (what is sold, price, one-off or subscription), `docs/architecture.md`, `docs/acceptance.md`.
- The payment provider's **official documentation** for hosted checkout, webhooks and test mode. Read it before
  writing code; if it cannot be read, stop.
- The student's explicit agreement on the provider (they create the account; never create it for them).

## Actions

1. **Design the flow** in `docs/architecture.md`: what is bought, price and currency, what the customer gets after
   paying (a flag, credits, a subscription status), and what happens on failure, cancellation and refund. Add
   acceptance criteria for: successful payment, cancelled checkout, failed payment, a user without payment trying a
   paid feature, and a repeated confirmation.
2. **Use the provider's hosted checkout page.** The app never receives, stores or logs card numbers. The server
   creates the checkout session with the price defined on the server (never trust a price sent by the browser).
3. **Grant access only from a verified confirmation:** a webhook endpoint that verifies the provider's signature with
   the webhook secret, then records the payment against the user. The "success" page the browser returns to is not
   proof of payment. Handle the same event arriving twice without granting twice.
4. **Settings:** test keys and the webhook secret as setting names in `app/.env.example`; values only in
   `app/.env`. The code refuses to start with a live key while `APP_ENV` (or the stack's equivalent) is not
   production, and the course project never sets production payments.
5. **Paid features check payment status on the server**, like any permission (`add-accounts`).
6. **Tests** (`test-and-check`): unit tests for granting access from a verified event, rejecting a bad signature,
   ignoring duplicates, and blocking unpaid users; use recorded or synthetic test events labelled as such.

## Outputs

Checkout, webhook handler with signature verification, payment records, paid-feature checks, tests, updated
documents, a change report that lists every test-mode scenario checked.

## Verification

- Tests pass for success, bad signature, duplicate and unpaid cases.
- With the student's test keys, the student completes a test-mode checkout with the provider's documented test card
  and the paid feature unlocks; a cancelled checkout leaves it locked. If the webhook cannot reach the laptop, use
  the provider's documented local forwarding tool or state the gap.
- The security reviewer has reviewed the change.

## Stop when

- All payment scenarios pass in test mode.
- **Stop and ask** before anything involving live keys, real money, storing card data, tax or invoicing rules, or
  refunds that move real funds. These are outside a course MVP unless the instructor approves them.

## Common mistakes

- Unlocking features on the success redirect instead of the verified webhook.
- Price or product id taken from the browser.
- Test and live keys mixed in one `.env`.
