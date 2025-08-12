# 🛠️ CAN MF4 Inspector

A CLI tool to inspect and decode CAN log data from `.MF4` files. Built for engineering teams working with automotive and IoT telemetry, the tool extracts unique CAN IDs, classifies them, optionally decodes them using DBC files, and exports results to CSV.

---

## 📦 Features

- 🔍 Lists all unique CAN IDs from `.MF4` log files
- ✅ Classifies Standard (11-bit) and Extended (29-bit) CAN frames
- 🧠 Optionally decodes CAN messages with a `.dbc` file
- 📡 Calculates PGNs for J1939 (extended ID) messages
- 📤 CSV export of all data with optional auto-naming
- 🧾 Sort results by CAN ID or Message Name
- ⚙️ Designed for CANedge, J1939, automotive OEMs, and diagnostics

---

## 🧰 Requirements

- Python 3.7+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Usage
python3 list_can_ids.py <your_file.MF4> [-d your_file.dbc] [--csv [output.csv]] [--sort id|name]

## 🔧 Examples

```bash
# Basic: just list unique CAN IDs
python3 list_can_ids.py logs/test.mf4

# Decode messages using a DBC file
python3 list_can_ids.py logs/test.mf4 -d dbc/j1939.dbc

# Export summary to CSV (auto-named)
python3 list_can_ids.py logs/test.mf4 --csv

# Export to custom CSV filename
python3 list_can_ids.py logs/test.mf4 --csv decoded_ids.csv

# Sort results by signal name
python3 list_can_ids.py logs/test.mf4 -d j1939.dbc --sort name
```

## 📋 Output Fields (CSV)

| Column        | Description                                  |
| ------------- | -------------------------------------------- |
| CAN\_ID (Hex) | Hex representation of the CAN ID             |
| CAN\_ID (Dec) | Decimal representation of the CAN ID         |
| Type          | Standard (11-bit) or Extended (29-bit)       |
| PGN           | J1939 Parameter Group Number (if applicable) |
| Message Name  | Signal/message name (from DBC) or `N/A`      |

## 🧠 Future Enhancements

- `--include-data`: Output timestamped raw CAN payloads
- PGN → full J1939 breakdown (priority, SA, DA)
- JSON export support
- PyPI packaging: pip install can-mdf-inspector

## 📝 License

MIT © 2025 — Five9nes