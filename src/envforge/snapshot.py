"""
Snapshot manager - create, load, save, and manage environment snapshots.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


SNAPSHOT_DIR = ".envforge"
SNAPSHOT_FILE = "envforge.snapshot.json"
SNAPSHOT_HISTORY_DIR = "snapshots"


class SnapshotManager:
    """Manage environment snapshots."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.snapshot_dir = self.project_path / SNAPSHOT_DIR
        self.history_dir = self.snapshot_dir / SNAPSHOT_HISTORY_DIR

    def save(self, snapshot: dict, name: Optional[str] = None) -> str:
        """Save a snapshot to disk."""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        # Add metadata
        snapshot_data = {
            **snapshot,
            "saved_at": datetime.now().isoformat(),
            "snapshot_name": name or "default",
        }

        # Save current snapshot
        snapshot_path = self.snapshot_dir / SNAPSHOT_FILE
        snapshot_path.write_text(json.dumps(snapshot_data, indent=2, ensure_ascii=False))

        # Save to history
        self.history_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_name = name or "auto"
        history_path = self.history_dir / f"{timestamp}_{history_name}.json"
        history_path.write_text(json.dumps(snapshot_data, indent=2, ensure_ascii=False))

        return str(snapshot_path)

    def load(self, filepath: Optional[str] = None) -> Optional[dict]:
        """Load a snapshot from disk."""
        if filepath:
            path = Path(filepath)
        else:
            path = self.snapshot_dir / SNAPSHOT_FILE

        if not path.exists():
            return None

        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def load_history(self) -> list:
        """Load all historical snapshots."""
        if not self.history_dir.exists():
            return []

        snapshots = []
        for filepath in sorted(self.history_dir.glob("*.json"), reverse=True):
            try:
                data = json.loads(filepath.read_text())
                data["_filepath"] = str(filepath)
                snapshots.append(data)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

        return snapshots

    def list_snapshots(self) -> list:
        """List available snapshots with metadata."""
        history = self.load_history()
        result = []
        for snap in history:
            result.append({
                "name": snap.get("snapshot_name", "unknown"),
                "saved_at": snap.get("saved_at", ""),
                "os": snap.get("os_info", {}).get("system", ""),
                "languages": [l["name"] for l in snap.get("languages", [])],
                "filepath": snap.get("_filepath", ""),
            })
        return result

    def export(self, snapshot: dict, output_path: str) -> str:
        """Export snapshot to a portable file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False))
        return str(path)

    def import_snapshot(self, filepath: str) -> Optional[dict]:
        """Import snapshot from a file."""
        path = Path(filepath)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def compare_with_current(self, saved_snapshot: dict, current_snapshot: dict) -> dict:
        """Quick comparison between saved and current snapshot."""
        from .diff import DiffEngine
        engine = DiffEngine(saved_snapshot, current_snapshot)
        diff = engine.compare()
        return {
            "tool_diffs": diff.tool_diffs,
            "lang_diffs": diff.lang_diffs,
            "dep_diffs": diff.dep_diffs,
            "total_diffs": len(diff.tool_diffs) + len(diff.lang_diffs) + len(diff.dep_diffs),
        }
