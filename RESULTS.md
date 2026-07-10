# RESULTS.md — zig-stdlib-async-io-footgun-lab

## Run summary

- Python: 3.12.3
- Platform: Linux-6.17.0-1009-aws-x86_64-with-glibc2.39
- Zig bin: zig_not_found
- Zig version: zig_not_found
- Cases: 43
- Methods: 16
- Result rows: 688
- Wall time: 0.004s
- Subprocesses: 0

## Correctness counts

- compile_pass: 0
- compile_fail: 0
- run_pass: 0
- run_fail: 0
- timeout_count: 0
- api_changed_count: 0
- skipped/not_tested: 688

## Scorecard (by category)

Categories present: async_api, async_context, await_cancel, build_mode, compile_check, concurrent_context, deadlock, hn_context, io_queue, safety_scope, stdlib_probe, version_probe

## Commands

```
python3 generate_cases.py
python3 run_lab.py
```

## Zig env

```
zig_not_found
```

## Safety scope

- Network calls: NO
- External payloads: NO
- Package manager: NO
- Docker: NO
- Socket listeners: NO
- TLS: NO
- Global async safety claim: NO — local compiler observation only

## Artifacts

- cases.json
- results_rows.csv
- results_rows.json
- generated_cases/*.zig

## Honest conclusion

This lab validates local Zig compiler behavior against generated case stubs only.
With zig_not_found=True, compile/run counts reflect skip status, not API correctness.
If Zig was present, compile failures would be recorded as api_changed/compile_changed with actual compiler errors.
No broad claims about Zig async IO safety, function coloring resolution, or production readiness are made.
The HN thread sentiment summary in README.md is sourced from the Hacker News API via the bundled HN tool.
