import sqlite3
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk
from typing import Dict, List, Optional, Sequence, Tuple

from initialize_esm_db import DB_FILE, TABLES, initialize_database

DARK_BG = "#101010"
PANEL_BG = "#161616"
LIST_BG = "#131313"
DETAIL_BG = "#0f0f0f"
ACCENT_COLOR = "#5ef2b0"
TEXT_COLOR = "#e6fff3"
TITLE_FONT = ("Courier", 18, "bold")
LABEL_FONT = ("Courier", 12, "bold")
TEXT_FONT = ("Courier", 12)
LIST_FONT = ("Courier", 12)

ALL_TABLES_ORDER = [
    "Weapon",
    "Ship",
    "Submarine",
    "Aircraft",
    "Platform",
    "GroundUnit",
    "Facility",
    "Satellite",
]

TABLE_DISPLAY_NAMES = {
    "Weapon": "Weapon",
    "Ship": "Ship",
    "Submarine": "Submarine",
    "Aircraft": "Aircraft",
    "Platform": "Platform",
    "GroundUnit": "Unit",
    "Facility": "Facility",
    "Satellite": "Satellite",
}

TYPE_CONFIG = OrderedDict(
    [
        ("All Types", {"tables": ALL_TABLES_ORDER}),
        ("Weapons", {"tables": ["Weapon"]}),
        ("Ships", {"tables": ["Ship"]}),
        ("Aircraft", {"tables": ["Aircraft"]}),
        (
            "Drones",
            {
                "tables": ["Platform"],
                "keywords": ["unmanned", "drone", "uav"],
            },
        ),
        ("Units", {"tables": ["GroundUnit"]}),
        ("Facilities", {"tables": ["Facility"]}),
        ("Submarines", {"tables": ["Submarine"]}),
        ("Satellites", {"tables": ["Satellite"]}),
        ("Platforms", {"tables": ["Platform"]}),
    ]
)

SPECIAL_COUNTRIES = ["Generic", "Terrorist", "Civilian"]


