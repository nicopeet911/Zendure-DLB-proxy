# Integrated DLB installation notes

These notes cover the integrated DLB flow. Start from the normal gast777/Gielz setup and read the upstream instructions first:

https://github.com/gast777/Zendure-zenSDK-proxy

## 1. Keep a rollback

Export the currently working Node-RED proxy before importing a DLB build.

The last build explicitly confirmed working during development was the v2.5 line. The latest recovered v2.6 build adds the final logging/settings cleanup and should be commissioned while monitoring phase currents.

## 2. Import the flow

Import the desired JSON from `code/integrated/` into Node-RED.

## 3. Configure Zendure IP addresses

In the main configuration function, set the IP addresses for the active Zendures exactly as required by the upstream gast777 proxy. Leave unused device slots empty.

## 4. Configure the real electrical phase mapping

Set:

```text
zendure_1_phase = "L1" / "L2" / "L3"
zendure_2_phase = "L1" / "L2" / "L3"
zendure_3_phase = "L1" / "L2" / "L3"
```

Use the actual physical wiring, not merely the device number.

Duplicate phase assignments are allowed in the later DLB versions; devices on the same phase share one phase budget.

## 5. Connect the P1 entities

Configure the six Home Assistant `Events: state` nodes for phase current and voltage.

Canonical names used during development:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

If your entities differ, edit those nodes or use `code/adapters/zendure_dlb_p1_adapter.yaml` as a mapping example.

## 6. Review DLB limits

Do not copy current limits blindly. Review at minimum:

- hard phase-current limit
- soft phase-current limit
- stale-P1 fail-safe current
- fallback voltage
- P1 maximum age
- ramp-down/ramp-up behavior
- redistribution setting

## 7. Deploy with DLB enabled

After deploy, confirm that fresh P1 values are visible inside Node-RED. The startup preflight/fail-safe behavior is intentionally conservative until usable current data has arrived.

## 8. Commissioning tests

Recommended tests from the development process:

1. Request a normal multi-device charge and confirm the expected SoC-aware split.
2. Add a significant load to one phase and verify that only the available phase budget is used.
3. Keep the constrained phase near/above the limit and confirm that DLB throttles it.
4. Confirm that redistribution uses other phases only when they have spare capacity.
5. Remove the added load and verify delayed stepped restoration.
6. Temporarily make one or more P1 inputs stale/unavailable and verify fail-safe limiting.
7. Reboot/redeploy Node-RED and verify that unrestricted power is not applied before fresh P1 data arrives.
8. If multiple Zendures share a phase, confirm their combined target remains inside that one phase budget.

Monitor actual P1 phase currents throughout commissioning.
