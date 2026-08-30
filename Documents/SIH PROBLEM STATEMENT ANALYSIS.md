# 🛢️ PS Deep-Dive: Satellite-Based Oil Spill Detection + Drift Hindcasting + AIS Vessel Attribution

> **Original short PS:** *"Leveraging satellite imagery to determine Oil spills at sea along with AIS data correlations to identify vessel responsible for the spill."*
>
> **Official SIH portal description (fuller scope):** Detect and characterize oil spills (geometric properties + **age**) from SAR/EO imagery → use oceanographic/meteorological data to **hindcast** the slick back to its origin point/time and **forecast** its future drift → attribute the spill to a vessel by reconstructing AIS traffic around the origin window, filtering irrelevant traffic, and scoring suspects on proximity, trajectory, and behavioral anomalies → deliver it through a visual interface.

> ⚠️ **This revision updates the whole analysis below.** The official PS is a **three-model pipeline**, not a two-stage one: (1) detection + age estimation, (2) physics-based drift hindcast/forecast, (3) AIS attribution scoring. This is meaningfully harder — and meaningfully more differentiated from Cerulean — than the short version implied. Read the ⭐ **UPDATE** callouts throughout for what changed.

---

## 1. Pain Points & Core Understanding 🔎

**Exact problem being addressed:**
- ⭐ **UPDATE — three linked sub-problems, not two:**
  1. **Detect & characterize** — segment the slick from SAR/EO imagery, compute geometric properties (area, length, shape/orientation) and, if feasible, **estimate its age** (how long it's been on the water).
  2. **Hindcast & forecast drift** — using ocean current + wind/meteorological data, run the slick's motion **backward in time** to estimate its origin point and time, and **forward in time** to predict where it will drift next.
  3. **Attribute to a vessel** — reconstruct AIS vessel traffic around that origin window (space + time), filter out irrelevant traffic, and rank suspect vessels by proximity, trajectory alignment, and behavioral anomalies.
- This is a **"detect → reverse-engineer physics → join with tracking data"** problem: it combines computer vision, oceanographic transport modeling, and spatio-temporal data fusion — a genuinely multi-disciplinary ask, not just an image classifier.

**Root causes:**
- 🌊 The open ocean is **unmonitored** — no CCTV, no traffic police. Illegal discharge (bilge dumping, tank cleaning) happens precisely because detection probability is near-zero.
- 📡 AIS is **self-reported and spoofable** — vessels can legally (or illegally) turn off transponders ("going dark"), report false MMSI/position, or simply not be required to carry AIS (small/local vessels).
- ⏱️ Oil slicks are **short-lived** (spread, evaporate, or disperse in 2–12 hours depending on oil type), so there's a race against time between satellite revisit rate and evidence decay.
- 🛰️ Good detection sensors (SAR) have **revisit gaps** — Sentinel-1 typically revisits the same spot only every 6–12 days in many regions.

**Primary stakeholders:**
| Stakeholder | Interest |
|---|---|
| Coast Guard / Navy (e.g., Indian Coast Guard) | Enforcement, legal action against polluters |
| Ministry of Environment / Pollution Control Boards | Regulatory compliance, penalties |
| Port & Shipping authorities, DG Shipping | Vessel accountability |
| Fishing communities & coastal population | Livelihood, health impact |
| Marine insurers | Liability assessment |
| Environmental NGOs (e.g., SkyTruth, Oceana) | Public accountability, advocacy |
| Tanker/shipping companies (legitimate) | Reputation, insurance, false-accusation risk |

**Current challenges/inefficiencies:**
- Attribution today is often **manual and forensic** — SAR image + AIS overlay is eyeballed by an analyst, then followed up with boarding inspections and physical evidence (tampering tools, log records) because satellite + AIS alone isn't legally conclusive.
- Vessels that turn AIS off near the time of dumping ("dark vessels") **cannot be attributed** by AIS correlation alone — this is the single hardest edge case in the entire problem space.
- False positives are common: <cite>look-alikes</cite> such as calm-sea wind shadows, algal blooms, and natural biogenic slicks mimic oil on SAR.

---

## 2. Feasibility of Execution ⚙️

**Can a prototype be built in a hackathon?**
✅ Yes — a **credible demo-level MVP** is realistic in 24–48 hours *if scoped correctly* (see MVP below). A production-grade, false-positive-hardened system is **not** feasible in hackathon time — and evaluators know this, so don't overpromise.

**Technical requirements:**

| Component | What you need |
|---|---|
| Satellite imagery | Sentinel-1 SAR (free, via Copernicus Open Access Hub / Alaska Satellite Facility / Google Earth Engine) |
| Oil spill detection model | Pre-trained/fine-tuned segmentation model (U-Net / DeepLabv3+ on SAR) |
| Labeled training data | Kaggle "Oil Spill Detection" dataset, EMSA CleanSeaNet-style annotated sets, or SkyTruth's open Cerulean data |
| ⭐ Age estimation | No mature open dataset/model exists for this — see feasibility note below |
| ⭐ Ocean current & wind data (for drift model) | Free reanalysis data: Copernicus Marine Service (CMEMS) for currents, ECMWF ERA5 for wind |
| ⭐ Drift/transport model | **Don't build from scratch.** Use an existing open-source Lagrangian trajectory model as a library: **NOAA's GNOME** (open-source, Python-integrable, purpose-built for exactly this) or **OpenDrift** (open-source, Norwegian Meteorological Institute, actively maintained, pip-installable) — both simulate oil "particles" drifting under current+wind forcing, forward *and* backward in time |
| AIS data | Global Fishing Watch API, MarineTraffic API (limited free tier), or simulated/dummy AIS tracks for demo |
| Correlation logic | Geospatial + temporal proximity scoring (distance from slick centerline, time-window overlap, trajectory heading vs. slick orientation, AIS-gap anomaly detection) |
| Backend/GIS | Python (GDAL, rasterio, GeoPandas, Shapely), PostGIS |
| Frontend | Leaflet/Mapbox map with slick polygon, backward/forward drift path, and AIS tracks overlaid on one timeline-scrubbable view |

**Likely blockers:**
- 🚫 Real-time AIS APIs are mostly **paid** (MarineTraffic, Spire, Windward) — free tiers are rate-limited or delayed.
- 🚫 Sentinel-1 raw scenes are **large (GBs)** and need pre-processing (calibration, speckle filtering) — compute-heavy for a laptop in a hackathon.
- 🚫 Truly live imagery isn't available on-demand for an arbitrary location — you're working with historical/archived scenes, not "point camera at ocean now."
- 🚫 Ground-truth labels for spill vs. look-alike are scarce and imbalanced.
- ⭐ 🚫 **Age estimation has no standard, off-the-shelf method.** Published research ties spreading/thinning rate to elapsed time, but it's oil-type- and weather-dependent — treat this as a "best-effort heuristic with a stated confidence interval," not a solved sub-problem. Being upfront about this in your pitch is safer than pretending it's precise.
- ⭐ 🚫 **Hindcast/forecast accuracy degrades fast** — real published drift models (MEDSLIK-II, GNOME) show trajectory error growing significantly over even 24–48 hrs due to wind-drift-factor and current-data uncertainty. Don't promise pinpoint-accurate origin coordinates; show it as a probability cone, matching how actual oil-spill responders present it.

**Realistic MVP to impress evaluators:**
1. Pick 2–3 **real historical spill events** (e.g., 2025 Kerala coast MSC ELSA 3 spill, a Bohai Sea case, a Cerulean-documented slick) with public Sentinel-1 imagery.
2. Run a pre-trained/fine-tuned segmentation model to draw the slick polygon, and compute basic geometric properties (area, length, elongation) — treat age as a rough heuristic, clearly labeled as low-confidence.
3. Feed the slick polygon + timestamp into **GNOME or OpenDrift** with CMEMS current data / ERA5 wind data to backward-hindcast an origin cone and forward-forecast a future drift cone — this is the step most teams will skip, so doing even a basic version is a strong differentiator.
4. Overlay historical AIS tracks for that origin time/place window and compute a **proximity + trajectory-alignment + AIS-gap anomaly score** per nearby vessel, ranking "most likely responsible vessel."
5. Wrap it all in a clean, timeline-scrubbable map dashboard with **confidence scores at every stage** (detection, age, origin, attribution) — not false certainty. This alone shows more maturity than 90% of teams.

---

## 3. Impact & Relevance 🌍

**Who benefits:** Coast guards & maritime enforcement agencies, environment ministries, coastal fishing communities, marine insurers, shipping regulators, and NGOs doing pollution accountability work.

**Real-world impact:**
- 🌱 **Environmental:** Marine ecosystems, birds, turtles, and fisheries are directly protected by faster detection and deterrence of illegal dumping.
- 💰 **Economic:** Fisheries and tourism losses from spills are reduced; insurers get better liability data.
- ⚖️ **Social/Legal:** Enables actual enforcement — currently the biggest gap globally is not detection but **legally attributable evidence**, which is exactly what this PS targets.

**Scalability beyond hackathon:**
- Directly extensible to a **national coastal surveillance layer** — India already has ISRO's EOS-4 SAR satellite and INCOIS's Oil Spill Advisory System, so there's a natural integration path with the Indian Coast Guard.
- Enterprise version could be licensed to port authorities, shipping insurers, or offered as a SaaS analytics layer on top of Global Fishing Watch–style AIS data.

**Why evaluators find it important:** It sits at the intersection of **space tech, environment, and maritime law enforcement** — high visibility for SIH-style national missions (aligns with Ministry of Earth Sciences / Ministry of Defence / Ministry of Environment problem tracks), with real institutional precedent (China's Bohai Sea program, EU's EMSA CleanSeaNet, India's own EOS-4 usage).

---

## 4. Scope of Innovation (Existing Solutions) 💡

### 🏆 Competitor / Prior-Art Landscape

| Solution | What it does | Limitation |
|---|---|---|
| **SkyTruth Cerulean** (skytruth.org/cerulean) | Free, global, near-real-time ML pipeline detecting oil slicks from Sentinel-1 using a ResNet34 U-Net, then auto-correlates with AIS via parity/proximity/temporality scoring | AIS-vessel attribution data lags by up to 72 hours, so real-time attribution isn't possible yet; only covers ~85% of offshore oil/gas activity and ~half of shipping lanes |
| **EMSA CleanSeaNet** (Europe) | Operational since 2007; satellite alerts to EU member states with rapid image delivery | Region-locked to European waters; not open-source/public |
| **ICEYE** (commercial SAR) | On-demand tasking of SAR + AIS fusion for spill response (e.g., Turku Archipelago case) | Paid/commercial, enterprise-only |
| **Global Fishing Watch** | Open AIS-based vessel activity & infrastructure mapping; used as a data source *by* Cerulean | Not itself an oil-spill detector — a data layer, not a full solution |
| **PierSight Space** (Indian startup) | Won the US-India INDUS-X DIU-IDEX Maritime Challenge for multi-sensor oil spill detection; building own SAR smallsats via ISRO's POEM platform | Still pre-operational/early-stage; hardware-heavy, not a hackathon-replicable approach |
| **INCOIS Oil Spill Advisory System** (India) | Predicts spill *trajectory forward* after an incident is manually reported (uses ocean circulation + atmospheric models) | Doesn't do initial *detection*, doesn't hindcast to origin, and has no *vessel attribution* — reactive, forward-only, not proactive |
| **ISRO EOS-4** | Indigenous C-band SAR satellite, used operationally to detect the 2025 Kerala coast spill | Detection only; no drift modeling or AIS-correlation/attribution layer built around it publicly |
| ⭐ **NOAA GNOME / OpenDrift / MEDSLIK-II** (drift models) | Mature, published, open-source (GNOME, OpenDrift) Lagrangian trajectory models that simulate oil movement forward *and* backward under current+wind forcing — the actual physics engines real responders use | These are **drift-modeling tools only** — none of them do satellite-based detection or AIS attribution. Nobody has wired one of these end-to-end into a detect→hindcast→attribute pipeline in a public, integrated tool. |

**The single biggest whitespace:** Two gaps, actually:
1. Almost nobody has solved the **"dark vessel" problem** (AIS deliberately switched off) well — Cerulean itself explicitly cannot attribute in real-time due to AIS data lag.
2. ⭐ **No public tool integrates detection + physics-based drift hindcasting + AIS attribution into one pipeline.** Cerulean does detection+AIS but *no drift modeling at all*. INCOIS does forward drift forecasting but *no detection or attribution*. GNOME/OpenDrift do drift physics but *nothing else*. **The official SIH PS is explicitly asking you to be the team that connects all three** — that integration itself is your innovation, even using existing open-source building blocks for each piece.

**Where you can genuinely innovate:**
- 🤖 **AI/ML:** Add a *behavioral anomaly* layer on AIS (sudden AIS gaps near a slick's time/space window = suspicious "dark period," using an Isolation Forest/anomaly model — this exact idea already appears in early academic work, so it's validated but not mainstream yet).
- 🔗 **Fusion confidence scoring:** Instead of binary "yes/no" attribution, output a ranked list of candidate vessels with an explainable confidence score (parity, proximity, temporality, dark-gap suspicion) — more legally defensible than a black-box guess.
- 🖥️ **UX differentiation:** A clean, explainable "evidence dossier" export (map + timeline + AIS gap chart) that could plausibly be used as a preliminary investigation aid — most existing tools are analyst dashboards, not investigation-report generators.
- 🌊 **India-specific angle:** Tie into INCOIS's spill-trajectory forecasting + ISRO EOS-4 imagery to make it a distinctly Indian-context solution rather than a Cerulean clone — strong SIH differentiation.

---

## 5. Clarity of Problem Statement 🧩

**What's explicitly asked (deliverables):**
1. A system that determines oil spills at sea **from satellite imagery**.
2. A correlation with **AIS data** to identify the **responsible vessel**.

**Where teams commonly misinterpret this:**
- ❌ Building *only* a spill-detection image classifier and treating AIS correlation as an afterthought/dummy overlay — the PS title puts equal weight on both halves.
- ❌ Assuming live/real-time satellite feed is available on-demand — it isn't; framing your solution around historical/near-real-time archived imagery is more honest and technically correct.
- ❌ Presenting attribution as a **certainty** ("this vessel did it") rather than a **confidence-scored candidate list** — real systems (including Cerulean) explicitly avoid legal certainty claims, and judges with domain knowledge will penalize overconfidence.
- ❌ Ignoring the "AIS switched off" edge case entirely — it's the crux of the real-world problem, and addressing it (even partially) shows depth.

**How to frame for evaluator clarity:**
Present it as a **two-stage pipeline with an explicit uncertainty layer**: (1) SAR-based slick segmentation with a confidence map, (2) spatio-temporal AIS correlation producing a ranked, explainable vessel-attribution score — explicitly flagging cases where no AIS match exists (potential "dark vessel" alert) as a distinct, valuable output rather than a failure state.

---

## 6. Evaluator's Perspective 🎯

**How this PS gets judged:**
- **Uniqueness** — will be judged relative to Cerulean/EMSA, since informed judges likely know these exist. You *must* show you know the landscape and articulate a real delta.
- **Feasibility** — can you demo on real data, not just synthetic toy data?
- **Sustainability** — is there a real data/business pathway post-hackathon (government partnership, open API)?
- **Impact** — environmental + enforcement narrative is inherently strong; don't waste it with a weak demo.
- **Product completeness** — does the "attribution" half actually work, or is it hand-waved?

**Red flags evaluators will notice immediately:**
- 🚩 Treating AIS correlation as a simple "nearest vessel" lookup with no time-windowing or trajectory logic.
- 🚩 No handling of false positives / look-alikes (claiming every dark patch is oil).
- 🚩 No acknowledgment of the AIS-spoofing/dark-vessel limitation.
- 🚩 Claiming "real-time" detection when SAR revisit cycles make that structurally impossible without owning tasking satellites.

---

## 7. Strategy for Team Fit & Execution 👥

**Skill sets needed:**
- 🧠 ML/Computer Vision (SAR image segmentation) — 2 people
- 🗺️ Geospatial/Backend (GIS, PostGIS, AIS data pipelines, trajectory math) — 1–2 people
- 🎨 Frontend/Dashboard (map visualization, UX) — 1 person
- 🎤 Research + storytelling/pitch — 1 person (can double up with above)

**Ideal team ratio (6 members):** 2 ML/CV, 2 Backend/Geospatial, 1 Frontend, 1 Research+Design/Pitch (flexible overlap is fine in a hackathon).

**Step-by-step approach before building:**
1. **Research (2–3 hrs):** Read Cerulean's public methodology page, the EMSA/Bohai Sea papers, and ISRO EOS-4 Kerala spill case — know exactly what exists.
2. **Pick your data sources & lock scope** — decide which 2–3 real historical spill events you'll demo against; don't try to be "global real-time."
3. **Define your attribution scoring formula** on paper *before* coding (proximity, temporality, trajectory-parity, dark-gap suspicion).
4. **Parallel-build:** ML team fine-tunes/adapts a segmentation model while geospatial team builds the AIS correlation + scoring pipeline.
5. **Integrate early** — connect a barebones end-to-end pipeline by the halfway mark, then polish.
6. **Build the "evidence dossier" UI last** — it's your differentiator and demo centerpiece.

---

## 8. AI-Buildability Split (20/80) 🤖

**The 20% AI can build fast:**
- Boilerplate: map UI, REST API scaffolding, data-loading scripts, a pre-trained segmentation model wired up to sample SAR images, basic distance/time filtering of AIS points.
- ⭐ **Wiring up GNOME/OpenDrift as a library call** — feeding it a start point/time and current+wind data files and getting particle-trajectory output back is genuinely fast to scaffold; it's a well-documented API, not something you're building from physics equations.

**The 80% requiring real judgment:**
- Tuning the segmentation model to actually distinguish oil from look-alikes (wind shadows, algal blooms) — this needs domain understanding of SAR backscatter physics, not just "call an API."
- ⭐ **Correctly configuring the drift model's physical parameters** (wind drift factor/angle, diffusion coefficient, Stokes drift inclusion) — published research shows these parameters materially change trajectory accuracy, and picking sane defaults vs. nonsense ones is a judgment call, not something an LLM can reliably infer without oceanography grounding.
- ⭐ **Communicating drift/origin uncertainty honestly** (as a probability cone, not a pinpoint) — a team that outputs a single confident "origin was exactly here" coordinate is scientifically wrong and will be caught by any judge who's seen real spill-response trajectory outputs.
- Designing a **defensible, explainable** attribution scoring methodology (weights for proximity vs. temporality vs. trajectory parity vs. behavioral anomaly) — this is a judgment call with legal/ethical weight (false accusation risk), not something you can blindly prompt an LLM to invent.
- Handling missing/dark-vessel AIS gracefully instead of either ignoring it or crashing.
- Correctly interpreting SAR imagery formats (GRD vs SLC, polarization bands) and coordinate reference systems — subtle geospatial bugs (e.g., silently misaligned projections) are easy to introduce and hard to notice in a demo.

**Risk of leaning only on AI output:** A team that vibe-codes this without understanding SAR physics or AIS semantics will very likely produce a system that "looks right" on a cherry-picked demo image but is either (a) trivially wrong on real data (mistaking a wind shadow for oil), or (b) unable to explain *why* it flagged a given vessel when a judge asks — which is fatal for a PS this explainability-sensitive.

**Structural change a judge could ask for live, and can you deliver it:**
> *"Show me what your system outputs when the responsible vessel had its AIS switched off."*
- If your pipeline only handles the happy path (AIS present), you cannot answer this live. **Build the "no AIS match found → flag as dark-vessel event" branch explicitly** — it's cheap to add and directly answers the hardest real question in this domain.

---

## 9. Data & Resource Availability 📊

| Data need | Availability |
|---|---|
| SAR imagery | ✅ Free & real: Sentinel-1 via Copernicus Open Access Hub, Alaska Satellite Facility, or Google Earth Engine. ISRO EOS-4 data is more restricted. |
| Labeled oil-spill training data | ✅ Kaggle's oil-spill segmentation dataset (public); ⚠️ EMSA CleanSeaNet's expert-annotated set is not freely public but referenced in papers |
| AIS data | ⚠️ Historical AIS: partially free (Global Fishing Watch API has a public tier); real-time/high-density AIS is mostly paid (MarineTraffic, Spire, Windward) |
| Vessel/infrastructure metadata | ✅ Global Fishing Watch's public infrastructure & vessel datasets |
| ⭐ Ocean currents (for drift model) | ✅ Free: Copernicus Marine Service (CMEMS) global/regional reanalysis + forecast products |
| ⭐ Wind data (for drift model) | ✅ Free: ECMWF ERA5 reanalysis |
| ⭐ Drift model software | ✅ Free & open-source: NOAA GNOME, OpenDrift (pip-installable) |

**If ideal data isn't available in time:**
- Fall back to **documented historical incidents** (Turku Archipelago 2019, Java Sea bilge case, Kerala MSC ELSA 3 2025) where both SAR imagery and AIS tracks are already publicly referenced in case studies/papers — you can reconstruct a realistic dataset without needing live paid APIs.

**Realistic backup/synthetic plan:**
- Generate **synthetic AIS tracks** (simple vessel-trajectory simulator: speed, heading, waypoints) around a real or synthetic slick polygon, clearly labeled in your demo as "simulated for demonstration" — judges respect transparency about synthetic data far more than a team that pretends fabricated data is real.

---

## 10. Judge Q&A Stress-Test 🎤

**Q1: "Cerulean already does exactly this and is free/public. Why should anyone use yours?"**
> **Answer:** "Cerulean's own documentation states vessel-identity AIS data lags by up to 72 hours, making real-time attribution impossible today, and their coverage misses dark-AIS vessels entirely. Our system adds an explicit 'dark-vessel suspicion' layer and is designed around India's own EOS-4/INCOIS infrastructure for sovereign, enforcement-ready deployment rather than a global research tool."
> *Likely follow-up:* "How would you actually get INCOIS/Coast Guard integration?" → Have a one-line answer: e.g., "as a pilot API layer consuming their existing Oil Spill Advisory outputs."

**Q2: "What happens when the responsible vessel turns off its AIS — doesn't your whole system fail?"**
> **Answer:** "That's the hardest real case in this domain — even EMSA and Cerulean can't solve it with AIS alone. Our system doesn't claim false certainty; it flags an 'AIS gap during slick window' as a high-priority investigation alert, which is itself actionable intelligence for enforcement, even without a name."
> *Likely follow-up:* "Isn't a gap alert just as good as doing nothing?" → "No — it narrows the search from 'entire ocean' to 'ships that were nearby right before going dark,' which is exactly the forensic lead investigators currently reconstruct manually."

**Q3: "How do you avoid false positives — wind shadows, algae, calm seas all look like oil in SAR?"**
> **Answer:** "We're aware this is the primary failure mode of naive SAR spill detection. We [mitigate via X — e.g., shape heuristics: real slick-from-vessel signatures are long linear streaks with a bright vessel at one tip, not amorphous blobs] and output a confidence score, not a binary flag."
> *Likely follow-up:* "Show me a false positive your model produced." → Be ready to actually show one — hiding failure cases looks worse than owning them.

**Q4: "Is this actually real-time, given satellite revisit times of 6–12 days?"**
> **Answer:** "No, and we don't claim that — we call it 'near-real-time within revisit constraints,' which is the same honest framing SkyTruth uses. For true real-time, tasked SAR (like ICEYE's on-demand model) would be needed, which is outside hackathon/API-cost scope."
> *Likely follow-up:* "So what's your actual latency end-to-end?" → Have a real number ready (e.g., "6–12 hrs from image availability + minutes of processing," per Cerulean's published pipeline benchmarks).

**Q5: "What's the weakest part of your idea?"**
> **The honest weak point:** attribution confidence when multiple vessels are near the slick simultaneously — the scoring can become ambiguous, and no public system has fully solved multi-candidate disambiguation. Naming this yourself, with a stated mitigation ("we surface top-3 ranked candidates with scores rather than a single answer"), is far stronger than being caught off-guard.

---

## ✅ Key Takeaways

- 🎯 **This PS has real prior art (Cerulean, EMSA, ICEYE, PierSight) — know it cold, and position your delta explicitly**, especially around the India-context integration (ISRO EOS-4 + INCOIS) and the dark-vessel/AIS-gap problem.
- ⚠️ **Never claim certainty in attribution** — confidence-scored, ranked, explainable outputs are both more technically honest and more evaluator-proof.
- 🧩 **Build the "no AIS match" branch** — it's the single question most likely to expose a shallow implementation.
- 📊 **Use real historical incidents + Sentinel-1/Kaggle data**, with clearly labeled synthetic AIS as backup — don't fabricate "real-time" claims.

---

## 🚦 Final Verdict (Updated): 🟢 GREEN LIGHT — *with a scope-discipline caveat*

**Biggest reason:** ⭐ The official PS description changes the calculus. It doesn't just ask you to rebuild Cerulean — it asks for detection **+ age estimation + physics-based hindcast/forecast drift modeling + AIS attribution**, and **no single public tool does all of this together** (Cerulean skips drift modeling entirely; INCOIS skips detection and attribution; GNOME/OpenDrift are physics-only with no satellite or AIS layer). That integration gap is real, well-resourced with free data and mature open-source building blocks (Sentinel-1, CMEMS, ERA5, GNOME/OpenDrift, Global Fishing Watch), and has strong India-specific hooks (ISRO EOS-4, INCOIS) for a compelling SIH narrative.

**The one real risk now is scope, not originality:** this is three hard sub-problems stitched together, and a team that tries to build all three from scratch in a hackathon will likely ship something shallow in all of them. **Win condition:** lean hard on existing open-source tools for the physics (GNOME/OpenDrift) and detection (a fine-tuned segmentation model, not a from-scratch architecture) so your team's actual engineering effort goes into the **integration layer and the attribution-scoring logic** — that's both the hardest-to-fake part and the part with the clearest unclaimed whitespace.

---

### 📚 Sources & Further Reading
- SkyTruth Cerulean — https://skytruth.org/cerulean and methods page https://skytruth.org/cerulean/methods
- Bellingcat, "An Open Source Guide to Marine Oil Spill Detection" (2024)
- EMSA CleanSeaNet overview — PMC review, "Oil Spill Detection by SAR Images"
- "Tracing illegal oil discharges from vessels using SAR and AIS in Bohai Sea of China" — ScienceDirect
- "Automated oil spill detection using deep learning and SAR satellite data for the Suez Canal" — Nature Scientific Reports
- ICEYE blog, "Timely SAR Data Speeds Up Marine Oil Spill Response"
- IIRS/ISRO Sudoor Manthan — "EOS-4 Detects Oil Spill near Kerala Coast" (May 2025)
- INCOIS Annual Report 2023–24 (Oil Spill Advisory System)
- PierSight Space — INDUS-X DIU-IDEX Maritime Challenge win announcement
- NOAA GNOME — response.restoration.noaa.gov (open-source oil trajectory model)
- OpenDrift — open-source trajectory framework (Dagestad et al., Geosci. Model Dev., 2018)
- MEDSLIK-II Lagrangian oil spill model (De Dominicis et al.) — theory & Brazil/Baltic case-study papers on wind-drift-factor sensitivity
