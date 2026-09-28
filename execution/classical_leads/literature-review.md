# Literature review: the confirmed Stage D mechanism

2026-09-28. This covers the mechanism confirmed in `stage-d-results.md` (H2),
in its minimal form `wick_linear` / `wick_real`. Search and reading were done
through the web tools on this date. Where only an abstract or summary was
available, that is stated. Nothing here was checked against every paper's
full text or code.

## 1. The mechanism, written out

For one head with score matrix S (L×L), p_i = softmax(S_i) and a_i = √p_i:

  H = (S + Sᵀ) / (2√L),  m_i = a_i Hᵀ,  i.e. m_ij = Σ_k H_jk √p_ik,
  A_ij ∝ (a_ij − Δt·m_ij)² = p_ij − 2Δt·√p_ij·m_ij + Δt²·m_ij²,
  out_i = Σ_j A_ij v_j,  with Δt ≈ 0.25 (fixed in practice).

This expansion was checked numerically against the implementation. With the
complex Hermitian H of `c1_wick`, the antisymmetric part appears only in the
Δt² term, through |m_ij|². That explains why D5 (complex against real H) was
0–0: at Δt = 0.25 the first-order term dominates, and it uses only the
symmetric part.

In words, query i's weight on key j is corrected by m_ij. This is how
strongly token j couples to the keys that query i already attends to, where
the coupling is the symmetrised score between token j and each other token k,
weighted by √p_ik. Positive coupling suppresses key j; negative coupling
boosts it. The quadratic term is always non-negative. So the mechanism has
five properties:

1. **Third order in tokens** (i, j, k), through a *factorised* product
   √p_ij · √p_ik · H_jk, without any new trilinear parameters.
2. **Signed**: it can suppress a key's weight below its softmax value.
3. **Parameter-free** beyond one scalar Δt per head, and it reuses the
   layer's own score matrix.
4. **O(L³) per head**, because of the L×L by L×L product a·Hᵀ. Softmax is
   O(L²). This matters at long context.
5. **Classical**: no complex arithmetic is needed (D5), no unitarity and no
   matrix exponential (D6).

## 2. Closest prior work

| Work | What it does | Relation to this mechanism |
|---|---|---|
| **2-simplicial attention**: Clift et al., 2019; Roy et al., "Fast and Simplex", arXiv 2507.02754, 2025 | Trilinear scores over a query and a *pair* of keys, generalising the dot product from the 1-simplex to the 2-simplex. Reported to improve token efficiency on maths, coding and reasoning. Cubic cost, reduced in practice by windowing. | **Closest in function.** Both let one attention layer express query–key–key interactions, which is exactly what 3-bit parity needs. Ours is a heavily *restricted* case: the three-way term factorises through existing pairwise scores, with no new projections, and it acts as a signed correction to softmax weights instead of a separate trilinear softmax. Formula details were taken from the abstract and secondary summaries, not the full text. |
| **Nexus**: arXiv 2512.03377 | Refines queries and keys with inner self-attention (softmax(QQᵀ)Q and softmax(KKᵀ)K), then applies ordinary attention to the results. | Also uses key–key structure within one layer, but to rebuild representations, not to reweight attention. It is unsigned, and it has no square-root or squaring step. The full text says it does **not** combine S_ij with S_jk as a two-hop score. |
| **Diffuser**: multi-hop attention diffusion, arXiv 2210.11794, AAAI 2023 | 𝒜 = Σ_k θ_k A^k with personalised-PageRank θ_k = α(1−α)^k, run as power iteration on values (K = 5, α = 0.1), over sparse attention. | Multi-hop, but a *positive* mixture of powers of the row-stochastic attention matrix, applied to values. It cannot suppress a key, and the hop uses attention probabilities rather than the symmetric score operator on amplitudes. |
| **Differential attention**: Ye et al., arXiv 2410.05258, ICLR 2025 | softmax(Q₁K₁ᵀ)V − λ·softmax(Q₂K₂ᵀ)V: subtracts a "noise" map. | Shares the **signed/subtractive** idea. The subtraction there comes from a second learned map, not from key–key structure, and there is no three-way term. |
| **Diffusion or heat-kernel attention**: arXiv 2604.09560; SSRN 5953096 | Softmax viewed as a diffusion-map operator; finite-time heat-kernel dynamics in place of softmax. | The same operator family as the matrix-exponential variants (`c1_wick`, `wick_real`). The confirmed minimal form is a *first-order* step of such dynamics, applied to √p and then squared. |
| **Mass-Aware Attention**: Yu and Ha, arXiv 2607.22781, 2026 | Lp normalisation of attention mass (recommended p ≈ 1.1). | Covers the rejected lead L1: √softmax is MAA with p = 2 at temperature 2. It is not related to the confirmed mechanism. |
| **Sigmoid attention**: Ramapuram et al., ICLR 2025 | Unnormalised σ(S − log L). | Baseline only. It solved 0/30 and 0/20 here. |
| **Born-rule views of softmax**: e.g. arXiv 2608.11173 (cited in the paper) | Born-rule analogues of softmax on the simplex. | The framing that led here. It doesn't propose this correction. |

