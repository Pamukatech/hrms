# Payroll System — HRMS Clone

A working replica of [mypayrollmanage.com](https://www.mypayrollmanage.com/) — a Kenyan
payroll & HR management web app — rebuilt with a Python stack because the original
runs on PHP/Laravel. The design system, page structure and payroll behaviour mirror the
original as closely as possible.

![stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![stack](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)
![stack](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=flat&logo=tailwindcss&logoColor=white)

---

## Features

| Module | What it does |
| --- | --- |
| **Auth** | Register a company + admin user, login, logout, forgot / reset password, CSRF-protected forms |
| **Logins** | The company administrator sets each employee's password — the account is active on the spot, so people just sign in (no activation link) |
| **Dashboard** | KPI cards (headcount, gross, net, PAYE, salary advances, pending leave) + recent runs & leave |
| **Employees** | Full CRUD, search & filters, recurring allowances/deductions, salary-increment history, salary advances, payroll history and private document uploads (contracts, passport/ID, certificates) |
| **Payroll runs** | Create a run for any month, editable spreadsheet-style grid with **live statutory recalculation**, approve & lock |
| **Payslips** | Per-employee printable payslip (Print / Save as PDF) |
| **Salary Advances** | Full-balance recovery from the first payroll in which the advance is due, with balances and automatic repayments posted on payroll approval; fully recovered advances are marked **Paid**. Payroll approval also captures salary increments entered after a draft run was created. Legacy loans are preserved as history and are not deducted twice |
| **Leave** | Leave types, requests, approve / reject, per-employee balances |
| **Offboarding** | Resignation / termination workflow with a printable final settlement statement and a one-click reinstate |
| **Reports** | Per-run statutory summary (gross, taxable, NSSF, SHIF, AHL, PAYE, net), salary advances, leave and a leavers report — all with CSV export |
| **Settings** | Company profile and all statutory parameters (editable) |
| **Admin panel** | Platform-owner console: connected accounts, on/off switch, payment states and site-wide settings |

Currency is **KES**. All statutory rates are Kenyan defaults and fully configurable in Settings.

---

## Tech stack

Deliberately close to the original's *look* while using what's installable here:

- **Backend:** FastAPI + SQLAlchemy 2 + SQLite (or MySQL/MariaDB)
- **Templates:** Jinja2 (server-rendered, Laravel-Blade-style layouts)
- **Styling:** Tailwind CSS **v4.3.3** — the exact version the original site ships — compiled to a static stylesheet
- **Interactivity:** Alpine.js 3.16.1 (vendored locally) + a small `app.js` port of the original payroll-grid logic
- **Auth:** Starlette signed session cookies, PBKDF2-HMAC-SHA256 password hashing (stdlib), `_token` CSRF fields mimicking Laravel
- **Font:** Inter

No PHP, Composer, Node or npm is required to run it — everything is vendored or pure Python.

---

## Quick start

```powershell
# From the project root (C:\HRMS Clone)
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

Then open **http://127.0.0.1:8000**

**Demo login:** `admin@demo.co.ke` / `password`

`run.ps1` creates the virtualenv and installs dependencies if needed, seeds demo data on
first run, and starts the dev server with auto-reload.

### Manual start

```powershell
.\.venv\Scripts\python.exe -m app.seed                 # create + populate hrms.db (once)
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

To reset the demo data, delete `hrms.db` and run the seed command again.

---

## Payroll engine

Implemented in `app/payroll.py` as pure functions. Default rates (all editable in **Settings**):

**Gross**

```
gross = basic_pay + allowances
```

**NSSF** (Tier I + Tier II, 6% each)

```
tier1 = min(gross, 8,000) * 6%
tier2 = max(0, min(gross, 72,000) - 8,000) * 6%
```

**SHIF** — 2.75% of gross, minimum KES 300

**AHL** (Affordable Housing Levy) — 1.5% of gross

**PAYE**

```
taxable = gross − NSSF − pension − AHL
tax     = banded(taxable) − personal_relief (2,400)
```

Monthly bands: `0–24,000 @ 10%` · `24,001–32,333 @ 25%` · `32,334–500,000 @ 30%` ·
`500,001–800,000 @ 32.5%` · `above 800,000 @ 35%`

**Net**

```
total_deductions = NSSF + SHIF + AHL + PAYE + pension + advances + loans + other
net_pay          = gross − total_deductions
```

The payroll grid recalculates every one of these live as you type, via
`PUT /api/payroll-runs/{run}/entries/{entry}` (the same endpoint shape as the original).

---

## Routes

| Method | Path | Page |
| --- | --- | --- |
| GET/POST | `/register`, `/login`, `/forgot-password`, `/reset-password/{token}` | Auth |
| POST | `/logout` | Sign out |
| GET | `/dashboard` | Dashboard |
| GET/POST | `/employees`, `/employees/new`, `/employees/{id}`, `/employees/{id}/edit` | Employees |
| POST | `/employees/{id}/delete`, `/allowances`, `/deductions` | Employee actions |
| POST/GET | `/employees/{id}/documents`, `/employees/{id}/documents/{document_id}` | Upload/download private employee documents |
| POST | `/employees/{id}/documents/{document_id}/delete` | Delete an employee document |
| POST | `/employees/{id}/set-password` | Issue a new login password for an employee (`intent=email` also emails it) |
| POST | `/employees/{id}/resend-invitation` | Replace the password and email the login details |
| GET/POST | `/team`, `/team/{id}/password`, `/team/{id}/resend`, `/team/{id}/role`, `/team/{id}/toggle` | Staff accounts |
| GET/POST | `/payroll-runs`, `/payroll-runs/create`, `/payroll-runs/{id}` | Payroll |
| POST | `/payroll-runs/{id}/approve`, `/payroll-runs/{id}/delete` | Payroll actions |
| **PUT** | `/api/payroll-runs/{run}/entries/{entry}` | Live recalculation API |
| GET | `/payslips`, `/payslips/{entry_id}` | Payslips |
| GET/POST | `/advances`, `/advances/new`, `/advances/{id}`, `/advances/{id}/approve` | Salary advances (`/loans` redirects here) |
| GET/POST | `/leave`, `/leave/new`, `/leave/{id}/approve`, `/leave/{id}/reject` | Leave |
| GET | `/reports`, `/reports/export/{run_id}` | Reports + CSV |
| GET | `/reports/advances`, `/reports/leave`, `/reports/leavers` | Advances, leave and leavers reports (CSV at `…/export`) |
| GET/POST | `/employees/{id}/offboard`, `/employees/{id}/rehire` | Offboarding / reinstate (settlement at `/employees/{id}/settlement`) |
| GET/POST | `/settings` | Settings |
| GET/POST | `/settings/payments` | Platform payment gateway credentials (platform admins only) |
| GET | **`/admin`** | Platform admin panel — dashboard of every connected account |
| GET | `/admin/accounts` | Connected accounts (search + status filters) |
| GET | `/admin/accounts/{id}` | One account: members, payments, audit trail |
| POST | `/admin/accounts/{id}/toggle` | Switch an account **off / on** |
| POST | `/admin/accounts/{id}/subscription` | Set plan, payment state, extend period, mark paid |
| POST | `/admin/accounts/{id}/users/{uid}/toggle` | Activate / deactivate a single user |
| GET | `/admin/payments` | All payments (filter by state, search) |
| POST | `/admin/payments/{id}/status` | Record a payment that arrived off-gateway |
| GET/POST | `/admin/site` | Site-wide settings |
| GET | `/admin/audit` | Platform-wide audit log |
| GET | `/health` | Liveness probe |
| GET | `/favicon.ico`, `/apple-touch-icon.png`, `/site.webmanifest` | App icon (favicon / installable app) |
| GET | `/robots.txt`, `/sitemap.xml` | Search engine crawling hints |

---

## Employee & staff logins (the administrator sets the password)

Nobody has to activate anything. The **company administrator** decides the
password for every account they create, and the account is active on the spot:

| Where | What happens |
| --- | --- |
| **Employees → New** | *Portal Login* card: type a password (or press **Generate**) and save. The employee's self-service login is created **active** with that password and the employee signs in with it — there is no activation link and no password for them to choose. |
| **Employee → Portal Login** | Shows the password that was just issued (with a **Copy** button) for 15 minutes. **Issue new password** replaces it; **Issue & email details** also mails it. |
| **Team → Add a Team Member** | Same deal for staff accounts (HR, payroll, managers, admins). The account is active immediately. |
| **Team → Login** | Per-member *Set new password*, and the newly issued password is shown for 15 minutes. |

Details worth knowing:

- **Leave the password field blank and the server generates one** — 12 characters
  with a mix of cases, digits and symbols, and no characters that look alike
  (`0`/`O`, `1`/`l`/`I`) so it can be read out over the phone.
- **Only the hash is stored.** The plaintext is kept in memory
  (`app/credentials.py`) for 15 minutes so the administrator can copy it, and
  is then gone for good — issue a new password if it is lost.
- **The password can be mailed** to the employee as part of the login details
  (see *Mail delivery* below).
- **The employee can change it themselves** afterwards under *Account settings*.
- **Older accounts still work.** `/activate/{token}` is still live for anyone
  holding an activation link from before, and *Send login details* replaces the
  old "resend invitation" button: it issues a fresh password, activates the
  account and emails the details.

The one-line summary: **the company admin creates the password, the employee
just logs in.**

---

## Platform admin panel

Everything an operator needs to run the installation lives under **`/admin`**.
It is restricted to the `platform_admin` role, which is **not** granted by
registration — you promote an existing account explicitly.

### Granting access

```powershell
# Promote an account that already exists
.\.venv\Scripts\python.exe -m tools.make_admin admin@demo.co.ke

# Create the account first if it does not exist yet
.\.venv\Scripts\python.exe -m tools.make_admin owner@example.com --create --name "Site Owner"

# Take the role away again
.\.venv\Scripts\python.exe -m tools.make_admin owner@example.com --demote
```

Platform administrators bypass the maintenance, suspension and subscription
checks, so they can always reach the panel to fix things.

### Restricting the panel to one address

The role decides who *may* be a platform administrator; `PLATFORM_ADMIN_EMAILS`
decides who actually *is* one. Set it in `.env` to a comma-separated list of
addresses and the panel is pinned to them:

```ini
PLATFORM_ADMIN_EMAILS=owner@example.com
```

Every other account is refused at `/admin` (403) and the **Admin panel** link
is hidden from its sidebar, even if its role was changed to `platform_admin`
by mistake. Leave the variable empty to allow every account that holds the
role.

To hand the panel to a different address in one step — moving the account into
the right company, granting the role, activating it, demoting everybody else
and switching the company back on:

```powershell
.\.venv\Scripts\python.exe -m tools.setup_platform_admin --email owner@example.com `
    --company-email owner@example.com --name "Site Owner" --password "s3cret"
```

### Deleting an account

`tools/purge_account.py` removes a company and everything under it (users,
branches, employees, payroll runs, loans, advances, leave, subscription,
payments, notifications and the audit trail). It prints what it is about to
remove and asks before deleting anything:

```powershell
.\.venv\Scripts\python.exe -m tools.purge_account --email info@company.co.ke
.\.venv\Scripts\python.exe -m tools.purge_account --id 2 --yes
```

### What it does

| Screen | `/admin` path | Purpose |
| --- | --- | --- |
| **Dashboard** | `/admin` | Connected accounts, active / on-trial / switched-off counts, MRR, outstanding payments, employee total, recent platform activity |
| **Connected accounts** | `/admin/accounts` | Every company on the platform with a search box and status chips (Active, On trial, Payment due, Expired, Switched off) |
| **One account** | `/admin/accounts/{id}` | Members, employee count, payment history, per-account audit trail — and the controls below |
| **Payments** | `/admin/payments` | Every invoice, filterable by state; record money that arrived outside the gateway (bank transfer, cheque) |
| **Site settings** | `/admin/site` | Site name, tagline, SEO description, footer note, support contacts, announcement banner, maintenance mode, registration lock, trial length, plan prices |
| **Audit log** | `/admin/audit` | Platform-wide trail of every administrative action |

### Switching an account off and on

`POST /admin/accounts/{id}/toggle` flips `Company.is_active`. Switching an
account **off**:

- blocks every user of that company from signing in (the recorded reason is
  shown on the login form),
- redirects any already-signed-in user to `/account/suspended`,
- notifies the company's administrators,

and switching it back **on** clears the reason and restores access. The company's
data is never touched. A single user inside an account can also be activated or
deactivated from the same screen.

### Payment states

The **account switch** and the **billing state** are deliberately separate:

- `Company.is_active` — a deliberate on/off decision by the operator
  (the switch above).
- `Subscription.status` — where the money stands: `trialing`, `active`,
  `past_due`, `expired`, `cancelled`.

So "payment not done" is `past_due` / `expired` on the subscription, on top of
which you can switch the account off entirely. On an account's page you can set
the plan, set the state by hand, extend the current period by a number of days,
record a note, or press **Payment received** — the manual equivalent of a
verified gateway callback, which activates the subscription and extends the
period. Individual payments can be marked `succeeded`, `pending`, `failed` or
`cancelled` from `/admin/payments`.

Everything above writes to the audit log. Suspending or re-enabling an account
writes **two** entries: one at platform level and one inside the company's own
trail, so both the operator and the customer see it.

### Site-wide settings

Stored as `site.`-prefixed keys in the existing `platform_settings` table (see
`app/site_config.py`), so no new table is needed and they stay clear of the
`payment_config` keys. Every value falls back to the `.env` / `app.config`
default, so a fresh install behaves exactly as before until you change
something. Site name, announcement text and maintenance mode are read lazily,
so edits apply without a restart.

### Smoke test

With the server running, this walks every admin route and the toggle,
subscription, payment, maintenance and registration flows:

```powershell
.\.venv\Scripts\python.exe -m tools.smoke_admin
```

---

## Branding & search visibility

The app ships with its own logo — a gradient badge holding a white disc with a
rising arrow cut out of it ("a coin split by growth"). It is used as the
favicon, the PWA / home-screen icon, the Open Graph preview image and as the
fallback mark whenever a company has not uploaded a logo of its own.

| File | Purpose |
| --- | --- |
| `static/img/logo.svg` | Vector master (used in the sidebar, login card, emails) |
| `static/favicon.ico` | Multi-resolution favicon (16/32/48/64) |
| `static/img/favicon-32.png`, `static/img/logo-192.png`, `static/img/logo-512.png` | Browser / PWA icons |
| `static/img/apple-touch-icon.png` | iOS home screen icon |
| `static/img/og-image.png` | 1200×630 social & search-result preview image |

Regenerate all of them (SVG + PNGs share one set of geometry constants):

```powershell
.\.venv\Scripts\python.exe tools\make_brand_assets.py
```

Every page emits the metadata search engines need: `description`, `canonical`,
Open Graph (`og:title`, `og:description`, `og:image`, `og:url`) and Twitter
card tags — see `templates/partials/seo.html`. Signed-in pages are marked
`noindex, nofollow` so private HR data is never indexed, while `/login` and
`/register` stay indexable and show the logo next to the search result.

Set `APP_BASE_URL` in production so the canonical and Open Graph URLs point at
the real domain (it falls back to the URL of the incoming request).

---

## Payments configuration

Gateway credentials can be supplied two ways. Values saved in the app take
precedence; anything left unset falls back to the environment (`.env`), so an
existing `.env`-based deployment keeps working untouched.

1. **Environment / `.env`** — see `.env.example` for every supported variable
   (`STRIPE_SECRET_KEY`, `PAYPAL_CLIENT_ID`, `MPESA_CONSUMER_KEY`, …).
2. **In-app** — a **platform administrator** opens **Settings → Payment
   gateway** (`/settings/payments`) and saves the keys. Secret values are
   encrypted at rest in the `platform_settings` table, keyed by
   `APP_SECRET_KEY` (see `app/crypto.py`). Rotating `APP_SECRET_KEY` makes saved
   secrets unreadable, so re-enter them from the screen.

No user is a `platform_admin` out of the box — the demo login is a *company*
administrator, so it does not see the payment-gateway link. To grant access:

```sql
UPDATE users SET role = 'platform_admin' WHERE email = 'you@example.com';
```

Only a **verified** provider result may extend a subscription, and raw card
numbers are never stored. Webhook endpoints are `POST /webhooks/visa`,
`/webhooks/paypal` and `/webhooks/mpesa`; Stripe needs its signing secret and
PayPal its webhook ID configured, or callbacks are rejected. While
`PAYMENTS_ENABLED=false` (the default) the built-in **Test mode** provider is
offered so the whole flow can be exercised with no credentials; enabling live
payments turns test mode off.

---

## Mail delivery (login details, activation & reset links)

Emails are sent through `app/emailer.py`, which has two drivers:

| `MAIL_DRIVER` | Behaviour |
| --- | --- |
| `console` (default) | Nothing leaves the machine. Each message is written to `outbox/<timestamp>-<recipient>.html` and logged in `email_logs` with status `console`. |
| `smtp` | Sent through a real SMTP server (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_TLS` / `SMTP_SSL`). Logged with status `sent`. |

**The mail only reaches a real inbox in `smtp` mode.** In `console`
mode the app says so explicitly — *"Login details NOT emailed — SMTP is not
configured, so the message was written to the outbox folder instead"* — instead
of claiming the mail went out.

To enable real delivery, copy `.env.example` to `.env` and fill in the SMTP
section:

```ini
MAIL_DRIVER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
MAIL_FROM=no-reply@yourcompany.com
```

For Gmail, `SMTP_PASSWORD` must be an **App Password**, not the account
password. Restart the server after editing `.env`.

Two things to check when a link "doesn't arrive":

1. **`APP_BASE_URL`** — links are built from it, so it must be reachable by the
   recipient (`http://127.0.0.1:8000` works locally but not for real staff).
2. **`outbox/`** — in `console` mode the message is there; open the `.html`
   file to read it. Every attempt is also recorded in the `email_logs` table
   with its status and error.

Mail failures are caught inside `send_email()`, so a broken SMTP server never
blocks adding an employee — the account is still created and the login details
can be sent again from **Employees → Send login details** (or **Team → Send
login details**), which issues a fresh password each time.

---

## Database (SQLite vs MySQL/MariaDB)

The app works with either database. Nothing in the code is SQLite-specific —
the engine picks the right driver and the migrations quote identifiers for the
active dialect.

| | SQLite (default) | MySQL / MariaDB (XAMPP) |
| --- | --- | --- |
| Setup | none — a `hrms.db` file is created | one-time database + user (below) |
| `DATABASE_URL` | *(leave empty)* | `mysql+pymysql://payroll:payroll@127.0.0.1:3306/payroll?charset=utf8mb4` |
| Driver | built in | `pip install pymysql` (already in `requirements.txt`) |
| Best for | development, demos, single-user installs | anything shared or served on a LAN/internet |

### One-time MySQL setup (XAMPP)

1. Open the XAMPP Control Panel and **start MySQL** (port 3306).
2. Create the database and a dedicated user — open a command prompt and run:

   ```bat
   C:\xampp\mysql\bin\mysql.exe -u root --skip-password
   ```

   then, inside the MySQL prompt:

   ```sql
   CREATE DATABASE payroll CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'payroll'@'localhost' IDENTIFIED BY 'payroll';
   CREATE USER 'payroll'@'127.0.0.1' IDENTIFIED BY 'payroll';
   GRANT ALL PRIVILEGES ON payroll.* TO 'payroll'@'localhost';
   GRANT ALL PRIVILEGES ON payroll.* TO 'payroll'@'127.0.0.1';
   FLUSH PRIVILEGES;
   ```

   Or run the helper script, which does exactly that:

   ```powershell
   powershell -ExecutionPolicy Bypass -File .\tools\setup_mysql.ps1
   ```

3. Set `DATABASE_URL` in `.env` (see the commented line above).
4. Restart the server. The schema is created automatically on start-up; to do
   it by hand run `python -m app.migrations`.

The database then shows up in **phpMyAdmin** at <http://localhost/phpmyadmin>
(select the `payroll` schema) if you want to inspect or edit records.

#### Moving existing data out of SQLite

With `DATABASE_URL` pointing at MySQL (so the schema exists there), this copies
every table across, column by column, and leaves MySQL-only columns at their
defaults:

```powershell
# 1. Make sure the MySQL schema exists first
.\.venv\Scripts\python.exe -m app.migrations

# 2. Copy the rows across (safe to re-run — it upserts on the primary key)
.\.venv\Scripts\python.exe -m tools.copy_sqlite_to_mysql
```

It refuses to run unless `DATABASE_URL` really is a MySQL connection, and it
prints a table-by-table row count so you can see what moved. Your `hrms.db` is
left untouched, so you can always point `DATABASE_URL` back at it.

### Serving through XAMPP's Apache (optional)

Apache cannot run a FastAPI application directly, but it can reverse-proxy to
the uvicorn process. Start the app first (`.\run.ps1`), then add a virtual host
to `C:\xampp\apache\conf\extra\httpd-vhosts.conf`:

```apache
<VirtualHost *:80>
    ServerName payroll.local
    ProxyPreserveHost On
    ProxyPass        / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Uncomment `LoadModule proxy_http_module modules/mod_proxy_http.so` in
`C:\xampp\apache\conf\httpd.conf`, add `127.0.0.1 payroll.local` to your
Windows `hosts` file, and restart Apache from the XAMPP Control Panel. The
site is then reachable at <http://payroll.local>.

---

## Rebuilding the stylesheet

The compiled CSS (`static/css/app.css`) is committed, so you only need this if you change
`tailwind/input.css` or add new utility classes in templates:

```powershell
powershell -ExecutionPolicy Bypass -File .\build-assets.ps1
```

This uses the standalone Tailwind CLI in `tools/tailwindcss.exe` (no Node required).

---

## Project structure

```
HRMS Clone/
├─ app/
│  ├─ main.py           # FastAPI app, session middleware, exception handling, enforcement
│  ├─ db.py             # engine / session / declarative base
│  ├─ models.py         # Company, User, Employee, PayrollRun/Entry, Loan, Leave…
│  ├─ payroll.py        # Kenyan statutory calculation engine
│  ├─ billing.py        # plans, subscription lifecycle (admin-editable plan catalogue)
│  ├─ site_config.py    # site-wide settings from the admin panel (platform_settings rows)
│  ├─ security.py       # password hashing, CSRF, password generator
│  ├─ credentials.py    # in-memory store of just-issued passwords (15 min TTL)
│  ├─ web.py            # Jinja env, currency filters, auth & flash helpers
│  ├─ seed.py           # demo company + 12 employees + runs/loans/leave
│  └─ routers/          # auth, dashboard, employees, payroll, payslips, loans, leave,
│                       # reports, settings, branding, admin (platform panel)
├─ templates/
│  ├─ layouts/          # app shell (sidebar + topbar) and auth card
│  ├─ partials/         # sidebar, flash messages, SEO metadata
│  ├─ admin/            # platform panel: dashboard, accounts, account, payments, site, audit
│  └─ auth|dashboard|employees|payroll|payslips|loans|leave|reports|settings/
├─ static/
│  ├─ css/app.css       # compiled Tailwind
│  ├─ img/              # app logo, favicons, PWA + Open Graph images
│  └─ js/               # app.js (grid logic) + alpine.min.js
├─ tailwind/input.css   # Tailwind source + component classes (.form-input, .btn-primary…)
├─ tools/               # Tailwind standalone CLI, make_brand_assets.py (logo generator),
│                       # setup_mysql.ps1 (create the XAMPP MySQL database + user),
│                       # copy_sqlite_to_mysql.py (one-time data move),
│                       # make_admin.py (grant the platform_admin role),
│                       # setup_platform_admin.py (make one account the only admin),
│                       # purge_account.py (delete an account and its data),
│                       # smoke_admin.py (exercise every /admin route),
│                       # test_login_passwords.py (admin-set-password end-to-end test)
├─ requirements.txt
├─ run.ps1              # one-command dev server
└─ build-assets.ps1     # rebuild CSS
```

---

## Notes & limitations

- The session secret key in `app/main.py` is a dev default — change it before deploying
  (set `APP_SECRET_KEY`), and set `SESSION_HTTPS_ONLY=true` when serving over HTTPS so the
  session cookie is only sent over TLS.
- Password reset links are shown on-screen (no mail server configured).
- The interface is reconstructed from the original's compiled CSS/JS design tokens
  (colours, spacing, component classes such as `.form-input`, `.btn-primary`, `.sidebar-link`,
  `.stat-card` and the `.badge-*` set) rather than from authenticated screenshots.
- SQLite is used for zero-setup; set `DATABASE_URL` in `.env` to use MySQL/MariaDB
  instead (see [Database](#database-sqlite-vs-mysqlmariadb)).
- New-install tip: the first platform administrator has to be granted by hand —
  `python -m tools.make_admin <email>` (see [Platform admin panel](#platform-admin-panel)).
