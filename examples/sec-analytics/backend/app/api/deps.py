"""Shared request dependencies."""

from fastapi import Request

from app.data.fixtures import FixtureStore
from app.settings import Settings


def get_store(request: Request) -> FixtureStore:
    """The fixture store loaded at startup by `create_app`."""
    return request.app.state.store


def get_settings(request: Request) -> Settings:
    """The validated settings of this app instance."""
    return request.app.state.settings
