#!/usr/bin/env python3
"""
Generate deterministic Zig case files for std.Io async IO footgun lab.
No network, no external payloads.
"""
import json, os, sys
from pathlib import Path

ROOT = Path(__file__).parent
CASES_DIR = ROOT / "generated_cases"
CASES_DIR.mkdir(exist_ok=True)

cases = [
    # version / env probes
    {"id":"local_zig_version_marker","category":"version_probe","purpose":"record local zig version","compile_expected":"probe","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"version_sensitive","version_sensitive":True},
    {"id":"zig_env_std_dir_marker","category":"version_probe","purpose":"zig env std dir probe","compile_expected":"probe","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"version_sensitive","version_sensitive":True},
    {"id":"std_io_namespace_probe_marker","category":"stdlib_probe","purpose":"check std.Io exists","compile_expected":"probe","run_expected":"skip","hn_marker":"standard_library_abstraction","article_marker":"std_io_design","version_sensitive":True},
    {"id":"std_io_threaded_exists_marker","category":"stdlib_probe","purpose":"check std.Io.Threaded exists","compile_expected":"probe","run_expected":"skip","hn_marker":"standard_library_abstraction","article_marker":"std_io_threaded","version_sensitive":True},
    {"id":"std_io_type_shape_marker","category":"stdlib_probe","purpose":"probe Io type shape","compile_expected":"probe","run_expected":"skip","hn_marker":"library_boundary_io","article_marker":"std_io_design","version_sensitive":True},
    {"id":"io_sleep_probe_marker","category":"stdlib_probe","purpose":"check io.sleep exists","compile_expected":"probe","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"async_model","version_sensitive":True},

    # async / concurrent API
    {"id":"io_async_exists_marker","category":"async_api","purpose":"check io.async exists","compile_expected":"probe","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"io_async","version_sensitive":True},
    {"id":"io_concurrent_exists_marker","category":"async_api","purpose":"check io.concurrent exists","compile_expected":"probe","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"io_concurrent","version_sensitive":True},
    {"id":"async_concurrent_renamed_context_marker","category":"async_api","purpose":"API renaming correction context","compile_expected":"probe","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"api_renaming","version_sensitive":True},
    {"id":"future_await_exists_marker","category":"await_cancel","purpose":"check future.await exists","compile_expected":"probe","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"await_api","version_sensitive":True},
    {"id":"future_cancel_exists_marker","category":"await_cancel","purpose":"check future.cancel exists","compile_expected":"probe","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"cancel_api","version_sensitive":True},

    # await / cancel ordering
    {"id":"await_idempotent_context_marker","category":"await_cancel","purpose":"await idempotency context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"await_ordering","version_sensitive":True},
    {"id":"cancel_idempotent_context_marker","category":"await_cancel","purpose":"cancel idempotency context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"cancel_ordering","version_sensitive":True},
    {"id":"cancel_cleanup_context_marker","category":"await_cancel","purpose":"cancel as cleanup context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"cancel_cleanup","version_sensitive":True},
    {"id":"try_before_second_await_footgun_marker","category":"await_cancel","purpose":"try before second await footgun","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"await_ordering","version_sensitive":True},
    {"id":"await_then_try_ordering_marker","category":"await_cancel","purpose":"await then try ordering","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"await_ordering","version_sensitive":True},
    {"id":"defer_cancel_cleanup_marker","category":"await_cancel","purpose":"defer cancel cleanup","compile_expected":"may_fail","run_expected":"skip","hn_marker":"cancellation_await_ordering","article_marker":"cancel_cleanup","version_sensitive":True},

    # async vs concurrent
    {"id":"async_not_concurrency_context_marker","category":"async_context","purpose":"async is not concurrency","compile_expected":"may_fail","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"async_model","version_sensitive":True},
    {"id":"concurrent_required_context_marker","category":"concurrent_context","purpose":"concurrent required context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"concurrent_required","version_sensitive":True},
    {"id":"concurrency_unavailable_context_marker","category":"concurrent_context","purpose":"error.ConcurrencyUnavailable context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"deadlock_concurrency_unavailable","article_marker":"concurrency_unavailable","version_sensitive":True},

    # Io.Queue
    {"id":"io_queue_exists_marker","category":"io_queue","purpose":"check Io.Queue exists","compile_expected":"probe","run_expected":"skip","hn_marker":"standard_library_abstraction","article_marker":"io_queue","version_sensitive":True},
    {"id":"io_queue_put_get_context_marker","category":"io_queue","purpose":"Io.Queue put/get context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"standard_library_abstraction","article_marker":"io_queue","version_sensitive":True},

    # deadlock
    {"id":"single_threaded_deadlock_context_marker","category":"deadlock","purpose":"single-threaded deadlock context","compile_expected":"may_fail","run_expected":"skip_timeout","hn_marker":"deadlock_concurrency_unavailable","article_marker":"deadlock","version_sensitive":True},
    {"id":"deadlock_not_run_timeout_marker","category":"deadlock","purpose":"deadlock NOT run, timeout guard","compile_expected":"skip","run_expected":"skip","hn_marker":"deadlock_concurrency_unavailable","article_marker":"deadlock","version_sensitive":False},
    {"id":"threaded_pool_context_marker","category":"deadlock","purpose":"threaded pool context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"async_vs_concurrent","article_marker":"threaded_io","version_sensitive":True},

    # HN debate markers
    {"id":"function_coloring_debate_marker","category":"hn_context","purpose":"function coloring debate","compile_expected":"n/a","run_expected":"skip","hn_marker":"function_coloring","article_marker":"function_coloring","version_sensitive":False},
    {"id":"io_effect_token_context_marker","category":"hn_context","purpose":"IO / effect token context","compile_expected":"n/a","run_expected":"skip","hn_marker":"effect_token","article_marker":"io_effect","version_sensitive":False},
    {"id":"allocator_vs_io_comparison_marker","category":"hn_context","purpose":"allocator vs IO comparison","compile_expected":"n/a","run_expected":"skip","hn_marker":"allocator_vs_io","article_marker":"allocator_comparison","version_sensitive":False},
    {"id":"library_boundary_io_context_marker","category":"hn_context","purpose":"library boundary IO context","compile_expected":"n/a","run_expected":"skip","hn_marker":"library_boundary_io","article_marker":"library_boundary","version_sensitive":False},
    {"id":"local_reasoning_limit_marker","category":"hn_context","purpose":"local reasoning limit","compile_expected":"n/a","run_expected":"skip","hn_marker":"local_reasoning","article_marker":"local_reasoning","version_sensitive":False},
    {"id":"standard_library_abstraction_context_marker","category":"hn_context","purpose":"stdlib abstraction level debate","compile_expected":"n/a","run_expected":"skip","hn_marker":"standard_library_abstraction","article_marker":"stdlib_abstraction","version_sensitive":False},

    # version / compile markers
    {"id":"pre_1_0_api_changed_marker","category":"version_probe","purpose":"pre-1.0 API churn marker","compile_expected":"probe","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"version_sensitive","version_sensitive":True},
    {"id":"compile_error_capture_marker","category":"compile_check","purpose":"compile error capture test","compile_expected":"may_fail","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"compile_validation","version_sensitive":True},
    {"id":"release_safe_build_context_marker","category":"build_mode","purpose":"ReleaseSafe build context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"build_mode","version_sensitive":True},
    {"id":"debug_build_context_marker","category":"build_mode","purpose":"Debug build context","compile_expected":"may_fail","run_expected":"skip","hn_marker":"pre_1_0_api_changed","article_marker":"build_mode","version_sensitive":True},

    # safety scope markers
    {"id":"no_network_io_marker","category":"safety_scope","purpose":"no network IO in lab","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_network","version_sensitive":False},
    {"id":"no_tls_marker","category":"safety_scope","purpose":"no TLS in lab","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_tls","version_sensitive":False},
    {"id":"no_socket_listener_marker","category":"safety_scope","purpose":"no socket listener","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_socket","version_sensitive":False},
    {"id":"no_external_payload_marker","category":"safety_scope","purpose":"no external payload","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_external","version_sensitive":False},
    {"id":"no_package_manager_marker","category":"safety_scope","purpose":"no package manager","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_pkg_mgr","version_sensitive":False},
    {"id":"no_global_async_safety_claim_marker","category":"safety_scope","purpose":"no global safety claim","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"no_global_claim","version_sensitive":False},
    {"id":"local_compiler_truth_marker","category":"safety_scope","purpose":"local compiler truth only","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"local_compiler_only","version_sensitive":False},
    {"id":"production_concurrency_verifier_not_tested_marker","category":"safety_scope","purpose":"not a production concurrency verifier","compile_expected":"n/a","run_expected":"skip","hn_marker":"safety_scope","article_marker":"not_production_verifier","version_sensitive":False},
]

zig_template = """// {id}
// Category: {category}
// Purpose: {purpose}
// HN marker: {hn_marker}
// Article marker: {article_marker}
// Generated by generate_cases.py - deterministic
const std = @import("std");

pub fn main() !void {{
    // Marker case: {id}
    // Purpose: {purpose}
    // This is a minimal probe stub. Real API validation depends on local Zig version.
    std.debug.print("CASE_ID={id}\\n", .{{}});
    std.debug.print("CATEGORY={category}\\n", .{{}});
    std.debug.print("HN_MARKER={hn_marker}\\n", .{{}});
    std.debug.print("ARTICLE_MARKER={article_marker}\\n", .{{}});
}}
"""

for c in cases:
    zig_path = CASES_DIR / f"{c['id']}.zig"
    src = zig_template.format(**c)
    zig_path.write_text(src)
    c["generated_zig_path"] = str(zig_path.relative_to(ROOT))
    c["zig_source_purpose"] = c["purpose"]
    c["expected_compile_status"] = c.pop("compile_expected")
    c["expected_run_status"] = c.pop("run_expected")
    c["expected_stdout_marker"] = f"CASE_ID={c['id']}"
    c["expected_stderr_marker"] = ""
    c["expected_skip_reason"] = "version_probe_or_hn_context" if c["expected_compile_status"] in ("probe","n/a","may_fail","skip") else ""
    c["expected_api_presence"] = "version_dependent"
    c["expected_async_concurrent_classification"] = c["category"]
    c["expected_cancellation_await_context"] = "context_marker" if "await" in c["id"] or "cancel" in c["id"] else "n/a"
    c["expected_debug_release_relevance"] = "both"
    c["expected_hn_context_marker"] = c["hn_marker"]
    c["expected_article_context_marker"] = c["article_marker"]
    c["expected_local_compiler_validation_command"] = f"zig build-exe {c['generated_zig_path']} -O Debug"
    c["expected_timeout_behavior"] = "timeout_context" if "deadlock" in c["id"] else "no_timeout_expected"
    # cleanup temp keys
    c.pop("purpose", None)

# write cases.json
with open(ROOT / "cases.json", "w") as f:
    json.dump(cases, f, indent=2)

print(f"Generated {len(cases)} cases in {CASES_DIR}/")
print(f"Wrote cases.json")
