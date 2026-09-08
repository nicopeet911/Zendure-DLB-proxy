# Using DLB with another P1 / three-phase meter

> [!IMPORTANT]
> **This page is only for users who are NOT using the normal HomeWizard Wi-Fi P1 Meter / P1 Dongle entity set.**
>
> If you use a HomeWizard P1 Dongle and Home Assistant already has `sensor.p1_meter_current_phase_1/2/3` and `sensor.p1_meter_voltage_phase_1/2/3`, stop here. You do **not** need the adapter. Return to the [main README](../README.md).

The ready-to-import DLB flow intentionally uses one stable P1 interface. HomeWizard P1 is the default because that is the setup used during the original development and testing. For another meter, the adapter makes its Home Assistant entities look like the same interface to Node-RED.

## What the adapter does

`code/adapters/zendure_dlb_p1_adapter.yaml` creates these six canonical entities:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

Your original P1/meter entities remain untouched. The Node-RED flow can therefore stay on its supplied HomeWizard-style entity names.

## The `last_reported` problem and why adapter v1.1 is different

DLB does more than read the current value. It must also know whether the meter is **still alive when the current happens to remain unchanged**.

DLB v2.3 introduced a 5-second targeted Home Assistant state read and uses the current entity's `last_reported` timestamp as the preferred freshness proof. This is important because relying only on `state_changed` events can make an unchanged integer/rounded current look stale.

The first adapter was a plain template mirror. That created a subtle problem:

```text
physical meter sensor
        ↓
Home Assistant template adapter
        ↓
DLB freshness check
```

The adapter's own `last_reported` timestamp is not necessarily the physical meter's reporting heartbeat. A user could therefore have a healthy source meter while DLB saw the mirror as stale and entered the conservative P1 fail-safe.

### Fix in DLB v2.6.1 + adapter v1.1

Each adapter **current** sensor now carries:

```yaml
attributes:
  dlb_source_entity_id: "sensor.your_real_l1_current_sensor"
```

When DLB sees that attribute, it keeps using the canonical adapter sensor for the normal Node-RED `Events: state` path, but its 5-second freshness read follows the **original source entity**:

```text
normal live updates:
source meter → adapter entity → Node-RED Events: state → DLB

freshness verification every 5 s:
DLB → Home Assistant → ORIGINAL source meter entity → last_reported
```

That is the important difference. The fail-safe is not disabled or bypassed; it is pointed at the correct heartbeat source.

## Compatibility requirement

The original current source entity must itself have a meaningful `last_reported` value when its integration writes a measurement to Home Assistant. Home Assistant provides `last_reported` specifically to represent state writes even when state/attributes did not change, but an integration still has to actually write/report the value to Home Assistant.

Some integrations may suppress identical reports before they reach Home Assistant. In that case no generic adapter can safely invent a heartbeat. **Do not use a periodic fake timestamp to keep DLB alive**, because that would hide a genuinely dead meter.

If your source integration has this behavior, use a real source-provided heartbeat/timestamp/counter entity if available, or configure that integration so repeated measurements are reported into Home Assistant.

## Installation

### 1. Use the source-aware DLB v2.6.1 compatibility build

Use:

```text
code/integrated/current/20260801-NL-DLB-v2.6.1.json
```

The normal HomeWizard `v2.6` build does not understand `dlb_source_entity_id` and will still poll the adapter mirror for freshness. `v2.6.1` is therefore required for this adapter path.

> [!WARNING]
> `v2.6.1` is a narrowly scoped compatibility fix created for the non-HomeWizard adapter path. Its JSON and embedded Node-RED function JavaScript have been validated, but this new adapter/source-freshness combination still requires real-world field testing before it should be treated as equally proven as the HomeWizard v2.6 base.

### 2. Install the adapter as a Home Assistant package

Copy:

```text
code/adapters/zendure_dlb_p1_adapter.yaml
```

to:

```text
/config/packages/zendure_dlb_p1_adapter.yaml
```

If packages are not enabled yet, add this under your existing `homeassistant:` section in `configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Do not create a second `homeassistant:` block.

### 3. Replace exactly six source entity IDs

The adapter is trigger-based so each real source entity is configured **once**. Search the YAML for:

```text
<<< CHANGE THIS SOURCE ENTITY ID >>>
```

There are six matches total:

1. L1 current
2. L2 current
3. L3 current
4. L1 voltage
5. L2 voltage
6. L3 voltage

Example for L1 current:

```yaml
- triggers:
    - trigger: state
      entity_id: sensor.my_meter_l1_current
  sensor:
    - name: "P1 Meter Current Phase 1"
      default_entity_id: sensor.p1_meter_current_phase_1
      unique_id: zendure_dlb_adapter_p1_meter_current_phase_1
      unit_of_measurement: "A"
      device_class: current
      state_class: measurement
      availability: >
        {{ trigger.to_state is not none
           and trigger.to_state.state not in ['unknown', 'unavailable', '']
           and is_number(trigger.to_state.state) }}
      state: "{{ trigger.to_state.state | float(0) }}"
      attributes:
        dlb_source_entity_id: "{{ trigger.entity_id }}"
```

You do **not** manually edit `dlb_source_entity_id`; the adapter fills it automatically from the trigger entity you selected.

### 4. Restart Home Assistant and verify

After checking the configuration and restarting Home Assistant, confirm all six canonical entities exist.

For each current adapter sensor, open **Developer Tools → States** and verify the attribute is present:

```text
dlb_source_entity_id: sensor.<your real source entity>
```

### 5. Check units, sign and phase order

Before enabling significant charging power:

- current must be in **A**;
- voltage must be in **V**;
- adding load on L1 must increase the L1 current, not L2/L3;
- more grid import/load must move current in the **positive** direction expected by DLB.

### 6. Check source freshness

Watch the original current source in Home Assistant. Its `last_reported` should continue to advance while the meter is reporting, including periods where the numeric current is unchanged.

Then deploy Node-RED. The DLB P1 status should remain reported/healthy instead of falling into fail-safe simply because the current value is stable.

## Troubleshooting

### DLB immediately says P1 is stale

Check these in order:

1. Does the canonical adapter current entity exist?
2. Does it have the correct `dlb_source_entity_id` attribute?
3. Does that attribute point to the **original** meter entity, not back to the adapter?
4. Does the original source have a recent `last_reported`?
5. Is `dynamic_load_balancing_p1_max_age_sec` large enough for the real source update interval?

### Adapter updates, but source `last_reported` does not

That is a source-integration behavior, not something the template adapter can safely repair. Do not create a periodic fake heartbeat. Look for a real telegram timestamp, packet counter, update timestamp or a `force_update`/always-report option in the source integration.

### Current is negative while importing

Do not enable DLB until the sign convention is corrected. The current adapter deliberately does not guess whether a vendor's signed current needs inversion.

## Why keep the adapter separate?

Keeping this compatibility layer outside the main flow has two benefits:

1. HomeWizard P1 Dongle users keep the simplest, tested path with no extra configuration.
2. Other integrations can be adapted without editing the six DLB Node-RED P1 nodes or forking the DLB controller itself.
