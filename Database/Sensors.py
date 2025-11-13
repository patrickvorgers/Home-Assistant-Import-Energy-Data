"""
Sensor definitions

A GUI application to visually select sensors from a MariaDB or SQLite database,
and generate SQL INSERT statements for the conversion SQL script.

Usage:
    python sensors.py --db-type <mariadb|sqlite> \
        [--host HOST --port PORT --user USER --password PASSWORD --database DB]
    python sensors.py --db-type sqlite --file path/to/file.db
"""

import argparse
import sqlite3
import sys
import tkinter as tk
from tkinter import messagebox, ttk

# --- Unit definitions and mappings ---
UNITS = {
    "Wh": 1.0,
    "kWh": 1000.0,
    "MWh": 1000000.0,
    "L": 1.0,
    "m³": 1000.0,
    "W": 1.0,
    "kW": 1000.0,
    "MW": 1000000.0,
    "L/s": 1.0,
    "m³/s": 1000.0,
    "m³/h": 1000.0 / 3600.0,
    "Pa": 1.0,
    "kPa": 1000.0,
    "bar": 100000.0,
    "psi": 6894.76,
}

# Map lowercase unit strings to their canonical forms
CANONICAL = {unit.lower(): unit for unit in UNITS}

# Group units into families for conversion calculations
FAMILIES = [
    ["Wh", "kWh", "MWh"],
    ["L", "m³"],
    ["W", "kW", "MW"],
    ["L/s", "m³/s", "m³/h"],
    ["Pa", "kPa", "bar", "psi"],
]

# Reverse lookup: unit -> its family list
UNIT_TO_FAMILY = {}
for family in FAMILIES:
    for unit in family:
        UNIT_TO_FAMILY[unit] = family

# Precompute correction factors between units in the same family
CORRECTION_MAP = {}
for family in FAMILIES:
    for src in family:
        for tgt in family:
            CORRECTION_MAP[(src, tgt)] = UNITS[src] / UNITS[tgt]

# Default cutoff thresholds for detecting new and invalid readings
CUTOFF_NEW = {
    "Wh": 25000.0,
    "kWh": 25.0,
    "MWh": 0.025,
    "L": 25000.0,
    "m³": 25.0,
    "W": 25000.0,
    "kW": 25.0,
    "MW": 0.025,
    "L/s": 25000.0,
    "m³/s": 25000.0,
    "m³/h": 25000.0,
    "Pa": 1000000.0,
    "kPa": 1000.0,
    "bar": 10.0,
    "psi": 145.038,
}

CUTOFF_INVALID = {
    "Wh": 1000000.0,
    "kWh": 1000.0,
    "MWh": 1.0,
    "L": 1000000.0,
    "m³": 1000.0,
    "W": 1000000.0,
    "kW": 1000.0,
    "MW": 1.0,
    "L/s": 1000000.0,
    "m³/s": 1000000.0,
    "m³/h": 1000000.0,
    "Pa": 10000000.0,
    "kPa": 10000.0,
    "bar": 100.0,
    "psi": 1450.38,
}


def _format_number(value: float) -> str:
    """
    Format a float without scientific notation, trimming trailing zeros.
    """
    return f"{value:.6f}".rstrip("0").rstrip(".")


