# Standalone DLB + Gast777 adapter — implementation guide

## Status

This is a **test architecture**, not yet the replacement for the confirmed integrated `20260701-NL-DLB-v2.5` baseline. Keep the working v2.5 export available for immediate rollback until the standalone version has passed controlled charging tests.

## Files

1. `20260701-NL-DLB-Standalone-v1.0-TEST.json` — independent DLB engine.
2. `20260701-NL-Gast777-Proxy-with-DLB-Adapter-v1.0-TEST.json` — original Gast777 NL proxy with only the adapter handover added.
3. `20260701-NL-Gast777-DLB-Adapter-v1.0-TEST.json` — disabled reference tab only.

## How it works

The Gast777 proxy still performs its normal SoC selection, mode handling, request parsing and per-device calculation. Before its existing Zendure POST nodes receive a charging command, the adapter packages the three calculated messages into one batch and calls the standalone DLB through a Node-RED `Link Call`.

The standalone DLB:

- requires fresh P1 current data after deployment before allowing charging;
- supports multiple Zendures mapped to one phase;
- uses one shared power budget per physical phase;
- uses a 23 A soft limit and the configured 25 A hard limit;
- soft-ramp-downs at 500 W per phase update;
- ramp-ups after 20 seconds, in 250 W steps every 10 seconds;
- uses warning logs only for hard protection, P1 fail-safe and real errors;
- returns approved per-device commands to the adapter;
- performs later P1-triggered corrective writes itself using the last approved message templates.

## Installation

1. Export and save your currently working integrated v2.5 flow as rollback.
2. Disable the current integrated DLB tab. Do not run both DLB controllers simultaneously.
3. Import `20260701-NL-DLB-Standalone-v1.0-TEST.json`.
4. Open `Standalone DLB settings` and check the phase mapping and `deviceMaxW` values.
5. Confirm all six P1 Home Assistant nodes show the correct entities.
6. Import `20260701-NL-Gast777-Proxy-with-DLB-Adapter-v1.0-TEST.json` into a new tab. Do not deploy it alongside another active Gast777 proxy using the same HTTP endpoint.
7. Enter the real Zendure IP addresses in the Gast777 settings node.
8. Deploy.
9. Verify that the standalone current node shows fresh L1/L2/L3 values.
10. Start with a small request such as 300–600 W total. Confirm the adapter Link Call returns and the Zendures receive the approved values.
11. Increase gradually while watching phase currents and Node-RED logs.
12. Test deployment while Gielz is requesting charging. The first approved batch must remain 0 W until fresh P1 current states have arrived after deployment.
13. Test soft throttling between 23 A and 25 A. It should not generate a warning.
14. Test P1 unavailability. The fail-safe should activate and generate a warning.

## Future Gast777 releases

This experimental standalone architecture is retained only for development history. No automatic patcher is distributed. For a future gast777 release, the safe approach is to port/review the handover manually against the new upstream flow and test the resulting differences before use.

## Rollback

Disable the standalone engine and adapter-patched proxy, then re-enable/import the confirmed integrated `20260701-NL-DLB-v2.5` flow. Never leave both implementations active because both could write charging commands.
