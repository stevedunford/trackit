# TRACKit Script Design Notes

**Version:** 1.0
**Last Updated:** 15 July 2026

---

# Purpose

This document records the design philosophy behind TRACKit's utility scripts.

The goal is to make data management predictable, safe and repeatable while protecting the integrity of the database.

---

# General Principles

## The database is an asset

The TRACKit database will eventually contain many hours of manually verified and imported data.

It should be treated as valuable.

Scripts should always prefer preserving data over deleting it.

---

## Idempotent by design

Wherever possible, scripts should be idempotent.

Running the same script multiple times should produce exactly the same database state as running it once, unless the input data has changed.

This applies particularly to:

* seed.py
* update scripts
* verification scripts

---

## Update rather than replace

Reference data should be updated in place.

Scripts should:

* insert new records
* update changed records
* leave unchanged records untouched

Scripts should **never** delete records simply because they no longer exist in a CSV file.

---

## Preserve history

Historical data has long-term value.

Where possible:

* set `active = False`
* retain historical relationships
* avoid physical deletion

Examples include:

* schools
* subjects
* localities

Deleting records should be extremely uncommon.

---

## Safety first

No script should silently destroy data.

Any destructive operation must:

* clearly explain what will happen
* provide an easy way to cancel
* create a timestamped database backup before continuing

Destructive scripts should be kept separate from everyday maintenance scripts.

---

# Script Categories

## Safe

Safe scripts may be run repeatedly without risk.

Examples:

* seed.py
* update_school_data.py
* verify_coordinates.py

These scripts should only insert or update records.

---

## Maintenance

Maintenance scripts perform administrative tasks without deleting data.

Examples:

* rebuild_aliases.py
* merge_duplicate_schools.py

---

## Dangerous

Dangerous scripts permanently modify or delete data.

Examples:

* drop_database.py
* purge_jobfeeds.py
* delete_vacancies.py

These scripts should:

* require explicit confirmation
* create automatic backups
* be stored in a separate `dangerous/` folder

---

# Seeder Philosophy

The initial seeder (`seed.py`) is responsible only for loading reference data.

It should never modify user-generated or imported historical data.

---

## Reference Data

The seeder is responsible for:

* Regions
* Localities
* School Types
* Faculties
* Subjects
* Schools

These records may be updated whenever the seed CSV files change.

---

## User Data

The seeder must never modify:

* JobFeeds
* Vacancies
* Vacancy history
* User-added aliases
* Future notes or annotations

---

# Import Order

Because of foreign key dependencies, tables should be imported in this order:

```text
Regions
    ↓
Localities
    ↓
School Types
    ↓
Faculties
    ↓
Subjects
    ↓
Schools
```

Additional importers (such as JobFeed imports) will define their own dependency order.

---

# Record Matching

Each table has a natural key used to determine whether a record already exists.

| Table       | Match On        |
| ----------- | --------------- |
| Region      | name            |
| Locality    | name + postcode |
| School Type | code            |
| Faculty     | code            |
| Subject     | code            |
| School      | school_code     |

If a matching record exists:

* update changed fields
* leave unchanged fields untouched

If no matching record exists:

* insert a new record

---

# Error Handling

Importing should continue wherever possible.

A single bad record should not prevent all remaining records from loading.

Errors should include:

* source file
* line number
* description of the problem

A summary should be displayed at the end of the import.

---

# Progress Reporting

Each import stage should report:

* records added
* records updated
* records unchanged
* errors encountered

Example:

```text
Loading Schools...

Added       : 5
Updated     : 2
Unchanged   : 2208
Errors      : 0
```

This provides immediate feedback if unexpected changes occur.

---

# Transactions

Each table should be imported as a single transaction.

Example:

```
Load Regions
Commit

Load Localities
Commit

Load Schools
Commit
```

If one table fails, previously imported tables remain intact.

---

# CSV Standards

Seed CSV files should:

* contain a header row
* use UTF-8 encoding
* avoid duplicate records
* use stable identifiers
* contain only authoritative data wherever possible

CSV files should remain easy to edit manually.

---

# Helper Functions

The seeder should use common helper functions rather than duplicating logic.

Examples include:

* CSV reader
* boolean conversion
* integer conversion
* float conversion
* record lookup
* update/create helper

This keeps each table importer concise and consistent.

---

# Future Direction

As TRACKit grows, standalone scripts may be replaced with Flask CLI commands.

For example:

```
flask seed
flask import-jobfeed
flask verify
flask backup
```

The internal logic should therefore remain modular so it can be reused regardless of how commands are launched.

---

# Guiding Principles

1. The database is valuable.
2. Updating is preferred over replacing.
3. History should be preserved.
4. Destructive actions must be deliberate.
5. Seed data and user data are kept separate.
6. Every script should produce clear, informative output.
7. A script should be safe to run more than once.
