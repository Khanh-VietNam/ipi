# S01 — Five-line deep-reading notes (draft for student review)

**Status:** The student confirmed having read the assigned literature thoroughly in chat on 23 November 2026. The `FULL_PAPER` values in `lit_table_v0.csv` are therefore **student self-reports**, not independent proof that the entire paper was read. The following notes were **drafted by ChatGPT using the cited papers**, and should be read, checked, personalized and corrected by the student before presenting them as their own analysis.

**Advisor's assignment:** Read L1, L5, L7, L13, L14, L15 (★★★) and L24 (★★); supply five-line deep notes for **L5, L13, L14 and L15**. These four entries have exactly five numbered research-note points each. Do not conflate bibliographic verification, self-reported reading, and note authorship.

## L5 — SONIC/TAILS (ASPLOS 2019) — baseline B2

**Paper:** [Intelligence Beyond the Edge: Inference on Intermittent Embedded Systems](https://doi.org/10.1145/3297858.3304011) · [Full author PDF](https://www.cs.cmu.edu/~beckmann/publications/papers/2019.asplos.sonic.pdf). Evidence in paper: Sections 5–9.

1. **Problem:** DNN inference on energy-harvesting MCUs must make forward progress despite frequent brownouts, very limited memory and the overhead of saving execution state.
2. **Method:** SONIC's *loop continuation* resumes loop-heavy layers; *loop-ordered buffering* and *sparse undo-logging* protect correctness. GENESIS optimizes network compression and TAILS accelerates computation using MCU hardware (including DMA/LEA).
3. **Experiments:** The authors evaluate three DNNs on a TI MSP430 with RF energy harvesting and multiple power-system/capacitor configurations; they compare against intermittent execution implemented using Alpaca tiling.
4. **Results:** The paper reports average improvements of **6.9× (SONIC)** and **12.2× (TAILS)** over the Alpaca-based state of the art for their evaluated setup; results depend on network and power configuration.
5. **Critical reading / relevance to S01:** This is baseline **B2** for intermittent inference costs and correct progress. Our proposed PSB/ETCT system should additionally measure the energy/bytes of persistent-state updates and compare *Exit/Persist/Skip* decisions; this last sentence is **our research interpretation**, not a claim made by SONIC's authors.

## L13 — Zygarde (IMWUT 2020) — baseline B4

**Paper:** [Zygarde: Time-Sensitive On-Device Deep Inference and Adaptation on Intermittently-Powered Systems](https://doi.org/10.1145/3411808) · [arXiv](https://arxiv.org/abs/1905.03854). Evidence in paper: Sections 2, 5, 7–9, 11.4–11.5.

1. **Problem:** Unpredictable harvested energy causes DNN tasks to miss soft deadlines, so the system must balance timeliness, energy and inference accuracy.
2. **Method:** Zygarde uses *imprecise computing*: mandatory vs. optional work, an energy predictability factor **η**, and a scheduler that exploits partial DNN execution and confidence/utility estimates.
3. **Experiments:** Evaluation on **TI MSP430FR5994** with **MNIST, ESC-10, CIFAR-100 and Visual Wake Words**, plus six real-world acoustic/visual sensing applications; EDF-style schedulers are used for comparisons.
4. **Results:** The paper reports up to **26%** lower execution time and **9–34%** more jobs scheduled, with accuracy gains under the compared experimental settings. These maxima should not be generalized to all traces or datasets.
5. **Limitations / relevance to S01:** The authors explicitly note that mandatory work is **not guaranteed** to finish before deadline, and that offline estimation of **η** may mismatch deployment conditions (Section 11). Zygarde is a **B4 scheduling baseline**, while S01 additionally studies persistent-state encoding and explicit persist/skip actions.

## L14 — Wu et al., DAC 2020 — baseline B4

**Paper:** [Intermittent Inference with Nonuniformly Compressed Multi-Exit Neural Network for Energy Harvesting Powered Devices](https://doi.org/10.1109/DAC18072.2020.9218526) · [Author arXiv PDF](https://arxiv.org/pdf/2004.11293). Evidence in paper: Sections III–V, especially V-A, V-C and Figs. 4–6.

1. **Problem:** EH-powered MCUs may require several power cycles to finish one DNN inference; always executing to the final exit wastes scarce energy or increases delay.
2. **Method:** Nonuniform per-layer **pruning/quantization** compresses a multi-exit network using a power trace and accuracy–energy objectives; the runtime uses **Q-learning** and output **entropy** to select an exit and decide whether to continue.
3. **Experiments:** The study targets **TI MSP432**, a solar energy trace, a LeNet-based network with **two early-exit branches**, **CIFAR-10**, and **500 simulated event times**; the paper uses an assumed energy/FLOP cost in evaluation.
4. **Results:** The paper reports **3.6×** more *interesting events per millijoule* than **SonicNet** (Fig. 5), under its setup. This is an event/energy metric, **not** a claim of 3.6× higher classification accuracy.
5. **Limitations / relevance to S01:** Its resource and trace assumptions must be matched before reproducing the baseline. The work informs **ETCT and early-exit policy (B4)**, but S01 should separately account for storing/restoring a compressed persistent state and for the *Persist/Skip* choice; this comparison is **our research interpretation**.

## L15 — HarvNet (MobiSys 2023) — baseline B5

**Paper:** [HarvNet: Resource-Optimized Operation of Multi-Exit Deep Neural Networks on Energy Harvesting Devices](https://doi.org/10.1145/3581791.3596845) · [Author-affiliation publication record](https://yonsei.elsevierpure.com/en/publications/harvnet-resource-optimized-operation-of-multi-exit-deep-neural-ne/). **Source limitation:** The accessible primary institutional record contains the official abstract and bibliographic data; we did **not** independently verify all details of the full experimental section.

1. **Problem:** Multi-exit DNNs for energy-harvesting sensors need both a compact architecture and an inference policy that responds to fluctuating energy and storage.
2. **Method:** **HarvNAS** searches for multi-exit network architectures under memory/energy constraints; **HarvSched** learns a progressive inference policy using the harvesting status and stored energy.
3. **Experiments:** The published abstract states that **HarvNAS is implemented in TensorFlow** and **HarvSched is evaluated on an MSP430-based sensor device**. The exact datasets, trace splits, baseline conditions and policy overhead need confirmation from the full text.
4. **Results:** Authors report up to **2.6 percentage points** higher accuracy with up to **70%** memory savings for HarvNAS, and **zero-downtime operation** for HarvSched in their evaluated configuration.
5. **Limitations / relevance to S01:** HarvNet is baseline **B5** for architecture + energy-aware exit scheduling. For a fair PSB/ETCT comparison, we must also evaluate **NVM write/restore cost, state size, and interruption recovery**; this is **our proposed evaluation gap**, not an independently verified limitation stated by HarvNet's authors.

## Other advisor-assigned readings — concise recall notes

- **L1, Chinchilla (B3):** Checkpoint overprovisioning guarantees progress with scarce energy; checkpoints can be disabled when energy is abundant. Different from SONIC's loop-specific continuation. [USENIX](https://www.usenix.org/conference/osdi18/presentation/maeng)
- **L7, Stateful Neural Networks:** Embeds recovery/progress indicators in DNN feature outputs. *Stateful* here does **not** refer to maintaining RNN/LSTM hidden state between sequences. [IEEE TCAD](https://doi.org/10.1109/TCAD.2022.3197513)
- **L24, Early-Exit survey (★★):** Survey context for branch placement, multi-exit training and static/dynamic exit selection. Use it to justify the experimental taxonomy; it is not a hardware implementation baseline. [ACM CSUR](https://doi.org/10.1145/3698767)

## Checklist before submitting to advisor

- Make sure `reading_status = FULL_PAPER` is accurate for **all seven** assigned papers; it currently follows the student's broad statement in chat that the assigned reading was completed.
- Verify all four note sets against the papers and revise the **research interpretation** sentences so they reflect the student's own understanding.
- In particular, review the full **L15 Experiment/Evaluation** section and fill in dataset, energy-source assumptions and baseline conditions if the paper provides them; don't invent these from the abstract.
- Copy each five-line block above into the GitHub notes file and, after the personal review, update `deep_notes_status` from `FIVE_LINE_DRAFT_READY_FOR_STUDENT_REVIEW` to `STUDENT_REVIEWED`.
- Only after these checks should the related reading and notes tasks be marked complete in Issue #1.
