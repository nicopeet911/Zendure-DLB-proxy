# Installation and commissioning

This page gives the more detailed installation steps for the integrated DLB proxy.

> [!IMPORTANT]
> The normal path is for **HomeWizard P1 Dongle** users with the standard `sensor.p1_meter_*` phase current/voltage entities.
>
> If you use another P1 / DSMR / three-phase meter, go to [OTHER-P1-METERS.md](OTHER-P1-METERS.md).

## 1. Import the correct flow

- **HomeWizard P1 Dongle:** `code/integrated/current/20260801-NL-DLB-v2.6.json`
- **Other P1 meters:** `code/integrated/current/20260801-NL-DLB-v2.6.1.json` together with the adapter guide

## 2. Configure Zendure IP addresses

Open the node:

```text
===> Vul hier de Zendure IP adressen in <===
```

Fill in the fixed IP addresses of your Zendure devices and leave unused slots empty.

## 3. Configure the real electrical phases

Set the actual phase of each active Zendure:

```javascript
let zendure_1_phase = "L1"
let zendure_2_phase = "L2"
let zendure_3_phase = "L3"
```

These must match the real wiring. Multiple Zendures may share one phase.

## 4. Review the key DLB settings

Important defaults:

```javascript
let dynamic_load_balancing_max_phase_current_amp = 25
let dynamic_load_balancing_soft_limit_amp = 23.0
let dynamic_load_balancing_failsafe_amp = 6
let dynamic_load_balancing_p1_max_age_sec = 15
let dynamic_load_balancing_ramp_up_wait_sec = 20
```

## 5. Recommended EV-priority setup for a Dutch 3×25A home

If your EV charger has its own load balancing, a simple safe setup is:

- set the **battery DLB hard limit** to **25A**;
- set the **battery DLB soft limit** to **23A**;
- set the **EV charger’s own load-balancing limit** to **24–25A**.

This lets the EV charger keep priority while the Zendures back off first.

## 6. Point Gielz to the proxy

In Home Assistant / Gielz, set the Zendure IP address field to your Node-RED proxy, for example:

```text
192.168.x.x:1880/endpoint
```

Set the maximum charge/discharge power to the combined capability of your installed Zendures.

## 7. Commission carefully

Start modestly and verify:

1. P1 current and voltage values are updating correctly.
2. Adding load to a phase reduces Zendure charging on that phase.
3. Other phases only take over when there is real spare capacity.
4. Removing the load causes controlled ramp-up.
5. Missing/stale P1 data activates the configured fail-safe.
6. After a Node-RED restart, startup preflight holds charging until fresh P1 data arrives.

## 8. Watch Node-RED logs during testing

Recommended commissioning profile:

```javascript
let dynamic_load_balancing_log_soft_info = 1
let dynamic_load_balancing_log_status_info = 1
let dynamic_load_balancing_log_warnings = 1
let dynamic_load_balancing_log_debug = 0
```

After successful testing, many users prefer to turn `status_info` back off.
