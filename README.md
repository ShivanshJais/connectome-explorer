# connectome-explorer

Remove cell types from the fruit fly connectome and see which sensory-to-descending routes survive. A small learning project with Django, PostgreSQL and Docker, built on FlyWire FAFB v783.

Work in progress.

## Data

The data is not in this repo. Sign in at [FlyWire Codex](https://codex.flywire.ai/api/download), choose FAFB v783, and put these files in `data/`:

- `classification.csv.gz`
- `consolidated_cell_types.csv.gz`
- `connections_princeton.csv.gz` (Connections, Filtered)
- `neurons.csv.gz`

Downloading means accepting the [FlyWire Terms of Service](https://flywire.ai/tos). Cite the FlyWire papers when using the data.

## Dev setup

```sh
docker compose up -d
```

Adminer runs at http://localhost:8080.
