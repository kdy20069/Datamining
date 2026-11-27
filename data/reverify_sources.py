#!/usr/bin/env python3
"""Single-attempt live CTD and PubChem PUG-REST rechecks (15 s timeout)."""
import csv, json, os, urllib.request, urllib.error
from datetime import date

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data")
TODAY="2026-11-27"

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Datamining-source-reverification/1.0","Accept":"application/json,text/tab-separated-values,text/plain,*/*"})
    with urllib.request.urlopen(req,timeout=15) as r: return r.read()

def csvread(path):
    with open(path,newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def csvwrite(path,rows,fields):
    with open(path,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def main():
    # CTD public downloads/API endpoints: preserve each attempted source and explicit failure.
    ctd_rows=[]
    queries=[("Permethrin (D026023) chemical-gene interactions for CYP3A4/GeneID 1576 and CYP2C19/GeneID 1557","https://ctdbase.org/detail.go?type=chem&acc=D026023&view=ixn","interaction"),
             ("Neurotoxicity Syndromes (MESH:D020258) associated genes","https://ctdbase.org/detail.go?type=disease&acc=MESH%3AD020258&view=gene","disease_gene")]
    for query,url,kind in queries:
        try:
            raw=get(url).decode("utf-8","replace")
            ctd_rows.append({"record_type":kind,"query":query,"source_url":url,"retrieval_date":TODAY,"status":"response_received_unparsed","gene_symbol":"","gene_id":"","chemical_id":"D026023" if kind=="interaction" else "","payload_excerpt":raw[:1000],"failure_reason":""})
        except Exception as e:
            ctd_rows.append({"record_type":kind,"query":query,"source_url":url,"retrieval_date":TODAY,"status":"failed","gene_symbol":"","gene_id":"","chemical_id":"D026023" if kind=="interaction" else "","payload_excerpt":"","failure_reason":f"{type(e).__name__}: {e}"})
    # CTD official report downloads are the structured fallback; one request per report, no retries.
    for report,query in [("CTD_chem_gene_ixns.tsv.gz","CTD chemical-gene interaction report; filter chemical D026023 and genes 1576/1557"),("CTD_genes_diseases.tsv.gz","CTD gene-disease report; filter disease MESH:D020258")]:
        url="https://ctdbase.org/reports/"+report
        try:
            raw=get(url)
            import gzip,io
            lines=gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode("utf-8","replace").splitlines()
            hdr=next((i for i,l in enumerate(lines) if l.startswith("ChemicalName\t") or l.startswith("GeneID\t")),None)
            hits=[]
            if hdr is not None:
                headers=lines[hdr].split("\t")
                for line in lines[hdr+1:]:
                    vals=line.split("\t")
                    if len(vals)<len(headers):continue
                    row=dict(zip(headers,vals))
                    if report.startswith("CTD_chem_gene") and row.get("ChemicalID")=="D026023" and row.get("GeneID") in {"1576","1557"}: hits.append(row)
                    if report.startswith("CTD_genes") and row.get("DiseaseID")=="MESH:D020258": hits.append(row)
            for row in hits:
                ctd_rows.append({"record_type":"interaction" if report.startswith("CTD_chem_gene") else "disease_gene","query":query,"source_url":url,"retrieval_date":TODAY,"status":"observed","gene_symbol":row.get("GeneSymbol",""),"gene_id":row.get("GeneID",""),"chemical_id":row.get("ChemicalID",""),"payload_excerpt":json.dumps(row,ensure_ascii=False),"failure_reason":""})
            ctd_rows.append({"record_type":"download_audit","query":query,"source_url":url,"retrieval_date":TODAY,"status":"download_parsed","gene_symbol":"","gene_id":"","chemical_id":"","payload_excerpt":f"matching rows={len(hits)}; report header found={hdr is not None}","failure_reason":""})
        except Exception as e:
            ctd_rows.append({"record_type":"download_audit","query":query,"source_url":url,"retrieval_date":TODAY,"status":"failed","gene_symbol":"","gene_id":"","chemical_id":"","payload_excerpt":"","failure_reason":f"{type(e).__name__}: {e}"})
    csvwrite(os.path.join(DATA,"ctd_neurotoxicity_live.csv"),ctd_rows,["record_type","query","source_url","retrieval_date","status","gene_symbol","gene_id","chemical_id","payload_excerpt","failure_reason"])
    # Correct the provenance labels on prior local-only CTD extracts.
    for name in ("ctd_neurotoxicity_genes.csv","ctd_neurotoxicity_gene_audit.csv","ctd_direction_audit.csv"):
        path=os.path.join(DATA,name)
        if not os.path.exists(path):continue
        old=csvread(path)
        if not old:continue
        for row in old:
            row["retrieval_date"]="Local extract (original query date unrecorded)"
            if "Source_Locator_Audit_Date" in row: row["Source_Locator_Audit_Date"]="Local extract (original query date unrecorded)"
        fields=list(old[0])
        if "retrieval_date" not in fields:fields.append("retrieval_date")
        csvwrite(path,old,fields)
    observed=[r for r in ctd_rows if r["record_type"]=="disease_gene" and r["status"]=="observed"]
    if observed:
        genes={r["gene_symbol"] for r in observed}
        candidates={"CYP3A4","CYP2C19","POR","GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"}
        overlap=sorted(genes&candidates); source="data/ctd_neurotoxicity_live.csv"
        note="Live CTD report gene rows; exact symbol intersection."
    else:
        old=csvread(os.path.join(DATA,"ctd_neurotoxicity_genes.csv"));genes={r.get("GeneSymbol","") for r in old}
        overlap=sorted(genes&{"CYP3A4","CYP2C19","POR","GABRA1","GABRA2","GABRA3","GABRA5","GABRB2","GABRG2"});source="data/ctd_neurotoxicity_genes.csv"
        note='CTD live request failed or returned no parsed gene records; local extract only. Original query date unrecorded; not a 2026-11-27 retrieval.'
    overlaprows=[{"summary":"CTD Neurotoxicity Syndromes ∩ 9 candidate target symbols","n_genes":len(overlap),"genes":";".join(overlap),"source_count":len(observed) if observed else len(genes),"query":"Exact symbol intersection: MESH:D020258 CTD genes with fixed 9 candidate targets","source_url":source,"retrieval_date":TODAY,"note":note}]
    other=next((r for r in csvread(os.path.join(ROOT,"experiment","gene_overlap_summary.csv")) if "Open Targets" in r.get("summary", "")),None)
    if other:overlaprows.append(other)
    csvwrite(os.path.join(ROOT,"experiment","gene_overlap_summary.csv"),overlaprows,list(overlaprows[0]))
    # PubChem PUG-REST summary verification; leave original values intact and append verification state.
    aids=csvread(os.path.join(DATA,"pubchem_aids.csv"));base="https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{}/summary/JSON"
    for r in aids:
        url=base.format(r["AID"]);r["PUG_REST_URL"]=url;r["verification_retrieval_date"]=TODAY
        r["retrieval_date"]="Local extract (original query date unrecorded)"
        try:
            d=json.loads(get(url));summary=d.get("AssaySummaries",{}).get("AssaySummary",[])
            r["verification_status"]="verified_summary_returned" if summary else "verified_response_no_summary_object"
            r["verification_detail"]=f"summary_records={len(summary)}"
        except Exception as e:
            r["verification_status"]="failed";r["verification_detail"]=f"{type(e).__name__}: {e}"
    fields=list(aids[0]);
    for x in ["PUG_REST_URL","verification_retrieval_date","verification_status","verification_detail"]:
        if x not in fields:fields.append(x)
    csvwrite(os.path.join(DATA,"pubchem_aids.csv"),aids,fields)

if __name__=="__main__":main()
