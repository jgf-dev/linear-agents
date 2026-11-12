# Evaluation-Model Requirements Specification

| Metadata | Specification |
| :--- | :--- |
| **Issue ID** | AIX-117 |
| **Parent Issue** | AIX-116 (*Choose the evaluation model*) |
| **Project** | Bittensor subtensor |
| **Milestone** | Designing an incentive mechanism |
| **Team** | `agent-automation` |
| **Status** | Approved Specification |
| **Author** | Antigravity AI Agent (`agy@antigravity.com`) |

---

## 1. Executive Summary & Problem Context

The core challenge in engineering a decentralized Bittensor subnet is aligning miner rewards with verifiable work through **Yuma Consensus**. Subnet emissions are distributed based on validator weight vectors submitted on-chain every subnet epoch (`tempo`). However, the fundamental nature of the subnet's workload governs every architectural layer:

1. **The Synapse Protocol** (data payload structures, transport mechanisms, serialization overhead).
2. **The Validator Verification Engine** (algorithmic validation vs. statistical scoring distributions).
3. **The Anti-Collusion and Game-Theoretic Safeguards** (resistance to weight-copying, cabal formation, pre-computed replay attacks, and Sybil swarms).

Parent issue **AIX-116** tasks the engineering team with selecting between two foundational paradigms:
* **Open-Ended Compute**: Continuous scoring of generative, subjective, or latent AI workloads (e.g., text generation, latent embeddings, multi-agent reasoning, diffusion modeling).
* **Deterministic Work**: Algorithmic, objectively verifiable evaluation of discrete tasks (e.g., zero-knowledge proofs, cryptographic hashing, verifiable storage challenges, deterministic WASM execution).

This document fulfills **AIX-117** by formally establishing the **task characteristics**, **success criteria**, and **empirical evidence requirements** required to make an objective, defensible architectural choice in **AIX-118**, while establishing protocol constraints for **AIX-119**, **AIX-120**, and **AIX-121**.

```
                           +-------------------------------------------------------+
                           | AIX-116: Choose the Evaluation Model                 |
                           +-------------------------------------------------------+
                                                      |
                                                      v
                           +-------------------------------------------------------+
                           | AIX-117: Define Evaluation-Model Requirements (HERE) |
                           |   - Task Characteristics & Taxonomy                   |
                           |   - Success Criteria & Consensus Framework            |
                           |   - Required Evidence Matrix                          |
                           +-------------------------------------------------------+
                                                      |
                                                      v
                           +-------------------------------------------------------+
                           | AIX-118: Compare Models & Record Choice               |
                           +-------------------------------------------------------+
                                   |                      |                     |
                                   v                      v                     v
                 +-----------------------+ +---------------------+ +----------------------+
                 | AIX-119: Protocol     | | AIX-120: Validator  | | AIX-121: Anti-       |
                 | Design Implications   | | Logic Specification | | Collusion Strategy   |
                 +-----------------------+ +---------------------+ +----------------------+
```

---

## 2. Task Characteristics: Open-Ended Compute vs. Deterministic Work

A subnet's workload exhibits intrinsic physical, mathematical, and algorithmic properties. The table below delineates the taxonomic boundary between open-ended compute and deterministic work across key system dimensions.

