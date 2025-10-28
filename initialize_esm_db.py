import sqlite3
from typing import Dict, Sequence

DB_FILE = "esm_operator.db"

TABLES: Dict[str, str] = {
    "Platform": """
        CREATE TABLE IF NOT EXISTS Platform (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Domain TEXT,
            Agility TEXT,
            DamagePoints INTEGER,
            OODA TEXT,
            Notes TEXT
        );
    """,
    "Aircraft": """
        CREATE TABLE IF NOT EXISTS Aircraft (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Agility TEXT,
            Length REAL,
            Span REAL,
            Height REAL,
            Crew INTEGER,
            Armor TEXT,
            MaxWeight REAL,
            MaxPayload REAL,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "Facility": """
        CREATE TABLE IF NOT EXISTS Facility (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Personnel INTEGER,
            Armor TEXT,
            MaxCapacity INTEGER,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "GroundUnit": """
        CREATE TABLE IF NOT EXISTS GroundUnit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Mobility TEXT,
            Length REAL,
            Width REAL,
            Height REAL,
            Crew INTEGER,
            Armor TEXT,
            MaxSpeed REAL,
            Range REAL,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "Submarine": """
        CREATE TABLE IF NOT EXISTS Submarine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Displacement REAL,
            Length REAL,
            Beam REAL,
            Draft REAL,
            Crew INTEGER,
            Armor TEXT,
            MaxDepth REAL,
            MaxSpeed REAL,
            Range REAL,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "Ship": """
        CREATE TABLE IF NOT EXISTS Ship (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Displacement REAL,
            Length REAL,
            Beam REAL,
            Draft REAL,
            Crew INTEGER,
            Armor TEXT,
            MaxSpeed REAL,
            Range REAL,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "Satellite": """
        CREATE TABLE IF NOT EXISTS Satellite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            OrbitType TEXT,
            Altitude REAL,
            Mass REAL,
            Power REAL,
            Mission TEXT,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
    "Weapon": """
        CREATE TABLE IF NOT EXISTS Weapon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
            Country TEXT,
            PhysicalSize TEXT,
            Type TEXT,
            Range REAL,
            Guidance TEXT,
            Speed REAL,
            Warhead TEXT,
            LaunchPlatform TEXT,
            DamagePoints INTEGER,
            OODA TEXT
        );
    """,
}

SAMPLE_DATA: Dict[str, Dict[str, Sequence[Sequence[object]]]] = {
    "Platform": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Domain",
            "Agility",
            "DamagePoints",
            "OODA",
            "Notes",
        ],
        "rows": [
            (
                "E-3 Sentry",
                "United States",
                "Airborne Early Warning",
                "Large",
                "AWACS",
                "Air",
                "Moderate",
                55,
                "Deliberate",
                "Airborne radar and battle management platform.",
            ),
            (
                "Bayraktar TB2",
                "Turkey",
                "Unmanned Aerial Vehicle",
                "Medium",
                "MALE UAV",
                "Air",
                "Low",
                25,
                "Tactical",
                "Medium-altitude long-endurance reconnaissance and strike drone.",
            ),
        ],
    },
    "Aircraft": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Agility",
            "Length",
            "Span",
            "Height",
            "Crew",
            "Armor",
            "MaxWeight",
            "MaxPayload",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "F-16 Fighting Falcon",
                "United States",
                "Fighter",
                "Medium",
                "Multirole Fighter",
                "High",
                15.0,
                9.96,
                4.8,
                1,
                "Composite",
                19.2,
                7.7,
                45,
                "Rapid",
            ),
            (
                "Su-35 Flanker-E",
                "Russia",
                "Fighter",
                "Large",
                "Air Superiority Fighter",
                "Very High",
                21.9,
                15.3,
                5.9,
                1,
                "Titanium Alloy",
                34.5,
                8.0,
                52,
                "Aggressive",
            ),
            (
                "JAS 39 Gripen",
                "Sweden",
                "Fighter",
                "Compact",
                "Lightweight Multirole",
                "High",
                14.1,
                8.4,
                4.5,
                1,
                "Composite",
                14.0,
                5.3,
                38,
                "Responsive",
            ),
        ],
    },
    "Facility": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Personnel",
            "Armor",
            "MaxCapacity",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "Ramstein Air Base",
                "Germany",
                "Air Base",
                "Large",
                "Air Force Installation",
                8600,
                "Hardened Shelters",
                120,
                80,
                "Strategic",
            ),
            (
                "Diego Garcia Support Facility",
                "United Kingdom",
                "Naval Support",
                "Medium",
                "Logistics Hub",
                2000,
                "Reinforced",
                40,
                60,
                "Strategic",
            ),
        ],
    },
    "GroundUnit": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Mobility",
            "Length",
            "Width",
            "Height",
            "Crew",
            "Armor",
            "MaxSpeed",
            "Range",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "M1A2 Abrams",
                "United States",
                "Main Battle Tank",
                "Large",
                "Armored",
                "Tracked",
                9.77,
                3.66,
                2.44,
                4,
                "Chobham",
                67.0,
                426,
                70,
                "Decisive",
            ),
            (
                "Leopard 2A7",
                "Germany",
                "Main Battle Tank",
                "Large",
                "Armored",
                "Tracked",
                10.97,
                3.75,
                3.0,
                4,
                "Composite",
                68.0,
                450,
                68,
                "Decisive",
            ),
        ],
    },
    "Submarine": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Displacement",
            "Length",
            "Beam",
            "Draft",
            "Crew",
            "Armor",
            "MaxDepth",
            "MaxSpeed",
            "Range",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "Virginia-class Block V",
                "United States",
                "Attack Submarine",
                "Large",
                "Nuclear",
                10200,
                115.0,
                10.4,
                9.8,
                132,
                "HY-100 Steel",
                488.0,
                25.0,
                12000,
                85,
                "Stealth",
            ),
            (
                "Yasen-class",
                "Russia",
                "Attack Submarine",
                "Large",
                "Nuclear",
                13800,
                139.0,
                13.0,
                10.0,
                90,
                "Steel-Titanium",
                520.0,
                31.0,
                15000,
                88,
                "Stealth",
            ),
        ],
    },
    "Ship": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Displacement",
            "Length",
            "Beam",
            "Draft",
            "Crew",
            "Armor",
            "MaxSpeed",
            "Range",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "Arleigh Burke-class Destroyer",
                "United States",
                "Destroyer",
                "Large",
                "Guided Missile Destroyer",
                9200,
                155.0,
                20.0,
                9.3,
                320,
                "Kevlar Protection",
                31.0,
                8330,
                78,
                "Coordinated",
            ),
            (
                "Type 052D Luyang III",
                "China",
                "Destroyer",
                "Large",
                "Guided Missile Destroyer",
                7500,
                157.0,
                17.0,
                10.0,
                280,
                "Steel",
                30.0,
                4500,
                72,
                "Coordinated",
            ),
            (
                "Queen Elizabeth-class Carrier",
                "United Kingdom",
                "Aircraft Carrier",
                "Very Large",
                "Fleet Carrier",
                65000,
                284.0,
                73.0,
                11.0,
                700,
                "Armored Deck",
                25.0,
                10000,
                95,
                "Coordinated",
            ),
        ],
    },
    "Satellite": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "OrbitType",
            "Altitude",
            "Mass",
            "Power",
            "Mission",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "USA-245",
                "United States",
                "Reconnaissance",
                "Medium",
                "Optical Imaging",
                "Low Earth Orbit",
                280.0,
                19600.0,
                13.0,
                "Imagery Intelligence",
                50,
                "Surveillance",
            ),
            (
                "Kosmos-2558",
                "Russia",
                "Inspection",
                "Compact",
                "Spacecraft",
                "Low Earth Orbit",
                435.0,
                500.0,
                3.0,
                "Orbital Inspection",
                35,
                "Surveillance",
            ),
        ],
    },
    "Weapon": {
        "columns": [
            "Name",
            "Country",
            "Category",
            "PhysicalSize",
            "Type",
            "Range",
            "Guidance",
            "Speed",
            "Warhead",
            "LaunchPlatform",
            "DamagePoints",
            "OODA",
        ],
        "rows": [
            (
                "AIM-120 AMRAAM",
                "United States",
                "Air-to-Air Missile",
                "Compact",
                "Beyond-Visual-Range",
                180.0,
                "Active Radar",
                4.0,
                "High-Explosive",
                "Fighter Aircraft",
                40,
                "Reactive",
            ),
            (
                "R-77",
                "Russia",
                "Air-to-Air Missile",
                "Compact",
                "Beyond-Visual-Range",
                110.0,
                "Active Radar",
                3.5,
                "Fragmentation",
                "Fighter Aircraft",
                38,
                "Reactive",
            ),
            (
                "AM39 Exocet",
                "France",
                "Anti-Ship Missile",
                "Compact",
                "Sea Skimming",
                70.0,
                "Inertial/Active Radar",
                0.9,
                "210 kg High-Explosive",
                "Ship, Aircraft",
                55,
                "Reactive",
            ),
        ],
    },
}


def ensure_country_column(conn: sqlite3.Connection, table: str) -> None:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cur.fetchall()}
    if "Country" not in columns:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN Country TEXT")


def populate_sample_data(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table, payload in SAMPLE_DATA.items():
        columns: Sequence[str] = payload["columns"]
        rows: Sequence[Sequence[object]] = payload["rows"]
        if not rows:
            continue
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        if cur.fetchone()[0] > 0:
            continue
        column_list = ", ".join(columns)
        placeholders = ", ".join("?" for _ in columns)
        statement = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"
        cur.executemany(statement, rows)


def initialize_database(db_file: str = DB_FILE) -> None:
    """Create the database, required tables, and example data."""
    conn = sqlite3.connect(db_file)
    try:
        cur = conn.cursor()
        for ddl in TABLES.values():
            cur.execute(ddl)
        for table in TABLES:
            ensure_country_column(conn, table)
        populate_sample_data(conn)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
