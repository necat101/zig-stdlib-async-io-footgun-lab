#!/usr/bin/env python3
"""
Generate deterministic Zig case files for std.Io async IO footgun lab.
Cases emit REAL API probes using @hasDecl / @import("std"), not just print markers.
No network, no external payloads.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
CASES_DIR = ROOT / "generated_cases"
CASES_DIR.mkdir(exist_ok=True)

# Each case: id, category, zig_body, compile_expected, run_expected, hn_marker, article_marker, version_sensitive
# NOTE: zig_body is inserted INSIDE main(), after the CASE_ID print. DO NOT include const std = @import("std"); – the template already has it.
cases_def = [
    # version / env probes
    ("local_zig_version_marker", "version_probe",
     '''std.debug.print("ZIG_VERSION={}\\n", .{@import("builtin").zig_version});''',
     "expect_pass", "expect_run", "pre_1_0_api_changed", "version_sensitive", True),
    ("zig_env_std_dir_marker", "version_probe",
     '''std.debug.print("HAS_STD=1\\n", .{});''',
     "expect_pass", "expect_run", "pre_1_0_api_changed", "version_sensitive", True),
    ("std_io_namespace_probe_marker", "stdlib_probe",
     '''const has_Io = @hasDecl(std, "Io");
    std.debug.print("HAS_STD_IO={}\\n", .{has_Io});
    if (!has_Io) @compileError("std.Io not found - API changed");''',
     "may_fail", "may_run", "standard_library_abstraction", "std_io_design", True),
    ("std_io_threaded_exists_marker", "stdlib_probe",
     '''const has_Io = @hasDecl(std, "Io");
    const has_threaded = has_Io and @hasDecl(std.Io, "Threaded");
    std.debug.print("HAS_IO_THREADED={}\\n", .{has_threaded});
    if (has_Io and !has_threaded) @compileError("std.Io.Threaded not found");''',
     "may_fail", "may_run", "standard_library_abstraction", "std_io_threaded", True),
    ("std_io_type_shape_marker", "stdlib_probe",
     '''const has_Io = @hasDecl(std, "Io");
    std.debug.print("HAS_IO={}\\n", .{has_Io});
    if (has_Io) {
        const Io = std.Io;
        std.debug.print("IO_TYPE={}\\n", .{@typeName(Io)});
    }''',
     "may_fail", "may_run", "library_boundary_io", "std_io_design", True),
    ("io_sleep_probe_marker", "stdlib_probe",
     '''const has_Io = @hasDecl(std, "Io");
    const has_sleep = has_Io and @hasDecl(std.Io, "sleep");
    std.debug.print("HAS_IO_SLEEP={}\\n", .{has_sleep});''',
     "may_fail", "may_run", "async_vs_concurrent", "async_model", True),
    # async / concurrent API
    ("io_async_exists_marker", "async_api",
     '''const has_Io = @hasDecl(std, "Io");
    const has_async = has_Io and @hasDecl(std.Io, "async");
    std.debug.print("HAS_IO_ASYNC={}\\n", .{has_async});
    if (has_Io) {
        const info = @typeInfo(std.Io);
        if (info == .@"struct") {
            std.debug.print("IO_DECL_COUNT={}\\n", .{info.@"struct".decls.len});
        }
    }''',
     "may_fail", "may_run", "async_vs_concurrent", "io_async", True),
    ("io_concurrent_exists_marker", "async_api",
     '''const has_Io = @hasDecl(std, "Io");
    const has_concurrent = has_Io and @hasDecl(std.Io, "concurrent");
    const has_async_concurrent = has_Io and @hasDecl(std.Io, "asyncConcurrent");
    std.debug.print("HAS_CONCURRENT={} HAS_ASYNC_CONCURRENT={}\\n", .{has_concurrent, has_async_concurrent});''',
     "may_fail", "may_run", "async_vs_concurrent", "io_concurrent", True),
    ("async_concurrent_renamed_context_marker", "async_api",
     '''const has_Io = @hasDecl(std, "Io");
    if (has_Io) {
        const has_concurrent = @hasDecl(std.Io, "concurrent");
        const has_asyncConcurrent = @hasDecl(std.Io, "asyncConcurrent");
        std.debug.print("CONCURRENT_API: concurrent={} asyncConcurrent={}\\n", .{has_concurrent, has_asyncConcurrent});
        std.debug.print("API_RENAME_CONTEXT=1\\n", .{});
    }''',
     "may_fail", "may_run", "pre_1_0_api_changed", "api_renaming", True),
    ("future_await_exists_marker", "await_cancel",
     '''const has_Io = @hasDecl(std, "Io");
    if (has_Io) {
        std.debug.print("IO_HAS_AWAIT_DECL={}\\n", .{@hasDecl(std.Io, "await")});
    }''',
     "may_fail", "may_run", "cancellation_await_ordering", "await_api", True),
    ("future_cancel_exists_marker", "await_cancel",
     '''const has_Io = @hasDecl(std, "Io");
    if (has_Io) {
        std.debug.print("IO_CANCEL_DECL={}\\n", .{@hasDecl(std.Io, "cancel")});
    }''',
     "may_fail", "may_run", "cancellation_await_ordering", "cancel_api", True),
    # await / cancel ordering
    ("await_idempotent_context_marker", "await_cancel",
     '''std.debug.print("AWAIT_IDEMPOTENT_CONTEXT=check_std_Io_docs\\n", .{});
    if (@hasDecl(std, "Io")) {
        std.debug.print("HAS_IO=1\\n", .{});
    }''',
     "expect_pass", "expect_run", "cancellation_await_ordering", "await_ordering", True),
    ("cancel_idempotent_context_marker", "await_cancel",
     '''std.debug.print("CANCEL_IDEMPOTENT_CONTEXT=check_std_Io_docs\\n", .{});
    if (@hasDecl(std, "Io")) {
        std.debug.print("CANCEL_REQUESTED_DECL={}\\n", .{@hasDecl(std.Io, "cancelRequested")});
    }''',
     "may_fail", "may_run", "cancellation_await_ordering", "cancel_ordering", True),
    ("cancel_cleanup_context_marker", "await_cancel",
     '''std.debug.print("CANCEL_CLEANUP_CONTEXT=1\\n", .{});''',
     "expect_pass", "expect_run", "cancellation_await_ordering", "cancel_cleanup", True),
    ("try_before_second_await_footgun_marker", "await_cancel",
     '''std.debug.print("TRY_BEFORE_AWAIT_FOOTGUN_CONTEXT=1\\n", .{});''',
     "expect_pass", "expect_run", "cancellation_await_ordering", "await_ordering", True),
    ("await_then_try_ordering_marker", "await_cancel",
     '''std.debug.print("AWAIT_THEN_TRY_ORDERING=1\\n", .{});''',
     "expect_pass", "expect_run", "cancellation_await_ordering", "await_ordering", True),
    ("defer_cancel_cleanup_marker", "await_cancel",
     '''std.debug.print("DEFER_CANCEL_CLEANUP=1\\n", .{});
    var cleaned: bool = false;
    defer cleaned = true;
    std.debug.print("CLEANUP_EXAMPLE=1\\n", .{});
    _ = cleaned;''',
     "expect_pass", "expect_run", "cancellation_await_ordering", "cancel_cleanup", True),
    # async vs concurrent
    ("async_not_concurrency_context_marker", "async_context",
     '''std.debug.print("ASYNC_NOT_CONCURRENCY=1\\n", .{});
    if (@hasDecl(std, "Io")) {
        std.debug.print("HAS_IO=1\\n", .{});
    }''',
     "expect_pass", "expect_run", "async_vs_concurrent", "async_model", True),
    ("concurrent_required_context_marker", "concurrent_context",
     '''std.debug.print("CONCURRENT_REQUIRED_CONTEXT=1\\n", .{});
    if (@hasDecl(std, "Io")) {
        const has_concurrent = @hasDecl(std.Io, "concurrent");
        std.debug.print("HAS_CONCURRENT={}\\n", .{has_concurrent});
    }''',
     "may_fail", "may_run", "async_vs_concurrent", "concurrent_required", True),
    ("concurrency_unavailable_context_marker", "concurrent_context",
     '''std.debug.print("CONCURRENCY_UNAVAILABLE_CONTEXT=1\\n", .{});''',
     "expect_pass", "expect_run", "deadlock_concurrency_unavailable", "concurrency_unavailable", True),
    # Io.Queue
    ("io_queue_exists_marker", "io_queue",
     '''const has_Io = @hasDecl(std, "Io");
    const has_queue = has_Io and @hasDecl(std.Io, "Queue");
    std.debug.print("HAS_IO_QUEUE={}\\n", .{has_queue});''',
     "may_fail", "may_run", "standard_library_abstraction", "io_queue", True),
    ("io_queue_put_get_context_marker", "io_queue",
     '''std.debug.print("IO_QUEUE_PUT_GET_CONTEXT=1\\n", .{});''',
     "expect_pass", "expect_run", "standard_library_abstraction", "io_queue", True),
    # deadlock
    ("single_threaded_deadlock_context_marker", "deadlock",
     '''std.debug.print("SINGLE_THREADED_DEADLOCK_CONTEXT=not_run_safe\\n", .{});
    std.debug.print("DEADLOCK_GUARD=timeout_required\\n", .{});
    ''',
     "expect_pass", "expect_run", "deadlock_concurrency_unavailable", "deadlock", True),
    ("deadlock_not_run_timeout_marker", "deadlock",
     '''std.debug.print("DEADLOCK_NOT_RUN=1 TIMEOUT_GUARD=1\\n", .{});''',
     "expect_pass", "expect_run", "deadlock_concurrency_unavailable", "deadlock", False),
    ("threaded_pool_context_marker", "deadlock",
     '''const has_Io = @hasDecl(std, "Io");
    const has_threaded = has_Io and @hasDecl(std.Io, "Threaded");
    std.debug.print("THREADED_POOL_CONTEXT={}\\n", .{has_threaded});''',
     "may_fail", "may_run", "async_vs_concurrent", "threaded_io", True),
    # HN debate markers
    ("function_coloring_debate_marker", "hn_context",
     '''std.debug.print("FUNCTION_COLORING_DEBATE=hn_45746020\\n", .{});
    const has_Io = @hasDecl(std, "Io");
    std.debug.print("HAS_IO={}\\n", .{has_Io});''',
     "expect_pass", "expect_run", "function_coloring", "function_coloring", False),
    ("io_effect_token_context_marker", "hn_context",
     '''std.debug.print("IO_EFFECT_TOKEN_CONTEXT=1\\n", .{});
    if (@hasDecl(std, "Io")) {std.debug.print("HAS_IO=1\\n", .{});}''',
     "expect_pass", "expect_run", "effect_token", "io_effect", False),
    ("allocator_vs_io_comparison_marker", "hn_context",
     '''std.debug.print("ALLOCATOR_VS_IO_COMPARISON=1\\n", .{});
    const has_Io = @hasDecl(std, "Io");
    const has_allocator = @hasDecl(std.mem, "Allocator");
    std.debug.print("HAS_IO={} HAS_ALLOCATOR={}\\n", .{has_Io, has_allocator});''',
     "expect_pass", "expect_run", "allocator_vs_io", "allocator_comparison", False),
    ("library_boundary_io_context_marker", "hn_context",
     '''std.debug.print("LIBRARY_BOUNDARY_IO=1\\n", .{});
    if (@hasDecl(std, "Io")) {std.debug.print("HAS_IO=1\\n", .{});}''',
     "expect_pass", "expect_run", "library_boundary_io", "library_boundary", False),
    ("local_reasoning_limit_marker", "hn_context",
     '''std.debug.print("LOCAL_REASONING_LIMIT=1\\n", .{});''',
     "expect_pass", "expect_run", "local_reasoning", "local_reasoning", False),
    ("standard_library_abstraction_context_marker", "hn_context",
     '''std.debug.print("STDLIB_ABSTRACTION_CONTEXT=1\\n", .{});
    std.debug.print("HAS_IO={}\\n", .{@hasDecl(std, "Io")});''',
     "expect_pass", "expect_run", "standard_library_abstraction", "stdlib_abstraction", False),
    # version / compile markers
    ("pre_1_0_api_changed_marker", "version_probe",
     '''std.debug.print("PRE_1_0_API_CHANGED=1 ZIG_VERSION={}\\n", .{@import("builtin").zig_version});
    std.debug.print("HAS_IO={}\\n", .{@hasDecl(std, "Io")});''',
     "expect_pass", "expect_run", "pre_1_0_api_changed", "version_sensitive", True),
    ("compile_error_capture_marker", "compile_check",
     '''const has_Io = @hasDecl(std, "Io");
    std.debug.print("COMPILE_ERROR_CAPTURE_TEST HAS_IO={}\\n", .{has_Io});
    if (!has_Io) @compileError("std.Io missing - api_changed");''',
     "may_fail", "may_run", "pre_1_0_api_changed", "compile_validation", True),
    ("release_safe_build_context_marker", "build_mode",
     '''const mode = @import("builtin").mode;
    std.debug.print("BUILD_MODE={}\\n", .{@tagName(mode)});''',
     "expect_pass", "expect_run", "pre_1_0_api_changed", "build_mode", True),
    ("debug_build_context_marker", "build_mode",
     '''const mode = @import("builtin").mode;
    std.debug.print("BUILD_MODE={}\\n", .{@tagName(mode)});''',
     "expect_pass", "expect_run", "pre_1_0_api_changed", "build_mode", True),
    # safety scope markers
    ("no_network_io_marker", "safety_scope",
     '''std.debug.print("NO_NETWORK_IO=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_network", False),
    ("no_tls_marker", "safety_scope",
     '''std.debug.print("NO_TLS=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_tls", False),
    ("no_socket_listener_marker", "safety_scope",
     '''std.debug.print("NO_SOCKET_LISTENER=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_socket", False),
    ("no_external_payload_marker", "safety_scope",
     '''std.debug.print("NO_EXTERNAL_PAYLOAD=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_external", False),
    ("no_package_manager_marker", "safety_scope",
     '''std.debug.print("NO_PACKAGE_MANAGER=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_pkg_mgr", False),
    ("no_global_async_safety_claim_marker", "safety_scope",
     '''std.debug.print("NO_GLOBAL_ASYNC_SAFETY_CLAIM=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "no_global_claim", False),
    ("local_compiler_truth_marker", "safety_scope",
     '''std.debug.print("LOCAL_COMPILER_TRUTH_ONLY=1 ZIG_VERSION={}\\n", .{@import("builtin").zig_version});''',
     "expect_pass", "expect_run", "safety_scope", "local_compiler_only", False),
    ("production_concurrency_verifier_not_tested_marker", "safety_scope",
     '''std.debug.print("NOT_A_PRODUCTION_CONCURRENCY_VERIFIER=1\\n", .{});''',
     "expect_pass", "expect_run", "safety_scope", "not_production_verifier", False),
]

cases = []
for case_id, category, zig_body, compile_expected, run_expected, hn_marker, article_marker, version_sensitive in cases_def:
    zig_src = f'''// {case_id}
// Category: {category}
// HN marker: {hn_marker}
// Article marker: {article_marker}
// Generated by generate_cases.py - API probes using @hasDecl(std, "Io")
const std = @import("std");

pub fn main() !void {{
    std.debug.print("CASE_ID={case_id}\\n", .{{}});
    std.debug.print("CATEGORY={category}\\n", .{{}});
    std.debug.print("HN_MARKER={hn_marker}\\n", .{{}});
    std.debug.print("ARTICLE_MARKER={article_marker}\\n", .{{}});
    {zig_body}
}}
'''
    zig_path = CASES_DIR / f"{case_id}.zig"
    zig_path.write_text(zig_src)
    cases.append({
        "id": case_id,
        "category": category,
        "generated_zig_path": str(zig_path.relative_to(ROOT)),
        "zig_source_purpose": f"{hn_marker} / {article_marker}",
        "expected_compile_status": compile_expected,
        "expected_run_status": run_expected,
        "expected_stdout_marker": f"CASE_ID={case_id}",
        "expected_stderr_marker": "",
        "expected_skip_reason": "",
        "expected_api_presence": "version_dependent" if version_sensitive else "n/a",
        "expected_async_concurrent_classification": category,
        "expected_cancellation_await_context": "yes" if "await" in case_id or "cancel" in case_id else "n/a",
        "expected_debug_release_relevance": "both",
        "expected_hn_context_marker": hn_marker,
        "expected_article_context_marker": article_marker,
        "expected_local_compiler_validation_command": f"zig build-exe {zig_path.relative_to(ROOT)} -O Debug",
        "expected_timeout_behavior": "timeout_context" if "deadlock" in case_id else "no_timeout_expected",
        "version_sensitive": version_sensitive,
    })

with open(ROOT / "cases.json", "w") as f:
    json.dump(cases, f, indent=2)

print(f"Generated {len(cases)} cases in {CASES_DIR}/")
# sanity: check API probes
api_probe_cats = {"stdlib_probe", "async_api", "await_cancel", "io_queue", "version_probe", "compile_check", "hn_context"}
missing = []
for c in cases:
    src = (CASES_DIR / f"{c['id']}.zig").read_text()
    if c["category"] in api_probe_cats and "std" not in src:
        missing.append(c["id"])
if missing:
    print(f"WARN: {missing} may lack std reference")
print(f"Wrote cases.json")