| Dimension | Open-Ended Compute | Deterministic Work |
| :--- | :--- | :--- |
| **Primary Workload Archetype** | LLM inference, embedding generation, synthetic data synthesis, image/audio generation, agent trajectory planning. | Zero-knowledge proof generation (zk-SNARK/STARK), proof-of-retrievability (PoR/PoS), cryptographic hash inversion, deterministic WASM bytecode execution. |
| **Determinism & Reproducibility** | **Probabilistic / Non-deterministic**. Identical inputs yield divergent outputs across different seeds, temperatures, hardware architectures, and numerical runtimes. | **Strictly Deterministic**. Identical inputs guaranteed to yield identical bit-exact outputs or verifiable mathematical invariants regardless of executor. |
| **Output Space & Dimensionality** | **High-dimensional continuous space**. Outputs are natural language tokens, vector embeddings ($\mathbb{R}^d$), tensor weights, or media matrices. | **Discrete, bounded scalar or proof struct**. Outputs are cryptographic proofs ($\pi \in \mathbb{G}$), Merkle roots ($H \in \{0,1\}^{256}$), or strict execution trace receipts. |
| **Hardware Heterogeneity Sensitivity** | **High sensitivity**. Non-deterministic floating-point accumulation order, tensor cores, CUDA/ROCm versions, driver levels, and quantization (FP16, BF16, INT8, FP4) cause numerical drift. | **Zero sensitivity**. Bytecode execution environments (WASM, eBPF) and algebraic proof verifiers enforce universal arithmetic invariants independent of physical silicon. |
| **Compute Asymmetry (Work vs. Verify)** | **Symmetric ($O(N) \approx O(N)$)**. Validating an LLM inference or generative output generally requires re-running inference on an equivalent validator model or utilizing a larger LLM-as-a-judge. | **Highly Asymmetric ($O(N) \gg O(1)$ or $O(\log N)$)**. Generating a cryptographic proof or computing storage permutations requires substantial miner compute; verification requires milliseconds on CPU. |
| **Statefulness & Locality** | **Primarily Stateless**. Inquiries are self-contained prompt-response cycles, though multi-turn memory buffers may exist. | **Stateful or Proof-of-State**. Requires holding persistent committed data stores (e.g., storage subnets) or maintaining global ledger state machine transitions. |
| **Ground Truth Availability** | **No absolute ground truth**. Quality is relative, graded against subjective rubrics, reference model perplexity, human preference distributions, or synthetic ground-truth proxies. | **Absolute ground truth**. Output is either mathematically valid ($\text{Verify}(\pi, x) = 1$) or invalid ($\text{Verify}(\pi, x) = 0$). No subjective ambiguity exists. |
| **Latency Tolerance & Duration** | **Interactive / Sub-second to seconds**. Inference queries typically target 200ms – 5s response windows to support real-time application pipelines. | **Batch / Asynchronous (Seconds to minutes)**. Proof synthesis and storage replication challenges can run over multi-block epochs without degrading end-user interaction. |

### 2.1 Deep-Dive: Open-Ended Compute Characteristics

1. **Distributional Equivalence**: In open-ended generative compute, multiple distinct outputs can represent equally optimal solutions. Evaluators cannot apply equality operators (`output == expected`); they must evaluate semantic proximity, factual consistency, structural fidelity, and stylistic quality.
2. **Evaluation Drift**: What constitutes "high quality" is vulnerable to reward-model exploitation, prompt sensitivity, and benchmark memorization. Miners adapt rapidly to static synthetic prompts, demanding continuous dynamic prompt generation by validators.
3. **Symmetric Compute Burden**: Because validators cannot verify generative output in $O(1)$, validator operational costs scale linearly with network query volume unless statistical subsampling or spot-checking is introduced.

### 2.2 Deep-Dive: Deterministic Work Characteristics

1. **Mathematical Verifiability**: Deterministic work delegates computation to miners while equipping validators with lightweight, non-interactive verification algorithms (NP-complete problem structures: hard to find, trivial to verify).
2. **Hardware Agnosticism**: Execution is sandboxed within deterministic virtual machines (e.g., WebAssembly with deterministic floating-point emulation or integer-only computation). Any node on any hardware platform arrives at the identical terminal state.
3. **Definitive Boundaries**: Verification failure indicates either computational error, hardware fault, deliberate cheat attempt, or timeout. Edge-case disputes are resolved without fuzzy confidence intervals.

---

## 3. Success Criteria & Verification Framework

The evaluation model dictates how validators measure performance, how scores translate into on-chain weights, and how Yuma Consensus maintains network security.

```
+---------------------------------------------------------------------------------------------------+
| OPEN-ENDED COMPUTE SCORING PIPELINE                                                               |
| Miner Output -> Validator Metric Pipeline (Loss/Cosine/Elo) -> Outlier Clipping -> Continuous W  |
+---------------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------------+
| DETERMINISTIC WORK VERIFICATION PIPELINE                                                          |
| Miner Output -> Algorithmic Verifier (Verify(pi, x) in {0, 1}) -> Binary Score -> Step Function W |
+---------------------------------------------------------------------------------------------------+
```

### 3.1 Verification Mechanics & Scoring Functions

#### Open-Ended Compute: Continuous Scoring Distribution
* **Scoring Function**: Produces continuous values $S_i \in [0.0, 1.0]$.
  $$S_i = \alpha \cdot \text{Quality}(y_i, y^*) + \beta \cdot \text{Speed}(\tau_i) + \gamma \cdot \text{Efficiency}(\kappa_i)$$
  where $\text{Quality}$ combines cosine similarity, cross-entropy loss relative to ground truth, or LLM-judge win rates; $\tau_i$ represents network round-trip time; and $\kappa_i$ represents resource consumption.
