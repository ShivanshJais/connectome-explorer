# Understanding the Connectome Explorer Data

This guide explains the files and vocabulary used in the project's FlyWire FAFB v783 analysis. Start with the file overview, then use the definitions as a reference while inspecting rows in your terminal.

The first project question is: **which directed routes from LC4 or LPLC2 neurons to DNp01 neurons remain after selected cell types are excluded?**

Column names below follow the file descriptions supplied for this project. Your downloaded headers are the authority for the importer. Example IDs and connection rows are invented for teaching.

## 1. The dataset and basic biology

| Term | Meaning |
| --- | --- |
| Neuron | A nerve cell that receives, processes, and transmits information. |
| Soma | The cell body, containing the nucleus. |
| Axon | A neuronal process commonly associated with sending signals toward other cells. |
| Dendrite | A neuronal process commonly associated with receiving input. These anatomical descriptions are not substitutes for the connection table's direction. |
| Synapse | A specialized contact through which one neuron communicates with another cell. |
| Chemical synapse | A synapse that uses chemical messengers called neurotransmitters. |
| Electrical synapse | A connection through gap junctions. Do not assume the downloaded chemical-connectivity table includes these. |
| Connectome | A map of neurons and their connections. |
| Neural circuit | A set of interconnected neurons studied in relation to a particular computation or behavior. |
| Morphology | A cell's shape and branching structure. |
| Neuropil | A region rich in neuronal branches and synapses. |

