from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata, CheckpointTuple

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / '.meridian' / 'checkpoints.db'

from langgraph.checkpoint.base import Checkpoint, CheckpointMetadata, CheckpointTuple
# no longer needed - defined locally
def pending_write_sort_key(task_path: str, task_id: str = '', idx: int = 0) -> tuple:
    return (task_path, task_id, idx)