* **Weight Transformation**: Validators apply non-linear scaling (e.g., softmax with temperature or rank-based polynomial power transforms $W_i = S_i^p / \sum S_j^p$) to reward top-tier miners while starving low-performing nodes.
* **Consensus Alignment**: Yuma Consensus requires validator consensus on relative rankings. Outlier clipping algorithms (e.g., median absolute deviation) must neutralize rogue validator score distributions.

#### Deterministic Work: Binary & Cryptographic Verification
* **Scoring Function**: Evaluates to a binary discrete decision with strict latency SLA gating:
  $$S_i = \begin{cases} 
  1.0 & \text{if } \text{Verify}(x, \pi_i) = \text{true} \text{ and } \tau_i \le \tau_{\text{max}} \\ 
  0.0 & \text{otherwise} 
  \end{cases}$$
* **Weight Transformation**: When all honest miners provide valid proofs, weights are allocated according to verifiable capacity, bandwidth benchmarks, stake, or proof generation rate (throughput $\mathcal{T}_i$).
* **Consensus Alignment**: Validator agreement is nearly unanimous ($\approx 100\%$) because verification is deterministic. Validators disagreeing with mathematical truth can be immediately identified as corrupt or out-of-sync.

### 3.2 Protocol Dynamics & Latency Constraints

1. **Subnet Tempo & Epoch Boundaries**:
   * Bittensor commits weights at regular block intervals defined by `tempo` (typically 360 blocks $\approx 72$ minutes on Finney).
   * **Open-Ended**: Requires continuous sampling across the epoch to build statistically stable moving averages (EMA) of miner scores. A single sample is noisy; 50–200 challenge iterations per miner per epoch are necessary.
   * **Deterministic**: Allows scheduled batch challenge rounds or cryptographic spot-checks. Fewer samples are required to achieve statistical confidence that a miner possesses the claimed data or compute capacity.
2. **Immunity Period Alignment**:
   * Newly registered hotkeys are shielded during `immunity_period` (e.g., 4096 blocks).
   * Verification latency must be substantially shorter than the immunity period. If evaluation requires hours of training or multi-step iterative refinement, the immunity period must be extended to prevent premature pruning of capable miners before evaluation stabilizes.
3. **Failure Modes & Edge Conditions**:
   * **Timeout Handling**: Both models must penalize dropped synapses ($S_i = 0$), but deterministic models must differentiate between transport packet loss and proof generation exhaustion.
   * **Sybil Flooding**: Open-ended models suffer from Sybil miners serving cloned or slightly mutated LLM responses; deterministic models resist this via non-transferable cryptographic proofs tied to unique miner hotkeys.

---

## 4. Evidence Needed for Model Choice

To make an empirical, data-driven decision in **AIX-118**, the subnet design team must gather concrete evidence across five critical dimensions. The table below details the evidence requirements, collection methodologies, and critical thresholds.

```
+---------------------------------------------------------------------------------+
|                         REQUIRED EVIDENCE REPOSITORY                            |
+---------------------------------------------------------------------------------+
|  1. Verification Cost & Scalability  ->  Validator Hardware & Bandwidth Ceiling  |
|  2. Collusion & Exploit Resistance   ->  Weight-Copying & Response Replay Risks |
|  3. Economic Viability & Emissions   ->  Miner Margins & Hardware ROI           |
|  4. Hardware & Node Heterogeneity    ->  Silicon Diversity vs. FP Drift         |
|  5. Commercial Utility & Demand      ->  Consumer Monetization & API Integration|
+---------------------------------------------------------------------------------+
```

### 4.1 Dimension 1: Verification Cost & Scalability Evidence

* **Question**: Can validators sustain the computational and network cost of evaluating all active miner UIDs ($N \le 256$) within the subnet tempo?
* **Required Data Artifacts**:
  1. **Validator Compute Utilization Profile**: CPU/GPU hours and memory footprint required per validation round per miner.
  2. **Bandwidth Footprint Measurements**: Total inbound/outbound gigabytes transferred per validator per epoch.
  3. **Verification Latency Benchmarks**: Milliseconds required to verify an average miner response across hardware tiers (consumer CPU vs. enterprise GPU).
