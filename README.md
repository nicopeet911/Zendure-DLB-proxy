<p align="center">
  <img src="assets/dlb-banner.svg" alt="Zendure zenSDK Proxy Dynamic Load Balancing" width="100%">
</p>

<p align="center">
  <a href="https://github.com/gast777/Zendure-zenSDK-proxy"><img alt="Based on gast777 proxy" src="https://img.shields.io/badge/upstream-gast777%2FZendure--zenSDK--proxy-181717?logo=github"></a>
  <a href="https://github.com/Gielz1986/Zendure-HA-zenSDK"><img alt="Home Assistant integration" src="https://img.shields.io/badge/Home%20Assistant-Gielz%20zenSDK-41BDF5?logo=homeassistant&logoColor=white"></a>
  <img alt="Node-RED" src="https://img.shields.io/badge/Node--RED-DLB%20v2.6-8F0000?logo=nodered&logoColor=white">
  <img alt="HomeWizard P1 ready" src="https://img.shields.io/badge/P1-HomeWizard%20ready-00AEEF">
  <img alt="Other P1 adapters supported" src="https://img.shields.io/badge/P1-other%20HA%20meters%20via%20adapter-5C6BC0">
  <img alt="Non-commercial license" src="https://img.shields.io/badge/license-non--commercial-orange">
</p>

# Zendure zenSDK Proxy — Dynamic Load Balancing extension

