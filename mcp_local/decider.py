import os
import asyncio
import importlib
import importlib.util
import sys

database_name = os.getenv("DATABASE","CSV")