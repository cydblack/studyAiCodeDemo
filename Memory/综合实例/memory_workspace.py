"""文件记忆 Workspace:承接 run.py 需要的 ingest / search / build_context。

当前安装的 Agently 4.1 没有 Agently.create_workspace。
库里的 TaskWorkspace 是任务文件沙箱,不是记忆库。
本模块按综合实例已经在用的接口,把记录落在本地目录。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from memory_pipeline import score_text


class FileMemoryWorkspace:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._records_path = self.root / "records.jsonl"
        self._records: list[dict[str, Any]] = []

    def _persist(self) -> None:
        self._records_path.write_text(
            "\n".join(json.dumps(row, ensure_ascii=False) for row in self._records)
            + ("\n" if self._records else ""),
            encoding="utf-8",
        )

    async def ingest(
        self,
        *,
        content: Any,
        collection: str,
        kind: str,
        summary: str,
        scope: dict[str, Any],
        source: dict[str, Any],
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        record = {
            "id": f"{collection}-{len(self._records) + 1:03d}",
            "collection": collection,
            "kind": kind,
            "summary": summary,
            "scope": scope,
            "source": source,
            "meta": meta or {},
            "content": content,
        }
        self._records.append(record)
        self._persist()
        return record

    async def search(
        self,
        query: str | None,
        *,
        filters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        matched = [
            record
            for record in self._records
            if _match_filters(record, filters or {})
        ]
        if query:
            matched.sort(
                key=lambda record: score_text(str(record.get("summary", "")), query),
                reverse=True,
            )
        return matched

    async def build_context(
        self,
        *,
        goal: str,
        scope: dict[str, Any],
        budget: dict[str, int],
        profile: str,
    ) -> dict[str, Any]:
        del profile
        candidates = [
            record
            for record in self._records
            if _scope_contains(record.get("scope") or {}, scope)
        ]
        ranked = sorted(
            candidates,
            key=lambda record: score_text(str(record.get("summary", "")), goal),
            reverse=True,
        )
        max_chars = int(budget.get("chars", 1600))
        item_chars = int(budget.get("item_chars", 400))
        items: list[dict[str, Any]] = []
        used_chars = 0
        for record in ranked:
            summary = str(record.get("summary", ""))[:item_chars]
            if used_chars + len(summary) > max_chars:
                break
            used_chars += len(summary)
            items.append(
                {
                    "ref": {
                        "id": record["id"],
                        "collection": record["collection"],
                    },
                    "kind": record["kind"],
                    "summary": summary,
                }
            )
        return {
            "items": items,
            "diagnostics": {"candidate_count": len(candidates)},
        }


def _match_filters(record: dict[str, Any], filters: dict[str, Any]) -> bool:
    for key, expected in filters.items():
        value: Any = record
        for part in key.split("."):
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(part)
        if value != expected:
            return False
    return True


def _scope_contains(record_scope: dict[str, Any], required: dict[str, Any]) -> bool:
    return all(record_scope.get(key) == value for key, value in required.items())
