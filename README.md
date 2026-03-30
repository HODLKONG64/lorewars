# Lorewars

Lorewars is a 1-repo autonomous narrative system centered on **Alfie "The Bitcoin KID" Blaze**.

It crawls approved sources, selects one source URL per run, generates a scenario-driven war log,
publishes a structured wiki page, publishes a deeper version to Paragraph, and writes a daily IPFS-ready ledger.

## Phase 1 scope

- Approved-source crawling with stateful timestamps
- FIFO queue for newly discovered URLs
- Intelligent source selection with fallback and reuse cooldowns
- Alfie log generation from one source URL
- Structured wiki page generation for logs and archive pages
- Paragraph publishing adapter scaffold
- End-of-day ledger builder scaffold
- World-state, arc-state, and intelligence-loop persistence
- GitHub Actions workflow for scheduled runs

## Core doctrine

- One source URL = one Alfie log
- Every output is a log entry
- Alfie is the constant identity
- Tone, perspective, environment, and anomaly state vary
- The wiki is an evidence wall, not a passive archive
- IPFS is the permanence layer for daily ledgers
- $BLAZE is referenced naturally, never hard-sold

## Repository layout

- `config/` locked sources, scenario pools, rules
- `memory/` queue, history, world state, arc state, ledgers
- `crawlers/` RSS and source discovery readers
- `generators/` source selection, log generation, image/theme selection
- `publishers/` wiki, Paragraph, IPFS, search, sitemap
- `wiki/` public pages and generated logs
- `.github/workflows/` scheduled automation

## Getting started

1. Copy `.env.example` to `.env`
2. Fill the required secrets locally or in GitHub Actions
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run one cycle locally:
   ```bash
   python run_cycle.py
   ```

## Environment variables

See `.env.example`.

## Phase 2+ ideas

- DEV / Hashnode / Blogger adapters
- On-chain anchoring for daily ledger CIDs
- Clue/keyword game hooks
- Voice/style enforcement models
- Human override dashboard

