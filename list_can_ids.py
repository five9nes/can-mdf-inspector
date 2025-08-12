import argparse
import csv
import os
from asammdf import MDF
import cantools

def load_dbc(dbc_path):
    try:
        db = cantools.database.load_file(dbc_path, strict=False)
        print(f"[✓] Loaded DBC file: {dbc_path}")
        return db
    except Exception as e:
        print(f"[!] Failed to load DBC: {e}")
        return None

def calculate_pgn(can_id):
    """Extract PGN from 29-bit CAN ID according to J1939 spec"""
    if can_id <= 0x7FF:
        return None  # Not a 29-bit extended frame
    pgn = (can_id >> 8) & 0x3FFFF
    return f"0x{pgn:X}"

def list_can_ids(mf4_file, dbc_file=None, output_csv=None, sort_key="id"):
    try:
        mdf = MDF(mf4_file)
        all_ids = set()

        # Loop through all data groups and collect IDs
        for group_index, group in enumerate(mdf.groups):
            for i, channel in enumerate(group.channels):
                if ".ID" in channel.name:
                    try:
                        signal = mdf.get(channel.name, group=group_index, index=i)
                        all_ids.update(set(map(int, signal.samples)))
                    except Exception:
                        continue

        if not all_ids:
            print("⚠️  No CAN IDs found in this MF4 file.")
            return

        print(f"\n📦 Unique CAN IDs in: {mf4_file} ({len(all_ids)} total)\n")
        db = load_dbc(dbc_file) if dbc_file else None

        # Build row data
        rows = []
        for cid in sorted(all_ids):
            id_type = "Extended (29-bit)" if cid > 0x7FF else "Standard (11-bit)"
            message_name = ""
            if db:
                try:
                    msg = db.get_message_by_frame_id(cid)
                    if msg:
                        message_name = msg.name
                except:
                    pass
            pgn = calculate_pgn(cid)
            rows.append({
                "CAN_ID (Hex)": f"0x{cid:X}",
                "CAN_ID (Dec)": cid,
                "Type": id_type,
                "PGN": pgn if pgn else "",
                "Message Name": message_name
            })

        # Sort rows
        if sort_key == "name":
            rows.sort(key=lambda x: x["Message Name"] or "")
        else:
            rows.sort(key=lambda x: x["CAN_ID (Dec)"])

        # Print rows to terminal
        for row in rows:
            printable = f"  {row['CAN_ID (Hex)']}  ({row['Type']})"
            if row["Message Name"]:
                printable += f" → {row['Message Name']}"
            if row["PGN"]:
                printable += f" [PGN {row['PGN']}]"
            print(printable)

        # Write CSV if requested
        if output_csv is not None:
            if output_csv == "":
                base = os.path.splitext(os.path.basename(mf4_file))[0]
                output_csv = f"{base}_can_ids.csv"

            with open(output_csv, mode='w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            print(f"\n[✓] Exported CAN ID summary to CSV: {output_csv}")

    except Exception as e:
        print(f"[!] Error reading MF4 file: {e}")

def show_manual():
    print("""
🧾 MF4 CAN ID Inspector

This tool lists unique CAN IDs from an MF4 file, identifies standard vs extended IDs,
and optionally decodes them using a DBC. You can also export results to CSV.

▶️ Usage:
    python3 list_can_ids.py <your_file.MF4> [-d your_file.dbc] [--csv [output.csv]] [--sort id|name]

🔧 Examples:
    python3 list_can_ids.py test.MF4
    python3 list_can_ids.py test.MF4 -d j1939.dbc
    python3 list_can_ids.py test.MF4 -d j1939.dbc --csv
    python3 list_can_ids.py test.MF4 -d j1939.dbc --csv output.csv
    python3 list_can_ids.py test.MF4 --csv --sort name

💡 Notes:
- If you use --csv without a filename, it will auto-generate one.
- PGNs are included for extended CAN frames (J1939).
""")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        show_manual()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="List unique CAN IDs from MF4 with DBC decoding, PGN extraction, and CSV export.")
    parser.add_argument("mf4_file", help="Path to the .mf4 file")
    parser.add_argument("-d", "--dbc", help="Path to DBC file (optional)")
    parser.add_argument("--csv", nargs="?", const="", help="Output CSV filename (optional). If omitted, auto-names it.")
    parser.add_argument("--sort", choices=["id", "name"], default="id", help="Sort by 'id' (default) or 'name'")
    args = parser.parse_args()

    list_can_ids(args.mf4_file, args.dbc, args.csv, args.sort)
