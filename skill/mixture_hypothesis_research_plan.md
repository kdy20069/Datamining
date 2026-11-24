# Mixture hypothesis: research question and test plan

## Research question

In the target pest species, does PBO inhibit the relevant CYP450 activity enough to reduce deltamethrin metabolism, increase internal deltamethrin exposure, and produce a mixture effect on knockdown or mortality that exceeds the expected effect of the two compounds alone?

**Scope note:** CYP isoforms and pyrethroid metabolism vary by species and strain. “CYP” in the sketch is a family-level candidate, not a confirmed specific enzyme for the classroom mixture.

## Network interpretation

- **Solid path, deltamethrin → VGSC → neuronal/behavioral effect:** established pyrethroid mode of action in the literature. Measure in the selected test organism; resistance mutations can alter the response.
- **Solid path, PBO → detoxification enzymes → reduced pyrethroid detoxification:** a well-established synergist rationale, but the actual CYP isoform, size, and direction of effect are organism- and assay-dependent.
- **Dashed link, PBO → CYP inhibition in this target species:** verify biochemical inhibition in the species/strain being studied.
- **Dashed link, inhibited metabolism → increased deltamethrin exposure at VGSC:** test internal parent compound and metabolite levels; do not infer from a CYP3A4 database entry.
- **Dashed link, mixture → greater-than-expected phenotype:** the central mixture hypothesis. A stronger response alone does not prove synergy; compare against a defined additivity model.

## Evidence already in hand and its limit

The previous ChEMBL heatmap reports 0 AChE and 0 human CYP3A4 activity records for deltamethrin, and 4 CYP3A4-related records for PBO. Inspection of the PBO records shows mixed assay labels (including CYP3A4 activator and inhibitor/substrate assay formats), so “4 records” cannot be summarized as “4 demonstrations of inhibition.” These records are not a direct assay of the target pest’s CYP isoforms, and the heatmap did not test a mixture. Thus ChEMBL helps locate a follow-up target but does not close the interaction gap.

## Minimal test design

1. **Choose and define the biological system.** Name the pest species and strain (susceptible and, if relevant, resistant); keep life stage, sex, temperature, and exposure route constant. Use a validated, locally approved organismal assay.
2. **Run single-agent dose responses.** Deltamethrin alone and PBO alone, with solvent/vehicle control, to identify a sublethal range and any PBO-only effect.
3. **Run a concentration-response mixture matrix.** Test multiple deltamethrin doses crossed with multiple PBO doses, including zero-dose rows/columns. Keep total vehicle and exposure conditions matched. Randomize treatment allocation and use independent biological replicates.
4. **Measure linked endpoints.** (a) CYP activity in relevant tissue or microsomes, with a validated probe substrate; (b) internal deltamethrin and major metabolites at fixed time points using an analytical method such as LC-MS; (c) blinded knockdown/recovery and mortality at predeclared time points. The primary endpoint should be chosen before data collection.
5. **Test interaction, not just difference.** Fit a dose-response model and compare mixture responses with an explicit additivity reference (for example, concentration addition/Loewe where appropriate); report interaction estimates and confidence intervals. Include an independent factorial interaction term as a sensitivity check. State the model and its assumptions.
6. **Use a mechanistic check.** If feasible, compare a CYP activity readout or a target CYP knockdown/inhibition control with the mixture. If the phenotype changes without CYP activity or internal deltamethrin changing, the proposed metabolic link is weakened and another mechanism should be considered.

## Gap → hypothesis → falsifiable predictions

**Gap:** the current database summary does not establish that PBO inhibits the target species’ relevant CYP enzyme, alters deltamethrin burden, or causes synergy in the exact mixture.

**Hypothesis:** PBO suppresses a deltamethrin-detoxifying CYP pathway in the selected pest, increasing internal parent deltamethrin and producing a mixture effect greater than the prespecified additive expectation.

Predictions that would support it: PBO reduces the selected CYP activity; the mixture increases parent deltamethrin or reduces its metabolite-to-parent ratio; and the phenotype interaction estimate is positive under the prespecified model. The hypothesis is weakened if CYP activity is unchanged, internal exposure does not shift, or the mixture is consistent with additivity after accounting for PBO-alone effects.

## Sources

- Soderlund, D. M. “Molecular mechanisms of pyrethroid insecticide neurotoxicity: recent advances.” [Archives of Toxicology (2012)](https://doi.org/10.1007/s00204-011-0726-x).
- “Synergist piperonyl butoxide enhances the efficacy of deltamethrin in deltamethrin-resistant *Anopheles culicifacies*...” [PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC6676828/).
- ChEMBL records from the prior analysis: PBO [CHEMBL1201131](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL1201131) and deltamethrin [CHEMBL1593566](https://www.ebi.ac.uk/chembl/explore/compound/CHEMBL1593566). Targeted count in the existing heatmap used human AChE CHEMBL220 and CYP3A4 CHEMBL340, so interpret as database coverage for those selected targets only.
