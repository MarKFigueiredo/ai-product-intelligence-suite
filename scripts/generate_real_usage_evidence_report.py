from services.evidence_report_service import save_real_usage_evidence_report

if __name__ == "__main__":
    path = save_real_usage_evidence_report()
    print(f"Saved {path}")
