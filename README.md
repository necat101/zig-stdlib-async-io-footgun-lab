# zig-stdlib-async-io-footgun-lab

A tiny local correctness and compiler-validation lab about Zig stdlib async IO footguns — `std.Io`, `std.Io.Threaded`, `io.async`, `io.concurrent`, `await`, `cancel`, `Io.Queue`, error-return ordering, cancellation-as-cleanup, function-coloring context markers, version-sensitive API probes.

**No network. No sockets. No TLS. No package manager. Local Zig compiler only.**

> **Status (2026-07-11, v2):** Generated Zig case files contain real API probes using `@hasDecl(std, "Io")`, `@hasDecl(std.Io, "async")`, `@hasDecl(std.Io, "concurrent")`, `@hasDecl(std.Io, "Queue")`, etc., with version-sensitive `@compileError` fallbacks. This addresses an audit finding that v1 case files were marker-only stubs. Compile/run validation has NOT been performed in the committed results — no local Zig compiler was available during the lab run, so all 688 result rows are honestly marked `compile_skip` / `run_skip` with `zig_not_found`. When a local portable Zig compiler IS available, `run_lab.py` will invoke it and record real compile/run/api_changed results.

## Hacker News thread access

The Hacker News thread at https://news.ycombinator.com/item?id=45746020 ("Zig's New Async I/O", 172 comments) was read via the bundled Hacker News CLI (`hackernews get-item --id 45746020` + child comment fetches, hitting the real Hacker News Firebase API) **before writing the sentiment summary below**.

This is a hard requirement for this lab — the README reflects actual HN discussion themes, not just the Andrew Kelley article title. See `hn_thread_evidence.md` and `hn_comments_sanitized.json` for auditable evidence.

## What Hacker News users were actually debating

