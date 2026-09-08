# DLB logging

DLB v2.6 introduced four independent logging switches so normal control actions, status changes, safety warnings and deep diagnostics can be enabled separately.

Configure them in the main Node-RED settings function:

```javascript
let dynamic_load_balancing_log_soft_info = 1
let dynamic_load_balancing_log_status_info = 0
let dynamic_load_balancing_log_warnings = 1
let dynamic_load_balancing_log_debug = 0
```

## What each switch does

| Setting | Recommended default | Output | Use it for |
|---|---:|---|---|
| `dynamic_load_balancing_log_soft_info` | `1` | `[DLB SOFT]` | Normal soft throttling, recovery/ramping and redistribution events |
| `dynamic_load_balancing_log_status_info` | `0` | `[DLB STATUS]` | Initialization, preflight and DLB state transitions |
| `dynamic_load_balancing_log_warnings` | `1` | `[DLB WARNING]` | Hard protection, stale/missing P1 fail-safe and invalid configuration |
| `dynamic_load_balancing_log_debug` | `0` | `[DLB DEBUG]` | Detailed wanted/previous/target values, eligibility, weights and phase modes |

The design deliberately keeps **safety warnings independent** from informational output. You can therefore run a quiet system while still seeing events that require attention.

## Suggested profiles

### Normal daily use

```javascript
dynamic_load_balancing_log_soft_info = 1
dynamic_load_balancing_log_status_info = 0
dynamic_load_balancing_log_warnings = 1
dynamic_load_balancing_log_debug = 0
```

This shows when DLB actually changes power and always keeps hard/fail-safe warnings visible.

### Quiet / warnings only

```javascript
dynamic_load_balancing_log_soft_info = 0
dynamic_load_balancing_log_status_info = 0
dynamic_load_balancing_log_warnings = 1
dynamic_load_balancing_log_debug = 0
```

### Commissioning or troubleshooting

```javascript
dynamic_load_balancing_log_soft_info = 1
dynamic_load_balancing_log_status_info = 1
dynamic_load_balancing_log_warnings = 1
dynamic_load_balancing_log_debug = 1
```

Do not leave debug enabled unnecessarily; it is intentionally detailed.

## Examples

The exact numbers depend on the live P1 currents, voltage and Zendure limits. The examples below use the real v2.6/v2.6.1 log prefixes and field layout; the numeric values are illustrative.

### One phase approaches the soft limit

```text
[DLB SOFT] active; request=6600W; P1=22.80/8.20/7.90A; budget=350/2400/2400W; applied=350/2400/2400W; Soft phase protection above 23.0A
```

Meaning: L1 has very little charging headroom left, so DLB reduces the Zendure(s) on L1 while keeping the other phases available.

### Blocked watts are moved to phases with spare capacity

```text
[DLB SOFT] active; request=6600W; P1=23.10/6.40/6.10A; budget=0/2400/2400W; applied=0/2400/2400W; Redistributed 1300W across phase groups
```

DLB never moves power blindly: redistribution remains limited by the measured phase budget and each Zendure's charge limit.

### Hard protection

```text
[DLB WARNING] HARD PROTECTION: request=7200W; P1=25.40/9.10/8.80A; budget=0/2400/2400W; applied=0/2400/2400W; Hard phase protection at 25.0A
```

Hard protection is intentionally a warning because the configured emergency boundary has been reached/exceeded.

### P1 data becomes stale

```text
[DLB WARNING] P1 FAILSAFE: request=6600W; P1=22.30/n/a/8.10A; budget=1290/1290/1290W; applied=1290/1290/1290W; P1 current stale/missing; fail-safe 6A
```

The controller does **not** assume missing data means spare capacity. It falls back to the configured safe current.

### Recovery and controlled ramp-up

```text
[DLB STATUS] hard_throttling → ramping; request=6600W; P1=17.10/8.30/8.00A; budget=2400/2400/2400W; applied=250/2400/2400W; Ramp-up waiting for consecutive phase headroom
[DLB SOFT] recovered; request=6600W; P1=15.90/8.20/7.90A; budget=2400/2400/2400W; applied=2200/2200/2200W; normal operation
```

This delayed/stepped restoration is one of the mechanisms added to avoid rapid oscillation when a large household load switches off.

## Relation to the original proposal

The original DLB proposal in [gast777 issue #18](https://github.com/gast777/Zendure-zenSDK-proxy/issues/18) emphasized that the logic should remain inside the proxy, leave Gielz intact, work with HomeWizard P1 by default, provide communication fail-safes, and make ramping/throttling visible in the Node-RED logs. The later DLB versions retained those goals while adding phase mapping, shared phase budgets, live control, startup preflight and the four-channel logging model documented above.