**Why parity matters here.** One-layer transformers are known to find
parity-like, high-sensitivity functions hard to learn: sharp loss landscapes,
and difficulty with length (for example "Parity, Sensitivity, and
Transformers", arXiv 2602.05896). Theory shows softmax attention *can*
represent sparse XOR with suitable training (arXiv 2502.07553,
arXiv 2505.19531). So the probe gains could come from easier optimisation,
not new expressivity. The probes do not separate those two explanations.

## 3. Novelty assessment

- **Not new:** the family, meaning higher-order, multi-hop and signed
  attention. Each ingredient on its own has close precedent: key–key
  interactions within a layer (Nexus, 2-simplicial), multi-hop mixing
  (Diffuser), subtractive attention (Differential) and diffusion operators
  (heat-kernel attention).
- **Not found in this search:** the specific combination.
  - √softmax amplitudes.
  - A *signed, first-order* correction by the layer's own *symmetrised score
    matrix*: key–key coupling weighted by the query's own √p.
  - Squaring and renormalising.

  As far as this search reached, that combination looks unpublished. It
  amounts to a **parameter-free, factorised special case of query–key–key
  (2-simplicial-style) attention obtained from an existing bilinear score
  matrix**.
- **Not established.** This was a targeted web search, not a systematic
  review. A claim of novelty needs:
  - a full-text check of the 2-simplicial papers, and of the "higher-order
    attention" line (for example arXiv 2603.11133), for an equivalent
    factorised form;
  - a check of the graph-attention literature, where signed and two-hop
    corrections on graphs are common.

## 4. What this means for claims and next experiments

1. **Describe it** as a cheap, parameter-free query–key–key correction of
   softmax, derived from, but not dependent on, a quantum-walk analogy. Do not
   describe it as quantum attention.
2. **The right baselines** for any further claim are 2-simplicial attention
   (the expressive upper bound, at higher cost), Differential attention (the
   signed baseline) and a Diffuser-style positive two-hop A + Δt·A² (a
   multi-hop baseline without sign or square root).
3. **Ablations the probes did not run,** needed to say which ingredient
   matters:
   - the same signed correction applied to p rather than √p, then clipped
     and renormalised;
   - an unsigned (positive) correction;
   - a correction using the attention matrix A instead of the score matrix H.
4. **Cost.** At O(L³) it is fine for the 13-token map benchmark, but it would
   need windowing or low-rank tricks for long contexts, as 2-simplicial
   attention does.

## Sources

- [Mass-Aware Attention, arXiv 2607.22781](https://arxiv.org/abs/2607.22781)
- [Nexus: Higher-Order Attention, arXiv 2512.03377](https://arxiv.org/html/2512.03377v1)
- [Diffuser, arXiv 2210.11794](https://arxiv.org/abs/2210.11794)
- [Fast and Simplex: 2-Simplicial Attention, arXiv 2507.02754](https://arxiv.org/abs/2507.02754)
- [Linearized 2-Simplicial Attention, arXiv 2608.09307](https://arxiv.org/pdf/2608.09307)
- [Differential Transformer, arXiv 2410.05258](https://arxiv.org/abs/2410.05258)
- [The Diffusion-Attention Connection, arXiv 2604.09560](https://arxiv.org/pdf/2604.09560)
- [Diffusion Attention (heat kernel), SSRN 5953096](https://papers.ssrn.com/sol3/Delivery.cfm/5953096.pdf?abstractid=5953096&mirid=1)
- [Sigmoid Self-Attention, arXiv 2409.04431](https://arxiv.org/abs/2409.04431)
- [Beyond Pairwise Attention: Higher-Order Modular Attention, arXiv 2603.11133](https://arxiv.org/html/2603.11133)
- [Parity, Sensitivity, and Transformers, arXiv 2602.05896](https://arxiv.org/html/2602.05896v2)
- [Transformers Provably Learn Sparse XOR, arXiv 2502.07553](https://arxiv.org/abs/2502.07553)
- [Minimalist Softmax Attention Provably Learns Constrained Boolean Functions, arXiv 2505.19531](https://arxiv.org/pdf/2505.19531)
- [A Quantum Roadmap for Softmax Attention, arXiv 2608.11173](https://arxiv.org/html/2608.11173)
