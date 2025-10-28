import sqlite3
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk
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
        self.master.configure(bg="#001b00")
        self.master.geometry("960x600")
        self.master.minsize(720, 480)

        initialize_database()
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

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
