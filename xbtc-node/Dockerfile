# Bitcoin Knots Cash (xBTC) node image for umbrelOS.
#
# WHY THIS EXISTS: the upstream community image (ghcr.io/bitcoinknotscash/umbrel-xbtc)
# ships a PLAIN Bitcoin Knots binary built with BITCOIN mainnet chainparams. On start it
# loads the BTC genesis (000000000019d668…) and tries to sync ~1M blocks / 810 GB — it can
# never sync xBTC. This image fixes that by overlaying the REAL Bitcoin Knots Cash binaries
# (BLAKE2b, xBTC genesis 00000ff9…) from the official source release onto the same umbrel
# wiring + node dashboard, so it works out of the box.
#
# Source of truth: https://github.com/BitcoinKnotsCash/BitcoinKnotsCash
#
# NOTE: the base below provides the umbrel entrypoint/frontend. It is only used for that
# scaffolding; its bitcoind is fully replaced here. A future version can build the whole
# image from the dev source instead of depending on the upstream image.

ARG BASE=ghcr.io/bitcoinknotscash/umbrel-xbtc:v0.2.1-xbtc
ARG XBTC_RELEASE=v0.2.2-xbtc
# sha256 of bitcoinknotscash-linux64.tar.gz for ${XBTC_RELEASE}, from the release's
# published SHA256SUMS. MUST be updated together with XBTC_RELEASE.
#   v0.2.2-xbtc: 6d62b9afd846b8b40abbf2a9c049bba972d34d5d994142306292a2a15ec53bb3
ARG XBTC_SHA256=6d62b9afd846b8b40abbf2a9c049bba972d34d5d994142306292a2a15ec53bb3

FROM ${BASE}
ARG XBTC_RELEASE
ARG XBTC_SHA256

# curl stays (blocknotify uses it). Pull the Cash binaries, VERIFY the checksum against the
# release's published SHA256SUMS, install over the BTC ones, and fail the build if the result
# is not actually the "Knots Cash" daemon.
RUN set -eux; \
    url="https://github.com/BitcoinKnotsCash/BitcoinKnotsCash/releases/download/${XBTC_RELEASE}/bitcoinknotscash-linux64.tar.gz"; \
    curl -fsSL -o /tmp/xbtc.tar.gz "$url"; \
    echo "${XBTC_SHA256}  /tmp/xbtc.tar.gz" | sha256sum -c -; \
    tar -xzf /tmp/xbtc.tar.gz -C /tmp; \
    bd="$(find /tmp -type f -name bitcoind | head -1)"; \
    bc="$(find /tmp -type f -name bitcoin-cli | head -1)"; \
    install -m 0755 "$bd" /usr/local/bin/bitcoind; \
    install -m 0755 "$bc" /usr/local/bin/bitcoin-cli; \
    rm -rf /tmp/xbtc.tar.gz /tmp/bitcoinknotscash-linux64; \
    bitcoind -version | head -1; \
    bitcoind -version | head -1 | grep -qi "Knots Cash"
