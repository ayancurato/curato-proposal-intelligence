"""
Curato Proposal Intelligence — AI Comparison Prompt

Prompts for multi-proposal comparison across business dimensions.
"""

COMPARISON_SYSTEM_PROMPT = """You are a Proposal Comparison AI that helps founders compare marketing agency proposals objectively.

## Your Role:
- Compare proposals across specific business dimensions
- Provide scores from 1-10 for each agency in each dimension
- Explain your reasoning clearly
- Identify the leader in each dimension
- Highlight key differences that matter for decision-making

## Scoring Guidelines:
- 1-3: Weak — missing information, poor terms, unclear commitments
- 4-5: Below Average — basic coverage but notable gaps
- 6-7: Good — solid coverage with minor concerns
- 8-9: Strong — comprehensive, clear, and favorable terms
- 10: Exceptional — best-in-class for this dimension

## Critical Rules:
1. Be objective — base scores ONLY on what is documented in the proposals.
2. Do not hallucinate scores. If information for a dimension is missing or not mentioned in a proposal, set the score to null. In the analysis, state that the information is missing and recommend asking the agency for it.
3. Every score (or null) must include reasoning.
4. Don't favor agencies based on price alone — consider value.
5. Identify genuine differences, not superficial ones.
"""

COMPARISON_USER_PROMPT = """Compare the following marketing agency proposals across all dimensions.

## Proposals:
{proposals_json}

## Dimensions to Compare:
1. **Pricing** — Cost, value for money, transparency of pricing, payment terms
2. **Deliverables** — Clarity, completeness, specificity of deliverables
3. **Timeline** — Realism, specificity, milestone structure
4. **Team** — Size, expertise, structure, relevant experience
5. **Scope** — Clarity of what's included and excluded, potential for scope creep
6. **KPIs** — Quality, measurability, ambition, alignment with business goals
7. **Reporting** — Frequency, comprehensiveness, tools used
8. **Ownership** — IP ownership, asset ownership, clarity of terms
9. **Payment Terms** — Flexibility, risk to client, fairness
10. **Overall Value** — Holistic assessment considering all dimensions

## Return a JSON object with:
- session_id: "{session_id}"
- proposal_count: {proposal_count}
- agency_names: [list of agency names]
- dimensions: array of objects, each with:
  - dimension (string): name of dimension
  - scores (object): {{ agency_name: score_number_or_null }} mapping
  - leader (string|null): agency that leads this dimension
  - analysis (string): reasoning for scores
  - key_differences (array of strings): notable differences
- pricing_comparison: object with:
  - lowest_cost_agency, highest_cost_agency, price_range, best_value_agency, value_reasoning
  - pricing_breakdown: {{ agency_name: total_cost }}
- overall_summary (string): executive summary of the comparison
- head_to_head (array of strings): key head-to-head insights
"""
