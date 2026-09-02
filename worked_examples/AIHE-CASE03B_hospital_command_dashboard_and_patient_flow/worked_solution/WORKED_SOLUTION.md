# Worked solution: Hospital Command Dashboard and Patient Flow

## 1. Decision framing

The dashboard should be treated as a management intervention rather than as a display product. Its value depends on data quality, forecast calibration, action latency, accountable ownership, downstream capacity, and a feedback process that connects signals to decisions and outcomes.

The appropriate comparator is not a hospital without information. It is the best feasible combination of current huddles, discharge redesign, staffing escalation, and selective analytics. The executive committee should therefore ask whether the complete command-centre model adds incremental value after the costs of data integration, dedicated review, coordination, training, monitoring, and governance.

## 2. Interpretation of the synthetic evidence

The worked dataset shows three recurring patterns.

First, occupancy pressure is not explained by arrivals alone. In several intervals, delayed discharges, imaging queues, transport delay, and staffing gaps jointly produce boarding. A dashboard that optimizes one department could therefore shift congestion rather than improve the full pathway.

Second, forecast error is acceptable in some intervals but operational value is lost when action latency exceeds the 30-minute decision window. A moderately accurate forecast reviewed promptly may be more useful than a more accurate forecast reviewed after capacity decisions have already been made.

Third, the discharge-completion rate varies materially. This makes planned discharge an unreliable input unless definitions, timing, and ownership are standardized. The hospital should not scale a forecast-dependent workflow while a key input remains inconsistently recorded.

## 3. Governance and accountability

Each indicator requires an owner, an interpretation rule, an escalation route, and a balancing measure. The patient-flow office may be responsible for operational review, but clinical services must remain accountable for care decisions. Quality and safety staff should review adverse events, workarounds, and unintended transfers of burden. Data and informatics teams should maintain the indicator dictionary, provenance, latency monitoring, and version history.

The dashboard should distinguish observed values, forecasts, and recommendations visually and in the audit log. Unit-level comparisons should not be used for punitive performance management without contextual review. Staff should be able to record why a recommendation was accepted, modified, or rejected.

## 4. Economic and implementation interpretation

The business case should not value dashboard use by views or logins. Benefits should be linked to reduced boarding, avoidable cancellation, overtime, delayed care, and unnecessary escalation. Costs include integration, support, dedicated command-centre staffing, meetings, workflow redesign, data stewardship, and monitoring.

The pilot evidence is not sufficient to attribute all observed change to the dashboard. A longer interrupted time-series evaluation, with annotations for staffing, seasonal pressure, policy changes, and major operational events, would provide stronger evidence. Process evaluation should examine how teams interpret and act on signals.

## 5. Recommendation

**Recommended decision: continue a redesigned and time-limited pilot; do not yet scale to permanent 24-hour operation.**

Conditions should include:

1. standardize definitions and ownership for planned discharge, bed status, boarding, and diagnostic queues
2. display data freshness, forecast uncertainty, and model version
3. establish a 30-minute action-latency standard for high-pressure signals
4. assign accountable owners and escalation routes for each indicator
5. include balancing measures for safety, staff workload, cancellations, readmissions, and downstream congestion
6. document actions, overrides, outcomes, and reasons for non-action
7. conduct a twelve-week controlled evaluation using time-series and qualitative evidence
8. report lifecycle cost and benefit-realization assumptions separately from forecast performance
9. prohibit punitive use of unit comparisons without contextual and governance review
10. return to the executive committee with proceed, redesign, restrict, or stop criteria.

The dashboard should be scaled only if it demonstrates timely and feasible action, sustained improvement in the whole pathway, acceptable workforce burden, reliable data provenance, and benefits that justify the continuing cost of the command-centre model.
