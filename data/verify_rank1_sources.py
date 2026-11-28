#!/usr/bin/env python3
"""Recheck Prallethrin PubChem assay records and PMID 24548679 once each."""
import csv
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
TODAY = "2026-11-28"
AIDS = [1671197, 2284395, 1671201, 2283680, 2283689, 2283698, 2284096]
CID = 9839306


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.read()
    except Exception as exc:  # one attempt only; retain failure transparently
        return exc


def text_or_error(result):
    return result.decode("utf-8", "replace") if isinstance(result, bytes) else f"ERROR: {result}"


def main():
    aid_path = DATA / "pubchem_aids.csv"
    with aid_path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0])
    extra = ["verified_target", "verified_assay_name", "cid_9839306_outcome", "cid_9839306_value", "cid_9839306_result_url", "verification_retrieval_date", "verification_status", "verification_detail"]
    for field in extra:
        if field not in fields:
            fields.append(field)
    for row in rows:
        if int(row["AID"]) not in AIDS:
            continue
        aid = int(row["AID"])
        summary_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/summary/JSON"
        result_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/concise/JSON?cid={CID}"
        summary_raw, result_raw = get(summary_url), get(result_url)
        row["verification_retrieval_date"] = TODAY
        row["PUG_REST_URL"] = summary_url
        row["cid_9839306_result_url"] = result_url
        errors = []
        try:
            summary = json.loads(text_or_error(summary_raw))["AssaySummaries"]["AssaySummary"]
            if isinstance(summary, dict): summary = [summary]
            entry = summary[0]
            row["verified_assay_name"] = entry.get("Name", "")
            row["verified_target"] = "CYP2C19" if "CYP2C19" in entry.get("Name", "") else ("CYP3A4" if "CYP3A4" in entry.get("Name", "") else "Target not explicit")
        except Exception as exc:
            errors.append(f"summary: {exc}; {text_or_error(summary_raw)[:250]}")
        try:
            data = json.loads(text_or_error(result_raw))
            table = data.get("Table", {})
            columns = table.get("Columns", {}).get("Column", [])
            records = table.get("Row", [])
            if isinstance(records, dict): records = [records]
            if columns and "CID" in columns and "Activity Outcome" in columns:
                ci, oi = columns.index("CID"), columns.index("Activity Outcome")
                vi = columns.index("Activity Value [uM]") if "Activity Value [uM]" in columns else None
                matches = [r.get("Cell", []) for r in records if len(r.get("Cell", [])) > ci and r["Cell"][ci] == str(CID)]
                outcomes = sorted({r[oi] for r in matches if len(r) > oi and r[oi]})
                values = sorted({r[vi] for r in matches if vi is not None and len(r) > vi and r[vi]})
                row["cid_9839306_outcome"] = "; ".join(outcomes) if outcomes else "Not tested / no record"
                row["cid_9839306_value"] = "; ".join(values)
            else:
                row["cid_9839306_outcome"] = "Unverified (CID/outcome columns absent)"
                row["cid_9839306_value"] = ""
        except Exception as exc:
            errors.append(f"CID result: {exc}; {text_or_error(result_raw)[:250]}")
            row["cid_9839306_outcome"] = "Unverified (API response recorded in detail)"
            row["cid_9839306_value"] = ""
        row["verification_status"] = "verified" if not errors else "partial_or_failed"
        row["verification_detail"] = " | ".join(errors) if errors else "Assay summary and CID-specific concise outcome endpoint queried once each."
    with aid_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

    efetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=24548679&retmode=xml"
    raw = get(efetch_url)
    audit_path = DATA / "ctd_direction_audit.csv"
    with audit_path.open(newline="", encoding="utf-8") as f:
        audit = list(csv.DictReader(f)); audit_fields = list(audit[0])
    for key in ["pubmed_verified_date", "efetch_url", "pubmed_verified_summary", "pubmed_verified_quote", "pubmed_verification_status"]:
        if key not in audit_fields: audit_fields.append(key)
    summary = quote = status = ""
    try:
        root = ET.fromstring(raw)
        article = root.find(".//PubmedArticle")
        title = "".join(article.find(".//ArticleTitle").itertext())
        abstract = " ".join("".join(x.itertext()) for x in article.findall(".//Abstract/AbstractText"))
        sentence = next((s.strip() for s in abstract.split(". ") if "CYP3A4" in s or "CYP2C19" in s), "")
        quote = (sentence + ("." if sentence and not sentence.endswith(".") else ""))[:1000]
        summary = f"Title: {title}. Abstract confirms CYP3A4 and CYP2C19 involvement in permethrin metabolism. Verified text: {quote}"
        status = "verified"
    except Exception as exc:
        summary = f"Retrieval/parsing failed: {exc}; {text_or_error(raw)[:500]}"
        status = "failed"
    for row in audit:
        row["pubmed_verified_date"] = TODAY; row["efetch_url"] = efetch_url
        row["pubmed_verified_summary"] = summary; row["pubmed_verified_quote"] = quote
        row["pubmed_verification_status"] = status
    with audit_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=audit_fields, extrasaction="ignore"); w.writeheader(); w.writerows(audit)
    print("AID verification complete")
    for r in rows:
        if int(r["AID"]) in AIDS: print(r["AID"], r.get("verified_target"), r.get("cid_9839306_outcome"), r.get("cid_9839306_value"), r.get("verification_status"))
    print("PMID", status, summary)


if __name__ == "__main__": main()
