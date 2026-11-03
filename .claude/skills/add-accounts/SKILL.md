---
name: add-accounts
description: Use when users must sign up, sign in or out, reset a password, see only their own data, or have different roles (user, admin), or when someone can see or change data they should not. Off by default; only if product.md needs it.
---

# Accounts and permissions (optional capability, off by default)

Only when `<docs>/product.md` says accounts or per-user data are needed. If it does not, ask whether the scope is
changing, and update `<docs>/product.md` first. In delegated mode (`docs/TOOLKIT.md` §4) adding accounts is new
scope and personal data: it is never a routine decision.

Paths: `<backend>`, `<frontend>`, `<docs>` come from `app-creator.config.json` (`app.backendDir`,
`app.frontendDir`, `app.docsDir`). Patterns and code for FastAPI + Next.js: [authn-authz.md](authn-authz.md).

## Inputs

- `<docs>/product.md` (capabilities), `<docs>/architecture.md` (stack, data model), `<docs>/acceptance.md`.
- The official documentation of the libraries chosen (FastAPI security, the password-hashing library, or a
  hosted identity provider) for the versions in use.

## Actions

1. **Write the permission rules first** in `<docs>/architecture.md` ("Security and privacy"): the roles, and for
   each kind of record who can create, read, change and delete it. Add one row per rule to the "Permissions" table
   of `<docs>/acceptance.md`, including at least: signed-out visitor, user A on user B's data, normal user on
   admin pages.
2. **Choose the mechanism** (guide, "Sessions or tokens"). Default for this stack: server-side sessions in an
   `HttpOnly` cookie, set by FastAPI and sent automatically through the same-origin `/api/*` rewrite. Never write
   your own password hashing or crypto: use a maintained library (Argon2 or bcrypt) or a hosted identity provider
   if the owner agrees (cost, personal data). For a demo that only needs to keep strangers out, a single shared
   password or the host's access control may be enough: discuss before building real accounts.
3. **Enforce permissions on the server**, in every endpoint that reads or changes data: a FastAPI dependency gives
   the signed-in user; queries filter by that user; ownership is checked before updates and deletes; other users'
   records answer 404 (do not reveal they exist). Hiding a button or a Next.js page guard is not a permission check.
4. **Protect the basics:** session secret from settings, never in code (a development-only value is refused
   unless debug is on and the host is local); cookies `HttpOnly`, `SameSite=Lax`, `Secure` outside local
   development; CSRF protection for state-changing requests (guide); a rate limit or delay on sign-in; no
   passwords, tokens or personal data in logs, URLs or error messages; the same message for "unknown user" and
   "wrong password"; a password-reset flow only if email is configured (otherwise list it as excluded).
5. **Frontend:** sign-in and sign-up forms (`design-interface`: labels, errors, loading); a `GET /api/me` call to
   know who is signed in; handle 401 by sending the user to sign-in. The frontend never stores tokens in
   `localStorage`.
6. **Tests** (`test-and-check`) for every row of the permissions table: create two users in the test, sign in as
   one, try the other's records and the admin endpoints, and assert the refusal. Test sign-in failure, sign-out
   (the old session no longer works), and a state-changing request without the CSRF check. One Playwright journey
   signs in a test user created by the test, never a real account.

## Outputs

Sign-up, sign-in, sign-out (and reset if in scope), the user dependency and permission checks in code, the rules in
`<docs>/architecture.md`, permission tests, a change report listing every protected endpoint and page.

## Verification

- Every permissions row has a test, and `npm run verify` passes.
- In the running app (`npm run dev`): sign up two test users, confirm each sees only their own data, confirm a
  signed-out visitor is sent to sign-in. Report what was checked by hand and what only by tests.
- The security reviewer (`review-changes`) has looked at the change before it is called finished.

## Stop when

- All permission tests pass and the manual two-user check was done (or explicitly left to the person).
- **Stop and ask** if the product would store sensitive personal data (identity documents, health, bank details),
  if a hosted identity provider would cost money, or if the requirement is "admin can see everything" without a
  stated reason.

## Common mistakes

- Checking permissions only in the Next.js page or by hiding links.
- Using the user id from the request body or URL instead of the signed-in user.
- A JWT in `localStorage` (readable by any injected script) "because it is easier".
- Real accounts or real email addresses during development: use test users created by the tests.
- An endpoint added later without the user dependency (list every route in the change report and check).

## Example

Product: "each user keeps a private list of notes; an admin can see how many users exist". Rules: visitor →
nothing but sign-in/sign-up; user → create/read/change/delete own notes; admin → `GET /api/admin/stats` only (not
other users' notes). Tests: `test_visitor_gets_401_on_notes`, `test_user_a_gets_404_on_user_b_note`,
`test_user_cannot_open_admin_stats`, `test_admin_stats_does_not_include_note_text`,
`test_post_without_matching_origin_is_refused`, `test_signed_out_session_is_rejected`.
