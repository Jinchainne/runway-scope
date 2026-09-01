# Builder Submission

## Title

RunwayScope — Consensus-Backed Operational Notice Applicability

## Notes / Description

RunwayScope is a standalone GenLayer Intelligent Contract that determines whether official operational notices apply to one frozen runway operation window. A submitter binds an airport, runway, arrival or departure, aircraft category, UTC interval, and allowlisted FAA/NAS/NWS sources. Validators independently fetch every source, assign BOUND, UNBOUND, or UNAVAILABLE status, preserve SHA-256 snapshot digests and literal excerpts, and reach consensus on APPLICABLE_RESTRICTION, CONDITIONAL_OPERATION, NO_APPLICABLE_RESTRICTION, or UNRESOLVED. Restriction results require a bound FAA NOTAM and allowlisted codes; even a no-restriction result requires bound primary evidence. Missing evidence fails closed and may be retried. Tests cover source spoofing, bounded windows, runway validation, excerpt grounding, strict result invariants, and consensus-driven state updates.

## Evidence

- Repository: https://github.com/Jinchainne/runway-scope
- Contract source: https://github.com/Jinchainne/runway-scope/blob/main/contracts/runway_scope.py
- Behavioral tests: https://github.com/Jinchainne/runway-scope/blob/main/tests/test_contract_behavior.py
- Architecture: https://github.com/Jinchainne/runway-scope/blob/main/docs/ARCHITECTURE.md
- Bradbury contract: https://explorer-bradbury.genlayer.com/address/0x0b45bb9a2d542C46FD4a615E32AB3107507f0DEc
- Deployment transaction: https://explorer-bradbury.genlayer.com/tx/0xc8299a66c4d358182c9e831d8d949900aa29b7f26c34ffc51c694a0d6a70fdc7
