# Phase 10: Live Literature Fetching

## Goal

Extend the project from static local corpora to retrievable research literature so the system better reflects the original proposal.

## Why this is important

Your proposal explicitly includes a `Literature Retrieval Agent`. A serious research prototype should eventually fetch real papers or metadata instead of relying only on handcrafted inputs.

## Current implementation

The repository now includes:

- a Semantic Scholar fetcher,
- an arXiv fetcher,
- a unified paper collection service,
- and a script to build corpus files from live query results.

## Research value

This helps in two ways:

- it makes the retrieval stage more realistic,
- and it supports larger experiments than the original sample corpus.

## Current limitation

The fetchers are implemented, but live API calls depend on internet access and optional environment configuration. In this local environment, the code is ready but external calls may need to be run later.
