---
name: add-accounts
description: Use when users must sign up, sign in or out, reset a password, see only their own data, or have different roles (customer, admin), or when someone can see or change data they should not.
---

# Accounts and permissions (optional capability)

Only when `docs/product.md` says accounts or per-user data are needed. If it does not, ask whether the scope is
changing, and update `docs/product.md` first.

## Inputs

- `docs/product.md` (capabilities), `docs/architecture.md` (stack, data model), `docs/acceptance.md`.
- The framework's official authentication documentation for the version in use.

## Actions

1. **Write the permission rules first** in `docs/architecture.md` ("Security and privacy"): the roles, and for each
   kind of record who can create, read, change and delete it. Add one row per rule to the "Permissions" table of
   `docs/acceptance.md`, including at least: signed-out visitor, user A on user B's data, normal user on admin pages.
2. **Use the framework's built-in or a well-known authentication system.** Never write your own password hashing,
   session or token code. Path B (Django): built-in `django.contrib.auth`, login-required views, per-object checks.
   Other stacks: the framework's documented library, or a hosted identity provider if the student agrees to it.
   Path A dashboards: prefer a single shared deployment password or the hosting platform's access control; real
   per-user accounts usually mean moving to path B (discuss before building).
3. **Enforce permissions on the server**, in every view or endpoint that reads or changes data: filter queries by
   the signed-in user, check ownership before updates and deletes, return "not found" or "forbidden" without
   revealing other users' data. Hiding a button is not a permission check.
4. **Protect the basics:** a secret key from settings, never in code (a development-only key is refused unless
   debug is on and the host is local); passwords hashed by the framework; session cookies secure in production; CSRF protection
   on forms (on by default in Django); no passwords, tokens or personal data in logs, URLs or error messages; a
   password-reset flow only if email is configured (otherwise list it as excluded).
5. **Tests** (`test-and-check`) for every row of the permissions table: create two users in the test, sign in as one,
   try the other's pages and records, and assert the refusal. Test sign-in failure and sign-out.

## Outputs

Sign-up, sign-in, sign-out (and reset if in scope), permission checks in code, the permission rules in
`docs/architecture.md`, permission tests, a change report listing every protected page or endpoint.

## Verification

- Every permissions row has a test, and the tests pass.
- In the running app: sign up two users, confirm each sees only their own data, confirm a signed-out visitor is
  redirected. Report what was checked by hand and what only by tests.
- The security reviewer (`review-changes`) has looked at the change before it is called finished.

## Stop when

- All permission tests pass and the manual two-user check was done (or explicitly left to the student).
- **Stop and ask** if the product would store sensitive personal data (identity documents, health, bank details), if
  a hosted identity provider would cost money, or if the requirement is "admin can see everything" without a
  stated reason.

## Common mistakes

- Checking permissions only in templates or the interface.
- Using the user id from a form or URL instead of the signed-in user.
- Real customer accounts during development: use test users.
