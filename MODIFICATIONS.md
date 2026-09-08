# Modifications relative to gast777/Zendure-zenSDK-proxy

This repository contains a modified DLB-oriented development line derived from gast777’s proxy.

Main additions and changes:

1. Dynamic Load Balancing (DLB) added for **charging** protection on L1/L2/L3.
2. Flexible mapping between Zendure number and physical phase.
3. Support for multiple Zendures on the same phase with one shared safe phase budget.
4. Live P1-triggered charge correction while a charge request remains active.
5. Safe redistribution of blocked requested power to other phase groups with spare capacity.
6. Per-phase voltage support for W ↔ A conversion.
7. Conservative fail-safe behavior for stale/missing P1 data.
8. Startup/deploy preflight so unrestricted charging waits for fresh P1 data after startup.
9. Soft limit, hard limit and controlled ramp-up / ramp-down behavior.
10. Separate DLB logging categories for soft info, status info, warnings and debug output.
11. Separate compatibility path for non-HomeWizard P1 users using the provided adapter.
12. Documentation, visuals and installation guidance focused on the integrated DLB proxy path.

What remains upstream behavior:

- gast777’s multi-Zendure proxy concept;
- general API request/response handling;
- SoC-aware distribution logic;
- standby/mode logic;
- the basic integration path with Gielz1986/Zendure-HA-zenSDK.
