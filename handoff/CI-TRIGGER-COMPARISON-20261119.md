# GitHub Actions trigger comparison

- Date: 2026-11-19
- Branch: feature/recipe-wizard-handoff
- Parent SHA: c5b05b0a7bb453fa21757f101061d7c280afb919
- Experiment: Operator-authenticated git push
- Scope: Source-only, CI trigger comparison
- Gate: Production remains BLOCKED

This file deliberately matches the workflow's handoff/**
path filter. It does not authorize any DGX runtime
operation, journal write, release, or PR merge.
