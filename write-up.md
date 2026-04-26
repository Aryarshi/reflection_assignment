# Write-Up: Design Rationale — Daily Reflection Tree

**Aryarshi Das | DT Fellowship Assignment**

---

## Why These Questions

The hardest design constraint was the "no moralizing" rule. A reflection tree that makes someone feel judged will be abandoned within three sessions. Every question had to feel like a curious colleague asking — not a therapist scoring you or a manager evaluating you.

This pushed me toward **framing questions around moments, not character**. Rather than "Do you take responsibility for your actions?" (which signals the 'right' answer immediately), I used "When something didn't go to plan, what was your first instinct?" The distinction matters: the first question asks who you *are*, the second asks what you *did* — and that's answerable without defensiveness.

For **Axis 1 (Locus)**, I deliberately split the opening question based on the employee's one-word descriptor. Someone who said "Productive" is already in a reflective, open state — they get asked what made it work (surfacing attribution style gently). Someone who said "Frustrating" is activated — they need a softer landing before being asked about agency. The branching isn't just routing logic; it's tone management.

For **Axis 2 (Orientation)**, the hardest problem was making entitlement visible without shame. Entitled behaviour is largely invisible to the person holding it — Campbell et al. (2004) show it's experienced as justified, not excessive. So I avoided the word "entitlement" entirely. "I was looking for recognition for something I'd already done" is something most people have felt and won't lie about. The reflection node then names what it is — gently but honestly — after the fact.

For **Axis 3 (Radius)**, I used Maslow's hierarchy as the branching architecture itself. The four options in the opening question map directly from narrow (self) to wide (end user/purpose), creating a spectrum the employee places themselves on without being told which end is "better."

---

## Branching Trade-offs

The tree has **two primary entry forks on Axis 1** based on the opening word. This was a deliberate choice over a single linear path — but it introduced complexity: two parallel question nodes (`A1_Q_WHAT_WORKED` and `A1_Q_HARD_MOMENT`) that must both lead to the same Axis 2 entry point. I managed this with bridge nodes and a shared decision on accumulated signals rather than answer matching for the reflection routing.

The **signal-based routing** on decision nodes (using `axis1.dominant`) rather than direct answer routing is the key structural decision. It means someone can give slightly different answers across two questions but still be routed to a coherent reflection. This makes the tree more robust than a pure answer-matching approach, at the cost of slightly more state management.

**Trade-off I accepted:** The tree doesn't currently cross-reference axes in summary reflections (e.g., "You recognized your agency in Axis 1 — but didn't extend that outward in Axis 3"). With more time, the summary templates would become a matrix of combinations rather than a sequence of independent axis summaries. The closing insight templates partially address this, but a 3×3 full combination set would be more precise.

---

## Psychological Sources

- **Locus of Control** — Rotter (1954/1966): Internal vs external attribution. I used this to design options that are neither obviously "good" nor "bad" — "I adapted quickly" and "I waited for someone to step in" are both honest human responses on a spectrum, not moral judgments.
- **Growth vs Fixed Mindset** — Dweck (2006): Informs the follow-up questions in Axis 1, particularly whether the employee sees a difficult moment as information or as evidence of external failure.
- **Psychological Entitlement** — Campbell et al. (2004): Guided my decision to never use the word "entitlement" in any question. Surface the behaviour; let the reflection name it.
- **Organizational Citizenship Behavior** — Organ (1988): Defined what "contribution" looks like in options — helping outside your role, teaching, volunteering.
- **Self-Transcendence** — Maslow (1969): The Axis 3 question options map directly to his needs hierarchy, with the end user/purpose option representing the transcendence level.

---

## What I'd Improve With More Time

1. **Full combination summary matrix** — 2×2×3 = 12 unique closing insights, one per possible axis-combination path. Currently I have ~6 templates with a default fallback.
2. **Streak and longitudinal tracking** — storing state across sessions to say "You've been in external locus three days running — what's the pattern?" This is the most powerful feature for a tool used daily.
3. **Question randomization within a branch** — to prevent click-through fatigue after 30 uses. The psychology stays the same; the surface question rotates from a pool.
4. **Tone calibration by fatigue signal** — if the employee answers "Frustrating" or "Tough" three sessions in a row, the tree opens with a different, gentler warm-up before the reflection proper.
5. **Web UI** — the CLI works, but a minimal browser interface with smooth transitions would make the experience feel more like a ritual and less like a script.
