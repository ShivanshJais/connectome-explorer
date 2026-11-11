# Connectome Explorer Project Plan

Build a small Django application that explores the fruit fly escape circuit in FlyWire FAFB v783, starting with routes from LC4 and LPLC2 neurons to DNp01 neurons. A user should be able to remove selected cell types from an analysis and compare which routes remain. General sensory-to-descending exploration can follow this worked example.

Work one milestone at a time. Each milestone should leave something you can run, inspect, and explain before moving on.

## Current progress

- [x] Write the project README and identify the four source data files.
- [x] Define PostgreSQL and Adminer services in `compose.yaml`.
- [x] Verify the services start and database access works.
- [ ] Inspect the data and decide the graph rules.
- [ ] Set up Django, import the data, and implement route analysis.
- [ ] Build a small interface and document a reproducible example.

The Compose configuration includes a persistent database volume, a read-only `data/` mount, and a database health check. PostgreSQL is exposed locally on port 5433 and Adminer on port 8080. Adminer is working, as reported by the user; database health and persistence checks can be completed separately.

## First version scope

Proposed starting behavior:

- Choose an LC4 or LPLC2 source neuron and a DNp01 target neuron from the imported annotations.
- Show whether the target is reachable and one shortest path by number of connections.
- Select one or more cell types to exclude from the analysis.
- Compare baseline and modified reachability using the same graph settings.
- Explain when an excluded type includes the selected source or target.

After this works for one pair, compare the LC4 and LPLC2 source sets against both DNp01 targets. Report reachability per source-target pair, with excluded sources counted separately from surviving sources that lose a route. Explore intermediate cell-type exclusions as well as removal of an entire source population.

Keep intermediate neurons available during traversal. Loading only the three named types would omit routes through other types. Any hop limit or neuropil restriction must be explicit in the results.

Keep the first interface to forms, counts, and path tables. Interactive network visualization, accounts, deployment, and exhaustive path enumeration can wait.

These results describe connectivity in the selected graph. They do not establish functional signaling or predict the biological effect of removing cells.

## Reported data findings to validate during import

The user's inspection reports 139,255 classification rows, 138,327 consolidated cell-type rows, and 139,255 neuron rows. It reports 104 LC4, 210 LPLC2, and 2 DNp01 neurons, along with 928 neurons without a cell type. Reproduce these counts using a documented label-selection rule during import. Keep the optional names file outside the initial import unless its labels become useful.

Connections reportedly contain 5,342,446 rows and 3,732,460 distinct directed neuron pairs. A stored connection row is unique on `(pre_root_id, post_root_id, neuropil)`. A graph edge between two neurons sums `syn_count` across those region rows. The reported five-synapse source filter applies to that pair total: do not discard individual region rows with counts below five.

Use `primary_type` as the proposed initial grouping label, preserve additional labels, and validate the choice against the escape-circuit counts. Preserve unlabeled neurons as individual nodes and report them explicitly.

A cell-type rollup can provide a smaller overview, but neuron-level traversal remains the basis for route claims. A type-level chain A → B → C can combine an A → B connection into one B neuron with a B → C connection from a different B neuron, even when no corresponding neuron-level path exists.

## Milestone 1 Verify the development environment

Learn how containers, ports, environment variables, and persistent volumes fit together.

- [x] Create a local `.env` with the database settings referenced by Compose.
- [x] Keep `.env` and downloaded data out of version control; provide an `.env.example` with placeholders.
- [x] Run `docker compose config --quiet` and `docker compose up -d`.
- [x] Inspect service status and logs; confirm the database becomes healthy.
- [x] Open Adminer and connect to the PostgreSQL service using `db` as the server.
- [x] Verify a normal service restart preserves a small test record, then clean up the test record.

Done when: you can connect to the database and explain the difference between the host address `localhost:5433` and the container address `db:5432`.

## Milestone 2 Inspect the source data and define the graph

Learn how to turn unfamiliar CSV files into an explicit data model.

- [x] Download the four files listed in the README for FAFB v783.
- [ ] Inspect headers and a small sample from each compressed CSV before designing tables.
- [ ] Record identifier columns, relevant annotations, missing values, and relationships between files.
- [ ] Identify the annotations that define sensory and descending neurons.
- [ ] Choose the source of cell-type labels and a rule for missing or conflicting labels.
- [ ] Validate uniqueness of `(pre, post, neuropil)` and reproduce the distinct directed pair count.
- [ ] Sum region-level synapse counts into pair strengths before applying the graph edge threshold.
- [ ] Decide whether an edge requires a minimum connection weight; record the chosen default.
- [ ] Decide how to handle self-loops and neurons without classification records.

Starting graph proposal: neurons are nodes and directed connections are edges. Excluding a cell type removes its neurons and their incident edges from the analysis without deleting imported data. Use connection weights for filtering initially; shortest path means fewest edges, not strongest biological connection.