* **Threshold Gate**:
  * *Open-Ended Pass Gate*: Validator compute costs must not exceed 15% of miner emissions value; validation round latency must complete within $<20\%$ of block tempo.
  * *Deterministic Pass Gate*: Verification algorithm must execute in $< 50\text{ ms}$ on single-thread commodity CPU ($O(1)$ or $O(\log N)$).

### 4.2 Dimension 2: Collusion & Exploit Resistance Evidence

* **Question**: What is the attack surface for dishonest miners and validators to siphon emissions without performing bona fide work?
* **Required Data Artifacts**:
  1. **Weight-Copying Vulnerability Audit**: Degree to which non-evaluating "parasite" validators can mirror top validator weights from chain transactions without querying miners directly.
  2. **Miner Response Replay / Caching Attack Vector Analysis**: Feasibility of miners caching static prompt responses or delegating generation to centralized third-party APIs (e.g., OpenAI, Anthropic) without detection.
  3. **Validator-Miner Cabal Modeling**: Mathematical proof of vulnerability to private out-of-band collusion where colluding validators assign maximum weight to designated miner hotkeys.
* **Threshold Gate**:
  * *Open-Ended Pass Gate*: Must incorporate dynamic synthetic challenge generation with zero pre-computation leakage risk, plus commit-reveal weight submission protocols.
  * *Deterministic Pass Gate*: Challenge parameters must incorporate block-hash entropy ($H(\text{block\_hash} \parallel \text{miner\_hotkey})$) rendering pre-computed or shared solutions cryptographically impossible.

### 4.3 Dimension 3: Economic Viability & Incentive Alignment Evidence

* **Question**: Does the emission distribution incentivize sustained miner capital expenditures and honest participation?
* **Required Data Artifacts**:
  1. **Miner Unit Economics Model**: Capex/Opex modeling comparing hardware amortization, electricity costs, and operational overhead against expected TAO emissions across network difficulty levels.
  2. **Emission Efficiency Ratio**: Proportion of subnet daily emissions ($E_{\text{daily}} \approx \text{owner\_cut} + \text{validator\_cut} + \text{miner\_cut}$) that directly rewards unique useful work versus redundant re-computation.
  3. **Pruning & Churn Dynamics**: Simulation of turnover rate at the $UID$ boundary under varying token price scenarios.
* **Threshold Gate**:
  * Honest miners operating standard recommended hardware specifications must reach profitability within $\le 90$ days at baseline token emission valuation.

### 4.4 Dimension 4: Hardware & Network Heterogeneity Evidence

* **Question**: Can the network operate securely across decentralized, heterogeneous hardware configurations without false disqualifications?
* **Required Data Artifacts**:
  1. **Floating-Point Variance Matrix**: Empirical measurement of output token divergence or embedding cosine distance when executing identical models across diverse hardware (NVIDIA H100, A100, RTX 4090, AMD MI300X, Apple Silicon).
  2. **Cross-Architecture Verification Consistency**: Rate of validator false-rejection caused purely by compiler optimizations, CUDA driver versions, or numerical libraries.
* **Threshold Gate**:
  * *Open-Ended Pass Gate*: Tolerance epsilon ($\epsilon$) in continuous scoring must accommodate architectural floating-point variance without penalizing legitimate nodes.
  * *Deterministic Pass Gate*: 100% platform-independent execution reproducibility guaranteed across all supported operating systems and CPU architectures.

### 4.5 Dimension 5: Commercial Utility & Market Demand Evidence

* **Question**: What is the commercial end-user market for the subnet's computed product, and how does it interface with organic demand?
* **Required Data Artifacts**:
  1. **Target Consumer Profile**: Identity and integration requirements of paying clients (e.g., external dApps requiring ZK rollups vs. enterprises demanding LLM inference endpoints).
  2. **Organic Gateway Feasibility**: Technical mechanism for routing external user queries through validators to miners while injecting synthetic validation challenges into the stream.
* **Threshold Gate**:
  * The protocol must demonstrate a viable architecture for dual-stream execution: organic user request serving interlaced with synthetic challenge verification.

---

## 5. Decision Matrix & Evaluation Rubric

This weighted decision matrix will be utilized in **AIX-118** to evaluate whether open-ended compute or deterministic work is the optimal selection for the subnet.

