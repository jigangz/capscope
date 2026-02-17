# CapScope 🔭

Historical U.S. stock market cap viewer — browse by GICS sector, any date, Top 100

## Features

- 📊 View historical market capitalizations (daily)
- 🏢 Browse by GICS sector classification
- 📅 Select any date to view that day's market cap rankings
- 🔝 Top 100 per sector
- 🔍 Real-time search filtering
- 💾 Export to CSV

## Screenshots

*(Coming soon)*

## Download

### Windows Portable

Download the latest version from [Releases](https://github.com/jigangz/capscope/releases), extract and run `CapScope.exe`.

### From Source

```bash
git clone https://github.com/jigangz/capscope.git
cd capscope
pip install -r requirements.txt
python run_gui.py
```

## Usage

### GUI (Recommended)

```bash
python run_gui.py
```

1. Select a date and click "Refresh" to load data
2. Switch sector tabs to view Top 100 per sector
3. Use the search box to filter stocks
4. Click "Export CSV" to save data

### CLI

```bash
# Query today's market caps
python -m capscope

# Query a specific date
python -m capscope --date 2024-01-15

# Export to CSV
python -m capscope --date 2024-01-15 --out result.csv

# Export to JSON
python -m capscope --date 2024-01-15 --out result.json --format json

# Filter by sector
python -m capscope --sector Technology --top 50
```

## Stock Universe

- S&P 500 (~503 stocks)
- Nasdaq 100 (~101 stocks)
- ~550 unique stocks after deduplication

## Calculation

```
Market Cap ≈ Current Shares Outstanding × Historical Close Price
```

> ⚠️ **V1 uses an approximate algorithm**
>
> Since current shares outstanding are used for historical calculations, there are known approximation errors:
> - **Stock splits:** Historical prices are adjusted, but shares use current count → historical market cap skews high
> - **Share issuance:** Historical actual float was less than current → skews high
> - **Buybacks:** Historical actual float was more than current → skews low
>
> Exact historical market cap requires a paid API (planned for V2 via Polygon.io)

## Build

### Windows

```bash
pip install pyinstaller
pyinstaller CapScope.spec
# or
build.bat
```

Output: `dist/CapScope.exe`

### macOS/Linux

```bash
chmod +x build.sh
./build.sh
```

## Tech Stack

- Python 3.10+
- yfinance (data)
- PyQt6 (GUI)
- PyInstaller (packaging)

## Roadmap

- [x] V1: Data contract, stock universe, core calculation, GUI, packaging
- [ ] V2: Exact historical market cap (Polygon.io)
- [ ] Local caching (reduce API calls)
- [ ] Offline mode
- [ ] Auto-update stock universe
- [ ] Chart visualizations

## FAQ

**Q: Slow startup?**
A: First launch needs to extract temp files, ~10-30 seconds.

**Q: Data loading fails?**
A: Check network connection and access to Yahoo Finance.

**Q: Some stocks show N/A?**
A: No trading data or missing metadata for that stock on the selected date.

**Q: What about non-trading days?**
A: Automatically falls back to the most recent prior trading day.

## License

MIT
