# VERIFY.md — Fresh-clone verification

Verified: 2026-07-11

## Fresh clone transcript

Cloned from: https://github.com/necat101/zig-stdlib-async-io-footgun-lab.git

```
$ cd /tmp && rm -rf zig-verify-gh2 && git clone https://github.com/necat101/zig-stdlib-async-io-footgun-lab.git zig-verify-gh2
Cloning into 'zig-verify-gh2'...
done.

$ cd zig-verify-gh2
$ python3 -m py_compile generate_cases.py run_lab.py
PY_COMPILE_OK

$ python3 generate_cases.py
Generated 43 cases in /tmp/zig-verify-gh2/generated_cases/
Wrote cases.json

$ python3 run_lab.py
Results: compile_pass=0 compile_fail=0 run_pass=0 run_fail=0 skipped=688
Wrote RESULTS.md, results_rows.csv/json
```

## Verification checks

- [x] `git clone https://github.com/necat101/zig-stdlib-async-io-footgun-lab.git` — fresh from GitHub
- [x] `py_compile generate_cases.py run_lab.py` — pass
- [x] `python3 generate_cases.py` — 43 cases generated
- [x] Generated Zig files contain real API probes: `@hasDecl(std, "Io")`, `@hasDecl(std.Io, "async")`, `@hasDecl(std.Io, "concurrent")`, `@hasDecl(std.Io, "Queue")`, `@hasDecl(std.Io, "cancel")`, etc., with version-sensitive `@compileError` fallbacks
- [x] `python3 run_lab.py` — completes, writes RESULTS.md + results_rows.csv/json
- [x] No network calls during run
- [x] No external payloads / package manager / Docker / socket listeners / TLS
- [x] Zig compiler: `zig_not_found` — honestly recorded, skip artifacts committed
- [x] README.md contains HN thread link
- [x] `hn_thread_evidence.md` present
- [x] `hn_comments_sanitized.json` present
- [x] `cases.json` present
- [x] `results_rows.csv` / `results_rows.json` present
- [x] Generated Zig sources committed in `generated_cases/`

## Scope note (v2)

The generated Zig case files contain real API probes using `@hasDecl(std, "Io")`, `@hasDecl(std.Io, "async")`, `@hasDecl(std.Io, "concurrent")`, `@hasDecl(std.Io, "Queue")`, `@hasDecl(std.Io, "cancel")`, etc., with version-sensitive `@compileError` fallbacks for API-changed detection. This addresses the audit finding that v1 case files were marker-only stubs that did not exercise the named APIs.

Compile/run validation was NOT performed in this verification run because no local Zig compiler was available. Results counts (0 compile_pass, 0 compile_fail, 688 skipped) reflect honest `zig_not_found` handling, not API correctness.

When a local portable Zig compiler IS available, `run_lab.py` will invoke it, capture real stdout/stderr/exit codes, and record `api_changed` / `compile_fail` with actual compiler errors.

All outputs are reproducible via the committed scripts with only the Python standard library.
