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
from typing import Dict, List, Sequence, Tuple

from initialize_esm_db import DB_FILE, initialize_database

CATEGORY_TABLES = OrderedDict(
    [
        ("Platforms", "Platform"),
        ("Aircraft", "Aircraft"),
        ("Ships", "Ship"),
        ("Submarines", "Submarine"),
        ("Ground Units", "GroundUnit"),
        ("Facilities", "Facility"),
        ("Satellites", "Satellite"),
        ("Weapons", "Weapon"),
    ]
)


class MilitaryCatalogApp:
    """Minimalist catalog browser for the CMSDB dataset."""

    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        self.master.title("CMSDB Military Catalog")
        self.master.configure(bg=DARK_BG)
        self.master.geometry("1024x640")
        self.master.minsize(820, 520)
        self.master.configure(bg="#001b00")
        self.master.geometry("960x600")
        self.master.minsize(720, 480)

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
        self.node_metadata: Dict[str, Dict[str, object]] = {}
        self.column_cache: Dict[str, List[str]] = {}

        self._build_ui()
        self.populate_tree()
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
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
        style.configure(
            "Treeview",
            background="#001b00",
            foreground="#00ff66",
            fieldbackground="#001b00",
            font=("Courier", 11),
            rowheight=24,
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", "#013220")],
            foreground=[("selected", "#a6ffae")],
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
            background="#001b00",
            darkcolor="#001b00",
            lightcolor="#001b00",
            troughcolor="#000a00",
            bordercolor="#001b00",
        )

        title_label = tk.Label(
            self.master,
            text="CMSDB Military Catalog",
            fg="#00ff66",
            bg="#001b00",
            font=("Courier", 18, "bold"),
            pady=10,
        )
        title_label.pack(fill=tk.X)

        separator = ttk.Separator(self.master, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, padx=18)

        content = tk.Frame(self.master, bg="#001b00")
        content.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        tree_frame = tk.Frame(content, bg="#001b00")
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        self.tree = ttk.Treeview(tree_frame, show="tree")
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, style="Vertical.TScrollbar")
        tree_scroll.configure(command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        details_frame = tk.Frame(content, bg="#001b00")
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        details_label = tk.Label(
            details_frame,
            text="Details",
            fg="#00ff66",
            bg="#001b00",
            font=("Courier", 14, "bold"),
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
            details_frame,
            bg="#000f00",
            fg="#00ff66",
            insertbackground="#00ff66",
            font=("Courier", 12),
            relief=tk.FLAT,
            wrap=tk.WORD,
            height=10,
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        detail_scroll = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, style="Vertical.TScrollbar")
        detail_scroll.configure(command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=detail_scroll.set)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_text.configure(state=tk.DISABLED)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.master.bind("<Escape>", lambda _: self.on_close())

    def populate_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.node_metadata.clear()
        country_nodes: Dict[str, str] = {}
        category_nodes: Dict[Tuple[str, str], str] = {}

        cursor = self.conn.cursor()
        for label, table in CATEGORY_TABLES.items():
            cursor.execute(
                f"SELECT id, Country, Name FROM {table} WHERE Country IS NOT NULL ORDER BY Country, Name"
            )
            for row in cursor.fetchall():
                country = row["Country"] or "Unknown"
                name = row["Name"] or "(Unnamed)"

                country_node = country_nodes.get(country)
                if not country_node:
                    country_node = self.tree.insert("", tk.END, text=country, open=True)
                    country_nodes[country] = country_node
                    self.node_metadata[country_node] = {
                        "type": "country",
                        "name": country,
                    }

                category_key = (country, label)
                category_node = category_nodes.get(category_key)
                if not category_node:
                    category_node = self.tree.insert(country_node, tk.END, text=label, open=False)
                    category_nodes[category_key] = category_node
                    self.node_metadata[category_node] = {
                        "type": "category",
                        "table": table,
                        "country": country,
                        "label": label,
                    }

                unit_node = self.tree.insert(category_node, tk.END, text=name)
                self.node_metadata[unit_node] = {
                    "type": "unit",
                    "table": table,
                    "id": row["id"],
                    "country": country,
                    "label": label,
                    "name": name,
                }

        if not country_nodes:
            self.display_message([
                "No records found.",
                "Run initialize_esm_db.py to seed the database with sample data.",
            ])
        else:
            self.display_message(
                [
                    "Select a platform to review its technical details.",
                    "Expand a country and category to see available entries.",
                ]
            )

    def on_tree_select(self, event: tk.Event) -> None:  # pragma: no cover - UI callback
        selection = self.tree.selection()
        if not selection:
            return
        node_id = selection[0]
        metadata = self.node_metadata.get(node_id)
        if not metadata:
            return

        node_type = metadata.get("type")
        if node_type == "unit":
            self.show_unit_details(metadata["table"], metadata["id"])
        elif node_type == "category":
            self.show_category_summary(metadata["table"], metadata["country"], metadata["label"])
        elif node_type == "country":
            self.show_country_summary(metadata["name"])

    def show_country_summary(self, country: str) -> None:
        cursor = self.conn.cursor()
        lines = [f"{country} inventory summary:"]
        for label, table in CATEGORY_TABLES.items():
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE Country = ?", (country,))
            count = cursor.fetchone()[0]
            if count:
                lines.append(f"  {label}: {count}")
        if len(lines) == 1:
            lines.append("  No entries in catalog.")
        self.display_message(lines)

    def show_category_summary(self, table: str, country: str, label: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Name FROM {table} WHERE Country = ? ORDER BY Name",
            (country,),
        )
        names = [row["Name"] or "(Unnamed)" for row in cursor.fetchall()]
        lines = [f"{country} — {label}"]
        if not names:
            lines.append("No entries found.")
        else:
            lines.append("")
            lines.extend(f" • {name}" for name in names)
        self.display_message(lines)

    def get_table_columns(self, table: str) -> List[str]:
        if table not in self.column_cache:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table})")
            self.column_cache[table] = [info[1] for info in cursor.fetchall() if info[1] != "id"]
            columns = [info[1] for info in cursor.fetchall() if info[1] != "id"]
            self.column_cache[table] = columns
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
        lines: List[str] = [f"{row['Name'] or 'Unnamed Entry'}"]
        lines.append("".ljust(1))
        for column in columns:
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
