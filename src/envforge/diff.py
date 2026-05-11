"""
Diff engine - compare environments between machines or snapshots.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class DiffResult:
    """Result of environment comparison."""
    tool_diffs: List[Dict] = field(default_factory=list)
    lang_diffs: List[Dict] = field(default_factory=list)
    dep_diffs: List[Dict] = field(default_factory=list)
    config_diffs: List[Dict] = field(default_factory=list)
    missing_local: List[str] = field(default_factory=list)
    missing_remote: List[str] = field(default_factory=list)
    version_mismatches: List[Dict] = field(default_factory=list)


class DiffEngine:
    """Compare two environment snapshots and generate migration guide."""

    def __init__(self, snapshot_a: dict, snapshot_b: dict):
        self.snapshot_a = snapshot_a  # Source / local
        self.snapshot_b = snapshot_b  # Target / remote

    def compare(self) -> DiffResult:
        """Run full comparison between two snapshots."""
        result = DiffResult()
        result.tool_diffs = self._compare_tools()
        result.lang_diffs = self._compare_languages()
        result.dep_diffs = self._compare_dependencies()
        result.config_diffs = self._compare_configs()
        return result

    def _compare_tools(self) -> List[Dict]:
        """Compare installed tools."""
        diffs = []
        tools_a = self.snapshot_a.get("tools", {})
        tools_b = self.snapshot_b.get("tools", {})

        all_tools = sorted(set(list(tools_a.keys()) + list(tools_b.keys())))

        for tool in all_tools:
            ver_a = tools_a.get(tool, "")
            ver_b = tools_b.get(tool, "")

            if ver_a and not ver_b:
                diffs.append({
                    "tool": tool,
                    "type": "missing_remote",
                    "local_version": ver_a,
                    "message": f"{tool} is installed locally ({ver_a}) but not on remote",
                })
            elif ver_b and not ver_a:
                diffs.append({
                    "tool": tool,
                    "type": "missing_local",
                    "remote_version": ver_b,
                    "message": f"{tool} is installed on remote ({ver_b}) but not locally",
                })
            elif ver_a != ver_b:
                diffs.append({
                    "tool": tool,
                    "type": "version_mismatch",
                    "local_version": ver_a,
                    "remote_version": ver_b,
                    "message": f"{tool} version differs: local={ver_a}, remote={ver_b}",
                })

        return diffs

    def _compare_languages(self) -> List[Dict]:
        """Compare detected languages."""
        diffs = []
        langs_a = {l["name"]: l for l in self.snapshot_a.get("languages", [])}
        langs_b = {l["name"]: l for l in self.snapshot_b.get("languages", [])}

        all_langs = sorted(set(list(langs_a.keys()) + list(langs_b.keys())))

        for lang in all_langs:
            info_a = langs_a.get(lang)
            info_b = langs_b.get(lang)

            if info_a and not info_b:
                diffs.append({
                    "language": lang,
                    "type": "missing_remote",
                    "message": f"{lang} detected locally but not on remote",
                })
            elif info_b and not info_a:
                diffs.append({
                    "language": lang,
                    "type": "missing_local",
                    "message": f"{lang} detected on remote but not locally",
                })

        return diffs

    def _compare_dependencies(self) -> List[Dict]:
        """Compare project dependencies."""
        diffs = []
        deps_a = self.snapshot_a.get("dependencies", {})
        deps_b = self.snapshot_b.get("dependencies", {})

        all_ecosystems = sorted(set(list(deps_a.keys()) + list(deps_b.keys())))

        for eco in all_ecosystems:
            pkgs_a = set(deps_a.get(eco, []))
            pkgs_b = set(deps_b.get(eco, []))

            only_a = pkgs_a - pkgs_b
            only_b = pkgs_b - pkgs_a

            if only_a:
                diffs.append({
                    "ecosystem": eco,
                    "type": "extra_local",
                    "packages": sorted(only_a),
                    "message": f"Dependencies only in local {eco}: {', '.join(sorted(only_a)[:5])}",
                })

            if only_b:
                diffs.append({
                    "ecosystem": eco,
                    "type": "extra_remote",
                    "packages": sorted(only_b),
                    "message": f"Dependencies only in remote {eco}: {', '.join(sorted(only_b)[:5])}",
                })

        return diffs

    def _compare_configs(self) -> List[Dict]:
        """Compare configuration files."""
        diffs = []
        configs_a = set(self.snapshot_a.get("config_files", []))
        configs_b = set(self.snapshot_b.get("config_files", []))

        only_a = configs_a - configs_b
        only_b = configs_b - configs_a

        if only_a:
            diffs.append({
                "type": "missing_remote",
                "files": sorted(only_a),
                "message": f"Config files only in local: {', '.join(sorted(only_a)[:5])}",
            })

        if only_b:
            diffs.append({
                "type": "missing_local",
                "files": sorted(only_b),
                "message": f"Config files only in remote: {', '.join(sorted(only_b)[:5])}",
            })

        return diffs

    def generate_migration_guide(self, diff: DiffResult) -> str:
        """Generate a migration guide based on diff results."""
        lines = [
            "# Environment Migration Guide",
            "",
            "## Tool Installation",
            "",
        ]

        if diff.tool_diffs:
            for td in diff.tool_diffs:
                if td["type"] == "missing_remote":
                    lines.append(f"- Install {td['tool']} {td.get('local_version', '')}")
                elif td["type"] == "version_mismatch":
                    lines.append(f"- Update {td['tool']}: {td.get('remote_version', '')} -> {td.get('local_version', '')}")
        else:
            lines.append("- All tools are in sync ✓")

        lines.extend(["", "## Dependencies", ""])

        if diff.dep_diffs:
            for dd in diff.dep_diffs:
                lines.append(f"- {dd['message']}")
        else:
            lines.append("- All dependencies are in sync ✓")

        lines.extend(["", "## Configuration Files", ""])

        if diff.config_diffs:
            for cd in diff.config_diffs:
                lines.append(f"- {cd['message']}")
        else:
            lines.append("- All configuration files are in sync ✓")

        return "\n".join(lines)

    def format_diff_report(self, diff: DiffResult) -> str:
        """Format diff results as a readable report."""
        lines = [
            "╔══════════════════════════════════════════════╗",
            "║       EnvForge Environment Diff Report       ║",
            "╚══════════════════════════════════════════════╝",
            "",
        ]

        # Tool diffs
        lines.append(f"🔧 Tools: {len(diff.tool_diffs)} difference(s)")
        for td in diff.tool_diffs:
            icon = {"missing_remote": "➡️", "missing_local": "⬅️", "version_mismatch": "🔄"}.get(td["type"], "❓")
            lines.append(f"   {icon} {td['message']}")
        lines.append("")

        # Language diffs
        lines.append(f"📝 Languages: {len(diff.lang_diffs)} difference(s)")
        for ld in diff.lang_diffs:
            icon = "➡️" if ld["type"] == "missing_remote" else "⬅️"
            lines.append(f"   {icon} {ld['message']}")
        lines.append("")

        # Dependency diffs
        lines.append(f"📦 Dependencies: {len(diff.dep_diffs)} difference(s)")
        for dd in diff.dep_diffs:
            icon = "➡️" if dd["type"] == "extra_local" else "⬅️"
            lines.append(f"   {icon} {dd['message']}")
        lines.append("")

        # Config diffs
        lines.append(f"⚙️  Config Files: {len(diff.config_diffs)} difference(s)")
        for cd in diff.config_diffs:
            icon = "➡️" if cd["type"] == "missing_remote" else "⬅️"
            lines.append(f"   {icon} {cd['message']}")

        total = len(diff.tool_diffs) + len(diff.lang_diffs) + len(diff.dep_diffs) + len(diff.config_diffs)
        lines.extend([
            "",
            "─" * 50,
            f"Total differences: {total}",
        ])

        return "\n".join(lines)
