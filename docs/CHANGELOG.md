# Recovered DLB development history

This changelog summarizes the main recovered milestones of the integrated DLB proxy line.

## v1.9

- Two-Zendure non-consecutive phase scenario fixed.
- Continued integrated DLB development on top of the gast777 proxy.

## v2.0

- Multiple Zendures can share the same physical phase.
- One shared safe phase budget is enforced per physical phase.
- Flexible phase assignment added.

## v2.4

- Current integrated DLB structure matured.
- Home Assistant `Events: state` based P1 handling retained.
- Live P1-based protection and redistribution behavior improved.

## v2.5

- Startup/deploy preflight added so old context is never trusted after restart.
- Fresh P1 data must arrive after start before unrestricted charging is allowed.
- This was the explicitly confirmed working baseline.

## v2.6

- DLB settings and logging section cleaned up and reorganized.
- Separate DLB logging categories added:
  - soft info
  - status info
  - warnings
  - debug
- Main README/documentation line aligned with the integrated DLB proxy.

## v2.6.1

- Non-HomeWizard compatibility improvement.
- Adapter path now supports source-aware freshness checking for the `last_reported` issue.
- Intended only for users following the separate other-P1 compatibility path.

## v2.7

- DLB recovery logic improved.

- Ramp-up protection now activates only after genuine DLB limiting or fail-safe events.

- Normal Gielz/NOM power reductions no longer trigger false recovery states.

- False soft/throttling states caused by redistribution, rounding or normal recovery were removed.

- Compact DLB logging, status transitions, shared heartbeat and Node-RED status colours improved.

## v2.8

- Minimum useful charging power per Zendure added.

- Small allocations below the configured threshold are removed and redistributed to other eligible Zendures where safely possible.

- 1 W rounding leftovers and false redistribution/throttling messages fixed.

- Redistribution of 50 W or less is no longer shown in normal operational logs.

- New setting:

    dynamic_load_balancing_min_device_charge_w = 100
    100 = every charging Zendure receives either 0 W or at least 100 W.
    Change the value to select another minimum charging threshold.
    0 = disable the feature and retain the previous allocation behaviour.