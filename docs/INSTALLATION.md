# Installation and commissioning

This guide describes the **normal HomeWizard P1 Dongle path**. It follows the current gast777 proxy setup sequence and then adds the DLB-specific steps.

> [!IMPORTANT]
> If your phase current/voltage comes from anything other than the normal HomeWizard P1 Dongle entity set, first use [OTHER-P1-METERS.md](OTHER-P1-METERS.md). Do not mix the adapter procedure into the standard installation.

## A. Upstream proxy prerequisites

- Working Home Assistant + Gielz ZenSDK setup.
- Node-RED installed and running.
- Fixed/stable IP addresses for Node-RED and each Zendure.
- Strong/reliable network connectivity to the Zendures.
- HomeWizard P1 Dongle integrated in Home Assistant.
- Export/backup of your existing Node-RED flows.

The proxy foundations and installation model originate from [gast777/Zendure-zenSDK-proxy](https://github.com/gast777/Zendure-zenSDK-proxy). Check upstream for the latest generic proxy instructions.

## B. Import the DLB proxy

Import:

```text
code/integrated/current/20260801-NL-DLB-v2.6.json
```

Use Node-RED **Menu → Import**. Review settings before deploying.

## C. Configure the Zendures

In `===> Vul hier de Zendure IP adressen in <===`, enter each installed Zendure's fixed local IP address. Leave unused slots empty.

Configure the actual electrical phase of each active device:

```javascript
let zendure_1_phase = "L1"
let zendure_2_phase = "L2"
let zendure_3_phase = "L3"
```

Duplicate phase assignments are supported; all devices on one physical phase share one phase budget.

## D. Verify HomeWizard P1 entities

The standard flow expects:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

If they exist, leave all six DLB P1 Node-RED nodes unchanged.

If they do not exist because you use a different meter/integration, stop this guide and use [OTHER-P1-METERS.md](OTHER-P1-METERS.md).

## E. Review DLB limits and behavior

At minimum review:

- `dynamic_load_balancing_max_phase_current_amp`
- `dynamic_load_balancing_soft_limit_amp`
- `dynamic_load_balancing_failsafe_amp`
- `dynamic_load_balancing_voltage_fallback`
- `dynamic_load_balancing_p1_max_age_sec`
- redistribution enable
- soft ramp-down step
- ramp-up wait, step and interval
- physical Zendure phase mapping

Do not copy electrical limits without checking your own installation.

## F. Choose logging

Recommended daily settings:

```javascript
let dynamic_load_balancing_log_soft_info = 1
let dynamic_load_balancing_log_status_info = 0
let dynamic_load_balancing_log_warnings = 1
let dynamic_load_balancing_log_debug = 0
```

See [DLB-logging.md](DLB-logging.md) for descriptions and example output.

## G. Deploy and verify preflight

Deploy the flow. Fresh P1 current must arrive after start/deploy before unrestricted charging is allowed. This prevents old flow-context data from immediately releasing a large charging command.

## H. Configure Gielz to use the proxy

Following gast777's upstream instructions, set the Zendure address in the Gielz dashboard to the Node-RED proxy, for example:

```text
192.168.x.x:1880/endpoint
```

Then configure Gielz's maximum charge/discharge power for the desired combined installed capacity.

### Node-RED as Home Assistant App

Gast777's current upstream instructions specify:

1. Node-RED App: disable `ssl`.
2. Enable **Show unused optional configuration options**.
3. Enable `leave_front_door_open`.
4. Save and restart Node-RED.
5. Configure Gielz's Zendure IP/address as:

```text
localhost:1880/endpoint
```

## I. Commissioning tests

1. Start with a modest charge request.
2. Confirm normal gast777 SoC distribution is still present.
3. Add a known load to L1 and confirm L1 charging is constrained.
4. Verify redistribution only uses phases with real headroom.
5. Remove the load and observe delayed/stepped ramp-up.
6. Test the hard limit carefully with monitored current; hard protection should reduce immediately.
7. Make P1 current unavailable/stale and verify the fail-safe budget activates.
8. Redeploy while a charge request exists; preflight should hold charging until fresh P1 is received.
9. If multiple Zendures share a phase, verify their **combined** charging remains inside the one phase budget.

Monitor the real P1 phase currents throughout testing.

## J. Optional upstream monitoring

Gast777 provides extra REST sensors/dashboard snippets for monitoring individual devices behind the proxy. Use the current upstream **Monitoring** section rather than duplicating those files here:

https://github.com/gast777/Zendure-zenSDK-proxy#monitoring
