# Phase 17: Live Corpus Integration and Contradiction Handling

## Goal

Bring live literature collection closer to the normal experiment workflow and make contradiction detection more research-relevant.

## What changed

The experiment runner now supports:

- optional live paper refresh from literature sources,
- saving refreshed corpora to JSON,
- and running the same benchmark pipeline on the updated corpus.

The verifier now also uses stronger contradiction-focused cues such as:

- `always`
- `sufficient`
- `eliminate`
- `regardless`
- `little effect`

## Why this matters

These improvements target two remaining thesis gaps:

- moving beyond a static toy corpus,
- and handling stronger contradiction claims more carefully.

## Current limitation

Live retrieval still depends on internet access and source availability, so this path is scaffolded and ready, but may need to be executed later in a network-enabled environment.
