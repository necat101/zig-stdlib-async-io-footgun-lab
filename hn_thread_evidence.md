# HN Thread Evidence — Zig's New Async I/O

Source: https://news.ycombinator.com/item?id=45746020
Accessed via: Hacker News Firebase API, bundled `hackernews` CLI (`/usr/lib/node_modules/openclaw/dist/extensions/hackernews/skills/hackernews/hackernews`)
Date accessed: 2026-07-10
Thread: "Zig's New Async I/O" — 172 comments, score 329
Linked article: https://andrewkelley.me/post/zig-new-async-io-text-version.html

## Key commenters and sentiments (summarized, not quoted verbatim unless noted)

### Function coloring / effect token debate

- **thefaux**: Found Zig's direction confusing — mix of high/low level, complex. IO interface looks like OO but violates Liskov substitution. Does NOT solve function coloring, hides it. Functions with an IO parameter can't be reasoned about locally due to unexpected interactions, especially across library boundaries. Library authors need to understand the IO object they're passed. Argued this shouldn't be in stdlib, separate into another package.

- **MRson**: "why is allocation not part of IO? This seems like effect oriented programming with a kinda strange grouping: allocation, and the rest (io)."

- **nrds**: TL;DR summary: "Zig now has an effect system with multiple handlers for alloc and io effects. But the designer doesn't know anything about effect systems and it's not algebraic, probably."

- **andyferris** (positive): Likes the design, locks in "platforms" concepts seen in Roc, fits Zig's "no hidden control flow" mantra. Effectful functions injected — good for creating sandboxes (e.g., game engines).

### Async vs concurrent / "not really async"

- **comex** (long detailed comment): Worth noting this is NOT async/await in the sense of essentially every other language. In Zig, `async` and `await` are just functions. In the threaded implementation, `await` just blocks the thread. Stackless coroutines plan seems like "vaporware" — zero agreement on how it would work or avoid function coloring. Stackful coroutines (green threads/fibers) more promising but has significant unknowns: static stack size calculation requires banning recursion/function pointers or adding complex tracking. "Early to claim victory, when all that works today is a thread-based I/O library that happens to have 'async' and 'await' in its function names." Also "early to finalize an I/O library design if you don't even know how the fancy high-performance implementations will work."

- **nialv7**: "This just sounds like a threadpool implementation to me. Sure you can brand it async, but it's not what we generally mean when we say async."

- **miki123211**: "How does downstream code know which kind of asynchrony is requested / allowed?" — raised the async vs concurrent distinction with an LED controller example.

- **PaulHoule**: Async IO struggles generally, Rust ownership issues, single-threaded async wastes cores.

### Cancellation / await ordering

- **pyrolistical**: "Example 7 is a bit of a mindfuck. You get the returned string in both in await and cancel." Feels like it violates Zig's "no hidden control flow" principle.

- **geon**: "So a cancelable function must poll the `cancelRequested` function, and return the error `Canceled`, right?" — with links to std/Io.zig source.

### API churn / pre-1.0

Multiple commenters noted this is pre-1.0, API names changing (asyncConcurrent vs concurrent corrections came up in discussion), too early to finalize stdlib design.

### Allocator comparison

Several comment threads compared Io to Zig allocators — passing an allocator is accepted in Zig, is Io the same pattern or fundamentally different (effect token vs resource)?

### Library boundary reasoning

thefaux's top comment: "Code that worked in one context may surprisingly not work in another context. As a library author, how do I handle an io object that doesn't behave as I expect?"

### Other themes

- **ancarda**: Hopes async is optional, worries async will permeate the ecosystem like in Rust. Prefers threads/mutexes/channels/Erlang-style. "Async just doesn't work for me."
- **travisgriggs**: Deals with async function coloring in Swift/Kotlin, avoids it in Python, prefers BEAM languages for concurrent computation.
- **HacklesRaised**: Worried this will prove to be a distraction.

## Related threads

- https://news.ycombinator.com/item?id=46121539 — "Zig's new plan for asynchronous programs" (264 comments) — LWN coverage of later async plan.

## HN tool access statement

The Hacker News thread at https://news.ycombinator.com/item?id=45746020 was accessed via the bundled Hacker News CLI (`hackernews get-item --id 45746020` and child comment fetches) before writing the README sentiment summary. Comment text was read from the Hacker News Firebase API directly, not from web search summaries. Sentiments above are summarized in my own words; no fabricated quotes.

See also: `hn_comments_sanitized.json` for a machine-readable evidence artifact.
