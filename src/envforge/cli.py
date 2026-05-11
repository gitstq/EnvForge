"""
EnvForge CLI - Main entry point for the environment configuration engine.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from . import __version__
from .detector import EnvironmentDetector
from .generator import ConfigGenerator
from .health import HealthChecker, Severity
from .diff import DiffEngine
from .snapshot import SnapshotManager


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="envforge",
        description="🔧 EnvForge - Lightweight Development Environment Intelligent Configuration & Sync Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  envforge detect                  Detect current project environment
  envforge detect --json           Detect and output as JSON
  envforge generate                Generate all config files
  envforge generate --dockerfile   Generate only Dockerfile
  envforge snapshot create         Create environment snapshot
  envforge snapshot list           List saved snapshots
  envforge health                  Run health checks
  envforge diff snapshot.json      Compare with a snapshot file
  envforge info                    Show system info
        """,
    )

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # detect command
    detect_parser = subparsers.add_parser("detect", help="🔍 Detect project environment")
    detect_parser.add_argument("--path", "-p", default=".", help="Project path (default: current directory)")
    detect_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    detect_parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode, only show summary")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="⚡ Generate configuration files")
    gen_parser.add_argument("--path", "-p", default=".", help="Project path")
    gen_parser.add_argument("--output", "-o", default=".", help="Output directory")
    gen_parser.add_argument("--env-example", action="store_true", help="Generate .env.example only")
    gen_parser.add_argument("--dockerfile", action="store_true", help="Generate Dockerfile only")
    gen_parser.add_argument("--docker-compose", action="store_true", help="Generate docker-compose.yml only")
    gen_parser.add_argument("--makefile", action="store_true", help="Generate Makefile only")
    gen_parser.add_argument("--gitignore", action="store_true", help="Generate .gitignore only")
    gen_parser.add_argument("--tool-versions", action="store_true", help="Generate .tool-versions only")
    gen_parser.add_argument("--devcontainer", action="store_true", help="Generate devcontainer.json only")
    gen_parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    gen_parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing files")

    # snapshot command
    snap_parser = subparsers.add_parser("snapshot", help="📸 Manage environment snapshots")
    snap_sub = snap_parser.add_subparsers(dest="snap_command", help="Snapshot subcommands")
    snap_create = snap_sub.add_parser("create", help="Create a new snapshot")
    snap_create.add_argument("--name", "-n", default=None, help="Snapshot name")
    snap_create.add_argument("--path", "-p", default=".", help="Project path")
    snap_create.add_argument("--export", "-e", default=None, help="Export to file")
    snap_list = snap_sub.add_parser("list", help="List saved snapshots")
    snap_list.add_argument("--path", "-p", default=".", help="Project path")
    snap_show = snap_sub.add_parser("show", help="Show a specific snapshot")
    snap_show.add_argument("filepath", help="Path to snapshot file")
    snap_import = snap_sub.add_parser("import", help="Import a snapshot")
    snap_import.add_argument("filepath", help="Path to snapshot file to import")

    # health command
    health_parser = subparsers.add_parser("health", help="🏥 Run environment health checks")
    health_parser.add_argument("--path", "-p", default=".", help="Project path")
    health_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    health_parser.add_argument("--severity", "-s", default="info",
                               choices=["info", "warning", "error", "critical"],
                               help="Minimum severity level to show")

    # diff command
    diff_parser = subparsers.add_parser("diff", help="📊 Compare two environments")
    diff_parser.add_argument("target", help="Target snapshot file to compare with")
    diff_parser.add_argument("--path", "-p", default=".", help="Current project path")
    diff_parser.add_argument("--migration", "-m", action="store_true", help="Generate migration guide")
    diff_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # info command
    info_parser = subparsers.add_parser("info", help="ℹ️ Show system information")
    info_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    return parser


