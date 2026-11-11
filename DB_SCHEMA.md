# Database Schema

This document defines the proposed PSQL schema.

## 1. Overview

| Table | One row represents | Source files |
|---|---|---|
| `Neuron` | One individual neuron | `classification.csv.gz`, `neurons.csv.gz` |
| `CellType` | One distinct cell-type label | `consolidated_cell_types.csv.gz` |
| `NeuronCellType` | One assignment of a neuron to a cell type | `consolidated_cell_types.csv.gz` |
| `Connection` | One directed neuron pair within one neuropil | `connections_princeton.csv.gz` |


## Neurons
