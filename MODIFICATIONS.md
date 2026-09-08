# Modifications relative to gast777/Zendure-zenSDK-proxy

Upstream: https://github.com/gast777/Zendure-zenSDK-proxy

This repository preserves a modified development line of the Dutch Node-RED proxy. The modifications are focused on Dynamic Load Balancing for grid-phase current protection.

Major modifications include:

1. Home Assistant phase-current and phase-voltage inputs for DLB.
2. Per-device physical phase mapping independent of device number.
3. One shared power budget per physical phase.
4. Support for two-device layouts and multiple Zendures on the same phase.
5. Per-phase soft and hard current protection.
6. Conservative fallback voltage and stale/missing-P1 fail-safe behavior.
7. Startup/deploy preflight requiring fresh P1 information before unrestricted operation.
8. Safe redistribution of blocked power to other physical phases with measured capacity.
9. P1-triggered live corrections and write debouncing/rate limiting.
10. Controlled soft ramp-down and delayed stepped ramp-up.
11. Additional DLB logging/status handling and, in v2.6, separate log-category switches.
12. Experimental standalone DLB/adapter work retained separately and clearly marked TEST.

The original gast777 proxy remains the foundation for the integrated flow. Upstream functionality, API proxy behavior and SoC-aware multi-device distribution were intentionally preserved rather than reimplemented from scratch.
