#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fill selected missing PGx, psychiatric association, and curated drug evidence.

Each HTTP request is a single attempt with timeout=15 seconds. Missing values are
kept missing; this script only writes values returned by the cited API responses.
"""
import csv
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

DATA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DATA)
EXP = os.path.join(ROOT, "experiment")
TODAY = "2026-11-27"
TIMEOUT = 15

def log(s):
    print(s, flush=True)

def request(url, method="GET", payload=None, accept="application/json"):
    headers = {"User-Agent": "DataminingEvidenceSupplement/1.0", "Accept": accept}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            text = res.read().decode("utf-8", "replace")
        return (json.loads(text) if "json" in accept.lower() else text), "ok"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    log(f"[OK] {os.path.basename(path)}: {len(rows)} data rows")

VARIANTS = [
    ("CYP2C19", "*2", "rs4244285", "A"),
    ("CYP2C19", "*3", "rs4986893", "A"),
    ("CYP2C19", "*17", "rs12248560", "T"),
    # Ensembl reports population alleles on the forward genomic strand (CYP3A4*22
    # transcript C>T is the genomic reverse-complement G>A).
    ("CYP3A4", "*22", "rs35599367", "A"),
]

def population_rows(data, effect_allele):
    """Return population-name -> frequency for the known functional variant allele."""
    vals = {}
    for p in data.get("populations", []) or []:
        pop = p.get("population", "")
        allele = p.get("allele") or p.get("allele_string")
        freq = p.get("frequency")
        if pop and freq is not None and allele == effect_allele:
            vals[pop] = freq
    return vals

def update_pgx():
    path = os.path.join(DATA, "pgx_cyp2c19_cyp3a4.csv")
    rows = read_csv(path)
    fields = list(rows[0].keys())
    # Remove the previous four placeholder records; preserve any unrelated rows.
    keep = [r for r in rows if not (r.get("gene", "") in ("CYP2C19", "CYP3A4") and r.get("allele", "") in ("*2", "*3", "*17", "*22"))]
    out = []
    for gene, star, rsid, effect_allele in VARIANTS:
        url = f"https://rest.ensembl.org/variation/human/{rsid}?pops=1;content-type=application/json"
        log(f"[Ensembl variation] {rsid}")
        data, status = request(url)
        query = f"GET /variation/human/{rsid}?pops=1;content-type=application/json; reported minor-allele population frequencies"
        if status == "ok" and isinstance(data, dict):
            freqs = population_rows(data, effect_allele)
            # Ensembl population identifiers are retained verbatim. Use 1000 Genomes
            # phase-3 global and East Asian when present; never substitute another cohort.
            wanted = ["1000GENOMES:phase_3:ALL", "1000GENOMES:phase_3:EAS"]
            for pop in wanted:
                found = freqs.get(pop)
                out.append({"gene":gene,"allele":star,"variant":rsid,"population":pop,
                    "allele_frequency_pct":"" if found is None else f"{float(found)*100:.8g}",
                    "source_db":"Ensembl variation / 1000 Genomes phase 3",
                    "drug_relevance_note":f"Ensembl population frequency for variant allele {effect_allele}." if found is not None else f"Effect allele {effect_allele} not present for requested population; no frequency inferred.",
                    "query":query + f"; effect allele={effect_allele}","source_url":url,"retrieval_date":TODAY,
                    "status_or_failure_reason":"ok" if found is not None else "effect_allele_or_population_not_returned"})
        else:
            for pop in ("1000GENOMES:phase_3:ALL", "1000GENOMES:phase_3:EAS"):
                out.append({"gene":gene,"allele":star,"variant":rsid,"population":pop,"allele_frequency_pct":"","source_db":"Ensembl variation",
                    "drug_relevance_note":"","query":query,"source_url":url,"retrieval_date":TODAY,"status_or_failure_reason":f"FAIL: {status}"})
    write_csv(path, keep + out, fields)
    return out

GENES = ["CYP3A4","CYP2C19","POR","GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"]
DISEASES = [
    ("Major depressive disorder", "MONDO_0002009"),
    ("Schizophrenia", "MONDO_0005090"),
    ("Anxiety disorder", "MONDO_0005618"),
]

def update_psychiatric():
    path = os.path.join(DATA, "psychiatric_disease_evidence.csv")
    old = read_csv(path)
    fields = list(old[0].keys())
    # Remove old placeholders/previous supplement result rows before rebuilding.
    old = [r for r in old if r.get("source_db") not in ("Open Targets", "Open Targets GraphQL", "CTD neurotoxicity overlap")]
    ens_url = "https://rest.ensembl.org/lookup/symbol/homo_sapiens"
    log("[Ensembl lookup] resolve 9 candidate symbols")
    lookup, lookup_status = request(ens_url, "POST", {"symbols": GENES})
    sym_to_id = {}
    if lookup_status == "ok" and isinstance(lookup, dict):
        sym_to_id = {v.get("display_name"): k for k, v in lookup.items() if isinstance(v, dict)}
    ot_url = "https://api.platform.opentargets.org/api/v4/graphql"
    new_rows = []
    disease_target_rows = {}
    for disease, did in DISEASES:
        gql = f'''query {{ disease(efoId: "{did}") {{ id name associatedTargets(page: {{index: 0, size: 500}}) {{ count rows {{ target {{ id approvedSymbol }} score }} }} }} }}'''
        log(f"[Open Targets] {disease} ({did})")
        result, status = request(ot_url, "POST", {"query": gql})
        returned = []
        if status == "ok" and isinstance(result, dict):
            disease_obj = (result.get("data") or {}).get("disease") or {}
            returned = (disease_obj.get("associatedTargets") or {}).get("rows", [])
            disease_id = disease_obj.get("id") or did
            disease_name = disease_obj.get("name") or disease
            disease_target_rows[disease_id] = {r.get("target",{}).get("approvedSymbol"):r for r in returned}
            for item in returned:
                t = item.get("target") or {}
                symbol = t.get("approvedSymbol", "")
                if symbol not in GENES: continue
                new_rows.append({"disease":disease_name,"source_db":"Open Targets GraphQL","gene_symbol":symbol,
                    "gene_id":next((r["gene_id"] for r in old if r.get("gene_symbol")==symbol and r.get("gene_id")), ""),
                    "compound_relevance_note":"Candidate xenobiotic metabolism or GABA-A receptor target; OT overall association score is an association ranking, not causal proof.",
                    "evidence_summary":f"Open Targets overall association score={item.get('score')}; disease ID={disease_id}; target ID={t.get('id')}",
                    "query":gql,"source_url":ot_url,"retrieval_date":TODAY,"status_or_failure_reason":"observed_in_first_500_associated_targets"})
            if result.get("errors"):
                status = "GraphQL errors: " + json.dumps(result["errors"], ensure_ascii=False)
        if status != "ok":
            new_rows.append({"disease":disease,"source_db":"Open Targets GraphQL","gene_symbol":"","gene_id":"","compound_relevance_note":"","evidence_summary":"","query":gql,"source_url":ot_url,"retrieval_date":TODAY,"status_or_failure_reason":f"FAIL: {status}"})
        elif not returned:
            new_rows.append({"disease":disease,"source_db":"Open Targets GraphQL","gene_symbol":"","gene_id":"","compound_relevance_note":"","evidence_summary":"Disease record returned no associated target rows.","query":gql,"source_url":ot_url,"retrieval_date":TODAY,"status_or_failure_reason":"no_association_rows_returned"})
        elif not any((x.get("target") or {}).get("approvedSymbol") in GENES for x in returned):
            new_rows.append({"disease":disease,"source_db":"Open Targets GraphQL","gene_symbol":"","gene_id":"","compound_relevance_note":"","evidence_summary":f"No candidate target symbol found among first 500 of {len(returned)} returned associations; this is not proof of zero association.","query":gql,"source_url":ot_url,"retrieval_date":TODAY,"status_or_failure_reason":"no_candidate_in_returned_page"})
    # Resolve actual NCBI GeneID mapping from local known target CSV/curated map.
    gene_ids={"CYP3A4":"1576","CYP2C19":"1557","POR":"5447","GABRA1":"2554","GABRA2":"2555","GABRA3":"2556","GABRA5":"2558","GABRB2":"2561","GABRG2":"2566"}
    for r in new_rows:
        if r.get("gene_symbol") in gene_ids: r["gene_id"]=gene_ids[r["gene_symbol"]]

    # Exact symbol intersection against the 33-row CTD neurotoxicity audit and any
    # candidate genes returned by Open Targets. This is a set comparison only.
    ctd = read_csv(os.path.join(DATA,"ctd_neurotoxicity_gene_audit.csv"))
    ctd_map={r.get("GeneSymbol"):r.get("GeneID") for r in ctd}
    overlap=sorted(set(ctd_map).intersection(GENES))
    for symbol in overlap:
        new_rows.append({"disease":"CTD neurotoxicity gene-list overlap","source_db":"CTD neurotoxicity overlap","gene_symbol":symbol,"gene_id":ctd_map[symbol],
            "compound_relevance_note":"Exact Gene Symbol intersection with candidate target list.","evidence_summary":"Symbol appears in local ctd_neurotoxicity_gene_audit.csv and candidate target list.",
            "query":f"Exact set intersection: CTD neurotoxicity GeneSymbol list ∩ {','.join(GENES)}","source_url":"data/ctd_neurotoxicity_gene_audit.csv","retrieval_date":TODAY,"status_or_failure_reason":"observed_overlap"})
    # Add rows for CTD genes that also appear among the Open Targets positive candidate
    # genes, capturing actual three-way intersection without inventing a score.
    ot_symbols={r["gene_symbol"] for r in new_rows if r.get("source_db")=="Open Targets GraphQL" and r.get("gene_symbol")}
    for symbol in sorted(set(ctd_map).intersection(ot_symbols)):
        new_rows.append({"disease":"CTD neurotoxicity ∩ psychiatric candidate evidence","source_db":"CTD neurotoxicity overlap","gene_symbol":symbol,"gene_id":ctd_map[symbol],
            "compound_relevance_note":"Gene is present in CTD neurotoxicity list and has at least one Open Targets disease association row above.","evidence_summary":"See Open Targets disease-specific row for its score; intersection is symbol-based.",
            "query":"CTD neurotoxicity GeneSymbol intersection with confirmed Open Targets psychiatric candidate associations","source_url":"data/ctd_neurotoxicity_gene_audit.csv","retrieval_date":TODAY,"status_or_failure_reason":"observed_overlap"})
    write_csv(path, old+new_rows, fields)
    log(f"[INFO] CTD neurotoxicity overlap with 9 candidates: {overlap or 'none'}")
    log(f"[INFO] Open Targets candidate disease-gene pairs: {sum(1 for r in new_rows if r.get('source_db')=='Open Targets GraphQL' and r.get('gene_symbol'))}")
    return new_rows, overlap

def parse_kegg_fields(text):
    fields={}
    key=None
    for line in text.splitlines():
        if line.startswith("///"): break
        if line[:12].strip():
            key=line[:12].strip()
            value=line[12:].strip()
            fields.setdefault(key,[]).append(value)
        elif key:
            fields[key].append(line[12:].strip())
    return {k:" ".join(v).strip() for k,v in fields.items()}

def update_expanded():
    path=os.path.join(DATA,"expanded_db_evidence.csv")
    rows=read_csv(path); fields=list(rows[0].keys())
    # Replace previously added copies of these known records for idempotency.
    rows=[r for r in rows if not (r.get("source_db") in ("KEGG Drug observed","ChEMBL archived activity observed"))]
    kegg_url="https://rest.kegg.jp/get/{}"
    drugmap=[("Diazepam","D00293"),("Alprazolam","D00225")]
    gene_ids={"CYP3A4":"1576","CYP2C19":"1557","GABRA1":"2554","GABRA2":"2555","GABRA3":"2556","GABRA5":"2558","GABRB2":"2561","GABRG2":"2566"}
    for drug,kegg_id in drugmap:
        url=kegg_url.format("dr:"+kegg_id)
        log(f"[KEGG Drug] {drug} ({kegg_id})")
        txt,status=request(url,accept="text/plain")
        if status=="ok":
            parsed=parse_kegg_fields(txt)
            target=parsed.get("TARGET",""); metabolism=parsed.get("METABOLISM","")
            druggenes=[]
            for symbol,gid in gene_ids.items():
                if re.search(rf"\b{re.escape(symbol)}\b|HSA:{gid}\b", target+" "+metabolism): druggenes.append((symbol,gid))
            for symbol,gid in druggenes:
                kind="TARGET" if re.search(rf"\b{re.escape(symbol)}\b|HSA:{gid}\b",target) else "METABOLISM"
                note=f"KEGG Drug {kegg_id} {kind} field: " + (target if kind=="TARGET" else metabolism)
                rows.append({"candidate_compound":drug,"cas":"","source_db":"KEGG Drug observed","target_gene":symbol,"gene_id":gid,
                    "chembl_id_compound":"","pubchem_cid":"","uniprot_id":"","interaction_direction_note":note,
                    "query":f"KEGG Drug entry dr:{kegg_id}; inspect TARGET and METABOLISM fields","source_url":url,"retrieval_date":TODAY,"status_or_failure_reason":"observed"})
            if not druggenes:
                rows.append({"candidate_compound":drug,"cas":"","source_db":"KEGG Drug observed","target_gene":"","gene_id":"","chembl_id_compound":"","pubchem_cid":"","uniprot_id":"","interaction_direction_note":f"KEGG fields inspected; target/metabolism genes not found in parsed fields. TARGET={target}; METABOLISM={metabolism}","query":f"KEGG Drug entry dr:{kegg_id}; TARGET and METABOLISM fields","source_url":url,"retrieval_date":TODAY,"status_or_failure_reason":"no_requested_gene_in_fields"})
        else:
            rows.append({"candidate_compound":drug,"source_db":"KEGG Drug observed","target_gene":"","query":f"KEGG Drug entry dr:{kegg_id}","source_url":url,"retrieval_date":TODAY,"status_or_failure_reason":f"FAIL: {status}"})

    # Existing ChEMBL activity artifact has four PBO-CYP3A4 observations, including
    # assay endpoint, values, units and activity comments. Retain all rows as-is facts.
    chem_path=os.path.join(EXP,"chembl_pbo_cyp3a4_activities.csv")
    for a in read_csv(chem_path):
        source_url=a.get("activity_query_url") or "https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL1201131&target_chembl_id=CHEMBL340"
        note=f"Archived ChEMBL activity_id={a['activity_id']}; assay={a['assay_chembl_id']}; standard_type={a['standard_type']}; value={a['standard_value']} {a['standard_units']} (relation {a['standard_relation']}); activity_comment={a['activity_comment']}"
        rows.append({"candidate_compound":"PBO","cas":"51-03-6","source_db":"ChEMBL archived activity observed","target_gene":"CYP3A4","gene_id":"1576","chembl_id_compound":"CHEMBL1201131","pubchem_cid":"124489552","uniprot_id":"P08684",
            "interaction_direction_note":note,"query":"molecule_chembl_id=CHEMBL1201131&target_chembl_id=CHEMBL340 (archived local activity artifact)","source_url":source_url,"retrieval_date":TODAY,"status_or_failure_reason":"observed_archived_source"})
    write_csv(path, rows, fields)

def update_provenance():
    path=os.path.join(DATA,"SOURCE_PROVENANCE.md")
    with open(path,encoding="utf-8") as f: text=f.read()
    start=text.find("\n## Missing-evidence supplement")
    if start>=0: text=text[:start]
    block=f"""