def cmd_detect(args):
    """Handle detect command."""
    detector = EnvironmentDetector(args.path)
    snapshot = detector.detect_all()

    if args.json:
        from dataclasses import asdict
        print(json.dumps(asdict(snapshot), indent=2, ensure_ascii=False))
        return

    if args.quiet:
        langs = ", ".join(l.name for l in snapshot.languages) if snapshot.languages else "None detected"
        fws = ", ".join(f.name for f in snapshot.frameworks) if snapshot.frameworks else "None detected"
        print(f"Languages: {langs}")
        print(f"Frameworks: {fws}")
        print(f"Tools: {len(snapshot.tools)} detected")
        return

    # Rich output
    print("╔══════════════════════════════════════════════════╗")
    print("║     🔧 EnvForge - Environment Detection Report   ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    # OS Info
    print(f"🖥️  OS: {snapshot.os_info.get('system', 'Unknown')} {snapshot.os_info.get('release', '')}")
    print(f"    Machine: {snapshot.os_info.get('machine', '')} | Python: {snapshot.os_info.get('python_version', '')}")
    print()

    # Languages
    print(f"📝 Languages ({len(snapshot.languages)}):")
    for lang in snapshot.languages:
        ver = f" v{lang.version}" if lang.version else ""
        print(f"   • {lang.name}{ver} ({lang.files_count} files)")
    if not snapshot.languages:
        print("   No languages detected")
    print()

    # Frameworks
    if snapshot.frameworks:
        print(f"🏗️  Frameworks ({len(snapshot.frameworks)}):")
        for fw in snapshot.frameworks:
            ver = f" v{fw.version}" if fw.version else ""
            print(f"   • {fw.name} ({fw.category}){ver}")
        print()

    # Package Managers
    if snapshot.package_managers:
        print(f"📦 Package Managers ({len(snapshot.package_managers)}):")
        for pm in snapshot.package_managers:
            ver = f" v{pm.version}" if pm.version else ""
            print(f"   • {pm.name}{ver}")
        print()

    # Tools
    if snapshot.tools:
        print(f"🛠️  Development Tools ({len(snapshot.tools)}):")
        tool_items = list(snapshot.tools.items())
        # Show in columns
        col_width = 20
        cols = max(1, 80 // (col_width + 25))
        for i in range(0, len(tool_items), cols):
            row = tool_items[i:i + cols]
            line = "  ".join(f"• {name:<{col_width}} {ver}" for name, ver in row)
            print(f"   {line}")
        print()

    # Config Files
    if snapshot.config_files:
        print(f"⚙️  Config Files ({len(snapshot.config_files)}):")
        for cf in snapshot.config_files[:15]:
            print(f"   • {cf}")
        if len(snapshot.config_files) > 15:
            print(f"   ... and {len(snapshot.config_files) - 15} more")
        print()

    # Dependencies summary
    if snapshot.dependencies:
        print("📚 Dependencies:")
        for eco, deps in snapshot.dependencies.items():
            print(f"   • {eco}: {len(deps)} packages")
        print()


def cmd_generate(args):
    """Handle generate command."""
    from dataclasses import asdict
    detector = EnvironmentDetector(args.path)
    snapshot_data = detector.detect_all()
    snapshot_dict = asdict(snapshot_data)

    generator = ConfigGenerator(snapshot_dict, args.output)

    if args.dry_run:
        print("🔍 Dry run - showing what would be generated:")
        print()

    # Determine which files to generate
    if args.env_example:
        files = {".env.example": generator._generate_env_example()}
    elif args.dockerfile:
        files = {"Dockerfile": generator._generate_dockerfile()}
    elif args.docker_compose:
        files = {"docker-compose.yml": generator._generate_docker_compose()}
    elif args.makefile:
        files = {"Makefile": generator._generate_makefile()}
    elif args.gitignore:
        files = {".gitignore": generator._generate_gitignore()}
    elif args.tool_versions:
        files = {".tool-versions": generator._generate_tool_versions()}
    elif args.devcontainer:
        content = generator._generate_devcontainer()
        files = {".devcontainer/devcontainer.json": content} if content else {}
    else:
        files = generator.generate_all()

    if not files:
        print("⚠️  No files to generate. Ensure you're in a project directory.")
        return

    generated_count = 0
    for filename, content in files.items():
        if not content:
            continue

        output_path = Path(args.output) / filename

        if args.dry_run:
            print(f"  ✅ {filename} ({len(content)} bytes)")
            continue

        if output_path.exists() and not args.force:
            print(f"  ⏭️  {filename} already exists (use --force to overwrite)")
            continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"  ✅ Generated: {filename}")
        generated_count += 1

    if args.dry_run:
        print(f"\n📋 Would generate {len(files)} file(s)")
    else:
        print(f"\n🎉 Generated {generated_count} file(s) successfully!")


def cmd_snapshot(args):
    """Handle snapshot command."""
    from dataclasses import asdict
    if args.snap_command == "create":
        detector = EnvironmentDetector(args.path)
        snapshot_data = detector.detect_all()
        snapshot_dict = asdict(snapshot_data)

        manager = SnapshotManager(args.path)
        path = manager.save(snapshot_dict, name=args.name)
        print(f"📸 Snapshot saved: {path}")

        if args.export:
            export_path = manager.export(snapshot_dict, args.export)
            print(f"📤 Exported to: {export_path}")

    elif args.snap_command == "list":
        manager = SnapshotManager(args.path)
        snapshots = manager.list_snapshots()

        if not snapshots:
            print("📭 No snapshots found. Run 'envforge snapshot create' first.")
            return

        print(f"📸 Snapshots ({len(snapshots)}):")
        for snap in snapshots:
            langs = ", ".join(snap["languages"][:3]) if snap["languages"] else "N/A"
            print(f"   • {snap['name']} | {snap['saved_at'][:19]} | {snap['os']} | {langs}")

    elif args.snap_command == "show":
        manager = SnapshotManager()
        data = manager.load(args.filepath)
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Could not load snapshot: {args.filepath}")

    elif args.snap_command == "import":
        manager = SnapshotManager()
        data = manager.import_snapshot(args.filepath)
        if data:
            print(f"✅ Imported snapshot from: {args.filepath}")
            print(f"   OS: {data.get('os_info', {}).get('system', 'Unknown')}")
            print(f"   Languages: {[l['name'] for l in data.get('languages', [])]}")
        else:
            print(f"❌ Could not import snapshot: {args.filepath}")

    else:
        print("❓ Use 'envforge snapshot create|list|show|import'")


def cmd_health(args):
    """Handle health command."""
    from dataclasses import asdict
    detector = EnvironmentDetector(args.path)
    snapshot_data = detector.detect_all()
    snapshot_dict = asdict(snapshot_data)

    checker = HealthChecker(snapshot_dict, args.path)
    report = checker.run_all_checks()

    if args.json:
        print(json.dumps({
            "score": report.score,
            "status": report.status,
            "total_checks": report.total_checks,
            "passed_checks": report.passed_checks,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "category": issue.category,
                    "message": issue.message,
                    "detail": issue.detail,
                    "suggestion": issue.suggestion,
                }
                for issue in report.issues
            ],
        }, indent=2, ensure_ascii=False))
        return

    severity_order = {Severity.CRITICAL: 0, Severity.ERROR: 1, Severity.WARNING: 2, Severity.INFO: 3}
    min_severity = severity_order.get(Severity(args.severity), 3)

    # Header
    status_icons = {"healthy": "🟢", "degraded": "🟡", "unhealthy": "🟠", "critical": "🔴"}
    icon = status_icons.get(report.status, "⚪")

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║      🏥 EnvForge - Environment Health Report     ║")
    print(f"╚══════════════════════════════════════════════════╝")
    print()
    print(f"{icon} Health Score: {report.score}/100 ({report.status})")
    print(f"   Checks: {report.passed_checks}/{report.total_checks} passed")
    print()

    if not report.issues:
        print("✅ All checks passed! Your environment looks healthy.")
        return

    # Group by severity
    severity_groups = {}
    for issue in report.issues:
        if severity_order.get(issue.severity, 3) >= min_severity:
            severity_groups.setdefault(issue.severity, []).append(issue)

    severity_icons = {
        Severity.CRITICAL: "🔴 CRITICAL",
        Severity.ERROR: "🟠 ERROR",
        Severity.WARNING: "🟡 WARNING",
        Severity.INFO: "🔵 INFO",
    }

    for sev in [Severity.CRITICAL, Severity.ERROR, Severity.WARNING, Severity.INFO]:
        if sev not in severity_groups:
            continue
        issues = severity_groups[sev]
        print(f"{severity_icons[sev]} ({len(issues)})")
        for issue in issues:
            print(f"   [{issue.category}] {issue.message}")
            if issue.suggestion:
                print(f"   💡 {issue.suggestion}")
            if issue.detail:
                for line in issue.detail.split("\n")[:3]:
                    print(f"      {line}")
            print()


