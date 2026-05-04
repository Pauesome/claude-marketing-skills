# Compliance Reference — EU / Spain

This file supersedes the US-centric `compliance.md` from the upstream
claude-ads package. Audit skills and the `audit-compliance` agent read this
instead. **Do not cite CCPA, CPRA, HIPAA, or US state privacy laws in reports**
— they are out of scope for Spanish clients unless the client explicitly serves
California or US healthcare markets.

---

## Regulatory Framework

### GDPR — Reglamento (UE) 2016/679
- Lawful basis required for all ad tracking. Legitimate interest is narrow for
  marketing; **consent** is the safe default.
- Data Processing Agreement (DPA) required with every ad platform and every
  vendor that receives personal data.
- DPIA required for large-scale behavioural profiling — this includes most
  retargeting and Lookalike/Predictive audiences sourced from customer data.
- Data subject rights: access, rectification, erasure, portability, objection.
  Client's privacy policy must describe how users exercise them.

### LOPDGDD — LO 3/2018
- Spanish implementation of GDPR. **AEPD** (Agencia Española de Protección de
  Datos) is the supervisory authority.
- **Article 9** categorises *datos de salud* (health data), biometric data,
  racial origin, religious belief, political opinion, sexual orientation as
  special category. Healthcare advertisers and pharmacy clients fall here and
  require explicit consent plus AEPD-compliant sensitive-data handling — **not**
  HIPAA-style rules.
- Derecho de supresión and Derecho al olvido must be implementable within 1
  month of request.

### ePrivacy Directive + AEPD Cookie Guidance (Nov 2023)
- Cookie banner must **not** use pre-ticked boxes.
- "Reject all" button must have the **same visual prominence** as "Accept all"
  (size, colour contrast, position). Violations are a direct AEPD finding.
- Banner must **not** block the primary CTA or push critical content below the
  fold. Flag this in `landing-page-audit`.
- Continuing to scroll / navigate is **not** valid consent under the 2023 guide.
- Refreshing consent every 24 months is acceptable; earlier if material changes.
- Essential cookies (session, security, load-balancing) do **not** need consent;
  analytics, ad-tracking, personalisation, and retargeting all do.

### Consent Mode v2
- Required for EEA / UK traffic since March 2024 to serve Google Ads
  personalisation and remarketing.
- Since **21 July 2025** (enforcement date used by upstream claude-ads),
  advanced Consent Mode v2 is mandatory for behavioural modelling — without it
  conversion modelling degrades and remarketing audiences shrink sharply.
- Microsoft Consent Mode deadline: **5 May 2025** for EEA / UK / Switzerland.
- Consent signals must be passed with every pixel / CAPI event.

### Meta EU User Consent Policy
- Meta requires a **registered CMP integration** (Cookiebot, OneTrust, Didomi,
  Funnel, Iubenda, Termly) for any EU-served campaign.
- Without CMP integration Meta may throttle or disable delivery.
- CAPI must propagate consent state on every event.

### DSA — Reglamento (UE) 2022/2065
- Transparency on targeted advertising required. Ad Repositories on platforms
  (Meta Ad Library, Google Ads Transparency Center, LinkedIn Ad Library,
  TikTok Creative Center) are the reference.
- Prohibits targeting minors with profiling-based ads. Meta / TikTok enforce
  at platform level; confirm client campaigns comply.
- Prohibits targeting based on special-category personal data (Art. 26.3).

---

## Special Ad Categories (EU)

Apply when the client advertises:

| Category | Platforms enforcing | Restrictions |
|---|---|---|
| Housing (alquiler / compraventa de vivienda) | Meta, Google | No ZIP / postal code targeting, limited age/gender/audience segments, no Lookalike / Predictive |
| Employment (ofertas de trabajo) | Meta, Google | Same restrictions as housing |
| Credit (crédito al consumo, tarjetas) | Meta, Google | Same restrictions + mandatory disclosures |
| Financial products (seguros, inversiones, crypto) | Meta (Jan 2025), Google | Category declaration required; restricted targeting |

**Meta** — declare the Special Ad Category before campaign creation; Meta auto-
disables non-compliant targeting. Ad Library publishes these ads.

