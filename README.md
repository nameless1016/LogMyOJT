# LogMyOJT — Vertical Slicing + Profile/Settings (Activity 2, Part 1)

This is the vertically-sliced version of the LogMyOJT project, following
the CSIT327 Vertical Slicing guide. **Supabase integration is not yet
wired in** — the project still runs on SQLite for now, by design, so this
restructuring could be tested independently first.

## Project structure

```
config/                 — project settings, root urls.py
apps/
  login/                — sign-in + logout
  register/             — new account creation
  home/                 — authenticated landing screen
  user_profile/         — Profile feature (Python package named
                           user_profile to avoid clashing with the
                           built-in Python "profile" module; URLs and
                           templates still use "profile")
  user_settings/        — Settings feature (dark mode, notifications)
templates/
  login/login.html
  register/register.html
  home/home.html
  profile/profile.html
  user_settings/settings.html
static/
  css/  <feature>/...   — one stylesheet per feature
  js/   <feature>/...   — one script per feature
  images/<feature>/...  — reserved for feature-specific images
  css/shared/base.css   — shared design tokens (colors, buttons, inputs)
                           imported by each feature's own CSS file —
                           this is the one intentional cross-cutting
                           utility, per the guide's rules
media/profile/          — uploaded profile photos (created at runtime)
```

Each feature app owns its own `views.py`, `urls.py`, template, CSS, and
JS. No feature imports another feature's views or models directly.

## URLs

| Screen   | URL          | Namespace         |
|----------|--------------|--------------------|
| Login    | `/login/`    | `login:login`      |
| Logout   | `/login/logout/` | `login:logout` |
| Register | `/register/` | `register:register`|
| Home     | `/`          | `home:home`         |
| Profile  | `/profile/`  | `profile:profile`   |
| Settings | `/settings/` | `user_settings:settings` |

## Models

- `apps/user_profile/models.py` — `Profile` (one-to-one with `User`):
  `full_name`, `bio`, `profile_image`.
- `apps/user_settings/models.py` — `UserSettings` (one-to-one with
  `User`): `dark_mode`, `email_notifications`.

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. You'll land on `/login/` if not signed
in yet — register first, then you'll be redirected to Home.

## Connecting to Supabase PostgreSQL

By default, if no `.env` file exists, the project falls back to local
SQLite automatically — so it still runs before Supabase is configured.

To switch to Supabase:

1. Copy `.env.example` to a new file named `.env`.
2. In your Supabase Dashboard, go to **Connect > Session pooler** and
   copy the connection string.
3. Paste it into `.env` as `DATABASE_URL=...`, replacing
   `[PROJECT-REF]`, `[YOUR-PASSWORD]`, and `[POOLER-HOST]` with your
   actual values.
4. Run:
   ```bash
   python manage.py check
   python manage.py migrate
   python manage.py runserver
   ```
5. Open your Supabase Dashboard > Table Editor and confirm tables like
   `auth_user`, `apps_user_profile_profile`, and
   `apps_user_settings_usersettings` now exist.
6. Register a test account through the app, then refresh Table Editor
   to confirm the row appears in `auth_user`.

`.env` is already listed in `.gitignore` — never commit your real
database password.
