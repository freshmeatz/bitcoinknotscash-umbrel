# Bitcoin Knots Cash — umbrelOS Community App Store

A community app store for **Bitcoin Knots Cash (xBTC)** — a BLAKE2b proof-of-work fork of
Bitcoin Knots v29.4 (fair launch, 21,000,000 supply, ASERT per-block difficulty, DATUM/TIDES
mining). Source: https://github.com/BitcoinKnotsCash/BitcoinKnotsCash

Add this store in umbrelOS: **Settings → App Store → Community App Stores →**
`https://github.com/freshmeatz/bitcoinknotscash-umbrel`

## Apps

| App | ID | What it is |
|-----|----|-----------|
| **Bitcoin Knots Cash Node** | `xbtc-node` | A full xBTC node. Implements the `bitcoin` dependency so mempool/electrs/DATUM can use it. |
| **DATUM for xBTC** | `xbtc-datum` | A dedicated DATUM gateway for mining xBTC (defaults to the crypto-eire xbtc-pool). Depends on `xbtc-node`. |

## Why the node app is a custom image

The earlier community image (`ghcr.io/bitcoinknotscash/umbrel-xbtc`) shipped a **plain Bitcoin
Knots** binary built with **Bitcoin mainnet chainparams**. Installed, it loads the BTC genesis
(`000000000019d668…`) and tries to sync ~1,000,000 blocks / ~810 GB — it can never sync xBTC
(genesis `00000ff9…`, ~17k blocks). `xbtc-node/Dockerfile` fixes this by overlaying the **real
Bitcoin Knots Cash binaries** from the official `v0.2.1-xbtc` release onto the umbrel scaffolding.

## The two gotchas this store bakes in

The Cash binary **ignores the included `umbrel-bitcoin.conf`** — both the `[main]` port section
AND the global `rpcauth` / `rpcbind` / `rpcallowip`. So in `xbtc-node/docker-compose.yml`,
everything is forced on the command line via `BITCOIND_EXTRA_ARGS`:

- `-rpcbind=0.0.0.0 -rpcallowip=10.21.0.0/16` — otherwise RPC binds only `127.0.0.1` and no
  other app can reach it.
- `-rpcuser=… -rpcpassword=…` — otherwise all RPC auth is rejected (the conf's `rpcauth` is ignored).
- `-rpcport`/`-port`/`-bind`/`-whitebind` — otherwise it falls back to the chain defaults (8555/8556).

## Build

The node image is built by `.github/workflows/build-images.yml` (manual or on Dockerfile change)
and pushed to `ghcr.io/<owner>/umbrel-xbtc-cash`. Run it once before installing, or pin the
`image:` in `xbtc-node/docker-compose.yml` to a tag you've built.

## Install

1. Add this store: **Settings → App Store → Community App Stores →** this repo's URL.
2. Install **Bitcoin Knots Cash Node** (`xbtc-node`) and let it sync the xBTC chain
   (BLAKE2b, genesis `00000ff9…`, ~17k blocks — not the 810 GB BTC chain).
3. Install **DATUM for xBTC** (`xbtc-datum`); its `bitcoin` dependency resolves to `xbtc-node`
   automatically, and `hooks/pre-start` wires the node's RPC into the DATUM config.
4. Open DATUM's dashboard — default admin login **`admin` / `umbrelxbtc`** (shown on the app's
   Umbrel page; **change it** in the Config tab). It defaults to the crypto-eire xbtc-pool (TIDES).
   Set `mining.pool_address` to a valid xBTC address first — until you do, DATUM logs
   `Could not generate output script for pool addr` and won't build templates.
5. Point your BLAKE2b miners at this device's IP on the Stratum port (host `23349`), with the
   **username set to your xBTC payout address** plus an optional worker:
   `<your-xbtc-address>.<worker>`. With `datum.pool_pass_full_users` (the default), the pool credits
   the address in the miner's username — `mining.pool_address` is only a fallback and does **not**
   override it.

The node image (`ghcr.io/freshmeatz/umbrel-xbtc-cash:v0.2.1-xbtc`) is built by CI and published
public, so both apps install without a manual build.

## Theming (DATUM dashboard)

`xbtc-datum` ships a small nginx **theme sidecar** that reverse-proxies the DATUM gateway
dashboard and, via `sub_filter`, injects the Crypto-Éire colours, logo and wordmark so the
dashboard matches crypto-eire.com. The whole nginx config (including the minified CSS) is
**base64-embedded in `xbtc-datum/docker-compose.yml`**, not bind-mounted — umbrelOS does not
copy non-`data/` app subdirs into app-data, so a bind mount there comes up as an empty dir.
The header logo is loaded from `crypto-eire.com`, so a themed dashboard needs internet for that
one image. To change the theme: edit `xbtc-datum/theme/assets/crypto-eire.css`, then run
`python3 xbtc-datum/theme/build.py` to regenerate the embedded config, and bump the app version.

## Status

**Tested working on umbrelOS.** The node syncs to the network tip and implements the `bitcoin`
dependency; DATUM connects to the node and the pool with its Stratum V1 server live, builds
block templates from the node, and serves the Crypto-Éire-themed dashboard.

## Credits

This store repackages the projects below for umbrelOS. All names, trademarks and logos belong
to their respective owners.

- **Bitcoin Knots Cash (xBTC)** — the chain and node binaries (a BLAKE2b fork of Bitcoin Knots):
  https://github.com/BitcoinKnotsCash/BitcoinKnotsCash
- **DATUM Gateway** — OCEAN, the gateway software and its dashboard:
  https://github.com/OCEAN-xyz/datum_gateway
- **DATUM BLAKE2b image** — horizon-btc, the xBTC/BLAKE2b build the `xbtc-datum` app runs
  (`ghcr.io/horizon-btc/datum`): https://github.com/horizon-btc
- **Crypto-Éire** — https://crypto-eire.com — the default xBTC DATUM/TIDES pool, and the logo
  and brand colours the dashboard theme reproduces.
- **nginx** (https://nginx.org) — the dashboard theme sidecar.
- **Tor** and **i2pd** — the node's privacy sidecars (via Umbrel's images).
- Base node scaffolding from the upstream `umbrel-xbtc` community image and **Bitcoin Knots**
  (https://bitcoinknots.org).
