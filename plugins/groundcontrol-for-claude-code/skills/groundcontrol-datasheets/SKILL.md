---
name: groundcontrol-datasheets
description: GROUNDCONTROL datasheets (user-defined tables, API path /tables) — full reference for the 13 gc_*table*/*field*/*rows* tools. Use when a task or the user mentions a datasheet or table in GROUNDCONTROL, before creating, reading or writing datasheet rows or columns.
tools:
  - gc_list_tables
  - gc_get_table
  - gc_create_table
  - gc_update_table
  - gc_delete_table
  - gc_add_field
  - gc_update_field
  - gc_delete_field
  - gc_list_rows
  - gc_create_rows
  - gc_update_rows
  - gc_delete_rows
  - gc_comment_table
---

# GROUNDCONTROL Datasheets

Datasheets are user-defined tables (speaker lists, budgets, inventories) that
humans edit in a grid and you read and write over the API. The tools say
`table` and the API path is `/tables`, because that is the internal name — to a
human it is always a **datasheet**.

The tool descriptions are deliberately short. This skill is the reference:
parameters, examples, filter operators, field types, paging and the workflow.

## Rules that apply to every tool

- **HTTP 404 on every call = this workspace has no datasheets module.** It
  answers `Not found`, exactly like a datasheet that does not exist. That is not
  a bug, not a permission error and not worth retrying: say this workspace has
  no datasheets and carry on.
- **Row data is keyed by FIELD ID** (`fld_…`), never by column name.
- **A select value is an OPTION ID** (`opt_…`), never its label — when writing
  and when filtering.
- `gc_get_table` (or `gc_list_tables`) is where those ids come from. Read it
  before you write.
- **Visibility is inherited from the initiative, exactly like a doc**: public
  initiative = the whole workspace, private initiative = its members, no
  initiative = you and your responsible user. There is no visibility field.
- Managing a datasheet (update, delete) is for its creator, an owner or an admin.

## Field types

| Type | Value in a row |
|------|----------------|
| `text` | string |
| `number` | number |
| `boolean` | true / false |
| `date` | ISO 8601 string |
| `single_select` | one option id (`"opt_…"`) |
| `multi_select` | array of option ids (`["opt_…", "opt_…"]`) |

## Tools

### `gc_list_tables`
Lists the datasheets you can see, each with its full field definitions.
Params: `initiative_id` (only datasheets in this initiative), `q` (search
datasheet names), `limit` (max 200, default 100), `offset`.

### `gc_get_table`
`table_id` → one datasheet with its fields: `id` (`fld_…`), `name`, `type`,
`required`, `position`, and for select fields `options: [{id: "opt_…", label}]`.
Those ids are what row data is keyed by and what select values must be.

### `gc_create_table`
Params: `name` (required, unique in the workspace), `description`,
`initiative_id` (decides who can see it), `fields` — the columns in order, each
`{name, type, options?, required?}`. `options` are plain labels (select types
only); the option ids are generated and come back in the response.

```
{"name":"Speakers","initiative_id":"<uuid>","fields":[{"name":"Speaker","type":"text","required":true},{"name":"Status","type":"single_select","options":["Invited","Confirmed"]}]}
```

### `gc_update_table`
`table_id` + any of `name`, `description`, `initiative_id`. Moving it to another
initiative changes who can see it; `initiative_id: null` moves it out of every
initiative.

### `gc_delete_table`
`table_id` → deletes the datasheet with all its rows and comments. Cannot be
undone.

### `gc_add_field`
`table_id`, `name`, `type` (required), `options` (labels, select types only),
`required`. The column is appended at the end; option ids (`opt_…`) are
generated and returned; existing rows simply have no value in the new column.

```
{"table_id":"<uuid>","name":"Stage","type":"single_select","options":["Draft","Sent"]}
```

### `gc_update_field`
`table_id`, `field_id` (`fld_…`) + any of `name`, `required`, `position`
(0-based), `options`. `options` is the **COMPLETE new list**: `{id, label}` keeps
an existing option (and its values in the rows), an entry without `id` is a new
option, an omitted one is removed. The type cannot be changed — add a new column
instead.

### `gc_delete_field`
`table_id`, `field_id` → removes the column. The values stored in it are no
longer shown or returned.

### `gc_list_rows`
`table_id` (required) + optional:
- `filter`: array of `{field, op, value}`, combined with AND. Ops:
  `eq`, `neq`, `gt`, `gte`, `lt`, `lte` (number/date), `contains` (text),
  `has_any`, `has_all` (multi_select), `is_empty`, `is_not_empty`. Select values
  are option ids, never labels.
- `sort`: `"fld_x:asc"` or `"fld_x:desc"` (default: newest first).
- `q`: searches all text columns.
- `all: true`: page to the end and return **every** matching row (the API caps
  one page at 200; the pages are walked for you, `limit`/`offset` are ignored).
- Otherwise one page: `limit` (default 50, max 200), `offset`; `meta.total`
  says how many rows matched.

```
{"table_id":"<uuid>","filter":[{"field":"fld_ab12","op":"eq","value":"opt_ef56"}],"sort":"fld_cd34:desc"}
```

### `gc_create_rows`
`table_id`, `rows`: an array of data objects keyed by field id, max 100 per
call. All or nothing: one invalid value rejects the whole batch with a
validation error naming the field, the expected type and the value received.

```
{"table_id":"<uuid>","rows":[{"fld_ab12":"Mara Weiss","fld_cd34":"opt_ef56","fld_gh78":3}]}
```

### `gc_update_rows`
`table_id`, `rows: [{id, data}]` — `id` is the row UUID (from
`gc_list_rows`), `data` holds ONLY the fields to change; everything else stays,
`null` clears a cell. Max 100 rows per call, all or nothing: one unknown row id
aborts the whole batch.

### `gc_delete_rows`
`table_id`, `ids` (max 100) → deletes those rows; unknown ids are skipped.
Answers `{ deleted: n }`.

### `gc_comment_table`
`table_id`, `body` → a comment visible to everyone who can see the datasheet.
Markdown and @-mentions work like task comments. It is the way to report back
what you changed and why.

## Workflow

1. `gc_get_table` (or `gc_list_tables`) → note each field's `id`, `type` and,
   for select fields, its `options[].id`.
2. Write with those ids (`gc_create_rows` / `gc_update_rows`).
3. A wrong value returns a validation error naming the field, the expected type
   and the value received — fix it and resend; nothing was written.
4. Report what you changed with `gc_comment_table`.

**Reading.** Never reason about totals from a single page. When you need the
whole datasheet — counting, summing, exporting — pass `all: true`.

**Changes.** `gc_get_changes` carries `table_rows_created`,
`table_rows_updated` and `table_comments` — but only for the datasheets you
created or have commented on. Comment once on a datasheet you are supposed to
watch and its rows start appearing in your heartbeat.
