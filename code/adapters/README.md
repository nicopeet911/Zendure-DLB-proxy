# P1 adapters for Zendure DLB

## Why this exists

The current integrated DLB flow is intentionally shipped with one stable P1 sensor interface. It is preconfigured for the six Home Assistant entity IDs used by the **HomeWizard P1** setup:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

With a three-phase HomeWizard P1 setup exposing these names, no P1-specific changes are required in Node-RED.

The DLB algorithm itself is **not HomeWizard-specific**. `zendure_dlb_p1_adapter.yaml` lets any suitable Home Assistant meter/integration present the same six names to DLB. This keeps the Node-RED flow standard and makes later DLB updates easier to install.

## What the YAML adapter does

The adapter creates six Home Assistant template sensors with the canonical DLB names. Each one simply reads from a source entity you select. Your original P1/DSMR/ESPHome/meter entities remain unchanged.

Your meter → **adapter template sensor** → canonical `sensor.p1_meter_*` name → **Node-RED DLB**

## Recommended installation

### 1. Copy the adapter

Copy:

```text
code/adapters/zendure_dlb_p1_adapter.yaml
```

to your Home Assistant configuration directory as:

```text
/config/packages/zendure_dlb_p1_adapter.yaml
```

### 2. Enable Home Assistant packages

In `/config/configuration.yaml`, packages must be enabled:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

If `configuration.yaml` already contains a `homeassistant:` section, add the `packages:` entry beneath that existing section. Do **not** add a second `homeassistant:` key.

If you already use Home Assistant packages, no configuration change is needed; just place the adapter file in the packages directory.

### 3. Map your six source entities

Open the adapter and find the six comments:

```text
<<< CHANGE THIS SOURCE ENTITY ID >>>
```

Replace the placeholders with your actual Home Assistant entities:

| Adapter input | Required source | Unit |
|---|---|---|
| L1 current | phase 1 net/import current | A |
| L2 current | phase 2 net/import current | A |
| L3 current | phase 3 net/import current | A |
| L1 voltage | phase 1 voltage | V |
| L2 voltage | phase 2 voltage | V |
| L3 voltage | phase 3 voltage | V |

Example only:

```yaml
availability: >
  {{ has_value('sensor.my_meter_l1_current') }}
state: >
  {{ states('sensor.my_meter_l1_current') | float }}
```

Do that for all six inputs. Do not change the template sensor names or `unique_id` values unless you deliberately want to change the DLB interface.

### 4. Check and restart Home Assistant

Run Home Assistant's configuration check, then restart Home Assistant.

After restart, verify these entities exist:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

All six should have fresh numeric values.

### 5. Verify units and current direction

Before relying on DLB:

- current must be in **A**;
- voltage must be in **V**;
- adding a known load to L1 should make L1's positive import/load current increase, and likewise for L2/L3.

If your integration uses the opposite sign convention, adapt the template calculation before commissioning DLB. For example, a source that reports import as negative may require multiplying the source value by `-1`.

### 6. Leave Node-RED unchanged

The important benefit of the adapter is that you do **not** need to customize the six P1 Events: state nodes in every new DLB flow version. Keep them on the canonical `sensor.p1_meter_*` entities.

## Alternative: edit Node-RED directly

It is technically possible to edit all six P1 Events: state nodes in Node-RED to point directly at another integration. The adapter is preferred because it keeps the distributed DLB JSON identical to the tested HomeWizard-based build and makes future upgrades easier.

## Files in this folder

- `zendure_dlb_p1_adapter.yaml` — recommended Home Assistant sensor-name adapter.
- `apply_gast777_dlb_adapter.py` — historical/experimental helper from the standalone-adapter development work; it is **not required** for the normal integrated v2.6 installation.
