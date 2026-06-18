# Publication Step-by-Step — Ubuntu, VS Code, GitHub, Streamlit Cloud

This guide assumes you are publishing the first public release: **AI Product Intelligence Suite 1.04**.

## 0. What you are publishing

- A portfolio case study, not a commercial product.
- Entry point: `app.py`.
- Python dependencies: `requirements.txt`.
- Safe local files ignored by Git: `.env`, `.venv/`, `.local_audit/`, `.streamlit/secrets.toml`, caches.

## 1. Install system tools on Ubuntu

Open Terminal and run:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git unzip
```

Check versions:

```bash
python3 --version
git --version
```

## 2. Install VS Code

Option A, easiest via Ubuntu Software: search for **Visual Studio Code** and install it.

Option B, terminal:

```bash
sudo snap install code --classic
```

## 3. Unzip the project

Put `ai_pm_winning_suite_1_02.zip` in `~/Downloads`, then run:

```bash
mkdir -p ~/Projects
unzip ~/Downloads/ai_pm_winning_suite_1_02.zip -d ~/Projects
cd ~/Projects/ai_pm_winning_suite_1_02
```

If the folder is nested, run:

```bash
ls
```

You should see files like:

```text
app.py
config.py
requirements.txt
README.md
```

## 4. Open in VS Code

```bash
code .
```

In VS Code, install the Python extension if prompted.

## 5. Create and activate a virtual environment

In the VS Code terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You should see `(.venv)` at the start of the terminal line.

## 6. Run tests locally

```bash
pytest -q
```

Expected result for release 1.04:

```text
73 passed, 1 skipped
```

## 7. Run the app locally

```bash
streamlit run app.py
```

A browser should open. If not, open the URL printed in the terminal, usually:

```text
http://localhost:8501
```

## 8. Check the app before publishing

Confirm:

- The title says `AI Product Intelligence Suite 1.04`.
- The default/focused review path starts with `Guided Demo — Portfolio Review`.
- `Claim Hygiene Audit` passes.
- `Real vs simulated` language is visible.
- No private phone number or secrets appear in the UI or repository.

## 9. Initialize Git

```bash
git init
git status
git add .
git commit -m "Publish AI Product Intelligence Suite 1.04"
```

If Git asks for your identity:

```bash
git config --global user.name "Marco Figueiredo"
git config --global user.email "marco6689@gmail.com"
```

Then rerun:

```bash
git commit -m "Publish AI Product Intelligence Suite 1.04"
```

## 10. Create the GitHub repository

### Option A — through GitHub website

1. Go to GitHub.
2. Click `+` → `New repository`.
3. Repository name suggestion:

```text
ai-product-intelligence-suite
```

4. Choose `Public` if you want recruiters/hiring managers to access it.
5. Do **not** add README, `.gitignore`, or license on GitHub because this project already has files locally.
6. Click `Create repository`.

GitHub will show commands. Use the HTTPS remote command, similar to:

```bash
git branch -M main
git remote add origin https://github.com/marco6689/ai-product-intelligence-suite.git
git push -u origin main
```

### Option B — GitHub CLI

Install and login:

```bash
sudo apt install -y gh
gh auth login
```

Create and push:

```bash
gh repo create ai-product-intelligence-suite --public --source=. --remote=origin --push
```

## 11. Deploy with Streamlit Community Cloud

1. Go to Streamlit Community Cloud.
2. Sign in with GitHub.
3. Click `Create app` or `New app`.
4. Select your repository:

```text
marco6689/ai-product-intelligence-suite
```

5. Branch:

```text
main
```

6. Main file path:

```text
app.py
```

7. Deploy.

## 12. If deployment fails

Check these first:

- The repository contains `requirements.txt` in the root.
- The app entry point is exactly `app.py`.
- There is no `.env` committed.
- No secrets are required for demo mode.
- If a package install fails, open the Streamlit build logs and copy the error.

## 13. After deployment

Update these places with the app URL:

- GitHub repository About section.
- README top section.
- LinkedIn Featured.
- CV project link.
- Outreach messages.

## 14. Safe public positioning

Use this wording:

```text
This is a portfolio case study, not a commercial product. It demonstrates how I design AI product workflows for regulated enterprise software: domain understanding, human-in-the-loop review, QA gates, claim hygiene, auditability, real local metrics and product strategy.
```

Avoid unsupported claims such as:

```text
complete SaaS readiness
legal/compliance outcomes without human review
career outcomes as guaranteed results
validated enterprise deployment
```
