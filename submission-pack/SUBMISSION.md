# Builder Submission

## Title

RunwayScope — Consensus-Backed Operational Notice Applicability

## Notes / Description

RunwayScope is a standalone GenLayer Intelligent Contract that determines whether official operational notices apply to one frozen runway operation window. A submitter binds an airport, runway, arrival or departure, aircraft category, UTC interval, and allowlisted FAA/NAS/NWS sources. Validators independently fetch every source, assign BOUND, UNBOUND, or UNAVAILABLE status, preserve SHA-256 snapshot digests and literal excerpts, and reach consensus on APPLICABLE_RESTRICTION, CONDITIONAL_OPERATION, NO_APPLICABLE_RESTRICTION, or UNRESOLVED. Restriction results require a bound FAA NOTAM and allowlisted codes; even a no-restriction result requires bound primary evidence. Missing evidence fails closed and may be retried. Tests cover source spoofing, bounded windows, runway validation, excerpt grounding, strict result invariants, and consensus-driven state updates.

## Evidence

- Repository: pending
- Contract source: pending
- Behavioral tests: pending
- Bradbury contract: pending deployment
