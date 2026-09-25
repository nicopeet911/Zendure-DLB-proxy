# Current integrated builds

- `20260801-NL-DLB-v2.6.json` — **standard HomeWizard P1 Dongle build**. Use this for the normal installation described in the main README.
- `20260801-NL-DLB-v2.6.1.json` — **non-HomeWizard compatibility build**. Use this only together with `docs/OTHER-P1-METERS.md` and the adapter.
- `20260801-NL-DLB-v2.7.json`
      Improved DLB recovery logic.
      Ramp-up protection now only activates after real DLB limiting/fail-safe events.
      Removed false soft/throttling states from normal Gielz power changes.
      Cleaner compact logging, status transitions, heartbeat and Node-RED status colours.
- `20260801-NL-DLB-v2.8.json`
      Added minimum useful charging power per Zendure.
      Small allocations are removed and redistributed to the other eligible batteries.
      Fixed 1 W rounding leftovers and false redistribution/throttling logs.
      Redistribution ≤50 W is no longer shown in normal logs.
  New setting:
        let dynamic_load_balancing_min_device_charge_w = 100
  Usage:
        100 = every charging Zendure gets either 0 W or at least 100 W.
        150 = minimum becomes 150 W.
        0 = disables this feature and keeps the old allocation behaviour.
        Removed sub-threshold power is always redistributed where safely possible.
