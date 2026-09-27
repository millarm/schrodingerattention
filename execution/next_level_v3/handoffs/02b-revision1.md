# Recovery A revision 1

Focused command exited 0: `14 passed in 0.65s`; full wall 0.748632084s, charged once as ledger UUID `0b6f1779-d76e-4d3f-afec-cba0b32ef176`.

Module SHA-256: `84f791992b81dbbebea66cba793f27481086b33335a2287359fd38d567e56e0a`.

Tests SHA-256: `2c7430719deacef1ced8ff2e9bc9cd29b3291a2f2894380c6b585498f60dd394`.

Sol05 mapping: global inventory validation is called before the proposal loop and builders have a `validate=False` safe seam; assembled records declare n12 and validation rejects bad n/endpoints/walls; rejected length evidence retains `accepted_rows` without committing the map; eligibility uses raw walls+n/support hash and profile bounds. Existing isolated tests exercise orientation shortage, cache hit/separation, lazy statuses, and orchestration ordering/short-circuit behavior.

Recovery B composed fixture work remains outside this revision and no production result is claimed.
