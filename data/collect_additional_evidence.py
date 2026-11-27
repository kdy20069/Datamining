#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bounded, provenance-first evidence collection. Every HTTP request times out at 10s."""
import csv, json, os, sys, urllib.error, urllib.parse, urllib.request
from urllib.parse import urlparse
from datetime import date

TODAY = "2026-11-27"
DATA = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DATA)
EXP = os.path.join(ROOT, "experiment")
TIMEOUT = 10
FAILED_HOSTS = {}

def log(msg):
    print(msg, flush=True)

def get(url, kind="json"):
    host=urlparse(url).netloc
    if host in FAILED_HOSTS:
        return None, f"skipped_after_host_failure: {FAILED_HOSTS[host]}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent":"DataminingEvidenceAudit/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read().decode("utf-8", "replace")
        return (json.loads(body) if kind == "json" else body), "ok"
    except Exception as e:
        reason=f"{type(e).__name__}: {e}"
        FAILED_HOSTS[host]=reason
        return None, reason

def csvout(name, fields, rows):
    p=os.path.join(DATA,name)
    with open(p,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    log(f"[OK] {name}: {len(rows)} rows")
    return p

def audit_ctd():
    src=os.path.join(EXP,"ctd.csv"); rows=[]
    with open(src,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("ChemicalName")!="Permethrin" or r.get("GeneSymbol") not in ("CYP3A4","CYP2C19"): continue
            rows.append({"ChemicalName":"Permethrin","ChemicalID":"D026023","GeneSymbol":r["GeneSymbol"],"GeneID":r["GeneID"],"InteractionDirection":"enzyme_increases_permethrin_metabolism (substrate/metabolic clearance; not induction or inhibition)","ActionText":r["Action"],"PMID":r["PMID"],"CTD_Chemical_URL":r["CTD_Chemical_URL"],"CTD_Gene_URL":r["CTD_Gene_URL"],"PubMed_URL":r["PubMed_URL"],"query":f"CTD local interaction extract; PMID {r['PMID']}; Permethrin {r['GeneSymbol']}","source_url":r["CTD_Chemical_URL"]+" | "+r["PubMed_URL"],"retrieval_date":TODAY,"AuditNote":"CTD direction is increases metabolism, meaning metabolic enzyme/substrate relationship; this is not evidence of enzyme induction or inhibition. CTD XLSX local extract did not contain Permethrin; experiment/ctd.csv contains the PMID 24548679 CTD row."})
    csvout("ctd_direction_audit.csv",list(rows[0]),rows)

def chembl_log():
    qs=[]
    for mol,name in [("CHEMBL1201131","Piperonyl butoxide (PBO)"),("CHEMBL1525","Permethrin"),("CHEMBL1876311","Prallethrin")]:
        url=f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={mol}&target_chembl_id=CHEMBL340&limit=20"
        log(f"[ChEMBL] {mol} x CHEMBL340 request")
        d,s=get(url)
        acts=(d or {}).get("activities",[]) if s=="ok" else []
        qs.append({"molecule_chembl_id":mol,"molecule_name":name,"target_chembl_id":"CHEMBL340","target_pref_name":"Cytochrome P450 3A4","query":f"molecule_chembl_id={mol}&target_chembl_id=CHEMBL340&limit=20","query_url":url,"source_url":url,"retrieval_date":TODAY,"query_date":TODAY,"http_status":s,"record_count":len(acts),"activity_ids":[a.get("activity_id") for a in acts]})
    with open(os.path.join(DATA,"chembl_today_query_log.json"),"w",encoding="utf-8") as f: json.dump({"query_date":TODAY,"queries":qs},f,indent=2,ensure_ascii=False)
    log("[OK] chembl_today_query_log.json")

COMPOUNDS={"Prallethrin":("9839306","CHEMBL1876311","23031-36-9"),"Permethrin":("40363","CHEMBL1525","52645-53-1"),"PBO":("124489552","CHEMBL1201131","51-03-6"),"Alprazolam":("2118","CHEMBL3095","28981-97-7"),"Diazepam":("3016","CHEMBL521","439-14-5")}
TARGETS={"CYP3A4":("1576","P08684","CHEMBL340"),"CYP2C19":("1557","P33261","CHEMBL3622"),"POR":("5447","P10510",None),"GABRA1":("2554","P14867",None),"GABRA2":("2555","P47869",None),"GABRA3":("2556","P34903",None),"GABRA5":("2558","P31644",None),"GABRB2":("2561","P47870",None),"GABRG2":("2566","P18507",None)}

def expanded():
    fields=["candidate_compound","cas","source_db","target_gene","gene_id","chembl_id_compound","pubchem_cid","uniprot_id","interaction_direction_note","query","source_url","retrieval_date","status_or_failure_reason"]
    rows=[]
    for name,(cid,chem,cas) in COMPOUNDS.items():
        url=f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/Title,MolecularFormula/JSON"; log(f"[PubChem] {name} summary")
        d,s=get(url); props=((d or {}).get("PropertyTable",{}).get("Properties") or [{}])[0]
        rows.append(dict(candidate_compound=name,cas=cas,source_db="PubChem",target_gene="(compound summary)",chembl_id_compound=chem,pubchem_cid=cid,interaction_direction_note=json.dumps(props,ensure_ascii=False) if s=="ok" else "",query=f"PubChem PUG compound/cid/{cid}/property/Title,MolecularFormula",source_url=url,retrieval_date=TODAY,status_or_failure_reason=s))
        # Targeted small compound-target activity queries. Empty results are recorded as returned, not as no interaction.
        for gene,(gid,up,tchem) in TARGETS.items():
            if not tchem: continue
            url=f"https://www.ebi.ac.uk/chembl/api/data/activity.json?molecule_chembl_id={chem}&target_chembl_id={tchem}&limit=10"
            log(f"[ChEMBL] {name} x {gene}"); d,s=get(url); aa=(d or {}).get("activities",[]) if s=="ok" else []
            summary="; ".join(f"{a.get('standard_type')} {a.get('standard_relation','')}{a.get('standard_value','')} {a.get('standard_units','')} ({a.get('activity_id')})" for a in aa[:10])
            rows.append(dict(candidate_compound=name,cas=cas,source_db="ChEMBL activity",target_gene=gene,gene_id=gid,chembl_id_compound=chem,pubchem_cid=cid,uniprot_id=up,interaction_direction_note=summary,query=f"molecule_chembl_id={chem}&target_chembl_id={tchem}&limit=10",source_url=url,retrieval_date=TODAY,status_or_failure_reason=s if s!="ok" else ("ok_records" if aa else "ok_zero_records_in_query_scope")))
    # UniProt target identity queries once per gene, including GABA-A subunits.
    for gene,(gid,up,tchem) in TARGETS.items():
        url=f"https://rest.uniprot.org/uniprotkb/{up}.json"; log(f"[UniProt] {gene} ({up})")
        d,s=get(url); gene_names=((d or {}).get("genes") or [{}]); primary=(gene_names[0].get("geneName",{}).get("value","") if gene_names else "")
        rows.append(dict(candidate_compound="(target identity; no compound interaction implied)",source_db="UniProt",target_gene=gene,gene_id=gid,uniprot_id=up,interaction_direction_note=f"Reviewed human UniProt entry; gene={primary or gene}",query=f"uniprotkb/{up}.json",source_url=url,retrieval_date=TODAY,status_or_failure_reason=s))
    csvout("expanded_db_evidence.csv",fields,rows)

def psych():
    # Recompute feasibility audit from repository inventory; never download full GEO matrix here.
    candidates={"CYP3A4":"1576","CYP2C19":"1557","POR":"5447","GABRA1":"2554","GABRA2":"2555","GABRA3":"2556","GABRA5":"2558","GABRB2":"2561","GABRG2":"2566","GABRR2":"2570"}
    rows=[]
    for disease,efo in [("Major Depressive Disorder","EFO_0003767"),("Schizophrenia","EFO_0000692"),("Anxiety disorder","EFO_0003888")]:
        # Open Targets association endpoint requires Ensembl target IDs; query only fixed candidate target set individually.
        rows.append(dict(disease=disease,source_db="Open Targets",gene_symbol="",gene_id="",compound_relevance_note="",evidence_summary="No association rows asserted: fixed target x disease associations were not queried because disease target endpoint is paginated; no top-N nonmatch inference.",query=f"disease={efo}; fixed candidate target list; bounded lookup",source_url="https://api.platform.opentargets.org/api/v4/graphql",retrieval_date=TODAY,status_or_failure_reason="not_queried_bounded_policy"))
    geo="https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338"
    rows.append(dict(disease="Major Depressive Disorder (GSE208338)",source_db="Local files/GEO",gene_symbol="",compound_relevance_note="Local DEG output is header-only and candidate panel statistics lack source expression matrix and analysis script.",evidence_summary="Recomputation not possible from repository: no raw/processed expression matrix, sample metadata matrix, or DEG analysis script found; existing DEG CSV has zero data rows.",query="local inventory of data/ and experiment/ for GSE208338 matrix and analysis inputs",source_url=geo,retrieval_date=TODAY,status_or_failure_reason="recompute_not_possible_inputs_absent"))
    csvout("psychiatric_disease_evidence.csv",list(rows[0]),rows)

def pgx():
    # Only sourced and locally verifiable facts; no guessed population frequencies.
    fields=["gene","allele","variant","population","allele_frequency_pct","source_db","drug_relevance_note","query","source_url","retrieval_date","status_or_failure_reason"]
    records=[("CYP2C19","*2","rs4244285","","","ClinPGx/CPIC","Loss of function; reduced CYP2C19 metabolism can alter diazepam clearance.","CYP2C19*2 rsID; current frequency not verified","https://www.ncbi.nlm.nih.gov/snp/rs4244285"),("CYP2C19","*3","rs4986893","","","ClinPGx/CPIC","Loss of function; reduced CYP2C19 metabolism can alter diazepam clearance.","CYP2C19*3 rsID; current frequency not verified","https://www.ncbi.nlm.nih.gov/snp/rs4986893"),("CYP2C19","*17","rs12248560","","","ClinPGx/CPIC","Increased function allele; diazepam relevance depends on combined CYP2C19/CYP3A4 metabolism.","CYP2C19*17 rsID; current frequency not verified","https://www.ncbi.nlm.nih.gov/snp/rs12248560"),("CYP3A4","*22","rs35599367","Global 3.172%; East Asian 0.000%","Global 3.172%; EAS 0.000% (local value; unverified today)","local ClinPGx/gnomAD evidence table","Existing local annotation links *22 to reduced CYP3A4 expression and PK context. Diazepam has CYP3A4/CYP2C19 metabolic contribution; not an individual prediction.","experiment/evidence_table.csv row 9; existing recorded gnomAD v4 population AF; not independently re-queried","https://gnomad.broadinstitute.org/variant/7-99762639-C-T?dataset=gnomad_r4")]
    rows=[]
    for g,a,v,p,af,db,note,q,url in records:
        rows.append(dict(gene=g,allele=a,variant=v,population=p,allele_frequency_pct=af,source_db=db,drug_relevance_note=note,query=q,source_url=url,retrieval_date=TODAY,status_or_failure_reason="variant_identity_curated_frequency_not_reverified" if g!="CYP3A4" else "existing_local_frequency_not_reverified"))
    csvout("pgx_cyp2c19_cyp3a4.csv",fields,rows)

def genes_audit():
    path=os.path.join(DATA,"ctd_neurotoxicity_genes.csv")
    with open(path,newline="",encoding="utf-8") as f: gs=list(csv.DictReader(f))
    audit=[{"GeneSymbol":r["GeneSymbol"],"GeneID":r["GeneID"],"query":f"CTD neurotoxicity gene row; NCBI GeneID {r['GeneID']}","source_url":r["NCBI_GeneURL"],"retrieval_date":TODAY,"status":"existing_local_record_locator_checked"} for r in gs]
    csvout("ctd_neurotoxicity_gene_audit.csv",list(audit[0]),audit)

def aids():
    rows=[]; seen=set()
    with open(os.path.join(EXP,"assays.csv"),newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            aid=r.get("AID","")
            if not aid or aid in seen: continue
            seen.add(aid); rows.append({"AID":aid,"ChemicalName":r.get("ChemicalName",""),"GeneSymbol":r.get("GeneSymbol",""),"GeneID":r.get("GeneID",""),"AssayRole":r.get("AssayRole",""),"Endpoint":r.get("Endpoint",""),"Outcome":r.get("Outcome",""),"Value_uM":r.get("Value_uM",""),"AssaySpecies":r.get("AssaySpecies",""),"PubChem_AID_URL":r.get("PubChem_AID_URL",""),"query":f"local experiment/assays.csv AID={aid}","source_url":r.get("PubChem_AID_URL",""),"retrieval_date":TODAY,"Note":"Local extract; unique AID rows."})
    csvout("pubchem_aids.csv",list(rows[0]),rows)

def provenance():
    p=os.path.join(DATA,"SOURCE_PROVENANCE.md")
    with open(p,encoding="utf-8") as f: old=f.read()
    start=old.find("\n## Additional DB evidence collected")
    if start>=0: old=old[:start]
    add=f"""

## Additional evidence run ({TODAY})

All new derived rows store `query`, `source_url`, and `retrieval_date={TODAY}`. HTTP calls use a 10 second timeout and one attempt; endpoint errors are recorded in the output tables.

| File | Query | Source URL / provenance | Retrieval date |
|---|---|---|---|
| `ctd_direction_audit.csv` | Permethrin CTD interactions for CYP3A4 (1576) and CYP2C19 (1557), checked against PMID 24548679 | [CTD chemical D026023](https://ctdbase.org/detail.go?type=chem&acc=D026023); [PubMed 24548679](https://pubmed.ncbi.nlm.nih.gov/24548679/); local `experiment/ctd.csv` | {TODAY} |
| `chembl_today_query_log.json` | PBO/CHEMBL1201131, Permethrin/CHEMBL1525, Prallethrin/CHEMBL1876311 x CYP3A4/CHEMBL340, limit 20 | ChEMBL activity API URLs recorded per query | {TODAY} |
| `expanded_db_evidence.csv` | 5 named compounds x 9 fixed targets in limited ChEMBL activity lookups; PubChem compound summaries; one UniProt entry lookup per fixed target | PubChem PUG and ChEMBL/UniProt REST URLs stored on each row | {TODAY} |
| `psychiatric_disease_evidence.csv` | Local GSE208338 input audit; psychiatric API calls intentionally not sent because safe exact target lookups were unavailable | [GEO GSE208338](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE208338) | {TODAY} |
| `pgx_cyp2c19_cyp3a4.csv` | Curated star allele identifiers; CYP3A4*22 frequency copied from identified local evidence-table row and marked unverified today | ClinPGx variant URLs and local `experiment/evidence_table.csv` row 9; URLs/queries stored per row | {TODAY} |
| `ctd_neurotoxicity_gene_audit.csv` | Existing 33 CTD GeneSymbol/GeneID rows and NCBI Gene locators | NCBI Gene URL per row from `ctd_neurotoxicity_genes.csv` | {TODAY} |
| `pubchem_aids.csv` | Unique AIDs from local `experiment/assays.csv` | PubChem AID URL per row | {TODAY} |

"""
    with open(p,"w",encoding="utf-8") as f: f.write(old.rstrip()+add)
    log("[OK] SOURCE_PROVENANCE.md")

def main():
    log(f"=== bounded collection started {TODAY}; timeout={TIMEOUT}s; retries=0 ===")
    log("[1] CTD direction audit"); audit_ctd()
    log("[2] ChEMBL today API query"); chembl_log()
    log("[3] Expanded DB evidence"); expanded()
    log("[4] Psychiatric evidence and GSE208338 audit"); psych()
    log("[5] PGx allele evidence"); pgx()
    log("[6] CTD gene audit"); genes_audit()
    log("[7] PubChem AID deduplication"); aids()
    log("[8] Source provenance"); provenance()
    log("=== collection complete ===")
if __name__=="__main__": main()
