# DLB architecture

## Purpose

The Dynamic Load Balancing layer protects the available current on each physical grid phase while preserving gast777's normal multi-Zendure behavior as much as possible.

The design principle is: **Gielz/gast777 remains the source of the requested total power and SoC-aware distribution; DLB only constrains or safely reallocates charging when electrical phase capacity requires it.**

## Inputs

The integrated flow consumes Home Assistant state changes for:

- L1/L2/L3 current
- L1/L2/L3 voltage

The current events also drive live recalculation. Voltage is used for converting current headroom to a power budget. If voltage is invalid or missing, the controller falls back to the configured conservative voltage.

## Phase mapping

Each configured Zendure has an independent physical phase assignment (`L1`, `L2` or `L3`). This means the device order no longer has to equal the phase order.

Examples supported by the development line:

- Z1=L1, Z2=L2, Z3=L3
- Z1=L1, Z2=L3, third device unused
- Z1=L1, Z2=L1, third device unused
- Multiple devices on the same phase

Multiple Zendures assigned to one phase share a single phase budget.

## Allocation stages

### 1. Requested distribution

The controller begins with the normal gast777/Gielz requested distribution, including the existing SoC-aware behavior and per-device limits.

### 2. Per-phase budget

For each phase, DLB calculates the usable charging power from measured phase current, configured soft/hard limits and measured/fallback phase voltage.

### 3. Shared-phase limiting

If the sum of the requested targets for all devices on a phase exceeds that phase's available budget, all devices in that phase group are scaled within the one shared budget. This prevents two devices on one phase from each assuming they can use the same spare current.

### 4. Redistribution

When redistribution is enabled, power removed from one constrained phase may be assigned to other phase groups, but only where measured electrical headroom and device capacity permit it.

### 5. Fail-safe

If P1 current information is unavailable or too old, DLB does not assume that the phase is safe. It limits charging to the configured fail-safe current budget per active phase.

### 6. Live control

Fresh P1 current updates trigger a debounced live controller. Only meaningful target changes are sent, and per-device writes are rate-limited.

### 7. Restoration

After throttling, available capacity is not immediately restored at full power. The phase must remain safe for the configured wait period, after which power is increased in configured steps and intervals.

## Soft versus hard limit

The soft limit is the normal operating target. Above this level, DLB can reduce charging gradually using the configured soft ramp-down step.

The hard limit is the protection boundary. When the phase reaches or exceeds the hard limit, DLB prioritizes immediate protection rather than gradual correction.

## Startup/deploy behavior

After a Node-RED start/deploy, the flow waits for fresh P1 information before allowing unrestricted DLB-controlled charging. Startup-only warnings can be suppressed for a grace period, but the safe fallback behavior remains active during that time.

## Logging

v2.6 separates DLB log output into four switches:

- `dynamic_load_balancing_log_soft_info`
- `dynamic_load_balancing_log_status_info`
- `dynamic_load_balancing_log_warnings`
- `dynamic_load_balancing_log_debug`

This keeps hard warnings visible without filling the Node-RED log with normal throttle/restoration status unless explicitly enabled.
