# CMSDB

Utilities for managing the Electronic Support Measures (ESM) operator console database.

## Initialization

Run the initialization script to create the SQLite database and platform tables:

```
python initialize_esm_db.py
```

This creates `esm_operator.db` with tables for Platform, Aircraft, Facility, GroundUnit, Submarine, Ship, Satellite, and Weapon.
