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

## Status

Folded in from a working install and reconstructed:

- `xbtc-node/`: `Dockerfile`, `docker-compose.yml`, `umbrel-app.yml`, **`exports.sh`** (real),
  **`scripts/rpcauth.py`**. The compose + exports together define all `APP_XBTC_NODE_*` vars and
  export the generic `APP_BITCOIN_*` vars the DATUM app consumes.
- `xbtc-datum/`: `docker-compose.yml` (matches real `btc-datum`), `umbrel-app.yml`,
  **`hooks/pre-start`** (injects the node RPC into the config), and a documented sample config
  pre-set to the crypto-eire xbtc-pool.

### Still to do before it's fully turnkey

1. **`xbtc-node/torrc.template`** (+ any `xbtc-node/hooks/`) — copy from `~/umbrel/app-data/xbtc-node/`;
   the compose mounts a generated `torrc`, so the template is needed for the Tor hidden services.
2. **Validate `xbtc-datum/hooks/pre-start`** against however your working `btc-datum` actually
   injected the node RPC (it has no `exports.sh`, so it used a hook or the image's entrypoint).
3. **Run the image workflow** (`Actions → Build xBTC node image`) so `ghcr.io/<you>/umbrel-xbtc-cash`
   exists, then **install `xbtc-node`, then `xbtc-datum`**, and set your payout address in DATUM's Config tab.

## Credits

Node: Bitcoin Knots Cash (https://github.com/BitcoinKnotsCash/BitcoinKnotsCash).
DATUM: OCEAN datum_gateway (https://github.com/OCEAN-xyz/datum_gateway).
