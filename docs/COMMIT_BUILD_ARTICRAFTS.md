# Should we commit compiled contract artifacts?

Recommendation:
- For reviewers, committing `contracts/substrate-poc/target/ink/metadata.json` and the `.contract` bundle eases verification.
- For best practice, prefer reproducible build (quickstart builds on reviewer machine) and optionally attach a release with compiled artifacts.

If you choose to commit:
- Only commit files in `contracts/substrate-poc/target/ink/`:
  - `metadata.json`
  - `<contract_name>.contract`
  - `<contract_name>.wasm` (optional; large)
- Add a note in README that these are build artifacts and how to rebuild.