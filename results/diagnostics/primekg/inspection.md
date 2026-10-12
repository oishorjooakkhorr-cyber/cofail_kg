# S4 raw inspection

Inputs extracted byte-for-byte from `data/prime_kg.zip`: `kg.csv` and `nodes.csv`.

Edge rows: 8,100,498. Unique canonical node indices: 129,375.
Every occurrence of each index agrees on ID, name, type, and source; the two input files agree exactly.

## Columns and five example rows

`relation`, `display_relation`, `x_index`, `x_id`, `x_type`, `x_name`, `x_source`, `y_index`, `y_id`, `y_type`, `y_name`, `y_source`

```json
[
  {
    "display_relation": "ppi",
    "relation": "protein_protein",
    "x_id": "9796",
    "x_index": "0",
    "x_name": "PHYHIP",
    "x_source": "NCBI",
    "x_type": "gene/protein",
    "y_id": "56992",
    "y_index": "8889",
    "y_name": "KIF15",
    "y_source": "NCBI",
    "y_type": "gene/protein"
  },
  {
    "display_relation": "ppi",
    "relation": "protein_protein",
    "x_id": "7918",
    "x_index": "1",
    "x_name": "GPANK1",
    "x_source": "NCBI",
    "x_type": "gene/protein",
    "y_id": "9240",
    "y_index": "2798",
    "y_name": "PNMA1",
    "y_source": "NCBI",
    "y_type": "gene/protein"
  },
  {
    "display_relation": "ppi",
    "relation": "protein_protein",
    "x_id": "8233",
    "x_index": "2",
    "x_name": "ZRSR2",
    "x_source": "NCBI",
    "x_type": "gene/protein",
    "y_id": "23548",
    "y_index": "5646",
    "y_name": "TTC33",
    "y_source": "NCBI",
    "y_type": "gene/protein"
  },
  {
    "display_relation": "ppi",
    "relation": "protein_protein",
    "x_id": "4899",
    "x_index": "3",
    "x_name": "NRF1",
    "x_source": "NCBI",
    "x_type": "gene/protein",
    "y_id": "11253",
    "y_index": "11592",
    "y_name": "MAN1B1",
    "y_source": "NCBI",
    "y_type": "gene/protein"
  },
  {
    "display_relation": "ppi",
    "relation": "protein_protein",
    "x_id": "5297",
    "x_index": "4",
    "x_name": "PI4KA",
    "x_source": "NCBI",
    "x_type": "gene/protein",
    "y_id": "8601",
    "y_index": "2122",
    "y_name": "RGS20",
    "y_source": "NCBI",
    "y_type": "gene/protein"
  }
]
```

## Relation and display-label counts

| Relation | Display label | Source type | Target type | Rows |
|---|---|---|---|---|
| anatomy_anatomy | parent-child | anatomy | anatomy | 28064 |
| anatomy_protein_absent | expression absent | anatomy | gene/protein | 19887 |
| anatomy_protein_absent | expression absent | gene/protein | anatomy | 19887 |
| anatomy_protein_present | expression present | anatomy | gene/protein | 1518203 |
| anatomy_protein_present | expression present | gene/protein | anatomy | 1518203 |
| bioprocess_bioprocess | parent-child | biological_process | biological_process | 105772 |
| bioprocess_protein | interacts with | biological_process | gene/protein | 144805 |
| bioprocess_protein | interacts with | gene/protein | biological_process | 144805 |
| cellcomp_cellcomp | parent-child | cellular_component | cellular_component | 9690 |
| cellcomp_protein | interacts with | cellular_component | gene/protein | 83402 |
| cellcomp_protein | interacts with | gene/protein | cellular_component | 83402 |
| contraindication | contraindication | disease | drug | 30675 |
| contraindication | contraindication | drug | disease | 30675 |
| disease_disease | parent-child | disease | disease | 64388 |
| disease_phenotype_negative | phenotype absent | disease | effect/phenotype | 1193 |
| disease_phenotype_negative | phenotype absent | effect/phenotype | disease | 1193 |
| disease_phenotype_positive | phenotype present | disease | effect/phenotype | 150317 |
| disease_phenotype_positive | phenotype present | effect/phenotype | disease | 150317 |
| disease_protein | associated with | disease | gene/protein | 80411 |
| disease_protein | associated with | gene/protein | disease | 80411 |
| drug_drug | synergistic interaction | drug | drug | 2672628 |
| drug_effect | side effect | drug | effect/phenotype | 64784 |
| drug_effect | side effect | effect/phenotype | drug | 64784 |
| drug_protein | carrier | drug | gene/protein | 864 |
| drug_protein | carrier | gene/protein | drug | 864 |
| drug_protein | enzyme | drug | gene/protein | 5317 |
| drug_protein | enzyme | gene/protein | drug | 5317 |
| drug_protein | target | drug | gene/protein | 16380 |
| drug_protein | target | gene/protein | drug | 16380 |
| drug_protein | transporter | drug | gene/protein | 3092 |
| drug_protein | transporter | gene/protein | drug | 3092 |
| exposure_bioprocess | interacts with | biological_process | exposure | 1625 |
| exposure_bioprocess | interacts with | exposure | biological_process | 1625 |
| exposure_cellcomp | interacts with | cellular_component | exposure | 10 |
| exposure_cellcomp | interacts with | exposure | cellular_component | 10 |
| exposure_disease | linked to | disease | exposure | 2304 |
| exposure_disease | linked to | exposure | disease | 2304 |
| exposure_exposure | parent-child | exposure | exposure | 4140 |
| exposure_molfunc | interacts with | exposure | molecular_function | 45 |
| exposure_molfunc | interacts with | molecular_function | exposure | 45 |
| exposure_protein | interacts with | exposure | gene/protein | 1212 |
| exposure_protein | interacts with | gene/protein | exposure | 1212 |
| indication | indication | disease | drug | 9388 |
| indication | indication | drug | disease | 9388 |
| molfunc_molfunc | parent-child | molecular_function | molecular_function | 27148 |
| molfunc_protein | interacts with | gene/protein | molecular_function | 69530 |
| molfunc_protein | interacts with | molecular_function | gene/protein | 69530 |
| off-label use | off-label use | disease | drug | 2568 |
| off-label use | off-label use | drug | disease | 2568 |
| pathway_pathway | parent-child | pathway | pathway | 5070 |
| pathway_protein | interacts with | gene/protein | pathway | 42646 |
| pathway_protein | interacts with | pathway | gene/protein | 42646 |
| phenotype_phenotype | parent-child | effect/phenotype | effect/phenotype | 37472 |
| phenotype_protein | associated with | effect/phenotype | gene/protein | 3330 |
| phenotype_protein | associated with | gene/protein | effect/phenotype | 3330 |
| protein_protein | ppi | gene/protein | gene/protein | 642150 |

