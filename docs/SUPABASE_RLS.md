# Supabase Row Level Security (RLS) Guide

## Why RLS is Required for Supabase

Supabase automatically exposes all tables in the `public` schema via PostgREST (the REST Data API) using the project's anonymous (`anon`) or authenticated API keys. 

If Row Level Security (RLS) is not enabled on tables in the `public` schema:
1. Anyone who obtains the public `anon` API key (often present in client applications or repository configurations) can directly query, read, insert, update, or delete records in those tables via `https://<project-ref>.supabase.co/rest/v1/`.
2. This bypasses Django's permission checks, view logic, and student data isolation.

### How Direct Django Connections Interact with RLS
When Django connects to PostgreSQL via the connection string (`DATABASE_URL`), it connects directly using the `postgres` administrative role (or an assigned database role that owns the tables). In PostgreSQL, table owners and superusers **bypass RLS by default**. 

Therefore:
- Enabling RLS on every table in `public` **without** adding permissive policies immediately blocks external HTTP/REST access via Supabase's Data API.
- Django continues to perform all migrations, queries, and transactions without interruption or performance penalty.

---

## SQL Statements to Run in Supabase SQL Editor

Open your [Supabase Dashboard](https://supabase.com/dashboard), navigate to **SQL Editor**, paste the following block, and click **Run**:

```sql
-- ============================================================================
-- LogMyOJT — Lock Down Public Tables with Row Level Security
-- ============================================================================

-- Core Application Tables (Approved ERD)
ALTER TABLE IF EXISTS profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS ojt_placement ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS time_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS activity_note ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS supervisor_verification ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS reminder ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS report ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS progress_summary ENABLE ROW LEVEL SECURITY;

-- Django Built-in & Authentication Tables
ALTER TABLE IF EXISTS auth_user ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS auth_group ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS auth_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS auth_user_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS auth_user_user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS auth_group_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS django_admin_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS django_content_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS django_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS django_session ENABLE ROW LEVEL SECURITY;

-- Rate Limiting & Security Tables (django-axes)
ALTER TABLE IF EXISTS axes_accessattempt ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS axes_accesslog ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS axes_accessfailurelog ENABLE ROW LEVEL SECURITY;
```

---

## Verification

After executing the query, run the following SQL command in the SQL Editor to confirm that all public tables have `rowsecurity = true`:

```sql
SELECT 
    schemaname, 
    tablename, 
    rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY tablename;
```

Every table in the `public` schema should return `t` (`true`) for `rowsecurity`. No REST client will be able to read or manipulate records through the Supabase PostgREST API.
