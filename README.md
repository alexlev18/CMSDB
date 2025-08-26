# CMSDB

Utilities for managing the Electronic Support Measures (ESM) operator console database.

## Initialization

Run the initialization script to create the SQLite database and platform tables:

```
python initialize_esm_db.py
```

This creates `esm_operator.db` with tables for Platform, Aircraft, Facility, GroundUnit, Submarine, Ship, Satellite, and Weapon.

## Ingestion

Use the ingestion CLI to load CSV or JSON data into the database. Sample CSV files are provided in the `templates/` directory.

```
python ingest.py csv Aircraft templates/Aircraft.csv
python ingest.py json Ship data/ships.json
```