class StatsMetaApp:
    """
    Main GUI application for sensor selection and SQL generation.
    """

    def __init__(self, master: tk.Tk, sensors: list, import_ids: list) -> None:
        """
        Initialize main window, load data structures, and build UI.
        """
        self.master = master

        master.title("Sensor definitions")
        master.geometry("800x600")
        master.resizable(False, False)

        # Prepare internal data list of dicts
        self.data = []
        for sensor_id, stat_id, unit in sensors:
            canonical = CANONICAL.get(unit.lower(), unit)
            record = {
                "id": sensor_id,
                "stat": stat_id,
                "unit": canonical,
                "source_unit": canonical,
                "selected": False,
                "import_id": None,
                "correction": 1.0,
                "cutoff_new": 0.0,
                "cutoff_invalid": 0.0,
            }
            self.data.append(record)

        self.import_ids = import_ids
        self._calculate_defaults()
        self._build_ui()
        self.update_all()

    def _calculate_defaults(self) -> None:
        """
        Compute default correction and cutoff thresholds for each sensor.
        """
        for entry in self.data:
            src = entry["source_unit"]
            tgt = entry["unit"]
            entry["correction"] = CORRECTION_MAP.get((src, tgt), 1.0)
            entry["cutoff_new"] = CUTOFF_NEW.get(tgt, 0.0)
            entry["cutoff_invalid"] = CUTOFF_INVALID.get(tgt, 0.0)

    def _build_ui(self) -> None:
        """
        Set up the paned UI with three sections and a SQL button.
        """
        # Bottom frame for Generate SQL button
        btn_frame = ttk.Frame(self.master)
        btn_frame.pack(side="bottom", fill="x")

        self.generate_button = ttk.Button(
            btn_frame, text="Generate SQL", command=self._generate_sql
        )
        self.generate_button.pack(pady=5)
        self.generate_button.config(state="disabled")

        # Vertical paned window
        self.paned = ttk.Panedwindow(self.master, orient=tk.VERTICAL)
        self.paned.pack(fill="both", expand=True)

        # All Sensors pane
        self.frame_all = ttk.Labelframe(self.paned, text="All Sensors")
        self.paned.add(self.frame_all, weight=40)
        self._build_all_section()

        # Target Sensors pane
        self.frame_sel = ttk.Labelframe(self.paned, text="Target Sensors")
        self.paned.add(self.frame_sel, weight=30)
        self._build_selected_section()

        # SQL Information pane
        self.frame_det = ttk.Labelframe(self.paned, text="SQL Information")
        self.paned.add(self.frame_det, weight=30)
        self._build_details_section()

    def _build_all_section(self) -> None:
        """
        Build the filter input and complete sensor list Treeview.
        """
        top = ttk.Frame(self.frame_all)
        top.pack(fill="x", padx=5, pady=5)

        label = ttk.Label(top, text="Filter:")
        label.pack(side="left")

        self.filter_entry = ttk.Entry(top)
        self.filter_entry.pack(side="left", fill="x", expand=True)
        self.filter_entry.bind("<KeyRelease>", self.update_all)

        container = ttk.Frame(self.frame_all)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("sel", "id", "stat", "unit")
        headings = ("Select", "Sensor ID", "Sensor", "Unit")
        widths = (60, 100, 250, 150)

        self.tree = ttk.Treeview(container, columns=columns, show="headings")
        for col, hd, wd in zip(columns, headings, widths):
            self.tree.heading(col, text=hd)
            self.tree.column(col, width=wd)

        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<ButtonRelease-1>", self.on_click_all)

    def _build_selected_section(self) -> None:
        """
        Build the Treeview for selected target sensors.
        """
        columns = ("id", "imp", "stat", "unit", "src")
        headings = ("Sensor ID", "Import name", "Sensor", "Unit", "Source unit")
        widths = (80, 200, 200, 100, 100)

        self.sel_tree = ttk.Treeview(self.frame_sel, columns=columns, show="headings")
        for col, hd, wd in zip(columns, headings, widths):
            self.sel_tree.heading(col, text=hd)
            self.sel_tree.column(col, width=wd)

        scrollbar = ttk.Scrollbar(
            self.frame_sel, orient="vertical", command=self.sel_tree.yview
        )
        self.sel_tree.configure(yscrollcommand=scrollbar.set)
        self.sel_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.sel_tree.bind("<ButtonRelease-1>", self.on_edit_selected)

    def _build_details_section(self) -> None:
        """
        Build the Treeview showing SQL parameters per sensor.
        """
        columns = ("id", "imp", "corr", "new", "inv")
        headings = (
            "Sensor ID",
            "Import name",
            "Correction",
            "Cutoff new",
            "Cutoff invalid",
        )
        widths = (80, 200, 80, 80, 80)

        self.det_tree = ttk.Treeview(self.frame_det, columns=columns, show="headings")
        for col, hd, wd in zip(columns, headings, widths):
            self.det_tree.heading(col, text=hd)
            self.det_tree.column(col, width=wd)

        scrollbar = ttk.Scrollbar(
            self.frame_det, orient="vertical", command=self.det_tree.yview
        )
        self.det_tree.configure(yscrollcommand=scrollbar.set)
        self.det_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.det_tree.bind("<ButtonRelease-1>", self.on_edit_details)

    def update_all(self, event=None) -> None:
        """
        Refresh the full sensor list based on the filter entry.
        """
        pattern = self.filter_entry.get().lower().strip()

        self.tree.delete(*self.tree.get_children())

        for entry in self.data:
            if not pattern:
                match = True
            else:
                match = (
                    pattern in entry["stat"].lower() or pattern in entry["unit"].lower()
                )
            if match:
                mark = "☑" if entry["selected"] else "☐"
                self.tree.insert(
                    "",
                    "end",
                    iid=entry["stat"],
                    values=(mark, entry["id"], entry["stat"], entry["unit"]),
                )

        self.update_selected()
        self.update_details()

    def update_selected(self) -> None:
        """
        Refresh the target sensors pane with currently selected entries.
        """
        self.sel_tree.delete(*self.sel_tree.get_children())

        for entry in self.data:
            if entry["selected"]:
                self.sel_tree.insert(
                    "",
                    "end",
                    iid=entry["stat"],
                    values=(
                        entry["id"],
                        entry["import_id"] or "",
                        entry["stat"],
                        entry["unit"],
                        entry["source_unit"],
                    ),
                )

    def update_details(self) -> None:
        """
        Refresh the SQL info pane and toggle the Generate SQL button.
        """
        self.det_tree.delete(*self.det_tree.get_children())
        any_valid = False

        for entry in self.data:
            if entry["selected"] and entry["import_id"]:
                cf = _format_number(entry["correction"])
                cn = _format_number(entry["cutoff_new"])
                ci = _format_number(entry["cutoff_invalid"])

                self.det_tree.insert(
                    "",
                    "end",
                    iid=entry["stat"],
                    values=(entry["id"], entry["import_id"], cf, cn, ci),
                )
                any_valid = True

        state = "normal" if any_valid else "disabled"
        self.generate_button.config(state=state)

    def on_click_all(self, event) -> None:
        """
        Toggle selection when clicking the checkbox column in all-sensors list.
        """
        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        if col == "#1" and row:
            for entry in self.data:
                if entry["stat"] == row:
                    entry["selected"] = not entry["selected"]

                    if not entry["selected"]:
                        # Reset fields on deselect
                        entry["import_id"] = None
                        entry["source_unit"] = entry["unit"]
                        entry["correction"] = 1.0
                        entry["cutoff_new"] = CUTOFF_NEW.get(entry["unit"], 0.0)
                        entry["cutoff_invalid"] = CUTOFF_INVALID.get(entry["unit"], 0.0)
                    break

            self.update_all()

    def on_edit_selected(self, event) -> None:
        """
        Allow editing of import name or source unit in target list.
        """
        region = self.sel_tree.identify("region", event.x, event.y)
        col = self.sel_tree.identify_column(event.x)
        row = self.sel_tree.identify_row(event.y)

        if region != "cell" or not row:
            return

        idx = int(col.replace("#", ""))
        entry = next(e for e in self.data if e["stat"] == row)

        # Column 2 = import_id, column 5 = source_unit
        if idx == 2:
            used_ids = [
                e["import_id"] for e in self.data if e["selected"] and e["stat"] != row
            ]
            options = [i for i in self.import_ids if i not in used_ids]
            current = entry["import_id"] or ""
        elif idx == 5:
            options = UNIT_TO_FAMILY.get(entry["unit"], [])
            current = entry["source_unit"]
        else:
            return

        if not options:
            return

        bbox = self.sel_tree.bbox(row, col)
        if not bbox:
            return
        x, y, w, h = bbox
        var = tk.StringVar(value=current)

        combo = ttk.Combobox(
            self.sel_tree, textvariable=var, values=options, state="readonly"
        )
        combo.place(x=x, y=y, width=w, height=h)
        combo.focus_set()

        def apply(event=None):
            val = var.get()

            if idx == 2:
                entry["import_id"] = val
            else:
                entry["source_unit"] = val
                self._calculate_defaults()

            combo.destroy()
            self.update_selected()
            self.update_details()

        def click_outside(event):
            try:
                # get combobox geometry
                x1 = combo.winfo_rootx()
            except tk.TclError:
                # widget gone → unbind and exit
                self.master.unbind_all("<Button-1>")
                return

            # if the dropdown list is open, clicks inside it should NOT close the combobox
            popdown = combo.tk.call("ttk::combobox::PopdownWindow", combo)
            if popdown:
                # event.widget path starts with popdown window’s path
                if str(event.widget).startswith(popdown):
                    return

            # compute widget bounds
            y1 = combo.winfo_rooty()
            x2 = x1 + combo.winfo_width()
            y2 = y1 + combo.winfo_height()

            # click outside → destroy and unbind
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                combo.destroy()
                self.master.unbind_all("<Button-1>")

        # bind globally so we catch clicks outside—but allow dropdown clicks through
        self.master.bind_all("<Button-1>", click_outside, add="+")

        combo.bind("<<ComboboxSelected>>", apply)
        combo.bind("<Return>", apply)

    def on_edit_details(self, event) -> None:
        """
        Allow inline editing of cutoff thresholds in SQL info pane.
        """
        region = self.det_tree.identify("region", event.x, event.y)
        col = self.det_tree.identify_column(event.x)
        row = self.det_tree.identify_row(event.y)

        if region != "cell" or not row:
            return

        idx = int(col.replace("#", ""))
        if idx not in (4, 5):
            return

        field = "cutoff_new" if idx == 4 else "cutoff_invalid"
        bbox = self.det_tree.bbox(row, col)
        if not bbox:
            return
        x, y, w, h = bbox

        popup = tk.Toplevel(self.master)
        popup.overrideredirect(True)
        popup.geometry(
            f"{w}x{h}+{self.det_tree.winfo_rootx()+x}+{self.det_tree.winfo_rooty()+y}"
        )
        popup.grab_set()

        current = next(e[field] for e in self.data if e["stat"] == row)
        var = tk.StringVar(value=_format_number(current))

        entry = ttk.Entry(popup, textvariable=var)
        entry.pack(fill="both", expand=True)
        entry.focus_set()
        # select the current text so typing replaces it immediately
        entry.selection_range(0, tk.END)

        # Commit the values and destroy the popup
        def commit(event=None):
            try:
                new_val = float(var.get())
            except ValueError:
                new_val = current

            for rec in self.data:
                if rec["stat"] == row:
                    rec[field] = new_val
                    break

            popup.destroy()
            self.update_details()

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)

        # Close the edit popup if the user clicks anywhere outside it
        def click_outside(event):
            try:
                # Popup bounds
                x1 = popup.winfo_rootx()
            except tk.TclError:
                # already destroyed → clean up
                self.master.unbind_all("<Button-1>")
                return

            y1 = popup.winfo_rooty()
            x2 = x1 + popup.winfo_width()
            y2 = y1 + popup.winfo_height()

            # If click was outside popup, commit & destroy
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                commit()
                self.master.unbind_all("<Button-1>")

        # Catch all left‐clicks while popup is open
        self.master.bind_all("<Button-1>", click_outside, add="+")

    def _generate_sql(self) -> None:
        """
        Generate aligned SQL INSERT statements and display them in a popup
        with a "Copy to Clipboard" button.
        """
        insert_prefix = "INSERT INTO SENSORS VALUES ("
        columns = [
            ("name", 25),
            ("sensor_id", 10),
            ("correction", 10),
            ("cutoff_new", 12),
            ("cutoff_invalid", 15),
        ]

        # Build header comment line
        header_parts = []
        for idx, (col_name, width) in enumerate(columns):
            if idx > 0:
                header_parts.append("  ")
            header_parts.append(col_name.ljust(width))
        indent = len(insert_prefix)
        pad = " " * (indent - 2)
        header_line = "/*" + pad + "".join(header_parts) + " */"

        lines = [header_line]

        # Generate one INSERT per selected sensor
        for entry in self.data:
            if entry["selected"] and entry["import_id"]:
                parts = []
                # name field
                parts.append(f"'{entry['import_id']}'".ljust(columns[0][1]))
                # numeric fields
                vals = [
                    entry["id"],
                    _format_number(entry["correction"]),
                    _format_number(entry["cutoff_new"]),
                    _format_number(entry["cutoff_invalid"]),
                ]
                for (_, width), val in zip(columns[1:], vals):
                    parts.append(f", {str(val):<{width}}")
                vals_str = "".join(parts)
                lines.append(f"{insert_prefix}{vals_str});")

        # Create popup window
        popup = tk.Toplevel(self.master)
        popup.title("Generated SQL")
        popup.geometry("1000x300")
        popup.resizable(False, False)

        # Frame for text widget
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        text_widget = tk.Text(text_frame, font=("Courier New", 10), height=12)
        text_widget.insert("1.0", "\n".join(lines))
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True)

        # Frame for copy button
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(fill="x", padx=5, pady=5)

        def copy_to_clipboard() -> None:
            popup.clipboard_clear()
            popup.clipboard_append(text_widget.get("1.0", "end-1c"))

        copy_button = ttk.Button(
            btn_frame,
            text="Copy to Clipboard",
            command=copy_to_clipboard,
        )
        copy_button.pack(fill="x")

        popup.lift()


