# Campus Issue Reporter (PS-02)

Report form + public status board (Open / In Progress / Fixed) with upvotes, built with Flask + SQLite + vanilla HTML/CSS/JS.

## Run it
live demo at- https://campus-issue-reporter-cvdv.vercel.app/

```
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000

## What it does
- **Report form**: title, category, location (required), optional description.
- **Status board**: three columns — Open / In Progress / Fixed — auto-refreshing every 15s.
- **Filter & sort**: by status, category, and most-recent vs. most-upvoted.
- **Upvotes** (stretch goal): click ▲ on any card to bump priority.
- **Status changes**: dropdown on each card updates status instantly (PATCH request).
- Data persists in `issues.db` (SQLite), created automatically on first run.

## Structure
```
app.py                 Flask backend + REST API
templates/index.html   Page markup
static/style.css       Dark F1-ish theme
static/script.js       Fetch calls, rendering, event handlers
```
