import sqlite3

DB_FILE = "esm_operator.db"

TABLES = {
    "Platform": """
        CREATE TABLE IF NOT EXISTS Platform (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT,
            Category TEXT,
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
    """
}

def initialize_database(db_file: str = DB_FILE) -> None:
    """Create the database and required tables."""
    conn = sqlite3.connect(db_file)
    try:
        cur = conn.cursor()
        for ddl in TABLES.values():
            cur.execute(ddl)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    initialize_database()