This repository preserves our **Dynamic Load Balancing (DLB)** development on top of **[gast777/Zendure-zenSDK-proxy](https://github.com/gast777/Zendure-zenSDK-proxy)** for use with **[Gielz1986/Zendure-HA-zenSDK](https://github.com/Gielz1986/Zendure-HA-zenSDK)**.

The upstream proxy solves the multi-device problem: Home Assistant talks to one Node-RED proxy, while that proxy controls up to three Zendure devices as one virtual battery system and performs SoC-aware power distribution. Our extension keeps that behavior and adds **per-phase electrical protection** around charging.

> **Credit:** the proxy foundation, multi-Zendure abstraction and SoC distribution are gast777's work. This repository documents and distributes modified non-commercial builds with DLB added on top. See [UPSTREAM.md](UPSTREAM.md), [MODIFICATIONS.md](MODIFICATIONS.md) and [LICENSE](LICENSE).

<p align="center">
  <img src="assets/system-overview.svg" alt="System architecture: Home Assistant, Node-RED proxy, P1 feedback and Zendure devices" width="100%">
</p>

## What this project adds

The objective is simple: **continue following the charge request from Gielz/gast777 as closely as possible, without allowing Zendure charging to overload a physical grid phase.**

DLB adds:

- Per-phase current protection for L1, L2 and L3.
- Home Assistant P1 input through Node-RED **Events: state** nodes.
- Per-phase voltage feedback for better W ↔ A calculations, with a conservative fallback voltage.
- Configurable mapping of each Zendure to its real electrical phase.
- Support for two-device systems and multiple Zendures on the same phase.
- One shared phase budget per physical phase, preventing double-counting of available headroom.
- Redistribution of blocked requested watts only toward phases that actually have spare capacity.
- Startup/deploy preflight protection: fresh P1 data is required before unrestricted charging is allowed.
- Stale/missing P1 fail-safe limiting.
- Live P1-triggered throttling instead of waiting for the next Gielz power command.
- Soft and hard current limits.
- Controlled ramp-down and delayed stepped ramp-up.
- Communication-error handling and cooldown behavior.
- Four independent DLB logging switches in v2.6: soft actions, status/configuration, safety warnings and technical debug.

## P1 compatibility: HomeWizard by default

The **base/current DLB flow is preconfigured for a three-phase HomeWizard P1 Meter / P1 dongle in Home Assistant**. It listens to these six entity IDs:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

If your HomeWizard integration exposes those entity IDs unchanged, **no P1 mapping changes are needed in Node-RED**: import the current flow, configure the Zendures and DLB settings, and the P1 inputs are already wired correctly.

| P1 source in Home Assistant | What to do |
|---|---|
| **HomeWizard P1** with the six entity IDs above | Works with the base flow **out of the box** |
| HomeWizard sensors that you manually renamed | Use the adapter below, or restore the canonical names |
| Another P1/DSMR/ESPHome/meter integration | Use `code/adapters/zendure_dlb_p1_adapter.yaml` to create the six canonical DLB entities |

> The DLB logic does not depend on the HomeWizard hardware itself. HomeWizard is simply the **default sensor interface** used by the ready-to-import flow. The included Home Assistant adapter lets another compatible three-phase meter present the same six sensor names to DLB.

### Using another P1 meter: the included Home Assistant adapter

Use:

```text
code/adapters/zendure_dlb_p1_adapter.yaml
```

The adapter creates the six canonical `sensor.p1_meter_...` entities expected by Node-RED while leaving your original meter sensors untouched. The recommended setup is:

1. In Home Assistant, create `/config/packages/` if you do not already use a packages directory.
2. Copy `zendure_dlb_p1_adapter.yaml` into `/config/packages/`.
3. Make sure packages are enabled in `configuration.yaml`:

   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```

   If you already have a `homeassistant:` section, add only the `packages:` line below the existing section; do **not** create a second `homeassistant:` block.
4. Open `zendure_dlb_p1_adapter.yaml` and replace only the six placeholders marked `<<< CHANGE THIS SOURCE ENTITY ID >>>` with your real Home Assistant sensors for L1/L2/L3 current and voltage.
5. Check the Home Assistant configuration and restart Home Assistant.
6. Confirm that the six canonical entities listed above now exist and update normally.
7. Verify the current direction before enabling high-power DLB operation: adding a known load to a phase should make that phase's reported import/load current increase in the positive direction.
8. **Do not change the six DLB Events: state nodes in Node-RED.** They can keep listening to the canonical HomeWizard-style entity IDs because the adapter now provides them.

For a fuller adapter walkthrough, see [`code/adapters/README.md`](code/adapters/README.md).

## How the control path works

```mermaid
flowchart LR
    HA[Home Assistant / Gielz] -->|requested total power| PROXY[gast777 Node-RED proxy]
    PROXY --> SOC[SoC-aware device distribution]
    SOC --> DLB[DLB phase limiter]
    P1[HomeWizard P1 by default\nor HA adapter\nL1/L2/L3 current + voltage] --> DLB
    DLB --> Z1[Zendure 1]
    DLB --> Z2[Zendure 2]
    DLB --> Z3[Zendure 3]
    DLB -->|blocked watts when safe| REALLOC[redistribute to another phase]
    REALLOC --> DLB
```

DLB only adjusts **AC charging `inputLimit`**. The upstream discharge logic is intentionally left unchanged.

---

# Installation

The base proxy installation below is **adapted from gast777's current upstream instructions** and then extended with the extra DLB steps required by this repository. For the authoritative upstream proxy instructions, see [gast777/Zendure-zenSDK-proxy](https://github.com/gast777/Zendure-zenSDK-proxy#instructions).

## Requirements before you start

For the upstream proxy setup, make sure:

- Home Assistant already has the current Gielz ZenSDK setup installed.
- Node-RED is installed and running.
- Each Zendure and the Node-RED host has a stable/fixed IP address.
- The Zendure devices are reachable over the local network and have strong Wi-Fi/network connectivity.
- You keep a backup/export of your currently working Node-RED flow before replacing anything.

For DLB you additionally need **live phase current data for L1/L2/L3** from Home Assistant. The current flow is preconfigured for the HomeWizard P1 entity names shown above, including L1/L2/L3 voltage. If you use another meter/integration, install the included adapter first so it exposes the same six canonical entities.

## 1. Import the Node-RED proxy flow

Use the current integrated flow:

```text
code/integrated/current/20260801-NL-DLB-v2.6.json
```

In Node-RED:

1. Open the menu in the upper-right corner.
2. Select **Import**.
3. Import the JSON flow.
4. If Node-RED offers to install missing nodes, install the required dependencies.
5. Do **not** deploy yet until you have reviewed the configuration below.

## 2. Configure the Zendure IP addresses

Open the main configuration node in the imported flow — the same configuration area used by gast777's proxy — and enter the local IP address for each Zendure you actually use.

Leave unused Zendure slots empty.

Example conceptually:

```text
Zendure 1 → 192.168.x.x
Zendure 2 → 192.168.x.x
Zendure 3 → 192.168.x.x
```

The exact addresses must match your own network.

## 3. Configure the physical phase mapping

This is the important DLB addition. Set the phase for each installed Zendure according to the **actual electrical wiring**:

```text
zendure_1_phase = "L1" / "L2" / "L3"
zendure_2_phase = "L1" / "L2" / "L3"
zendure_3_phase = "L1" / "L2" / "L3"
```

Do not assume Zendure 1 = L1 unless that is how it is physically connected.

Later DLB versions also allow more than one Zendure on the same phase. Those devices then share one physical phase budget.

## 4. Connect the P1 phase sensors

### HomeWizard P1 — default / out-of-the-box path

The base flow is already configured to listen to the standard sensor interface used for our **HomeWizard P1** setup:

```text
sensor.p1_meter_current_phase_1
sensor.p1_meter_current_phase_2
sensor.p1_meter_current_phase_3
sensor.p1_meter_voltage_phase_1
sensor.p1_meter_voltage_phase_2
sensor.p1_meter_voltage_phase_3
```

If those six entities exist in Home Assistant, **leave the Node-RED P1 Events: state nodes exactly as supplied**. No P1-specific Node-RED editing is required.

### Other P1 meters/integrations — adapter path

If your meter uses different entity IDs, the preferred method is **not** to rewrite the DLB flow. Use:

```text
code/adapters/zendure_dlb_p1_adapter.yaml
```

That Home Assistant template adapter maps your real current/voltage entities to the six canonical names above. Replace only the six marked source entity IDs, install it as a Home Assistant package, restart Home Assistant, verify the new entities, and keep the Node-RED flow unchanged. See [P1 compatibility](#p1-compatibility-homewizard-by-default) and [`code/adapters/README.md`](code/adapters/README.md) for the complete procedure.

## 5. Review the DLB limits

The recovered v2.6 defaults are:

| Setting | Default | Function |
|---|---:|---|
| DLB enabled | `1` | Enables phase protection |
| Redistribution | `1` | Uses spare capacity on other phases when possible |
| Hard phase limit | `25 A` | Emergency/main phase limit |
| Soft phase limit | `23 A` | Normal operating target |
| Fail-safe current | `6 A` | Limit when P1 is stale/missing |
| Voltage fallback | `215 V` | Conservative conversion fallback |
| P1 max age | `15 s` | Older data is considered stale |
| Ramp-up wait | `20 s` | Stable headroom needed before restoration |
| Ramp-up step | `250 W` | Restore power gradually |
| Ramp-up interval | `10 s` | Minimum interval between restore steps |
| Soft ramp-down step | `500 W` | Reduction step above soft limit |
| Live minimum change | `50 W` | Suppresses unnecessary small writes |

These are **project defaults, not universal electrical recommendations**. Set them for your own installation and protective devices.

## 6. Special setup when Node-RED runs as a Home Assistant App

Gast777's upstream instructions require the following Node-RED App configuration when Node-RED runs on the same Home Assistant host:

1. Disable **SSL** for the Node-RED App.
2. Show the unused/optional configuration options.
3. Enable `leave_front_door_open`.
4. Save the App configuration.
5. Restart Node-RED.

Then the Gielz **Zendure IP-address** should point to:

```text
localhost:1880/endpoint
```

If Node-RED runs elsewhere on your LAN, use that host's address and port instead, normally in the form:

```text
IP_ADDRESS:1880/endpoint
```

## 7. Point Gielz/Home Assistant at the proxy

On the Gielz Home Assistant dashboard, open the **Settings** tab and change the **Zendure IP-address** from a physical Zendure to the Node-RED proxy endpoint.

Once the endpoint is correct, the Gielz sensors should start receiving data through the proxy.

## 8. Set total charge/discharge capacity in Gielz

In the same Gielz Settings area, set **Max Charge Power** and **Max Discharge Power** for the combined virtual system.

Gast777 gives these examples for equal 2400 W devices:

- 2 devices → up to `4800 W`
- 3 devices → up to `7200 W`

Use the real limits of the hardware you have installed. DLB then applies an additional per-phase safety budget on top of the requested charge power.

## 9. Deploy and verify P1 preflight

Deploy the flow in Node-RED.

Before testing high charge power, confirm that the flow is receiving fresh current values for all three phases. v2.6 intentionally starts conservatively: it will not immediately apply an unrestricted charging request after deploy/restart until fresh P1 data has arrived.

## 10. First commissioning test

A safe sequence is:

1. Start with a modest charge request.
2. Confirm that gast777's normal SoC-aware distribution still behaves correctly.
3. Add a meaningful load to one physical phase.
4. Confirm that DLB reduces Zendure charging on that constrained phase.
5. Confirm that spare requested watts move only to other phases with available headroom.
6. Remove the added load and verify the delayed, stepped restoration.
7. Temporarily make a P1 input unavailable/stale and confirm that fail-safe limiting engages.
8. Reboot/redeploy Node-RED and verify that the startup preflight again waits for fresh P1 values.

Keep the real P1 phase currents visible during these tests.

## Optional: upstream proxy monitoring sensors

Gast777 also provides additional Home Assistant proxy sensors and dashboard snippets for monitoring the individual Zendures behind the virtual proxy. His installation process places the language-matched proxy sensor YAML inside the Gielz package/configuration and then restarts Home Assistant.

Those upstream-only auxiliary files are **not duplicated here unless we modified them**. Get the latest matching Dutch/English monitoring files directly from gast777's repository:

- [gast777/Zendure-zenSDK-proxy](https://github.com/gast777/Zendure-zenSDK-proxy#monitoring)

This avoids this DLB repository carrying stale copies of unrelated upstream files.

---

# Releases in this repository

## Current

```text
code/integrated/current/20260801-NL-DLB-v2.6.json
```

The current file is the `20260801-NL-DLB-v2.6` flow preserved from our final development work. Its internal release notes identify it as based on gast777 proxy release **20260801** with all integrated DLB v2.6 functionality. Before publication, the three private Zendure IP addresses were replaced with harmless example addresses (`192.168.1.101`–`103`); users must enter their own device IPs.

## Known-good rollback

The **v2.5** line was explicitly field-tested and confirmed working during development. Keep it available when commissioning v2.6:

```text
code/integrated/archive/20260801-NL-DLB-v2.5.json
```

## Historical / experimental

- `code/integrated/archive/` — prior integrated DLB development builds.
- `code/standalone-experimental/` — the earlier standalone DLB experiment and adapter test package.
- `code/adapters/` — sensor mapping and adapter-development helpers.

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for the recovered development history.

# Safety model

The DLB controller is an automation-layer limiter, not an electrical protective device.

At a high level:

1. Gielz/gast777 calculates the requested charge distribution.
2. DLB reads the latest current/voltage for L1/L2/L3.
3. Each physical phase gets one shared charging budget.
4. A constrained phase is reduced first.
5. If enabled, blocked watts are redistributed only where measured spare capacity exists.
6. Stale or missing P1 information activates a conservative fail-safe.
7. Power is restored gradually after the restriction clears.

Keep correctly rated wiring, breakers/fuses and all normal electrical protections in place.

# Attribution

This repository is a modified derivative of **gast777/Zendure-zenSDK-proxy**, originally by Casper Rijnders. The full upstream non-commercial license is included unchanged in [LICENSE](LICENSE), and our changes are listed in [MODIFICATIONS.md](MODIFICATIONS.md).

Upstream projects:

- **gast777 — Zendure-zenSDK-proxy:** https://github.com/gast777/Zendure-zenSDK-proxy
- **Gielz1986 — Zendure-HA-zenSDK:** https://github.com/Gielz1986/Zendure-HA-zenSDK

# Disclaimer

This is community-developed automation controlling residential energy equipment. Test changes carefully, watch real phase currents during commissioning, retain a known-good rollback, and never treat software current limiting as a substitute for normal electrical protection.