def cmd_diff(args):
    """Handle diff command."""
    from dataclasses import asdict
    # Load target snapshot
    manager = SnapshotManager()
    target = manager.load(args.target)

    if not target:
        print(f"❌ Could not load snapshot: {args.target}")
        return

    # Detect current environment
    detector = EnvironmentDetector(args.path)
    snapshot_data = detector.detect_all()
    current = asdict(snapshot_data)

    engine = DiffEngine(target, current)
    diff = engine.compare()

    if args.json:
        print(json.dumps({
            "tool_diffs": diff.tool_diffs,
            "lang_diffs": diff.lang_diffs,
            "dep_diffs": diff.dep_diffs,
            "config_diffs": diff.config_diffs,
        }, indent=2, ensure_ascii=False))
        return

    if args.migration:
        guide = engine.generate_migration_guide(diff)
        print(guide)
    else:
        report = engine.format_diff_report(diff)
        print(report)


def cmd_info(args):
    """Handle info command."""
    import platform

    info = {
        "envforge_version": __version__,
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "hostname": platform.node(),
    }

    if args.json:
        print(json.dumps(info, indent=2))
        return

    print("╔══════════════════════════════════════════════════╗")
    print("║         ℹ️  EnvForge - System Information         ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    for key, value in info.items():
        print(f"  {key}: {value}")


def asdict_safe(obj):
    """Safely convert a dataclass to dict."""
    try:
        from dataclasses import asdict
        return asdict(obj)
    except (TypeError, AttributeError):
        return str(obj)


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "detect": cmd_detect,
        "generate": cmd_generate,
        "snapshot": cmd_snapshot,
        "health": cmd_health,
        "diff": cmd_diff,
        "info": cmd_info,
    }

    handler = commands.get(args.command)
    if handler:
        try:
            handler(args)
        except KeyboardInterrupt:
            print("\n👋 Operation cancelled.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
