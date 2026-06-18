# Start Here — Ubuntu

```bash
mkdir -p ~/Projetos
cd ~/Transferências
unzip ai_pm_winning_suite_1_02.zip -d ~/Projetos
cd ~/Projetos/ai_pm_winning_suite_1_02
code .
```

In the VS Code terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Open `.env` and add your API key only when you want live generation:

```text
OPENAI_API_KEY=sk-proj-your-key-here
```

Start with **Demo Mode ON**. It uses synthetic outputs and does not call the API.
