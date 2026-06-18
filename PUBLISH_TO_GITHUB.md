# Publish to GitHub and Streamlit Cloud

## 1. GitHub

```bash
git init
git add .
git commit -m "Add AI Product Intelligence Suite 1.04"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-product-intelligence-suite.git
git push -u origin main
```

## 2. Streamlit Cloud

Deploy `app.py` from the repository root.

Add this secret in Streamlit Cloud:

```toml
OPENAI_API_KEY="your_key_here"
```

Keep **Demo Mode ON** for public demos to avoid API cost and protect secrets.

## 3. Before sharing with recruiters

- Replace mock screenshots with real screenshots.
- Add Streamlit demo URL to the README.
- Add video demo link.
- Use the hero SAF-T/e-invoicing sample.