The linked article (https://andrewkelley.me/post/zig-new-async-io-text-version.html) introduces the new `std.Io` async model with examples using `io.async`, `await`, `cancel`, `io.concurrent`, and `Io.Queue`, where different resource-management and scheduling choices have different consequences.

The HN discussion broadened significantly beyond the article:

### Function coloring — solved or just moved?

A top commenter argued the new IO interface looks like OO but violates Liskov substitution, and does **not** solve the function color problem — it hides it. Every function taking an `IO` parameter can't be reasoned about locally because of unexpected interactions with whatever IO object is passed in. Code that worked in one context may surprisingly fail in another.

Others pushed back: passing an IO object is just a library interface, not a language-level problem. One commenter liked that it locks in "platform" concepts seen in Roc, fitting Zig's "no hidden control flow" mantra — good for injecting effectful functions / creating sandboxes (e.g., game engines).

### IO / effect token comparison

Multiple commenters framed `std.Io` as an effect system: "Zig now has an effect system with multiple handlers for alloc and io effects." One asked: "why is allocation not part of IO? This seems like effect oriented programming with a kinda strange grouping: allocation, and the rest (io)."

This led to comparisons between `Io` and Zig allocators — passing an allocator is accepted idiomatic Zig, is `Io` the same pattern or fundamentally different? Is it an effect token?

### Library boundary reasoning

Library authors need to understand the IO object they're passed. If a caller shares an IO object across library boundaries, how does the library handle an IO object that doesn't behave as expected? Local reasoning breaks down when the IO object is caller-controlled.

### Async vs concurrent — easy to confuse

Several commenters highlighted that "async" and "concurrent" are easy to confuse in the new API, and downstream code needs to know which kind of asynchrony is requested/allowed. One commenter asked: "How does downstream code know which kind of asynchrony is requested / allowed?" with an LED controller example where blocking for up to 10s matters.

Another detailed comment explained: **this is NOT async/await in the sense of essentially every other language**. In the current threaded implementation, `async` and `await` are just functions — `await` blocks the thread until done. The stackless coroutines plan was characterized as having "zero agreement on how the feature would work, how it would improve on traditional async/await, or how it would avoid function coloring." Stackful coroutines (green threads) were seen as more promising but with significant unknowns around static stack size calculation, recursion bans, and function pointer restrictions.

Related: "This just sounds like a threadpool implementation to me. Sure you can brand it async, but it's not what we generally mean when we say async."

### Deadlock / ConcurrencyUnavailable

`error.ConcurrencyUnavailable` came up in the discussion, along with single-threaded deadlock concerns when async is used where concurrent was required.

### Cancellation and await ordering

One commenter called Example 7 "a bit of a mindfuck — You get the returned string in both in await and cancel" — feeling like a violation of Zig's "no hidden control flow" principle. Others discussed that cancelable functions must poll `cancelRequested` and return `error.Canceled`, with links to `std/Io.zig` source. Await/try ordering and whether cancel is idempotent were discussion points.

### std.Io.Threaded / API renaming corrections

Pre-1.0 API churn came up repeatedly — corrections like `asyncConcurrent` versus `concurrent` matter, API names are still moving. Multiple commenters noted it's early to finalize a stdlib IO design when the high-performance implementations (stackless/stackful coroutines) aren't settled yet. One commenter: "early to claim victory, when all that works today is a thread-based I/O library that happens to have 'async' and 'await' in its function names."

### Allocator vs IO comparison (again)

Zig's explicit allocator-passing pattern was compared to the new IO-passing pattern — is Io just "allocator 2.0" or is it a fundamentally different effect-token problem?

### "This compiled locally" ≠ "the async model is proven"

The HN consensus (from the more critical comments) was roughly: interesting experiment, glad Zig is trying new things rather than copying Rust async/await, but far too early to claim the async model is safe or solved. Local compilation proving nothing about global async design safety was an implicit theme throughout.

## What this lab does

Turn the HN debate into a tiny reproducible lab showing that **local compiler behavior, API names, await/cancel ordering, async-vs-concurrent distinction, and resource-cleanup patterns need to be checked carefully against the actual Zig version being used**.

- 43 deterministic case files in `generated_cases/`
- Each case: Zig source stub, expected observations, HN/context markers, article-context markers
- `run_lab.py` invokes local portable Zig compiler, captures stdout/stderr/exit codes/timeouts
- Honest skip matrix when Zig is missing or APIs changed
- No network, no sockets, no TLS, no package manager, no Docker, no real deadlock

### Case categories

`version_probe`, `stdlib_probe`, `async_api`, `await_cancel`, `async_context`, `concurrent_context`, `io_queue`, `deadlock`, `hn_context`, `compile_check`, `build_mode`, `safety_scope`

Full list in `cases.json`.

### Methods

`zig_version_probe`, `zig_env_probe`, `stdlib_source_probe`, `compile_only_debug`, `compile_only_release_safe`, `run_debug_safe_case`, `run_release_safe_case`, `std_io_api_context_observer`, `async_api_context_observer`, `concurrent_api_context_observer`, `await_cancel_context_observer`, `io_queue_context_observer`, `timeout_guard_context_observer`, `no_network_guard`, `hnsentiment_context_marker`, `deliver_no_external_truth_marker`

## Running the lab

```bash
python3 -m py_compile generate_cases.py run_lab.py
python3 generate_cases.py
python3 run_lab.py
```

With an explicit portable Zig binary:

```bash
ZIG_BIN=/path/to/zig python3 run_lab.py
```

`run_lab.py` records: Python version, platform, Zig version, zig env, case/method counts, compile/run/skip counts, timeout counts, api_changed counts, HN-thread-access status, network/package-manager status, safety scope.

Results: `RESULTS.md`, `results_rows.csv`, `results_rows.json`

## Scope — what this lab is NOT

- NOT proving Zig async IO is safe or unsafe
- NOT attacking Zig
- NOT testing real network servers
- NOT opening sockets / TLS
- NOT intentionally deadlocking the machine
- NOT benchmarking async runtimes
- NOT depending on bleeding-edge master
- NOT claiming the Andrew Kelley article is right or wrong
- NOT building a production concurrency verifier
- NOT making broad claims about function coloring

It validates **local compiler behavior only** against generated stubs, with honest version-sensitive skip marking.

If the local Zig version does not expose the exact APIs from the article, the lab records `compile_skip`, `api_changed`, or `compile_changed` with actual compiler errors — that is a valid finding.

## Repository layout

- `generate_cases.py` — deterministic case generator
- `run_lab.py` — compiler driver / result collector
- `cases.json` — case catalog
- `generated_cases/*.zig` — generated Zig source stubs
- `RESULTS.md` — run summary
- `results_rows.csv` / `results_rows.json` — per-case/per-method results
- `hn_thread_evidence.md` — HN thread sentiment summary with tool access statement
- `hn_comments_sanitized.json` — sanitized HN API response
- `VERIFY.md` — fresh-clone verification transcript

## License

MIT / public domain — do what you want with the lab harness. Zig source stubs are trivial.
