import csv
import os
from collections import Counter
from pathlib import Path
from typing import Any

from base_mcp_tools import MCPTools


class CSVTools(MCPTools):
    """Provide bounded inspection tools for CSV files in a local directory."""

    def __init__(self) -> None:
        self.data_dir = Path(
            os.getenv("DATA_DIR", "/app/data")
        ).resolve()
        self.encoding = os.getenv("CSV_ENCODING", "utf-8")
        self.delimiter = os.getenv("CSV_DELIMITER", ",")
        self.preview_limit = self._read_limit("CSV_PREVIEW_LIMIT", 20)
        self.max_results = self._read_limit("CSV_MAX_RESULTS", 100)

        if len(self.delimiter) != 1:
            raise ValueError("CSV_DELIMITER must contain exactly one character")

    @staticmethod
    def _read_limit(name: str, default: int) -> int:
        value = int(os.getenv(name, str(default)))
        if value < 1:
            raise ValueError(f"{name} must be greater than zero")
        return value

    def _resolve_source(self, source: str) -> Path:
        """Resolve a CSV source without allowing access outside DATA_DIR."""
        candidate = (self.data_dir / source).resolve()

        if candidate != self.data_dir and self.data_dir not in candidate.parents:
            raise ValueError("CSV source must remain inside DATA_DIR")
        if candidate.suffix.lower() != ".csv":
            raise ValueError("CSV source must have a .csv extension")
        if not candidate.is_file():
            raise FileNotFoundError(f"CSV source does not exist: {source}")

        return candidate

    def _source_name(self, path: Path) -> str:
        return str(path.relative_to(self.data_dir))

    def _read_rows(self, path: Path) -> tuple[list[str], list[dict[str, str]]]:
        with path.open(newline="", encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
        return fieldnames, rows

    async def check_is_local(self) -> bool:
        """Return whether this backend reads local files."""
        return True

    async def list_data_sources(self) -> list[str]:
        """List CSV files below DATA_DIR."""
        if not self.data_dir.is_dir():
            return []

        return sorted(
            self._source_name(path)
            for path in self.data_dir.rglob("*.csv")
            if path.is_file()
        )

    async def get_source_metadata(self, source: str) -> dict[str, Any]:
        """Return metadata for one CSV file."""
        path = self._resolve_source(source)
        stat = path.stat()
        return {
            "source": source,
            "size_bytes": stat.st_size,
            "last_modified": stat.st_mtime,
        }

    async def list_objects(self, source: str | None = None) -> list[str]:
        """List CSV files as the backend's available data objects."""
        if source is not None:
            self._resolve_source(source)
            return [source]
        return await self.list_data_sources()

    async def describe_object(self, source: str) -> dict[str, Any]:
        """Describe the columns and row count for one CSV source."""
        path = self._resolve_source(source)
        fieldnames, rows = self._read_rows(path)
        return {
            "source": source,
            "columns": fieldnames,
            "column_count": len(fieldnames),
            "record_count": len(rows),
        }

    async def preview_object(
        self,
        source: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return a bounded preview from one CSV source."""
        path = self._resolve_source(source)
        limit = min(max(limit, 1), self.max_results)

        with path.open(newline="", encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            return [row for _, row in zip(range(limit), reader)]

    async def count_records(self, source: str) -> int:
        """Count data rows in one CSV source."""
        path = self._resolve_source(source)
        with path.open(newline="", encoding=self.encoding) as file:
            reader = csv.reader(file, delimiter=self.delimiter)
            next(reader, None)
            return sum(1 for _ in reader)

    async def search_records(
        self,
        source: str,
        column: str,
        value: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return CSV rows whose column exactly matches value."""
        path = self._resolve_source(source)
        limit = min(max(limit, 1), self.max_results)

        with path.open(newline="", encoding=self.encoding) as file:
            reader = csv.DictReader(file, delimiter=self.delimiter)
            if column not in (reader.fieldnames or []):
                raise ValueError(f"Unknown CSV column: {column}")

            matches = []
            for row in reader:
                if row.get(column) == value:
                    matches.append(row)
                    if len(matches) >= limit:
                        break
            return matches

    async def summarize_objects(self, source: str) -> dict[str, Any]:
        """Return row counts and distinct-value summaries for one CSV."""
        path = self._resolve_source(source)
        fieldnames, rows = self._read_rows(path)
        columns: dict[str, dict[str, Any]] = {}

        for fieldname in fieldnames:
            values = [row.get(fieldname, "") for row in rows]
            counts = Counter(values)
            columns[fieldname] = {
                "null_or_empty_count": sum(not value for value in values),
                "distinct_count": len(counts),
                "top_values": counts.most_common(10),
            }

        return {
            "source": source,
            "record_count": len(rows),
            "columns": columns,
        }

    async def validate_sources(self) -> dict[str, Any]:
        """Validate that each CSV source can be read and has headers."""
        errors: dict[str, str] = {}
        valid_sources = 0

        for source in await self.list_data_sources():
            try:
                path = self._resolve_source(source)
                with path.open(newline="", encoding=self.encoding) as file:
                    reader = csv.reader(file, delimiter=self.delimiter)
                    if not next(reader, None):
                        raise ValueError("CSV file has no header row")
                valid_sources += 1
            except (OSError, UnicodeError, csv.Error, ValueError) as error:
                errors[source] = str(error)

        return {
            "data_dir_exists": self.data_dir.is_dir(),
            "valid_source_count": valid_sources,
            "invalid_sources": errors,
            "valid": not errors and self.data_dir.is_dir(),
        }

    async def check_source_status(self) -> dict[str, Any]:
        """Report whether DATA_DIR is available and contains CSV sources."""
        sources = await self.list_data_sources()
        return {
            "status": "ready" if self.data_dir.is_dir() else "unavailable",
            "data_dir": str(self.data_dir),
            "source_count": len(sources),
        }