def fetch_sensors(conn) -> list:
    """
    Fetch sensor definitions from the database.
    """
    print("Loading sensors...")
    cursor = conn.cursor()
    placeholders = ", ".join(f"'{u.lower()}'" for u in UNITS)
    query = (
        "SELECT id, statistic_id, unit_of_measurement "
        f"FROM statistics_meta "
        "WHERE has_sum = 1 "
        f"AND LOWER(unit_of_measurement) IN ({placeholders})"
    )

    try:
        cursor.execute(query)
    except Exception as err:
        messagebox.showerror("Database Error", str(err))
        sys.exit(1)

    records = cursor.fetchall()

    if not records:
        messagebox.showerror("Data Error", "No sensor definitions found.")
        sys.exit(1)

    return records


def fetch_import_ids(conn) -> list:
    """
    Fetch distinct import_data IDs from the database.
    """
    print("Loading import data identifiers...")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT id FROM import_data")
    except Exception as err:
        messagebox.showerror("Database Error", str(err))
        sys.exit(1)

    rows = cursor.fetchall()
    ids = [row[0] for row in rows]

    if not ids:
        messagebox.showerror("Data Error", "No import_data entries found.")
        sys.exit(1)

    return ids


def load_data(args) -> tuple:
    """
    Connect to the specified database, fetch sensor and import IDs.
    """
    if args.db_type == "mariadb":
        try:
            import mysql.connector
        except ImportError:
            messagebox.showerror(
                "Dependency Error",
                "mysql-connector-python is required. "
                "Install with: pip install mysql-connector-python",
            )
            sys.exit(1)

        conn = mysql.connector.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password or "",
            database=args.database,
        )
    else:
        conn = sqlite3.connect(args.sqlite_db)

    sensors = fetch_sensors(conn)
    import_ids = fetch_import_ids(conn)

    conn.close()
    return sensors, import_ids


def parse_args() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Sensor definitions GUI")

    parser.add_argument(
        "--db-type",
        choices=["mariadb", "sqlite"],
        required=True,
        help="Database type to use",
    )
    parser.add_argument("--host", default="localhost", help="MariaDB host name")
    parser.add_argument("--port", type=int, default=3306, help="MariaDB port number")
    parser.add_argument("--user", help="MariaDB user name")
    parser.add_argument("--password", help="MariaDB password")
    parser.add_argument("--database", help="MariaDB database name")
    parser.add_argument("--sqlite-db", help="Path to SQLite database file")

    args = parser.parse_args()

    if args.db_type == "mariadb" and not args.user:
        parser.error("--user is required for MariaDB")

    if args.db_type == "mariadb" and not args.database:
        parser.error("--database is required for MariaDB")

    if args.db_type == "sqlite" and not args.sqlite_db:
        parser.error("--sqlite-db is required for SQLite")

    return args


def main() -> None:
    """
    Main entry point: parse arguments, load data, and launch the GUI.
    """
    args = parse_args()
    sensors, import_ids = load_data(args)

    root = tk.Tk()
    StatsMetaApp(root, sensors, import_ids)
    root.mainloop()


if __name__ == "__main__":
    main()
