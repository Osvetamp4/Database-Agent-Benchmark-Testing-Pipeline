from abc import ABC, abstractmethod
from typing import Any


class MCPTools(ABC):
    @abstractmethod
    async def check_is_local(self) -> bool:
        """Return whether the selected data source is local."""
        ...

    @abstractmethod
    async def list_data_sources(self) -> list[str]:
        """List configured databases, files, buckets, or collections."""
        ...

    @abstractmethod
    async def get_source_metadata(self, source: str) -> dict[str, Any]:
        """Return metadata for one configured source."""
        ...

    @abstractmethod
    async def list_objects(self, source: str | None = None) -> list[str]:
        """List tables, collections, files, sheets, or directories."""
        ...

    @abstractmethod
    async def describe_object(self, source: str) -> dict[str, Any]:
        """Return columns, fields, types, indexes, or metadata."""
        ...

    @abstractmethod
    async def preview_object(
        self,
        source: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return a bounded sample from one object."""
        ...

    @abstractmethod
    async def count_records(self, source: str) -> int:
        """Count rows, documents, or records in one object."""
        ...

    @abstractmethod
    async def search_records(
        self,
        source: str,
        column: str,
        value: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return records matching a field value."""
        ...

    @abstractmethod
    async def summarize_objects(self, source: str) -> dict[str, Any]:
        """Return counts and basic field summaries for one object."""
        ...

    @abstractmethod
    async def validate_sources(self) -> dict[str, Any]:
        """Check whether configured sources are readable and valid."""
        ...

    @abstractmethod
    async def check_source_status(self) -> dict[str, Any]:
        """Check source connectivity and availability."""
        ...