Done when: a short data dictionary explains the columns you will use, and a small hand-drawn example makes the graph and exclusion rules unambiguous.

## Milestone 3 Set up Django and the database schema

Learn Django configuration, models, and migrations.

- [ ] Choose whether Django initially runs on the host or in Compose. Suggested first step: run it on the host while learning Django.
- [ ] Create the Django project and an app for connectome data and analysis.
- [ ] Configure its database connection through environment variables.
- [ ] Design neuron, cell-type, and neuropil-level directed connection records from the inspected data.
- [ ] Enforce connection uniqueness on `(pre, post, neuropil)` and define how missing neuropil values are represented.
- [ ] Preserve original neuron identifiers without losing precision.
- [ ] Add constraints and indexes for the lookups the analysis will need.
- [ ] Create and run migrations.
- [ ] Add a basic page that confirms Django can read from the database.

Done when: Django can store and retrieve a tiny set of neurons and connections through its models.

## Milestone 4 Build a repeatable data import

Learn streaming imports, validation, and the separation between source files and application tables.

- [ ] Create a Django management command for importing data.
- [ ] Start with a small development fixture, then import the full dataset.
- [ ] Read compressed files in batches rather than loading every CSV into memory.
- [ ] Define rerun behavior so a repeated import cannot silently duplicate records.
- [ ] Report imported, skipped, and invalid rows with useful error messages.
- [ ] Check duplicate identifiers, duplicate connection triples, missing endpoint records, and unexpected null annotations.
- [ ] Reproduce the reported escape-circuit populations and unlabeled-neuron count; explain discrepancies rather than silently dropping records.
- [ ] Record dataset version, source filenames, import settings, and row counts.
- [ ] Measure full import time and database size before optimizing.

Done when: an import can be repeated predictably, record counts are explainable, and sampled database records match the source files.

## Milestone 5 Implement and check route analysis

Learn directed graph traversal and keep analysis logic separate from web views.

- [ ] Build a tiny fixture with a direct route, an alternative route, a cycle, and an unreachable target.
- [ ] Implement baseline reachability and one shortest path.
- [ ] Apply cell-type exclusions without changing stored source data.
- [ ] Compare baseline and modified results.
- [ ] Test exclusions that break all routes, preserve an alternative, or remove an endpoint.
- [ ] Test missing labels and invalid neuron selections under the agreed rules.
- [ ] Test a neuron pair split across multiple neuropils to confirm summation happens before thresholding.
- [ ] Test a type-level chain with no valid neuron-level path to prevent rollup results being mistaken for neuron routes.
- [ ] Check the invariant that deleting nodes cannot make a previously unreachable target reachable.
- [ ] Measure query duration and memory use on the imported graph; choose limits appropriate to the observed cost.

Start with one LC4 or LPLC2 neuron and one DNp01 neuron. Extend to both source populations and both targets after the small cases are correct. Choose an in-memory graph or database traversal approach based on the measured graph size and a simple prototype.

Done when: fixture results match manual reasoning and a real-data query completes with recorded settings and acceptable resource use.

## Milestone 6 Build the comparison interface

Learn Django forms, views, validation, and templates.

- [ ] Start with LC4, LPLC2, and DNp01 presets, with access to individual neurons.
- [ ] Add a cell-type exclusion control and show how many neurons it excludes.
- [ ] Display baseline and modified reachability and path lengths.
- [ ] Show the neuron IDs and available labels in each displayed path.
- [ ] Distinguish invalid input, an excluded endpoint, and a valid query with no path.
- [ ] Display dataset version and graph filter settings alongside results.
- [ ] Add source-to-target-set comparison once pairwise analysis works.

Done when: a user can run and understand a complete comparison in the browser without using Adminer or a shell.

## Milestone 7 Make the project reproducible

- [ ] Update the README with environment setup, migrations, import, and run commands.
- [ ] Document graph definitions, exclusion behavior, and interpretation limits.
- [ ] Include a small synthetic fixture so core checks do not require the full download.
- [ ] Add the required FlyWire citations and link to the data terms.
- [ ] Write one worked example with inputs, settings, and expected results.
- [ ] Verify the documented setup from a clean development database.

Done when: someone can follow the README and reproduce the small example.

## Decisions to settle during development

- Which annotations count as sensory and descending?
- Which cell-type labels are authoritative for this application?
- What connection threshold should the first version use?
- Does the full graph fit comfortably in memory for local analysis?
- How many targets and how much path detail should a single request return?

Resolve annotation and graph-definition questions before importing the full dataset. Resolve performance questions with measurements before adding caching or background jobs.

## Next working session

With Adminer working, move to Milestone 2: inspect the exact CSV headers and a few sample rows together, then sketch the Neuron, CellType, and Connection models. Use the reported escape-circuit counts and connection aggregation rules as import checkpoints. Complete any remaining environment checks alongside this work.

For each session, keep a short note:

- Objective:
- What I tried:
- What happened:
- What I learned:
- Next small step:
