# TRACKit Database Schema

**Version:** 1.0 (Initial Design)
**Last Updated:** 15 July 2026

---

# Purpose

TRACKit is designed to help NSW teachers visualise and analyse employment opportunities across the state.

The database stores **facts** about schools and vacancies. It deliberately avoids storing derived information or policy decisions where those can be calculated from authoritative data.

The map is the primary user interface, but the database is intended to support future reporting, statistics and historical analysis.

---

# Design Philosophy

The schema follows several guiding principles.

## 1. Facts, not opinions

The database stores objective information only.

Examples:

* School name
* School code
* Location
* Transfer points
* Connected Communities status
* Vacancy details

The application will interpret these facts rather than storing conclusions.

---

## 2. Stable data belongs with the School

Anything that is a permanent or slowly changing property of a school is stored directly in the `School` table.

Examples include:

* address
* phone
* website
* transfer points
* enrolment
* latitude/longitude

This avoids unnecessary joins and keeps the data model simple.

---

## 3. Historical information is never overwritten

Job advertisements are historical records.

If a vacancy changes, a new record is created rather than modifying the previous one.

This allows historical analysis of:

* repeated advertisements
* subject demand
* vacancy trends
* recruitment patterns

---

## 4. One source of truth

Each concept exists only once.

Examples:

* School location exists only in `School`
* Subject definitions exist only in `Subject`
* JobFeed dates exist only in `JobFeed`

Other tables reference these records using foreign keys.

---

# Entity Relationship Overview

```
Region
   │
   ▼
Locality
   │
   ▼
School
   ├── SchoolAlias
   └── Vacancy
           │
           ├── JobFeed
           └── VacancySubject
                     │
                     ▼
                  Subject
```

---

# Tables

## Region

Represents an NSW Department administrative region.

One Region contains many Localities.

---

## Locality

Represents a town or suburb.

Stores:

* name
* postcode
* region

One Locality contains many Schools.

---

## SchoolType

Lookup table describing school classifications.

Examples:

* High School
* Central School
* Community School

---

## Faculty

Lookup table grouping teaching subjects.

Examples:

* TAS
* Science
* Mathematics

---

## Subject

Teaching subject definitions.

Examples:

* IPT
* IST
* SDD
* Technology Mandatory

Each Subject belongs to one Faculty.

---

## School

The central table in TRACKit.

Stores permanent information describing each NSW Government school.

Includes:

* school code
* name
* address
* postcode
* locality
* latitude
* longitude
* website
* phone
* enrolment
* transfer points
* Connected Communities status
* school type
* selective status
* boarding status

A School has:

* many aliases
* many vacancies

---

## SchoolAlias

Stores historical or alternative names for schools.

Purpose:

Older JobFeeds often refer to schools using different names.

Examples:

* Dubbo College Senior Campus
* Dubbo College - Senior Campus
* Dubbo College (Senior Campus)

Aliases allow reliable matching without changing the canonical school name.

---

## JobFeed

Represents a single weekly NSW JobFeed publication.

Stores:

* publication date
* original PDF filename

One JobFeed contains many Vacancies.

---

## Vacancy

Represents one advertised teaching position.

Stores information including:

* school
* employment type
* full-time / part-time
* position fraction
* number of positions
* signing bonus
* advertisement text
* start date
* end date
* closing date

A Vacancy may require multiple teaching subjects.

---

## VacancySubject

Joins Vacancies to Subjects.

Each record also stores whether the subject requirement is:

* Approved
* Willing

This allows advertisements requiring multiple teaching areas to be modelled accurately.

Example:

Approved:

* Industrial Technology (Metal)

Willing:

* Technology Mandatory

---

# Deliberate Design Decisions

## Transfer points are stored on School

Transfer points are treated as an attribute of the school rather than a separate table.

This keeps the model simple and reflects the way the NSW Department publishes the information.

---

## Signing bonuses belong to Vacancy

A signing bonus is attached to a particular advertisement rather than to a school.

Different vacancies at the same school may or may not include a recruitment bonus.

---

## School codes are Integers

NSW school codes are numeric.

They are stored as integers for efficient indexing and sorting.

---

## Locations use school coordinates

Latitude and longitude refer to the physical school location rather than the town centre.

These coordinates are intended to support future:

* mapping
* routing
* travel time calculations
* nearest service calculations

---

# Future Enhancements

Possible additions include:

* Historical principal records
* School facilities
* Local amenities
* Travel-time caching
* Vacancy status tracking
* Statistical reporting
* Vacancy trend analysis

These features should be added only when supported by a clear use case.

---

# Guiding Principle

> **If a piece of information is permanently true about a school, it belongs in the School table.**
>
> **If it changes over time, it belongs in a related table.**
