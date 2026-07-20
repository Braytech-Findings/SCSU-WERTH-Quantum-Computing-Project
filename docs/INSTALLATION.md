# Installation

Use Python 3.11 or newer. Public installation, tests, proxy experiments, and reports do not require provider credentials and do not submit jobs.

## macOS and Linux

```bash
git clone https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project.git
cd SCSU-WERTH-Quantum-Computing-Project
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cp .env.example .env
python -m pytest -q
```

## Windows PowerShell

```powershell
git clone https://github.com/Braytech-Findings/SCSU-WERTH-Quantum-Computing-Project.git
Set-Location SCSU-WERTH-Quantum-Computing-Project
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
python -m pytest -q
```

The `.env` copy contains empty placeholders. It is unnecessary for offline work and must never be committed.
