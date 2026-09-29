# HST-Project


# Paninian Pratyahara Generator

A web tool that generates Paninian pratyaharas from the 14 Shiva Sutras (Panini 1.1.71, *ādir antyena sahetā*). Type one or more pratyaharas and get the sounds each one covers. Type `all` to list every validated pratyahara.

**Live site:** https://YOUR-APP-NAME.onrender.com

## Features

- Computes the range of any pratyahara from its starting sound and ending marker (anubandha).
- Validates notations against an inventory of pratyaharas used in the Ashtadhyayi, so mechanically possible but unattested combinations (such as ऋष्) are rejected.
- Handles the ambiguous marker ण् with a sense number (`अण्:1` or `अण्:6`).
- Accepts several inputs at once, separated by spaces or commas.
- Shows all results in one large output column.

## How to use

| Input | Result |
|-------|--------|
| `हल्` | Sounds covered by हल् |
| `अण् इक् यण्` | Results for each pratyahara |
| `अण्:6` | The sutra-6 sense of अण् |
| `all` | Every validated pratyahara |

## Run locally

Requires Python 3 and Git.

### Windows (PowerShell)

```
git clone https://github.com/YOUR-USERNAME/HST-Project.git
cd HST-Project\codes
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

### Mac / Linux

```
git clone https://github.com/YOUR-USERNAME/HST-Project.git
cd HST-Project/codes
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser. Stop the server with `Ctrl+C`.

### Troubleshooting

- If PowerShell blocks the activate script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.
- If `python` is not recognized on Windows, use `py` instead (for example `py -m venv .venv`).
- To get later updates, run `git pull` inside the project folder and restart `python app.py`.

## Project structure

```
HST-Project/
└── codes/
    ├── pratyahara_engine.py   # core engine (Shiva Sutras, range logic, validation)
    ├── app.py                 # Flask backend
    ├── requirements.txt
    └── templates/
        └── index.html         # web page
```

## Notes on validity

The range of a pratyahara is computed directly from the sutra order. Whether a notation is a valid pratyahara depends on its use in the Ashtadhyayi, so it comes from an editable inventory (`ASHTADHYAYI_INVENTORY` in `pratyahara_engine.py`). Sources differ slightly in how they list these, so verify the inventory against the Kashika or your preferred edition.

## Deployment

Hosted on Render as a Flask web service:

- Root Directory: `codes`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
