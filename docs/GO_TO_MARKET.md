# HyperGen Go-to-Market Plan

**Status:** Hypotheses to validate, not proven traction.  
**Last updated:** 2026-10-17  
**Product stage:** Early prototype.

## 1. Positioning

HyperGen is an early-stage agent reliability and security testing harness. It runs an agent in a controlled stateful environment, records tool calls, verifies resulting state against expected outcomes, and reports observable security checks.

**Initial positioning to test:** "Find out whether your AI agent actually respects authorization and data boundaries when it uses tools—before deployment."

Do not claim HyperGen makes agents secure, prevents every attack, or is production-ready. The current synthetic store is not connected to real payment systems.

## 2. Initial ideal customer profile

Prioritize teams that deploy agents capable of taking consequential actions.

### Tier 1: AI-agent startups
- Customer support agents with refund/account tools.
- Sales and operations agents that modify CRM data or send messages.
- Finance/admin agents that initiate workflow actions.
- Buyer: founder, CTO, head of engineering, AI engineering lead.
- Trigger: preparing to launch an agent, adding tool access, a failed evaluation, enterprise customer security review, or an incident.
- Why HyperGen may matter: action-level tests with explicit expected state and reproducible tool traces.

### Tier 2: AI implementation agencies
- Build multiple agents for clients and repeat similar QA/security work.
- Buyer: technical founder, delivery lead, head of AI engineering.
- Potential value: reusable regression packs and client-facing evidence across projects.
- Risk: agencies may prefer open-source/free tools or bill QA as services; validate willingness to pay.

### Tier 3: Agent builders and vibe-coding platforms
- Could embed pre-deployment checks into an app/agent release flow.
- Buyer: platform product/security/engineering leadership.
- Defer integration asks until the core engine is validated and a low-friction API/CLI exists.

### Tier 4: Enterprise security teams
- Larger potential contracts, but higher expectations for isolation, deployment, auditability, support, access controls, and procurement.
- Do not make enterprise-readiness claims until those controls are implemented and independently reviewed.

## 3. Customer discovery

Run 15–20 interviews before expanding scope. Ask:
1. What actions can your agent take in external systems?
2. Which three failures would create the most cost, risk, or customer harm?
3. How do you test those failures today?
4. What does your existing test suite miss?
5. Can you verify actual tool/state changes, or only final text?
6. What would make a test result credible enough to block a release?
7. Who owns this budget and what tool/service is paid for today?
8. Would you try a scoped pilot? What evidence would you require to pay?

Do not lead with a demo. Learn the customer's current workflow and failure modes first. Record anonymized, consented findings; do not collect secrets or production customer data.

## 4. Discovery scorecard

Score each potential use case 1–5:
- Severity of failure
- Frequency/exposure
- Cost of current testing
- Ability to reproduce in a safe environment
- Ability to verify actual state
- Urgency / deadline
- Identified budget owner
- Willingness to run or pay for a pilot
- Relevance to multiple customers

Prioritize repeated, expensive problems with observable ground truth. Do not build a custom vertical for a single low-value request without commercial evidence.

## 5. Pricing hypotheses (USD, validate in conversations)

These are experiments, not established market prices:
- Community: free local runner / sample benchmark.
- Startup: $99–$299 per month for limited agents/runs and core reports.
- Agency: $500–$1,500 per month for multiple projects and reusable packs.
- Scoped pilot: $1,000–$5,000 depending on workflow, integration, and deliverables.
- Enterprise: custom only after deployment/security requirements are met.

For India-based early design partners, test a lower-priced pilot if needed. Avoid promising custom integrations, compliance certification, or production prevention that do not exist.

## 6. First 100-prospect experiment

Target only public, relevant business profiles and role-based contacts. Do not scrape personal contact details or send bulk spam.

Hypothesis funnel (not a forecast):
- 100 carefully selected prospects
- 15–25 meaningful conversations
- 3–8 qualified pilot opportunities
- 1–3 paid pilots

Track: company, agent use case, evidence source, role, why relevant, date contacted, response, current tool, pain point, pilot status, next step, and opt-out. Do not fabricate contact names or claim a prospect has a problem without evidence.

### Outreach message

Subject: Testing what your agent does—not just what it says

Hi [Name] — I saw that [company] is building [specific agent/workflow]. How are you currently testing the actions it can take through tools—for example, authorization boundaries, data access, or incorrect state changes?

I'm building HyperGen, an early-stage harness that runs agents in controlled scenarios and checks tool traces and resulting state against expected outcomes. We're looking for a few teams to help validate whether this catches failures their current tests miss.

Would a 15-minute conversation be useful? No worries if it's not a priority.

[Founder]

Personalize the first sentence with a verifiable public product detail. Never imply the company has a security flaw.

## 7. Competitive research and differentiation

Adjacent categories include:
- Open-source LLM evaluation and red-teaming tools.
- LLM observability and tracing platforms.
- Agent runtime security / governance.
- Application security testing.

OASB (Open Agent Security Benchmark) describes 223 attack scenarios and product-agnostic adapters. Promptfoo offers open-source evaluations and red-teaming. These make "more tests" an insufficient differentiation claim.

Investigate and test, rather than assume, potential differentiators:
1. Ground-truth verification of actual state changes.
2. Authorization-aware tool-action testing.
3. Reproducible traces connecting attack input → attempted action → policy decision → resulting state.
4. Customer-specific policy and workflow regression packs.
5. CI release gates that fail on verified violations.
6. Clear false-positive / false-negative measurement.

Do not claim these are unique until a hands-on comparison confirms what competitors support.

## 8. Proof required before raising the ambition

Minimum evidence targets:
- 15–20 customer interviews.
- 3–5 design partners (target, not guarantee).
- At least one external agent or customer workflow tested with consent.
- A deliberately vulnerable baseline that HyperGen detects reliably.
- Safe controls that do not trigger false positives.
- Reproducible reports and documented limitations.
- Preferably 1–3 paid pilots; not required to be honest about current stage.

## 9. 30-day execution plan

### Week 1
- Freeze current 8-scenario baseline.
- Update stale README and publish benchmark methodology.
- Draft discovery scorecard and prospect tracker.
- Interview first five builders.

### Week 2
- Complete 10–15 interviews.
- Implement negative controls and measure detection / false-positive behavior.
- Choose one repeated high-cost use case.

### Week 3
- Add cases only for validated failure modes.
- Demo to design partners using synthetic or explicitly authorized environments.
- Ask for pilot commitments.

### Week 4
- Review evidence and willingness to pay.
- Continue, narrow, or change the initial vertical based on results.
- Build investor narrative from measured outcomes, not scenario count.

## 10. Stop / continue rules

Continue investing in a use case when multiple independent prospects report the same costly problem, the failure can be reproduced, the evaluator can measure it, and a buyer will commit time or money.

Reconsider the use case if customers say existing tools already solve it, no buyer owns the problem, or the result cannot be verified reliably.
