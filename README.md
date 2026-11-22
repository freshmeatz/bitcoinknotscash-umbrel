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
4. Set your xBTC payout address in DATUM's **Config tab** (`mining.pool_address`). It defaults to
   the crypto-eire xbtc-pool (TIDES).
5. Point your BLAKE2b miners at this device's IP on the Stratum port (host `23349`), with username
   `<your-xbtc-address>.<worker>`.

The node image (`ghcr.io/freshmeatz/umbrel-xbtc-cash:v0.2.1-xbtc`) is built by CI and published
public, so both apps install without a manual build.

## Status

**Tested working on umbrelOS.** The node syncs to the network tip and implements the `bitcoin`
dependency; DATUM connects to the node and the pool with its Stratum V1 server live and builds
block templates from the node.

## Credits

Node: Bitcoin Knots Cash (https://github.com/BitcoinKnotsCash/BitcoinKnotsCash).
DATUM: OCEAN datum_gateway (https://github.com/OCEAN-xyz/datum_gateway).