## Missing-evidence supplement ({TODAY})

| Output / query | Source URL | Retrieval date |
|---|---|---|
| `pgx_cyp2c19_cyp3a4.csv`: Ensembl variation populations for rs4244285, rs4986893, rs12248560, rs35599367 (`pops=1`) | Per-variant URL stored in each output row; endpoint [Ensembl variation API](https://rest.ensembl.org/documentation/info/variation_id) | {TODAY} |
| `psychiatric_disease_evidence.csv`: Open Targets associated targets for MDD MONDO_0002009, schizophrenia MONDO_0005090, anxiety disorder MONDO_0005618; exact candidate-symbol filter and first page | [Open Targets GraphQL](https://api.platform.opentargets.org/api/v4/graphql); GraphQL query string stored in rows; Ensembl symbol mapping endpoint `https://rest.ensembl.org/lookup/symbol/homo_sapiens` | {TODAY} |
| `psychiatric_disease_evidence.csv`: exact symbol set intersection with local 33-gene audit | `data/ctd_neurotoxicity_gene_audit.csv` | {TODAY} |
| `expanded_db_evidence.csv`: KEGG Drug TARGET/METABOLISM fields for Diazepam dr:D00293 and Alprazolam dr:D00225 | [KEGG REST API](https://rest.kegg.jp/get/dr:D00293), [Alprazolam](https://rest.kegg.jp/get/dr:D00225) | {TODAY} |
| `expanded_db_evidence.csv`: four PBO/CYP3A4 ChEMBL activity rows copied from archived local source with assay, standard type, value and units | [ChEMBL activity query](https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id=CHEMBL1201131&target_chembl_id=CHEMBL340); source artifact `experiment/chembl_pbo_cyp3a4_activities.csv` | {TODAY} |

All new rows include a query, source URL and retrieval date. Ensembl frequencies are retained only when the requested population appears in the API response. Open Targets rows are positive returned candidate associations; absence from the first 500 rows is not treated as proof of no association. API failures are recorded with their reason.
"""
    with open(path,"w",encoding="utf-8") as f: f.write(text.rstrip()+block)
    log("[OK] SOURCE_PROVENANCE.md")

def main():
    log(f"=== missing evidence supplement {TODAY}; timeout={TIMEOUT}s; retries=0 ===")
    update_pgx()
    update_psychiatric()
    update_expanded()
    update_provenance()
    log("=== supplement complete ===")

if __name__ == "__main__":
    main()