## Reverse-row sample

Python `random.Random(42).sample`, 10,000 rows without replacement; reverse identity is (relation, y_index, x_index).

| Relation | Sampled | Reverse present |
|---|---|---|
| anatomy_anatomy | 34 | 34 |
| anatomy_protein_absent | 63 | 63 |
| anatomy_protein_present | 3702 | 3702 |
| bioprocess_bioprocess | 127 | 127 |
| bioprocess_protein | 379 | 379 |
| cellcomp_cellcomp | 14 | 14 |
| cellcomp_protein | 182 | 182 |
| contraindication | 85 | 85 |
| disease_disease | 100 | 100 |
| disease_phenotype_negative | 2 | 2 |
| disease_phenotype_positive | 395 | 395 |
| disease_protein | 180 | 180 |
| drug_drug | 3282 | 3282 |
| drug_effect | 157 | 157 |
| drug_protein | 64 | 64 |
| exposure_bioprocess | 6 | 6 |
| exposure_cellcomp | 0 | 0 |
| exposure_disease | 7 | 7 |
| exposure_exposure | 4 | 4 |
| exposure_molfunc | 0 | 0 |
| exposure_protein | 3 | 3 |
| indication | 36 | 36 |
| molfunc_molfunc | 38 | 38 |
| molfunc_protein | 177 | 177 |
| off-label use | 7 | 7 |
| pathway_pathway | 8 | 8 |
| pathway_protein | 116 | 116 |
| phenotype_phenotype | 52 | 52 |
| phenotype_protein | 9 | 9 |
| protein_protein | 771 | 771 |

## Node types

| Type | Nodes |
|---|---|
| anatomy | 14035 |
| biological_process | 28642 |
| cellular_component | 4176 |
| disease | 17080 |
| drug | 7957 |
| effect/phenotype | 15311 |
| exposure | 818 |
| gene/protein | 27671 |
| molecular_function | 11169 |
| pathway | 2516 |

## Input checksums

```json
{
  "kg.csv": {
    "bytes": 981751236,
    "md5": "aac8191d4fbc5bf09cdf8c3c78b4e75f",
    "sha256": "0a5a010fcd88dcec572a573d98c26c1c244a11567092b6161d3ded611cfb5c69"
  },
  "nodes.csv": {
    "bytes": 7869553,
    "md5": "7f9ab4109c54049e819ecd14e15a6038",
    "sha256": "301644c421b436fb6d5f548954a5d77749d87ff8ecbf27d42f41c07a075a2ad3"
  }
}
```

The full kg.csv MD5 matches the published value recorded in `docs/S4_findings.md`.
The nodes.csv MD5 begins with the published prefix `7f9ab410` recorded there;
the earlier report does not record the full published node-file digest.
An attempt to retrieve fresh Harvard Dataverse API metadata on 2026-10-12 returned HTTP 403,
so this run does not independently confirm the full published nodes.csv checksum.
Unlike the earlier `nodes.tab` inspection, this archive supplies `nodes.csv`; the standard CSV parser reproduces every node field in `kg.csv`, including node 98266.

This inspection computes candidate S4 values. It does not fill the protocol or freeze the graph fingerprint.
