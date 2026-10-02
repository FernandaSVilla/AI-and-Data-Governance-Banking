# Evaluability · AI & Data Governance · Banking – Open Source

**Open audit of access before the credit model** — open non-entry governance kit (Python package `evaluabilidad`, v0.3)

**The industry already audits how a model treats the people it scores. This kit audits who got to be scored.**

Fairness tests for creditworthiness systems are computed on the applications that reach the model. If a person's document, address, channel or identity-verification step filters them out earlier, the model can pass those tests while exclusion still exists. The kit makes that stage visible with data institutions already hold, and shows, for each *entry profile*, **at which stage** the first gap appears: at onboarding, on reaching the model, or in the decision. It measures associations, not causes.

- **Web version (no installation, bilingual ES/EN):** https://fernandasvilla.github.io/AI-and-Data-Governance-Banking/?lang=en — everything runs in the browser; no data leaves the device and no third-party resources are loaded.
- **Python:** `python -m evaluabilidad --altas attempts.csv [--credito credit.csv] --salida report.html --umbral 0.8` (the generated report is in Spanish).

## Entry profiles
Standard document (reference) · International protection document · Pending residence number or official receipt · Non-EU passport without a chip · No fixed address or no proof of address · Phone or connection not good enough for verification · Needs help to complete the digital process · Needs an accessibility adjustment · No credit history · Other. Definitions: `evaluabilidad/perfiles_en.py`.

## What it measures
**Stage views**, each measured among those who passed the previous stage so earlier losses are not carried forward: *onboarding* — gets the account? (account / attempts); *reaching the model* — with an account, is the person scored? (scored / account); *decision* — among those scored, is there an approval gap? (approved / scored). **Cumulative views** summarise the total effect: *evaluability*, the essay's concept (scored / attempts), and *effective access* (approved / attempts). An approval gap is descriptive: it may reflect differences in risk, system variables or prior selection. Each ratio carries a 95% Katz confidence interval (identical to `scipy.stats.contingency.relative_risk`, checked by the tests; Haldane-Anscombe correction when a profile has zero successes) and a three-level signal (clear signal, to be confirmed, no signal) against a configurable review threshold (default 0.80, the conventional "four-fifths" benchmark — a practical rule, not an EU legal standard) and a configurable minimum sample (`--n-min`, default 100).

**Basic mode** needs only `id_intento, fecha, canal, perfil_entrada, resultado`. **Full mode** adds the standardised cause of non-entry, traceability fields and credit decisions (`id_intento, aprobado`). Data column names and codes are in Spanish; see `esquema/registro_no_acceso.schema.json`.

## Survey mode (experimental)

To test the kit's logic on **public data** before any institution shares logs, `evaluabilidad.encuestas` applies it to survey microdata (e.g. Global Findex or UNHCR forced-displacement surveys from its microdata library). The unit is the person, not the attempt, so only the first stage (account ownership) is measured rigorously; formal credit is descriptive and reasons for having no account are self-reported. It uses **survey weights** and, when published, **strata and clusters** (Taylor-linearised CI for the ratio; with equal weights and no clusters it matches the log-mode interval, as the tests check). Only aggregate results are stored, cells with fewer than 30 observations are suppressed, and microdata stay in the local `microdatos/` folder, excluded from the repository. Adapters: `src/encuestas/fuentes.py`; runner: `src/encuestas/ejecutar.py`.

## Status and limits
Working prototype (v0.3) tested with synthetic data; not yet validated with data from an institution. It measures aggregate associations, not causation or discrimination, and requires comparable records for each stage (attempt, account, scoring, decision) linked by an identifier. Use it *before* fairness testing of the model, not instead of it. Published as an open proposal for review. Licence: Apache 2.0.
