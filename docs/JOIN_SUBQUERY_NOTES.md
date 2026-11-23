# LogMyOJT — SQL JOIN and SUBQUERY Implementation Guide

This document contains the relational schema design, Django ORM code, generated SQL queries, handwritten SQL for the Supabase SQL Editor, and the 3-part presentation script for the school activity.

---

## Part 1: SQL JOIN Feature — Time Log History

### 1. Tables & Relationships
- **Main Table:** `time_log` (stores daily time-in/out records and computed hours)
  - Primary Key: `id` (bigint)
  - Foreign Key: `placement_id` → `ojt_placement.id`
- **Related Table 1:** `ojt_placement` (stores company and supervisor information)
  - Relationship: **Many-to-One** (Each placement can have many time logs; each log belongs to one placement).
  - Join Type: **`INNER JOIN`** (the foreign key `placement_id` is required / `NOT NULL`).
- **Related Table 2:** `activity_note` (stores daily task summaries)
  - Relationship: **One-to-One** (Each time log has at most one activity note; `time_log_id` is unique).
  - Join Type: **`LEFT OUTER JOIN`** (a student might log hours before adding an accomplishment note, so the note is optional).

### 2. Django ORM Implementation
Located in `apps/time_log/selectors.py`:

```python
def logs_with_placement_and_note(user):
    """JOIN time_log with ojt_placement and activity_note in ONE query."""
    return (
        TimeLog.objects
        .select_related('placement', 'activity_note')
        .filter(placement__user=user)
        .order_by('-log_date', '-time_in')
    )
```

### 3. Generated SQL (from Django ORM)
Run `python manage.py show_join_sql <username>` to display:

```sql
SELECT
    "time_log"."id",
    "time_log"."placement_id",
    "time_log"."log_date",
    "time_log"."time_in",
    "time_log"."time_out",
    "time_log"."hours_computed",
    "time_log"."status",
    "time_log"."created_at",
    "time_log"."updated_at",
    "ojt_placement"."id",
    "ojt_placement"."user_id",
    "ojt_placement"."company_name",
    "ojt_placement"."company_address",
    "ojt_placement"."supervisor_name",
    "ojt_placement"."supervisor_email",
    "ojt_placement"."supervisor_phone",
    "ojt_placement"."required_hours",
    "ojt_placement"."start_date",
    "ojt_placement"."end_date",
    "ojt_placement"."created_at",
    "activity_note"."id",
    "activity_note"."time_log_id",
    "activity_note"."description",
    "activity_note"."created_at"
FROM "time_log"
INNER JOIN "ojt_placement"
    ON ("time_log"."placement_id" = "ojt_placement"."id")
LEFT OUTER JOIN "activity_note"
    ON ("time_log"."id" = "activity_note"."time_log_id")
WHERE "ojt_placement"."user_id" = <user_id>
ORDER BY
    "time_log"."log_date" DESC,
    "time_log"."time_in" DESC;
```

### 4. Equivalent SQL for Supabase SQL Editor
Run this directly in the Supabase Dashboard SQL Editor:

```sql
SELECT 
    t.id AS log_id,
    t.log_date,
    t.time_in,
    t.time_out,
    t.hours_computed,
    t.status,
    p.company_name,
    p.supervisor_name,
    n.description AS activity_note
FROM time_log t
INNER JOIN ojt_placement p 
    ON t.placement_id = p.id
LEFT OUTER JOIN activity_note n 
    ON n.time_log_id = t.id
WHERE p.user_id = 1  -- Replace with your auth_user id
ORDER BY t.log_date DESC, t.time_in DESC;
```

### 5. Why a JOIN is the Right Tool Here
1. **Eliminates the N+1 Query Problem:** Without `select_related`, accessing `log.placement.company_name` and `log.activity_note.description` in a loop over 15 logs would trigger up to 31 individual database queries instead of just 1.
2. **Unified Data Retrieval:** Combining the base record with its parent company details and child note in a single SQL round-trip drastically reduces network latency to the cloud Supabase database.
3. **Appropriate Nullability Handling:** Using an `INNER JOIN` ensures logs only appear for valid student placements, while a `LEFT OUTER JOIN` safely includes logs that do not yet have an activity note.

---

## Part 2: SQL SUBQUERY Feature — Above-Average Days & Missing Notes

### 1. Purpose & Logic
- **Primary Subquery ("Above-Average Days"):** Filters logs whose `hours_computed` exceeds the student's own average daily logged hours.
  - **Inner Query:** Computes a scalar value: `SELECT AVG(hours_computed) FROM time_log ...` for the logged-in student.
  - **Outer Query:** Retrieves `time_log` records where `hours_computed > (inner_query_result)`.
- **Secondary Subquery ("Missing Notes", Task 3B):** Finds time logs that do not have any corresponding row in `activity_note`.
  - **Inner Query:** `SELECT time_log_id FROM activity_note`
  - **Outer Query:** `SELECT * FROM time_log WHERE id NOT IN (inner_query_result)`

### 2. Django ORM Implementation
Located in `apps/time_log/selectors.py`:

```python
# Subquery 1: Above-average days
def above_average_logs(user):
    own_logs = TimeLog.objects.filter(placement__user=user, hours_computed__gt=0)
    avg_hours = (
        own_logs
        .values('placement__user')
        .annotate(avg=Avg('hours_computed'))
        .values('avg')[:1]
    )
    return (
        own_logs
        .select_related('placement')
        .filter(hours_computed__gt=Subquery(avg_hours))
        .order_by('-hours_computed', '-log_date')
    )

# Subquery 2: Logs missing activity notes
def logs_missing_notes(user):
    noted_ids = ActivityNote.objects.values('time_log_id')
    return (
        TimeLog.objects
        .filter(placement__user=user)
        .exclude(id__in=Subquery(noted_ids))
        .select_related('placement')
        .order_by('-log_date', '-time_in')
    )
```

