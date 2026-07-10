# VERIFY.md — Fresh-clone verification

Verified: 2026-07-10

## Fresh clone transcript

```
$ cd /tmp && rm -rf zig-verify && git clone /home/ubuntu/.openclaw/workspace/zig-stdlib-async-io-footgun-lab zig-verify
Cloning into 'zig-verify'...
done.

$ cd zig-verify
$ python3 -m py_compile generate_cases.py run_lab.py
===py_compile OK===

$ python3 generate_cases.py
Generated 43 cases in /tmp/zig-verify/generated_cases/
Wrote cases.json
===generate OK===

$ python3 run_lab.py
Results: compile_pass=0 compile_fail=0 run_pass=0 run_fail=0 skipped=688
Wrote RESULTS.md, results_rows.csv/json
===run OK===
```

## Verification checks

- [x] `py_compile generate_cases.py run_lab.py` — pass
- [x] `python3 generate_cases.py` — 43 cases generated
- [x] `python3 run_lab.py` — completes, writes RESULTS.md + results_rows.csv/json
- [x] No network calls during run
- [x] No external payloads
- [x] No package manager invocations (apt/brew/choco/pip install etc.)
- [x] No Docker
- [x] No socket listeners / TLS
- [x] Zig compiler: `zig_not_found` — honestly recorded in RESULTS.md, skip artifacts committed
- [x] README.md contains HN thread link (news.ycombinator.com/item?id=45746020)
- [x] `hn_thread_evidence.md` present
- [x] `hn_comments_sanitized.json` present
- [x] `cases.json` present
- [x] `results_rows.csv` / `results_rows.json` present
- [x] Generated Zig sources committed in `generated_cases/`
- [x] No global async safety claims in docs

## Environment

- Python: 3.12
- Platform: Linux
- Zig: not found (honest skip — no fake validation)

All outputs are reproducible via the committed scripts with only the Python standard library.
