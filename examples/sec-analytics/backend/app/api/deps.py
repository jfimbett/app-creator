"""Shared request dependencies."""

from fastapi import Request

from app.data.fixtures import FixtureStore
from app.data.source import DataSource
from app.settings import Settings


def get_store(request: Request) -> FixtureStore:
    """The fixture store loaded at startup by `create_app`."""
    return request.app.state.store


def get_data(request: Request) -> DataSource:
    """The per-app data layer (fixtures, cache, SEC)."""
    return request.app.state.data


def get_settings(request: Request) -> Settings:
    """The validated settings of this app instance."""
    return request.app.state.settings