**Google** — declared at campaign level under "Audiences, keywords and content
→ Restricted data processing / Category". Enforcement varies by country but
EU-targeted campaigns should assume full restrictions apply.

### Spain-specific credit rules

- **Ley 16/2011 de contratos de crédito al consumo** — APR, total cost, and
  lender identity must appear in ads offering credit, both on-platform
  (creative) and on the landing page.
- Audit skill should flag credit campaigns whose creative omits APR or lender.

### Healthcare & pharmaceuticals (Spain)

- Prescription drug advertising to consumers is **prohibited** in Spain
  (Ley 29/2006). Flag campaigns that promote Rx products direct-to-consumer.
- Clínicas / dentistas / estéticos must include colegio profesional / número
  de registro sanitario where applicable.
- Wellness products making medical claims trigger LOPDGDD Art. 9 exposure.

---

## Cookie Consent / Tracking Stack Checklist

The `audit-tracking` agent uses this as the cross-platform privacy gate:

| Platform | Client-side | Server-side | Consent signalling |
|---|---|---|---|
| Google Ads | gtag.js / GTM | Enhanced Conversions + GTM Server-Side | Consent Mode v2 advanced |
| Meta Ads | Pixel | CAPI with EMQ ≥ 8 | CMP integration + event-level consent |
| LinkedIn Ads | Insight Tag | CAPI (launched 2025) | Consent Mode v2 (Microsoft-owned) |
| Google Analytics 4 | gtag.js | Measurement Protocol (optional) | Consent Mode v2 |
| TikTok / Microsoft | N/A in current client base | — | — |

Missing any of: CMP integration, Consent Mode v2 advanced, CAPI / Enhanced
Conversions → **Critical** finding. Client is either out of compliance or
leaking measurement fidelity.

---

## Deprecated Features (Do Not Recommend)

Use this list to flag obsolete configurations that still exist in live accounts:

- **ECPC** (Enhanced CPC) — deprecated March 2025. Migrate to tCPA / tROAS /
  Maximize Conversions.
- **Video Action Campaigns (VAC)** — replaced by Demand Gen by April 2026.
  VAC frequency caps do **not** carry over to Demand Gen — flag reach / frequency
  management after migration.
- **Rule-based attribution models** — sunset on Google. Use DDA (data-driven
  attribution) exclusively.
- **Offline Conversions API (Meta)** — discontinued May 2025. Migrate all
  offline events to CAPI.
- **Lookalike Audiences (LinkedIn)** — replaced by Predictive Audiences
  February 2024.
- **Sponsored Messaging / InMail (LinkedIn)** — discontinued for EU targeting
  since January 2022. **Never** recommend Message or Conversation Ads for
  Spanish clients.
- **Creative Sets (Apple Ads)** — discontinued. Irrelevant for current clients
  but noted for completeness.

---

## Things to Ignore in Upstream Claude-Ads

When porting a skill or agent from the upstream claude-ads repo, **strip** or
**rewrite** these sections:

- All CCPA / CPRA / US state privacy law references
- All HIPAA references — use LOPDGDD Art. 9 instead for health data
- US FTC disclosure rules — Spanish equivalents live in LSSI-CE, RD 1/2007
  (Ley General para la Defensa de Consumidores), and the AEPD guide
- US-specific political ad disclosure rules — replace with DSA + LOREG
  (LO 5/1985) if a political client ever comes in (none currently)
- LegitScript references — irrelevant outside US healthcare
- Dollar-denominated benchmarks — replace with values from `benchmarks-spain.md`

---

## Audit Output Conventions

When writing a compliance finding:

1. Cite the **specific regulation** (`GDPR Art. 6`, `LOPDGDD Art. 9`, `AEPD
   Guía cookies Nov 2023`, `DSA Art. 26.3`, `Ley 16/2011 Art. 5`, etc.).
2. State the **observed evidence** (e.g. "Cookie banner lacks reject-all
   button of equal prominence").
3. State the **remediation** (e.g. "Reconfigure CMP to render reject-all with
   same pixel height and contrast as accept-all").
4. Assign severity: **Critical** if legal / regulatory exposure, **High** if
   platform-policy exposure (risk of ad account suspension), **Medium** for
   data-quality degradation.
