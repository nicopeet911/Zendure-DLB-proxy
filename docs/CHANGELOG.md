# Recovered DLB development history

This changelog summarizes the recovered development line. It is not the upstream gast777 changelog.

## 20260801-NL-DLB-v2.6.1

Compatibility bugfix on top of v2.6.

- Fixes non-HomeWizard adapter freshness handling.
- Adapter current entities can expose `dlb_source_entity_id`.
- The 5-second Home Assistant freshness read follows the original physical meter current entity and uses its `last_reported`, rather than trusting the template mirror timestamp.
- HomeWizard P1 Dongle behavior is unchanged because the canonical HomeWizard entity remains the freshness source when no adapter attribute is present.
- No changes to phase allocation, redistribution, ramping or discharge behavior.

Status: source-aware non-HomeWizard compatibility candidate; code/syntax validated, not yet field-validated on the affected third-party meter setup.

## 20260801-NL-DLB-v2.6

Latest recovered integrated build based on gast777's 20260801 proxy.

- Retains integrated per-phase DLB behavior from v2.5.
- Adds four separate DLB logging switches: soft information, status information, warnings and debug.
- Reorganizes the configuration so operational DLB settings remain together and the DLB logging section follows them cleanly.
- Keeps hard protection/fail-safe warnings independently selectable from routine informational messages.

Status: latest recovered build; not separately recorded as field-validated after the final settings/logging layout correction.

## 20260801-NL-DLB-v2.5

Port of the accepted integrated DLB behavior onto gast777's 20260801 proxy revision.

Status: development migration build.

## 20260701-NL-DLB-v2.5 / soft-limit-final

Main working baseline during testing.

Key behavior accumulated in this line included:

- fresh-P1 startup/deploy preflight
- soft and hard phase limits
- safe stale-P1 behavior
- live phase control
- controlled restoration
- redistribution across phases with actual headroom
- phase-voltage input
- flexible phase mapping
- multiple Zendures sharing one phase budget

Status: v2.5 was explicitly confirmed working during development.

## v2.0

- Added support for multiple Zendures on the same physical phase.
- Changed allocation from one-device/one-phase assumptions to shared physical phase budgets.

## v1.9

- Corrected two-Zendure scenarios where devices may be on non-consecutive phases (for example L1 + L3).

## Earlier v2.4 snapshots

Recovered intermediate settings/behavior iterations are retained under `code/integrated/archive/` for traceability.

## Standalone v1.0 TEST

Experimental attempt to separate the DLB engine from the gast777 proxy and connect it through an adapter. Includes a standalone flow, patched proxy test build and adapter tooling.

Status: TEST only. The integrated DLB proxy remained the preferred path.
