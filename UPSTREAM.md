# Upstream references

## gast777 — Zendure-zenSDK-proxy

https://github.com/gast777/Zendure-zenSDK-proxy

This is the primary upstream project on which the integrated DLB flow is based. gast777's Node-RED proxy allows multiple Zendure devices to be controlled through the Gielz Home Assistant integration as one logical device while distributing power between the individual units.

## Gielz1986 — Zendure-HA-zenSDK

https://github.com/Gielz1986/Zendure-HA-zenSDK

The Gielz Home Assistant integration is the control layer for which gast777's proxy was designed. Our DLB work remains layered between the requested Gielz/gast777 power behavior and the physical per-phase grid constraints.
