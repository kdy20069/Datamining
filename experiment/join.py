import pandas as pd

# 1. CSV 파일 읽기
ctd_df = pd.read_csv('ctd.csv')
assays_df = pd.read_csv('assays.csv')

# 2. numeric GeneID를 기준으로 Inner Join 수행
# (assays.csv의 7개 행과 ctd.csv의 일치하는 GeneID를 결합)
joined_df = pd.merge(assays_df, ctd_df, on='GeneID', how='inner', suffixes=('_assay', '_ctd'))

# 3. Preserve the assay and CTD record locators in the joined output.
joined_df['GeneSymbol'] = joined_df['GeneSymbol_assay']
joined_df['Interpretation'] = joined_df.apply(
    lambda r: (
        f"{r['Action']}; shared GeneID links the Prallethrin assay record to this "
        "CTD metabolism record. This supports a cross-dataset association only; "
        "it does not establish that Prallethrin alters permethrin metabolism or "
        "causes an in-vivo interaction."
    ), axis=1
)
joined_df['Source_Locator_Audit_Date'] = '2026-11-23'

output_columns = [
    'GeneID', 'GeneSymbol', 'AssayRole', 'ChemicalName_assay', 'CID', 'AID',
    'Endpoint', 'Outcome', 'Value_uM', 'AssaySpecies', 'PubChem_CID_URL',
    'PubChem_AID_URL', 'ChemicalName_ctd', 'ChemicalID', 'Interpretation',
    'Action', 'Species', 'PMID', 'CTD_Chemical_URL', 'CTD_Gene_URL',
    'PubMed_URL', 'Source_Locator_Audit_Date'
]
joined_final = joined_df[output_columns]
joined_final.to_csv('joined.csv', index=False)
print(f"Successfully merged! Total rows saved: {len(joined_final)}")