### 3. Generated SQL (from Django ORM)
Run `python manage.py show_subquery_sql <username>` to display:

```sql
-- Above-Average Subquery:
SELECT 
    "time_log"."id", 
    "time_log"."placement_id", 
    "time_log"."log_date", 
    "time_log"."hours_computed",
    ...
FROM "time_log"
INNER JOIN "ojt_placement" 
    ON ("time_log"."placement_id" = "ojt_placement"."id")
WHERE (
    "ojt_placement"."user_id" = <user_id>
    AND "time_log"."hours_computed" > 0
    AND "time_log"."hours_computed" > (
        SELECT AVG(U0."hours_computed") AS "avg"
        FROM "time_log" U0
        INNER JOIN "ojt_placement" U1 ON (U0."placement_id" = U1."id")
        WHERE (U1."user_id" = <user_id> AND U0."hours_computed" > 0)
        GROUP BY U1."user_id"
        LIMIT 1
    )
)
ORDER BY "time_log"."hours_computed" DESC, "time_log"."log_date" DESC;
```

### 4. Equivalent SQL for Supabase SQL Editor
Run this directly in Supabase to verify:

```sql
-- Query 1: Above-Average Days
SELECT 
    t.id, 
    t.log_date, 
    t.hours_computed, 
    t.status, 
    p.company_name
FROM time_log t
INNER JOIN ojt_placement p ON t.placement_id = p.id
WHERE p.user_id = 1
  AND t.hours_computed > (
      SELECT AVG(t2.hours_computed)
      FROM time_log t2
      INNER JOIN ojt_placement p2 ON t2.placement_id = p2.id
      WHERE p2.user_id = 1 AND t2.hours_computed > 0
  )
ORDER BY t.hours_computed DESC;

-- Query 2: Missing Activity Notes
SELECT 
    t.id, 
    t.log_date, 
    t.hours_computed, 
    p.company_name
FROM time_log t
INNER JOIN ojt_placement p ON t.placement_id = p.id
WHERE p.user_id = 1
  AND t.id NOT IN (
      SELECT time_log_id FROM activity_note
  )
ORDER BY t.log_date DESC;
```

### 5. Why a SUBQUERY is the Right Tool Here
1. **Dynamic Dynamic Thresholding:** The comparison target (the student's average hours) is not a hardcoded constant; it must be calculated dynamically from the database rows before the outer condition can be evaluated.
2. **Encapsulated Execution:** A subquery allows PostgreSQL to calculate the aggregated metric and filter the matching records in a single database statement rather than performing two separate round trips from Python.
3. **Data Scoping & Security:** Scoping the inner query to `p.user_id` ensures each student's baseline is computed strictly from their own logs without leaking or skewing data across accounts.

---

## Part 3: Video Demonstration Script

Use this 3-minute outline when recording your submission video:

### 1. Introduction (30 seconds)
- State your name and project: "This is LogMyOJT, a digital internship logbook built with Django and Supabase PostgreSQL."
- Explain the goal: "Today I will demonstrate one SQL JOIN and one SQL SUBQUERY integrated into real student workflows."

### 2. Part 1: SQL JOIN Demo (60 seconds)
1. **In the Web Browser:**
   - Log into the app. On the dashboard, navigate to **Recent Time Logs** → click **"View full history →"** (URL: `/logs/`).
   - Point out the data columns: `Date`, `Company`, `Supervisor`, `Hours`, `Status`, and `Activity Note`.
   - Point out the small caption: *"Data source: time_log + ojt_placement + activity_note"*.
   - Mention that rows with notes show the text, while rows without notes cleanly display *"No note"*.
2. **In Code & Terminal:**
   - Show `apps/time_log/selectors.py` and explain `.select_related('placement', 'activity_note')`.
   - Run the command:
     ```bash
     python manage.py show_join_sql <your_username>
     ```
   - Point out the `INNER JOIN "ojt_placement"` and `LEFT OUTER JOIN "activity_note"` in the generated query output, followed by the actual rows returned.

### 3. Part 2: SQL SUBQUERY Demo (60 seconds)
1. **In the Web Browser:**
   - Click the **"Insights (SUBQUERY)"** tab or visit `/logs/insights/`.
   - Show the banner: *"Your Daily Average: X.XX hrs/day"*.
   - Show the **Above-Average Days** table, highlighting days exceeding that average with their `+X.XX h` badge.
   - Show the **Logs Missing Activity Notes** table (demonstrating `NOT IN (SELECT time_log_id FROM activity_note)`).
2. **In Code & Terminal:**
   - Show `apps/time_log/selectors.py` (`above_average_logs` and `logs_missing_notes`).
   - Run the command:
     ```bash
     python manage.py show_subquery_sql <your_username>
     ```
   - Highlight the nested `SELECT AVG(...)` inside the `WHERE` clause.

### 4. Part 3: Supabase Database Verification (30 seconds)
1. Open your **Supabase Dashboard**:
   - Go to **Table Editor**: show the rows inside `time_log`, `ojt_placement`, and `activity_note`.
   - Go to **Schema Visualizer** or **SQL Editor**:
     - Paste the SQL query from Section 4 of this document into the SQL Editor.
     - Click **Run** and verify that the exact same rows appear as on your web page!
