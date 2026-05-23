# forza_motorsport

## Purpose
Utilities to receive and log telemetry data from Forza Motorsport and Forza Horizon games via their UDP "data out" stream. Parses binary packets and writes structured output (TSV/CSV) to file.

## Stack
- Python 3.6+
- stdlib only (`struct`, `socket`, `argparse`)
- Optional: `PyYAML` for configuration file support (`pip install pyyaml`)

## Commands

**Run the data logger:**
```bash
python data2file.py <port> <output_file>
# Example: listen on port 1123, write TSV
python data2file.py 1123 forza_data.tsv

# CSV output
python data2file.py -f csv 1123 forza_data.csv

# Append mode (no header row written)
python data2file.py -a 1123 forza_data.tsv

# Use sled (V1) or fh4 packet format
python data2file.py -p sled 1123 forza_data.tsv
python data2file.py -p fh4  1123 forza_data.tsv

# Use a YAML config to filter logged fields
python data2file.py -c example_configuration.yaml 1123 forza_data.tsv
```

**Install (one-shot):**
```bash
curl -fsSL https://raw.githubusercontent.com/jasperan/forza_motorsport/master/install.sh | bash
```

## Layout
```
fdp.py                    # ForzaDataPacket class — parses UDP binary packets
data2file.py              # CLI script — listens on UDP port, writes to file
example_configuration.yaml
configuration_file.md     # Config file format docs
install.sh
```

## Packet Formats
| Name   | Description                          |
|--------|--------------------------------------|
| `dash` | Default — Forza Motorsport 7 V2      |
| `sled` | Legacy V1 format                     |
| `fh4`  | Forza Horizon 4 (patched byte range) |

## Conventions
- `ForzaDataPacket` in `fdp.py` is the single data model; extend it for new packet formats by adding a format string and props list.
- `data2file.py` handles all I/O, argument parsing, and the UDP listen loop.
- No external dependencies beyond PyYAML (config files only); keep it that way unless there is a strong reason.
- Game setup: enable "data out" in HUD options, set IP + port to match the machine running the script.
