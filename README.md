# Premier League 2025/26 — Shooting Stats Dashboard

An interactive, dark-themed analytics dashboard for Premier League team shooting performance in the 2025/26 season. Built with [Plotly Dash](https://dash.plotly.com/) and styled as a modern single-page app.

![Preview](docs/preview.png)

> Replace `docs/preview.png` with a screenshot of the running dashboard once you take one.

## Features

- **KPI summary cards** — total goals, total shots, average shot accuracy, goals per shot, and penalty conversion, with best-in-league callouts.
- **Comparative bar chart** — switch the metric on the fly (Goals, Shots, SoT%, Sh/90, G/Sh, etc.).
- **Shooting efficiency scatter** — Shots vs. Goals, with bubble size encoding shot accuracy (SoT%).
- **Goal breakdown** — stacked open-play vs. penalty goals per team.
- **Shot accuracy view** — ranked by SoT% with gradient-encoded intensity.
- **Detailed stats table** — every shooting metric, with league-leading values highlighted per column.
- **Team filter** — isolate or compare any subset of the 20 PL clubs.
- **Club-accurate colour palette** — each team is rendered in its primary brand colour across all visuals.

## Tech stack

| Layer         | Tool                           |
|---------------|--------------------------------|
| Web framework | Dash (Flask under the hood)    |
| Charts        | Plotly Graph Objects           |
| Data          | pandas                         |
| Styling       | Inline CSS + custom `index_string` with Inter font |
| Data source   | [FBref](https://fbref.com/)    |

## Getting started

### Prerequisites
- Python 3.10+

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/pl-shooting-dashboard.git
cd pl-shooting-dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
python dashboard/app.py
```
Then open [http://localhost:8050](http://localhost:8050) in your browser.

## Project structure

```
.
├── dashboard/
│   ├── app.py              # Dash app: layout, callbacks, styling
│   └── PL_team_stats.csv   # PL 2025/26 shooting stats (from FBref)
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## Data

Shooting statistics for all 20 Premier League clubs, manually exported from FBref's "Squad Standard Stats — Shooting" table. Columns include:

| Column        | Description                              |
|---------------|------------------------------------------|
| `Squad`       | Team name                                |
| `Gls`         | Goals scored                             |
| `Sh`          | Total shots                              |
| `SoT`         | Shots on target                          |
| `SoT%`        | Shots on target percentage               |
| `Sh/90`       | Shots per 90 minutes                     |
| `SoT/90`      | Shots on target per 90 minutes           |
| `G/Sh`        | Goals per shot                           |
| `G/SoT`       | Goals per shot on target                 |
| `PK`, `PKatt` | Penalties scored / attempted             |

Two additional metrics are derived in-app:
- `Non-PK Goals` = `Gls` − `PK`
- `PK Conversion%` = `PK` / `PKatt` × 100

## What this project demonstrates

- **End-to-end dashboard delivery** — data cleaning, metric engineering, interactive visualisation and UI polish in a single deployable app.
- **Callback-driven interactivity** — a single Dash callback fans out to five synchronised outputs (KPIs, four charts, and a table).
- **UX / design sensibility** — consistent design tokens, typography, hover states, and a custom scrollbar and dropdown theme, all implemented without a component library.
- **Domain translation** — turning a raw CSV of shooting metrics into insights a football analyst could actually read.

## Roadmap ideas

- Automate the data refresh by scraping FBref on a schedule (e.g. GitHub Actions + pandas).
- Add player-level drilldowns.
- Persist user selections in the URL for shareable views.
- Deploy to Render / Fly.io with a live demo link.

## License

Released under the [MIT License](LICENSE).
