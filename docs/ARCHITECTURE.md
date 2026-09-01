# Architecture

## Distinct purpose

RunwayScope does not infer why a flight was delayed. It evaluates whether public operational notices apply to one proposed arrival or departure window. The output is a scoped evidence record, never an official clearance.

## Consensus boundary

Deterministic code freezes identity, validates source provenance, bounds the UTC window, constrains result codes, and enforces state transitions. Validators perform the non-deterministic source retrieval and semantic binding. Agreement is required on the operational result, normalized restriction codes, and all source bindings.

## Provenance

Each validator hashes its bounded rendered source. The accepted leader stores those digests and literal excerpts. Excerpts prove grounding but do not become the validator agreement key because render output can differ harmlessly across nodes.

## Failure model

The FAA NOTAM source is mandatory. If it cannot be fetched, the result is `UNRESOLVED`. An unbound primary source cannot produce either a restriction or a no-restriction result. Unresolved windows may be retried; terminal records are immutable.