FlyWire reconstructs neurons from electron microscopy images. Segmentation assigns image regions to reconstructed objects; proofreading corrects errors such as wrongly merged or split cells. Proofread does not mean error-free. The released data combine reconstructed neuron identities, detected synapses, and neurotransmitter predictions. [FlyWire data description](https://zenodo.org/records/10676866)

FAFB refers here to the female adult fly brain dataset. Version 783 identifies the snapshot used by this project. Codex is its exploration and download interface. Root IDs can change between snapshots; keep your input files together and record the release and download date. [Codex FAQ](https://codex.flywire.ai/faq)

## 2. How the files fit together

| File | Main purpose | Expected row meaning |
| --- | --- | --- |
| `classification.csv.gz` | Broad classification and anatomy | An annotation record for a neuron |
| `consolidated_cell_types.csv.gz` | Specific type labels | A cell-type record for a neuron |
| `neurons.csv.gz` | Neuron metadata and transmitter predictions | A neuron record |
| `connections_princeton.csv.gz` | Directed anatomical connections | A presynaptic neuron, postsynaptic neuron, and neuropil combination |
| `names.csv.gz` | Human-readable names | Inspect the header and uniqueness before assuming its exact structure |

The shared `root_id` connects neuron metadata across files. A connection references two such IDs: one for its sender and one for its receiver.

Do not join by row position. Row 20 in one file need not describe row 20 in another.

## 3. Identifiers, types, and names

**`root_id`** identifies one reconstructed neuron in the chosen snapshot. It is not a cell-type number, a location, or a rank.

**Cell type** groups neurons with shared identifying properties. For example, many individual neurons can have the type `LC4`.

**`primary_type`** is the selected main type label. **`additional_type(s)`** holds other assignments. Inspect how multiple values are encoded before splitting this field. Codex combines typing information from multiple sources. Automatic **names** are based on regions containing many of a neuron's connections. [Codex annotation and naming explanations](https://codex.flywire.ai/faq)

For this project:

- Join records using IDs.
- Initially select populations using `primary_type`.
- Preserve additional labels for inspection.
- Keep neurons without a type: missing annotation does not mean missing connectivity.
- Do not convert IDs to floating-point numbers. Python integers, appropriate database integer types, or strings can preserve them exactly; spreadsheet and JavaScript number conversions can lose precision.

## 4. Reading classification fields

These fields describe different aspects of a neuron. Broad-to-fine classification is useful, but it is not a graph path and does not tell you which neuron connects to which.

| Field | Interpretation |
| --- | --- |
| `flow` | Relationship to the brain boundary: afferent enters, efferent exits, intrinsic remains within it. |
| `super_class` | Broad category, such as sensory, central, or descending. |
| `class` | More specific classification. |
| `sub_class` | A finer subdivision where assigned. |
| `side` | Anatomical side annotation; interpret it using the source convention. |
| `hemilineage` | Developmental grouping within a neuronal lineage; useful for anatomical context, not needed for initial route queries. |
| `nerve` | Associated nerve where applicable. A nerve is a bundle of neuronal processes. |

The annotation repository documents the hierarchy and lineage fields. Its side convention uses soma position for brain-intrinsic neurons and nerve-entry side for sensory/ascending neurons. Do not infer that every branch or synapse lies on the annotated side. Annotation sources can differ, so retain the convention used by your export. [FlyWire annotation column definitions](https://github.com/flyconnectome/flywire_annotations/blob/main/supplemental_files/README.md)

Useful category vocabulary:

- **Sensory neuron:** carries information about a stimulus, such as light, touch, or odor.
- **Visual projection neuron:** carries processed visual information between visual-system regions and downstream centers.
- **Descending neuron:** carries information from the brain toward the ventral nerve cord.
- **Ascending neuron:** carries information toward the brain from the ventral nerve cord.
- **Motor neuron:** provides output to muscles.
- **Interneuron:** connects neurons within neural circuitry.
- **Ventral nerve cord, or VNC:** the insect central nervous system structure serving much of the body outside the brain.

Descending neurons and motor neurons are not interchangeable categories. For the initial application, DNp01 is the target endpoint; the project does not need to reconstruct the whole route to a muscle.

## 5. Reading connection rows

| Field | Meaning |
| --- | --- |
| `pre_root_id` | Presynaptic neuron ID: sending side of the connection. |
| `post_root_id` | Postsynaptic neuron ID: receiving side. |
| `neuropil` | Region containing the counted synapses. |
| `syn_count` | Number of counted synaptic contacts for that pair in that region. |
| `nt_type` | Transmitter annotation supplied with the connection export; preserve it and check its documented provenance before using it in a model. |

**Presynaptic** and **postsynaptic** are roles at a connection. The same neuron can receive from one partner and send to another. **Upstream** means toward input partners; **downstream** means toward output partners.

Region suffixes can identify hemispheres: `ME_L`, for example, is the left medulla. Region membership describes synapse location, not the location of the whole neuron. [FlyWire connectivity field definitions](https://zenodo.org/records/10676866)

### Rows are not the same as neuron-pair edges

Invented example:

```csv
pre_root_id,post_root_id,neuropil,syn_count
101,202,region_A,3
101,202,region_B,4
202,101,region_A,2
```

The first two rows describe one directed pair, `101 → 202`, with a total weight of `3 + 4 = 7`. The third row describes a separate reverse edge, `202 → 101`.

For this project's loader, check the reported uniqueness rule `(pre_root_id, post_root_id, neuropil)`. For neuron-level traversal, group rows by `(pre_root_id, post_root_id)` and sum `syn_count`.

FAFB's default connectivity threshold is five synapses per directed pair, summed across regions. Individual region rows may contain fewer than five. A filtered file cannot recover pairs omitted by that threshold. [Codex connectivity rules](https://codex.flywire.ai/faq)

Therefore, do not discard each region row with `syn_count < 5`. In the example, that would incorrectly remove the seven-synapse edge.

If you later restrict analysis to selected neuropils, explicitly decide whether the threshold applies inside those regions or across the whole brain. Those answer different questions.

## 6. Neurotransmitters and confidence

A **neurotransmitter** is a chemical messenger released at chemical synapses.

| Abbreviation | Name |
| --- | --- |
| `ACH` | Acetylcholine |
| `GABA` | Gamma-aminobutyric acid |
| `GLUT` | Glutamate |
| `DA` | Dopamine |
| `SER` | Serotonin |
| `OCT` | Octopamine |

Published FlyWire fields such as `ach_avg` and `gaba_avg` summarize transmitter prediction probabilities. Their aggregation level matters: an average for a connection is not automatically the same as an average for a whole neuron. [FlyWire neurotransmitter definitions](https://zenodo.org/records/10676866)

In your `neurons` export, inspect `nt_type`, `nt_type_score`, and any `*_avg` columns. Treat them as predicted labels and scores, not measurements of neurotransmitter concentration or firing rate. Confirm the exact export definitions before reproducing their calculation.

The annotation project's neuron-level method averages predictions over presynapses and selects the transmitter with the highest average confidence. That documents the general approach, but does not establish every Codex column's implementation. [Neuron annotation prediction method](https://github.com/flyconnectome/flywire_annotations/blob/main/supplemental_files/README.md)

**Excitatory** effects tend to promote activity; **inhibitory** effects tend to suppress it; **modulatory** effects alter how a circuit responds. Receptors and cellular context matter. Avoid automatically turning each transmitter label into a universal positive or negative edge weight.

For initial reachability, preserve transmitter metadata without using it to decide whether an anatomical path exists.

## 7. Escape-circuit vocabulary

| Term | Meaning for this project |
| --- | --- |
| Looming | An image expanding in the visual field, as when an object approaches. |
| LC4 | Lobula columnar type 4, a visual projection neuron type. |
| LPLC2 | Lobula plate/lobula columnar type 2, a visual projection neuron type. |
| Giant Fiber, or GF | A descending neuron involved in rapid escape. The project's target type is DNp01. |
| Population | A selected set of neurons, such as all cells labeled LC4. |
| Silencing | Experimentally suppressing neuronal activity or transmission. |
| Ablation | Removal or destruction of cells; in this software, a graph exclusion is only a structural approximation. |

Experiments identify LC4 and LPLC2 as direct visual inputs to the Giant Fiber. LC4 conveys information related to looming angular velocity, while LPLC2 contributes angular-size information. These are biological motivations for the selected endpoints, not conclusions to infer from synapse counts alone. [Ache and colleagues, 2019](https://doi.org/10.1016/j.cub.2019.01.079)

DNp01 is the Giant Fiber designation in descending-neuron nomenclature. [Namiki and colleagues, 2018](https://elifesciences.org/articles/34272)

The CSV graph does not contain stimulus responses, spike timing, or a complete behavioral model. Describe your output as surviving anatomical routes under selected rules.

## 8. Graph terms used by the application

| Term | Project meaning |
| --- | --- |
| Node or vertex | One neuron in the main analysis graph. |
| Directed edge | A connection from a presynaptic neuron to a postsynaptic neuron. |
| Weight | Initially, the summed synapse count for that directed pair. |
| Source | The neuron or population where a query starts. |
| Target | The neuron or population the query tries to reach. |
| Intermediate neuron | A neuron between the source and target on a route. |
| Hop | Traversing one edge. |
| Path | A sequence of connected nodes following edge direction. |
| Reachability | Whether at least one permitted directed path exists. |
| Shortest path | Initially, a path with the fewest hops. |
| Cycle | A directed route that returns to its starting node. |
| Self-loop | An edge from a neuron to itself. |
| In-degree | Number of distinct incoming neighbors, not number of synapses. |
| Out-degree | Number of distinct outgoing neighbors. |
| Input/output strength | Sum of incoming/outgoing edge weights. |
| Subgraph | A graph restricted to selected nodes or edges. |
| Baseline | The graph before the requested exclusions. |
| Exclusion | Removing selected nodes and their incident edges from an analysis. |
| Rollup | Aggregating individual neurons into groups, such as cell types. |

The route `101 → 303 → 202` has two hops. Its hop count says nothing by itself about physical length, transmission delay, or biological effectiveness.

Summed synapse count is a useful structural weight. It is not automatically a path cost: minimizing the sum of raw counts would favor weaker connections. Keep the first shortest-path algorithm unweighted.

### Why paths should remain neuron-level

Suppose neuron A connects to B1, while B2 connects to C. B1 and B2 share type B but have no connecting route. A type-level rollup shows `A → B → C`, although no corresponding neuron-level path exists.

Use the rollup for summaries; verify route claims on individual neurons. Keep unlabeled and other-type neurons available as intermediates.

When a source or target itself is excluded, report that separately from an intact endpoint becoming unreachable. Keep exclusions temporary; do not delete imported records.

## 9. File and database vocabulary

| Term | Meaning |
| --- | --- |
| CSV | Comma-separated values, with quoting rules for commas and line breaks inside fields. |
| Header | First CSV record naming the columns. |
| Row or record | One entry with values corresponding to the columns. |
| `.gz` | Gzip compression around a file. |
| Schema | Defined columns, types, relationships, and constraints. |
| Primary key | Unique identifier for a database record. |
| Foreign key | Reference to a record in another table. |
| Composite key | A key made from several columns, such as the connection triple. |
| Join | Combining records by matching keys. |
| Aggregation | Combining records into summaries, such as sums by neuron pair. |
| Null | Missing or unknown data; distinguish it from zero and empty text. |
| Index | Database structure that speeds selected lookups. |
| Streaming | Processing records incrementally rather than loading the entire file. |
| Idempotent import | A repeatable import whose rerun does not create unwanted duplicates. |

For a neuron annotation join, prefer keeping the base neuron even when its type annotation is missing. An inner join can silently discard untyped neurons; a left join preserves them.

## 10. Inspecting files in the terminal

Run commands from the project root, where `data/` contains the downloads.

```bash
# Header and first nine data lines
gunzip -c data/classification.csv.gz | head

# Header only
gunzip -c data/classification.csv.gz | head -n 1

# Header plus five data lines
gunzip -c data/consolidated_cell_types.csv.gz | head -n 6

# Browse without wrapping long lines
gunzip -c data/connections_princeton.csv.gz | less -S

# Check gzip integrity without unpacking the file
gzip -t data/connections_princeton.csv.gz
```

- `gunzip` decompresses gzip data.
- `-c` sends the decompressed text to standard output and preserves the original file.
- `|` passes one command's output to the next command's input.
- `head` stops after the requested number of lines.
- `less -S` opens a pager without wrapping long lines. Scroll horizontally with arrow keys, search with `/text`, and quit with `q`.
- `gzip -t` checks compression integrity; it does not validate biological content or CSV uniqueness.

When `head` exits early, the decompressor may report a broken pipe. That alone does not mean the gzip file is damaged.

These tools operate on text lines. A quoted CSV field can contain a newline, so line counts are not universally record counts. Likewise, `grep LC4` is a text search, not an exact `primary_type` filter. Use a CSV parser for import checks and final counts.

## 11. A first reading exercise

1. Inspect each header and a few records.
2. Find an LC4 row in `consolidated_cell_types` and copy its exact ID.
3. Find the same ID in `classification` and `neurons`.
4. Find connections where it is the presynaptic neuron.
5. Select one postsynaptic partner and find its type.
6. Check whether that pair appears in several neuropils; sum its counts.
7. Explain the connection in one sentence: “Neuron X, of type Y, connects to neuron Z through N counted contacts across these regions.”

For milestone 2, record the observed headers, missing-value conventions, identifier relationships, and connection uniqueness rule. Treat the earlier reported population and row counts as validation targets until your own parser reproduces them.

You are ready to design the database when you can distinguish a neuron ID from a type, a region row from a pair edge, and anatomical reachability from a prediction of escape behavior.
