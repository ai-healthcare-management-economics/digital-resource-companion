# Scenario: Hospital Command Dashboard and Patient Flow

## Institutional context

A 520-bed regional teaching hospital has experienced recurrent emergency-department boarding, delayed discharges, uneven diagnostic capacity, and short-notice staffing gaps. Senior management has approved an eight-week controlled pilot of a command dashboard that combines current bed occupancy, forecast admissions, planned and completed discharges, imaging queues, transport delay, and staffing variance.

The dashboard is reviewed during a morning operational huddle and continuously by the patient-flow office. It presents observed measures, forecasts, and recommended escalation actions. During the pilot, however, several concerns emerge:

- the forecast is sometimes accurate but the recommended action is reviewed after the relevant decision window;
- planned discharges are recorded inconsistently across services;
- units respond differently to the same escalation signal;
- high occupancy is sometimes relieved by transferring congestion to imaging, transport, or community care;
- staff are concerned that unit-level comparisons could be used punitively;
- managers cannot always reconstruct which data and forecast version supported an action;
- the dashboard reports improvement in waiting time, but the hospital has not established whether this resulted from the dashboard, seasonal variation, or a temporary staffing increase.

The executive committee must decide whether to scale the dashboard to a permanent 24-hour command-centre model, continue a restricted pilot, redesign the intervention, or stop.

## Decision question

Under what conditions, if any, should the hospital scale the command dashboard as a permanent patient-flow management intervention?

## Realistic comparators

1. Continue the current spreadsheet and twice-daily huddle process.
2. Improve discharge planning and escalation protocols without predictive analytics.
3. Retain the dashboard only as a descriptive operational display.
4. Use forecasting and optimization selectively for high-pressure periods.
5. Scale the complete command-centre model with dedicated staffing and governance.

## Evidence supplied

The synthetic dataset records six operational intervals during a high-demand day. It includes forecast and actual arrivals, staffed and occupied beds, planned and completed discharges, imaging queues, transport delay, staffing gaps, action latency, and boarded patients. The wb calculates occupancy, forecast error, discharge completion, pressure level, and timeliness of response.

## Questions for analysis

1. Which indicators are observations, forecasts, process measures, outcomes, and balancing measures?
2. Which signals arrive within the relevant decision window, and which arrive too late to create value?
3. Does the dashboard reveal a system bottleneck or merely shift pressure between services?
4. Which data definitions and provenance records require correction before scale?
5. What evidence is needed to attribute changes in flow to the dashboard rather than to concurrent staffing or seasonal effects?
6. Which roles should own interpretation, action, escalation, and review?
7. What safeguards are required to reduce gaming, surveillance concerns, and false precision?
8. What monitoring thresholds would justify continuation, redesign, restriction, or withdrawal?
9. What is the recommended decision, with conditions and a review date?
