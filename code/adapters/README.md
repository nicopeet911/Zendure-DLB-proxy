# P1 adapter

> [!IMPORTANT]
> This folder is **not part of the normal HomeWizard P1 Dongle installation**.

If you use the standard HomeWizard Wi-Fi P1 Meter / P1 Dongle and Home Assistant exposes the six expected `sensor.p1_meter_*` entities, do not install anything from this folder.

For another three-phase P1/DSMR/energy-meter integration, use:

- [`zendure_dlb_p1_adapter.yaml`](zendure_dlb_p1_adapter.yaml)
- Full instructions: [`../../docs/OTHER-P1-METERS.md`](../../docs/OTHER-P1-METERS.md)

Adapter v1.1 is designed for DLB v2.6.1+ and fixes the earlier `last_reported` problem by identifying the original physical meter current entity through the `dlb_source_entity_id` attribute.
