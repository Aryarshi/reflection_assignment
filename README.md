# Daily Reflection Tree — DT Fellowship Submission

**Candidate:** Aryarshi Das
**Assignment:** Role Simulation — Knowledge Engineering

---

## Structure

```
/tree/
  reflection-tree.json     ← Part A: full tree data (35 nodes)
/agent/
  agent.py                 ← Part B: Python CLI agent (no LLM at runtime)
/transcripts/
  persona-1-transcript.md  ← Victor / Contributing / Altrocentric path
  persona-2-transcript.md  ← Victim / Entitled / Self-centric path
write-up.md                ← Design rationale (2 pages)
README.md                  ← This file
```

---

## Part A: Reading the Tree

`reflection-tree.json` contains an array of **35 nodes**. Each node has:

| Field | Purpose |
|---|---|
| `id` | Unique identifier |
| `parentId` | Tree parent (null = root or cross-linked node) |
| `type` | `start` / `question` / `decision` / `reflection` / `bridge` / `summary` / `end` |
| `text` | Employee-facing text. `{NODE_ID.answer}` and `{axis.dominant}` are interpolated at runtime |
| `options` | For questions: fixed choices. For decisions: routing rules (`answer=X\|Y:TARGET` or `signal=axis:pole:TARGET`) |
| `target` | Explicit next node (overrides child lookup) |
| `signal` | State tally recorded when this node is visited (`axis1:internal`, `axis2:contribution`, etc.) |

**To trace a path manually:**
1. Start at node `START`
2. Follow `target` field or first child node
3. At `question` nodes, pick an option — store answer, follow child
4. At `decision` nodes, evaluate the `options` routing rules against stored state
5. At `reflection`/`bridge` nodes, read text, follow `target`
6. At `summary`, interpolate templates using accumulated signals
7. End at `END`

**Node count by type:**

| Type | Count |
|---|---|
| start | 1 |
| question | 10 |
| decision | 8 |
| reflection | 8 |
| bridge | 2 |
| summary | 1 |
| end | 1 |
| **Total** | **35** |

---

## Part B: Running the Agent

**Requirements:** Python 3.10+. No external dependencies.

```bash
# From the repo root:
python agent/agent.py

# With explicit tree path:
python agent/agent.py tree/reflection-tree.json

# With debug state dump at end:
python agent/agent.py --debug
```

The agent:
- Loads the tree from JSON (not hardcoded)
- Renders each node type with appropriate interaction
- Routes deterministically — same answers → same path → same reflection
- Accumulates axis signals and interpolates all reflection/summary text
- Makes **zero LLM or network calls** at runtime

---

## The Three Axes

| Axis | Spectrum | Psychological basis |
|---|---|---|
| 1: Locus | Victim → Victor | Rotter (1954) Locus of Control + Dweck (2006) Growth Mindset |
| 2: Orientation | Entitlement → Contribution | Campbell et al. (2004) + Organ (1988) OCB |
| 3: Radius | Self-centric → Altrocentric | Maslow (1969) Self-Transcendence + Batson (2011) Perspective-Taking |

---

## Key Design Constraints Honoured

- ✅ No LLM at runtime
- ✅ Fully deterministic (same answers = same path)
- ✅ Fixed options only — no free text
- ✅ No moralizing — tone is curious colleague, not therapist or manager
- ✅ Axes flow as a sequence (1→2→3), with bridges connecting them
- ✅ Interpolation using `{node_id.answer}` and `{axis.dominant}` placeholders
- ✅ Signal-based state accumulation for dominant-axis routing
