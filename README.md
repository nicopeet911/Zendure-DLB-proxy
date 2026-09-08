# Zendure zenSDK Proxy — Dynamic Load Balancing extension

This repository contains an experimental/extended **Dynamic Load Balancing (DLB)** development line for the Zendure zenSDK Node-RED proxy.

The work started from **gast777's Zendure-zenSDK-proxy**, which provides the multi-Zendure proxy layer used together with the Gielz1986 Zendure Home Assistant zenSDK integration. The original proxy makes two or three Zendure devices behave like one larger virtual device while retaining intelligent SoC-based power distribution.

**Upstream projects**

- gast777 / Zendure-zenSDK-proxy: https://github.com/gast777/Zendure-zenSDK-proxy
- Gielz1986 / Zendure-HA-zenSDK: https://github.com/Gielz1986/Zendure-HA-zenSDK

This repository does **not** replace those projects. It documents and preserves our DLB modifications on top of gast777's proxy.

## What we added

The main goal was to let the proxy continue following the power request from the Gielz automation while preventing Zendure charging from overloading a physical grid phase.

The DLB extension adds:

- Per-phase current protection for a three-phase connection.
- Home Assistant P1 current input using Node-RED **Events: state** nodes instead of REST polling.
- Per-phase voltage input for more accurate W ↔ A conversion, with a conservative fallback voltage when unavailable.
- Configurable mapping of each Zendure to its real physical phase.
- Support for two-Zendure systems and for multiple Zendures sharing the same phase.
- A shared phase budget so multiple devices on one phase cannot double-count available headroom.
- Safe redistribution of blocked requested power to other phases that still have real capacity.
- Startup/deploy preflight protection: fresh P1 data must be available before unrestricted charging is allowed.
- Stale/missing P1 fail-safe limiting.
- Live P1-triggered corrections, so the Zendures can be throttled without waiting for a new Gielz POST request.
- Soft and hard current limits.
- Controlled ramp-down and delayed stepped ramp-up to avoid unnecessary oscillation.
- Communication-error handling and cooldown behavior.
- DLB-specific logging controls so routine information, status information, warnings and debug output can be enabled separately.

## Current files

### Latest recovered build

`code/integrated/current/20260801-NL-DLB-v2.6.json`

This is the latest recovered integrated build. It is based on gast777's **20260801** Dutch proxy and contains the reorganized DLB configuration/logging section.

Important status distinction:

- **v2.5** was explicitly confirmed working during our testing.
- **v2.6** is the latest recovered build and adds the final logging/configuration cleanup; it was not separately recorded as field-validated after that last layout change.

For that reason, keep the v2.5 archive available as a rollback when first testing v2.6.

### Archive

`code/integrated/archive/` contains recovered development snapshots from the DLB evolution. These are kept for traceability and comparison, not because every historical build should be deployed.

### Standalone experiment

`code/standalone-experimental/` contains the earlier attempt to separate DLB from the gast777 proxy. This was deliberately a **TEST** package. The integrated proxy remained the preferred/working path.

### Adapters

`code/adapters/` contains:

- `zendure_dlb_p1_adapter.yaml` — Home Assistant adapter example for mapping other P1 sensors to the canonical DLB entity names.
- `apply_gast777_dlb_adapter.py` — experimental helper used during the standalone-adapter work.

## Default DLB configuration in v2.6

The current recovered flow uses these defaults in the main Zendure configuration function:

| Setting | Default | Purpose |
|---|---:|---|
| DLB enabled | `1` | Enables phase protection |
| Redistribution | `1` | Redistribute blocked watts to other phase groups when possible |
| Hard phase limit | `25 A` | Emergency/main-fuse phase limit |
| Soft phase limit | `23 A` | Normal operating target before the hard limit |
| Fail-safe current | `6 A` | Maximum charging current per active phase with stale/missing P1 data |
| Voltage fallback | `215 V` | Conservative W ↔ A conversion fallback |
| P1 max age | `15 s` | Older data activates fail-safe behavior |
| Startup warning grace | `30 s` | Suppresses startup-only warnings while retaining safe limiting |
| Ramp-up wait | `20 s` | Stable headroom required before restoration starts |
| Ramp-up step | `250 W` | Maximum power restoration per affected phase step |
| Ramp-up interval | `10 s` | Minimum time between restoration steps |
| Soft ramp-down step | `500 W` | Maximum step while above soft but below hard limit |
| Live minimum change | `50 W` | Avoids unnecessary small Zendure writes |

These are configuration defaults, not universal recommendations. Set phase mappings and limits for the actual electrical installation.

## Home Assistant P1 entities

The DLB development used these canonical entity names:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

If your P1 integration uses different entity IDs, change the six Home Assistant `Events: state` nodes in the Node-RED flow or use the adapter example under `code/adapters/`.

## Safety model

The DLB controller is a protective limiter layered on top of gast777/Gielz power allocation. It is not a replacement for correctly sized wiring, circuit breakers or grid connection protection.

At a high level:

1. Gielz/gast777 determines the requested charging distribution.
2. DLB reads the latest current and voltage for L1/L2/L3.
3. Each physical phase receives one shared safe power budget.
4. Zendure targets on an overloaded/restricted phase are reduced.
5. If enabled, unused requested power is reassigned only to phase groups with measured spare capacity.
6. When P1 information is stale or missing, the fail-safe budget is applied rather than blindly continuing full charging.
7. After a restriction clears, power is restored in controlled steps.

See `docs/DLB-architecture.md` for more detail.

## Attribution and license

This work is a modification/extension of **gast777/Zendure-zenSDK-proxy**, originally by Casper Rijnders. The upstream repository uses a custom non-commercial license and requires redistributed modified versions to include the full upstream license text, clearly identify modifications, and remain non-commercial.

Upstream license: https://github.com/gast777/Zendure-zenSDK-proxy/blob/main/LICENSE

**Do not publish/distribute the modified full proxy flows from this package until the complete upstream LICENSE file has been copied into the repository unchanged.** See `LICENSE-NOTICE.md`.

## Disclaimer

This is community-developed automation for residential energy equipment. Test changes carefully, monitor real phase currents during commissioning, keep normal electrical protections in place, and retain a known-good rollback flow.