| Decision Factor | Weight | Evaluation Criteria | Open-Ended Indicator | Deterministic Indicator |
| :--- | :---: | :--- | :--- | :--- |
| **Verification Efficiency** | **25%** | Ratio of validation compute to mining compute; operational overhead on validators. | Validator must spend high compute/memory to grade outputs. | Validator verifies proofs in milliseconds with negligible CPU overhead. |
| **Collusion Resistance** | **25%** | Robustness against weight copying, validator cartels, and off-chain miner pooling. | Vulnerable to subjective bias, model distillation, and cabal scoring. | Cryptographically enforced; impossible to counterfeit valid proofs. |
| **Consensus Stability** | **20%** | Variance of validator scoring in Yuma Consensus; risk of weight divergence. | High variance; requires outlier filtering and subjective ranking consensus. | Near-zero variance; unanimous binary mathematical consensus. |
| **Commercial Demand** | **15%** | Market willingness to pay for the generated decentralized compute output. | High demand for generative intelligence, specialized LLMs, and AI agents. | High demand for verifiable proofs, decentralized storage, or zk-compute. |
| **Decentralization / Barrier to Entry** | **15%** | Accessibility of mining and validating to independent operators without elite clusters. | Requires high-end GPU clusters for state-of-the-art inference/training. | Allows specialized hardware or commodity nodes depending on proof system. |

### 5.1 Scorecard Calculation Formula

Each candidate model will be scored from 1 to 10 across all five categories:
$$\text{Composite Score} = \sum_{k=1}^5 w_k \cdot S_k$$

A model choice in **AIX-118** requires a Composite Score $\ge 7.5$ and must pass all non-negotiable threshold gates specified in Section 4.

---

## 6. Downstream Protocol Implications (Traceability Matrix)

The choice of evaluation model directly determines the technical design of all downstream issues in the milestone:

```
+----------------------------------------------------------------------------------------------------+
| AIX-117 Requirements -> Downstream Milestone Issues                                                |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  --> AIX-118: Compare Open-Ended and Deterministic Evaluation                                      |
|      * Consumes: Evidence requirements (Section 4) & Decision Matrix (Section 5)                   |
|      * Produces: Final architecture choice and formalized selection rationale                     |
|                                                                                                    |
|  --> AIX-119: Design Protocol Implications for Selected Model                                      |
|      * Open-Ended Path: `bt.Synapse` streaming payloads, prompt serialization, latent tensor types |
|      * Deterministic Path: Proof challenge headers, binary commitment hashes, verification receipts|
|                                                                                                    |
|  --> AIX-120: Specify Validator Logic for Selected Model                                           |
|      * Open-Ended Path: Synthetic prompt factory, reward loss functions, EMA score normalization |
|      * Deterministic Path: Verification algorithms (e.g. elliptic curve pairings, Merkle audits)   |
|                                                                                                    |
|  --> AIX-121: Define Anti-Collusion Strategy                                                       |
|      * Open-Ended Path: Watermarking, canary prompts, response entropy analysis, commit-reveal    |
|      * Deterministic Path: Nonce-randomized challenge nonces, hotkey-bound proof salts             |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
```

### 6.1 Requirements Checklist for Model Implementation

When evaluating protocol designs in AIX-119 through AIX-121, the following operational requirements established by this document must be satisfied:

* [ ] **R-EVAL-01**: The evaluation pipeline must guarantee validator score generation latency strictly less than $0.2 \times \text{tempo}$ blocks.
* [ ] **R-EVAL-02**: The scoring mechanism must map outputs to normalized on-chain weights $\mathbf{W} \in [0, 65535]^N$ with $\sum W_i = 65535$.
* [ ] **R-EVAL-03**: The protocol must support validator outlier clipping to prevent colluding cartels from skewing emissions.
* [ ] **R-EVAL-04**: The system must provide reproducible challenge generation where honest miners can reliably prove capacity without exposing secrets to competitors.
* [ ] **R-EVAL-05**: Verification overhead must scale at sub-linear cost relative to network miner registration limits (`max_uids`).

---

## 7. Conclusion & Next Steps

This document formally defines the requirements, taxonomy, success criteria, and evidence gathering standards for the Bittensor subtensor evaluation model. 

* **Immediate Action**: Proceed to **AIX-118** (*Compare open-ended and deterministic evaluation*) to populate the evidence matrix with empirical workload benchmarks and record the formal architectural decision.