class MilitaryCatalogApp:
    """Dark-themed catalog browser for the CMSDB dataset."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("CMSDB Military Catalog")
        self.master.configure(bg=DARK_BG)
        self.master.geometry("1024x640")
        self.master.minsize(820, 520)

        initialize_database()
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

        self.column_cache: Dict[str, List[str]] = {}
        self.list_data: List[Tuple[str, int]] = []

        self._build_ui()
        self.refresh_country_options()
        self.refresh_platform_list()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Escape>", lambda _: self.on_close())

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Filter.TCombobox", fieldbackground=LIST_BG, background=LIST_BG, foreground=TEXT_COLOR, arrowcolor=ACCENT_COLOR, borderwidth=0)
        style.map(
            "Filter.TCombobox",
            fieldbackground=[("readonly", LIST_BG)],
            foreground=[("readonly", TEXT_COLOR)],
        )
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background=LIST_BG,
            darkcolor=LIST_BG,
            lightcolor=LIST_BG,
            troughcolor=DARK_BG,
            bordercolor=LIST_BG,
        )

        self.master.option_add("*TCombobox*Listbox.background", LIST_BG)
        self.master.option_add("*TCombobox*Listbox.foreground", TEXT_COLOR)
        self.master.option_add("*TCombobox*Listbox.selectBackground", ACCENT_COLOR)
        self.master.option_add("*TCombobox*Listbox.selectForeground", DARK_BG)

    def _build_ui(self) -> None:
        self._configure_styles()

        header = tk.Frame(self.master, bg=DARK_BG)
        header.pack(fill=tk.X, padx=24, pady=(20, 10))

        title_label = tk.Label(
            header,
            text="CMSDB Military Catalog",
            fg=ACCENT_COLOR,
            bg=DARK_BG,
            font=TITLE_FONT,
            anchor="w",
        )
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        content = tk.Frame(self.master, bg=DARK_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))

        filters_panel = tk.Frame(content, bg=PANEL_BG, padx=18, pady=18)
        filters_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 18))
        filters_panel.pack_propagate(False)

        type_label = tk.Label(
            filters_panel,
            text="Type",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=LABEL_FONT,
            anchor="w",
        )
        type_label.pack(fill=tk.X)

        self.type_var = tk.StringVar(value=list(TYPE_CONFIG.keys())[0])
        self.type_menu = ttk.Combobox(
            filters_panel,
            textvariable=self.type_var,
            values=list(TYPE_CONFIG.keys()),
            state="readonly",
            style="Filter.TCombobox",
        )
        self.type_menu.pack(fill=tk.X, pady=(6, 18))
        self.type_menu.bind("<<ComboboxSelected>>", self.on_filter_change)

        filter_by_label = tk.Label(
            filters_panel,
            text="Filter by",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=LABEL_FONT,
            anchor="w",
        )
        filter_by_label.pack(fill=tk.X)

        class_label = tk.Label(
            filters_panel,
            text="Class keyword",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Courier", 11),
            anchor="w",
        )
        class_label.pack(fill=tk.X, pady=(12, 0))

        self.class_var = tk.StringVar()
        self.class_entry = tk.Entry(
            filters_panel,
            textvariable=self.class_var,
            bg=LIST_BG,
            fg=TEXT_COLOR,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            font=TEXT_FONT,
        )
        self.class_entry.pack(fill=tk.X, pady=(4, 12))
        self.class_entry.bind("<KeyRelease>", self.on_filter_change)

        country_label = tk.Label(
            filters_panel,
            text="Country",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=("Courier", 11),
            anchor="w",
        )
        country_label.pack(fill=tk.X)

        self.country_var = tk.StringVar(value="All Countries")
        self.country_menu = ttk.Combobox(
            filters_panel,
            textvariable=self.country_var,
            values=("All Countries",),
            state="readonly",
            style="Filter.TCombobox",
        )
        self.country_menu.pack(fill=tk.X, pady=(4, 0))
        self.country_menu.bind("<<ComboboxSelected>>", self.on_filter_change)

        right_panel = tk.Frame(content, bg=PANEL_BG, padx=18, pady=18)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        list_label = tk.Label(
            right_panel,
            text="Available Platforms",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=LABEL_FONT,
            anchor="w",
        )
        list_label.pack(fill=tk.X)

        list_container = tk.Frame(right_panel, bg=PANEL_BG)
        list_container.pack(fill=tk.BOTH, expand=True, pady=(8, 16))

        self.platform_list = tk.Listbox(
            list_container,
            bg=LIST_BG,
            fg=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            selectforeground=DARK_BG,
            activestyle="none",
            relief=tk.FLAT,
            font=LIST_FONT,
            highlightthickness=0,
            exportselection=False,
        )
        self.platform_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_scroll = ttk.Scrollbar(
            list_container,
            orient=tk.VERTICAL,
            command=self.platform_list.yview,
            style="Vertical.TScrollbar",
        )
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.platform_list.configure(yscrollcommand=list_scroll.set)
        self.platform_list.bind("<<ListboxSelect>>", self.on_platform_select)

        details_label = tk.Label(
            right_panel,
            text="Details",
            fg=TEXT_COLOR,
            bg=PANEL_BG,
            font=LABEL_FONT,
            anchor="w",
        )
        details_label.pack(fill=tk.X)

        self.details_text = tk.Text(
            right_panel,
            bg=DETAIL_BG,
            fg=TEXT_COLOR,
            insertbackground=ACCENT_COLOR,
            relief=tk.FLAT,
            font=TEXT_FONT,
            wrap=tk.WORD,
            height=12,
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        detail_scroll = ttk.Scrollbar(
            right_panel,
            orient=tk.VERTICAL,
            command=self.details_text.yview,
            style="Vertical.TScrollbar",
        )
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.configure(yscrollcommand=detail_scroll.set)
        self.details_text.configure(state=tk.DISABLED)

        self.display_message(
            [
                "Use the selectors to browse the catalog.",
                "Choose a platform on the right to view its details.",
            ]
        )

    def refresh_country_options(self) -> None:
        cursor = self.conn.cursor()
        countries = set()
        for table in TABLES:
            cursor.execute(
                f"SELECT DISTINCT Country FROM {table} WHERE Country IS NOT NULL AND TRIM(Country) != ''"
            )
            countries.update(row[0] for row in cursor.fetchall() if row[0])
        countries.update(SPECIAL_COUNTRIES)
        sorted_countries = sorted(countries)
        values = ["All Countries", *sorted_countries]
        self.country_menu.configure(values=values)
        if self.country_var.get() not in values:
            self.country_var.set("All Countries")

    def on_filter_change(self, event: Optional[tk.Event] = None) -> None:
        self.refresh_platform_list()

    def refresh_platform_list(self) -> None:
        self.platform_list.delete(0, tk.END)
        self.platform_list.selection_clear(0, tk.END)
        self.list_data = []

        selected_type = self.type_var.get()
        config = TYPE_CONFIG.get(selected_type, TYPE_CONFIG["All Types"])
        tables = config.get("tables", [])
        keywords = [kw.lower() for kw in config.get("keywords", [])]

        class_filter = self.class_var.get().strip().lower()
        country_filter = self.country_var.get()

        cursor = self.conn.cursor()
        matches: List[Tuple[str, int, str, str]] = []

        for table in tables:
            if table not in TABLES:
                continue

            conditions: List[str] = []
            params: List[object] = []

            if country_filter and country_filter != "All Countries":
                conditions.append("Country = ?")
                params.append(country_filter)

            if class_filter:
                like_value = f"%{class_filter}%"
                conditions.append(
                    "(LOWER(IFNULL(Name, '')) LIKE ? OR "
                    "LOWER(IFNULL(Category, '')) LIKE ? OR "
                    "LOWER(IFNULL(Type, '')) LIKE ?)"
                )
                params.extend([like_value, like_value, like_value])

            if keywords:
                keyword_clauses: List[str] = []
                for keyword in keywords:
                    keyword_clauses.append(
                        "(LOWER(IFNULL(Category, '')) LIKE ? OR LOWER(IFNULL(Type, '')) LIKE ?)"
                    )
                    pattern = f"%{keyword}%"
                    params.extend([pattern, pattern])
                if keyword_clauses:
                    conditions.append("(" + " OR ".join(keyword_clauses) + ")")

            query = f"SELECT id, Name, Country FROM {table}"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY LOWER(IFNULL(Name, ''))"

            cursor.execute(query, params)
            for row in cursor.fetchall():
                name = row["Name"] or "(Unnamed)"
                country = row["Country"] or "Unknown"
                matches.append((table, row["id"], name, country))

        matches.sort(key=lambda item: item[2].lower())

        display_hint = "Select a platform from the list to view its details."
        if not matches:
            self.display_message(
                [
                    "No matching platforms found.",
                    "Adjust the filters to explore other catalog entries.",
                ]
            )
            return

        for table, record_id, name, country in matches:
            if selected_type == "Drones":
                display_type = "Drone"
            else:
                display_type = TABLE_DISPLAY_NAMES.get(table, table)
            entry_text = f"{name} — {country} [{display_type}]"
            self.platform_list.insert(tk.END, entry_text)
            self.list_data.append((table, record_id))

        self.display_message([display_hint])

    def on_platform_select(self, event: tk.Event) -> None:  # pragma: no cover - UI callback
        if not self.list_data:
            return
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        table, record_id = self.list_data[index]
        self.show_unit_details(table, record_id)

    def get_table_columns(self, table: str) -> List[str]:
        if table not in self.column_cache:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            self.column_cache[table] = [info[1] for info in cursor.fetchall() if info[1] != "id"]
        return self.column_cache[table]

    def show_unit_details(self, table: str, record_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        if row is None:
            self.display_message(["Record unavailable."])
            return

        columns = self.get_table_columns(table)
        lines: List[str] = [row["Name"] or "Unnamed Entry", ""]
        for column in columns:
            if column == "Name":
                continue
            value = row[column]
            if value in (None, ""):
                continue
            if isinstance(value, float):
                value_text = f"{value:.2f}".rstrip("0").rstrip(".")
            else:
                value_text = str(value)
            lines.append(f"{column}: {value_text}")

        self.display_message(lines)

    def display_message(self, lines: Sequence[str]) -> None:
        text = "\n".join(lines)
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete("1.0", tk.END)
        self.details_text.insert(tk.END, text)
        self.details_text.configure(state=tk.DISABLED)

    def on_close(self) -> None:
        try:
            self.conn.close()
        finally:
            self.master.destroy()


def main() -> None:
    root = tk.Tk()
    app = MilitaryCatalogApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
