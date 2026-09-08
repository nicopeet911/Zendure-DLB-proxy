# Installation — gast777 proxy foundation + DLB extension

This guide combines two layers:

1. the **base proxy installation** adapted from gast777's upstream documentation; and
2. the **additional DLB configuration** required by this repository.

Authoritative upstream documentation:

https://github.com/gast777/Zendure-zenSDK-proxy#instructions

## A. Base proxy setup

### A1. Requirements

- Current Gielz Zendure Home Assistant zenSDK setup installed.
- Node-RED installed and running.
- Fixed/stable local addresses for the Zendures and Node-RED server.
- Reliable network/Wi-Fi connectivity to every Zendure.
- A backup of the currently working Node-RED flow before changing anything.

### A2. Import the flow into Node-RED

Import:

```text
code/integrated/current/20260801-NL-DLB-v2.6.json
```

Use the Node-RED menu → **Import**. Install any missing node dependencies Node-RED offers.

### A3. Configure Zendure addresses

Open the main proxy configuration node and enter the local IP addresses for the installed Zendures. Leave unused device entries empty.

### A4. Home Assistant App settings for Node-RED

When Node-RED runs as a Home Assistant App on the same machine, the upstream instructions specify:

- SSL disabled
- optional/unused configuration options shown
- `leave_front_door_open` enabled
- save the App configuration
- restart Node-RED

### A5. Point Gielz to the proxy

In the Gielz dashboard Settings tab, set **Zendure IP-address** to the Node-RED proxy rather than a physical Zendure.

Same Home Assistant host:

```text
localhost:1880/endpoint
```

Separate Node-RED host:

```text
IP_ADDRESS:1880/endpoint
```

After this is correct, the normal Gielz sensors should start reading through the proxy.

### A6. Configure combined power limits

Set Gielz **Max Charge Power** and **Max Discharge Power** to the combined capability of the installed system.

Example for identical 2400 W units:

- 2 devices: 4800 W
- 3 devices: 7200 W

Use your actual device limits.

### A7. Optional upstream monitoring

Gast777 provides extra REST sensor YAML and dashboard snippets to expose individual proxy-device values. Follow the current upstream Monitoring section for those auxiliary files rather than keeping potentially stale duplicates here:

https://github.com/gast777/Zendure-zenSDK-proxy#monitoring

## B. DLB-specific setup

### B1. Configure real electrical phases

Set the real physical phase of every Zendure:

```text
zendure_1_phase = "L1" / "L2" / "L3"
zendure_2_phase = "L1" / "L2" / "L3"
zendure_3_phase = "L1" / "L2" / "L3"
```

Duplicate phase assignments are supported by later DLB versions; all devices on one phase share one phase budget.

### B2. Configure P1 current and voltage entities

Canonical development entities:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

Edit the six Home Assistant **Events: state** nodes if your entity IDs differ, or use `code/adapters/zendure_dlb_p1_adapter.yaml` as a mapping example.

### B3. Review limits

Review at minimum:

- hard phase-current limit
- soft phase-current limit
- stale-P1 fail-safe current
- fallback voltage
- P1 maximum age
- ramp-down/ramp-up settings
- redistribution setting
- phase mapping

Do not copy electrical current limits without checking the actual installation.

### B4. Deploy and verify preflight

Deploy the flow and confirm fresh P1 values are arriving. The startup preflight is deliberately conservative and prevents unrestricted charging immediately after Node-RED starts/redeploys without fresh phase-current data.

## C. Commissioning tests

Recommended test sequence:

1. Request a modest multi-device charge and confirm normal SoC-aware distribution.
2. Add a significant load to one phase and verify that DLB reduces the available charging budget on that phase.
3. Keep a phase constrained and verify that the hard/soft behavior prevents the requested charging from exceeding the configured phase budget.
4. Confirm redistribution only uses other phase groups with real spare capacity.
5. Remove the load and verify delayed stepped restoration.
6. Make a P1 input stale/unavailable and verify fail-safe limiting.
7. Reboot/redeploy Node-RED and verify startup preflight again.
8. If multiple Zendures share one phase, confirm their combined target remains within that one phase budget.

Monitor actual P1 phase currents throughout commissioning.
