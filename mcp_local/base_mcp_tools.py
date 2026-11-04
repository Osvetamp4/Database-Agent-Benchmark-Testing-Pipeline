from abc import ABC, abstractmethod

class MCPTools(ABC):

    @abstractmethod
    async def check_is_local(self):
        """Determines if the dataset is local or not"""
        pass

    @abstractmethod
    async def list_data_sources(self):
        """List configured databases, files, buckets, or collections"""
        pass

    @abstractmethod
    async def get_source_metadata(self):
        """Return source type, location, size, encoding, and last-modified information"""
        pass

    @abstractmethod
    async def list_objects(self):
        """List tables, collections, files, sheets, or directories"""
        pass

    @abstractmethod
    async def describe_object(self):
        """Return columns, fields, types, indexes, or metadata"""
        pass

    @abstractmethod
    async def preview_object(self):
        """Return a small, bounded sample"""
        pass

    @abstractmethod
    async def count_records(self):
        """Count rows, documents, or records"""
        pass

    @abstractmethod
    async def search_records(self):
        """Search for matching values or text"""
        pass

    @abstractmethod
    async def summarize_objects(self):
        """Inspect unique values for a field or column"""
        pass

    @abstractmethod
    async def validate_sources(self):
        """Check whether the source is readable and structurally valid"""
        pass

    @abstractmethod
    async def check_source_status(self):
        """Check connectivity and availability"""
        pass

