from __future__ import annotations

import urllib.parse
from dataclasses import field
from typing import Optional

from pydantic import BaseModel, computed_field


class People(BaseModel):
    people: list[Person]


class NameAndRedirect(BaseModel):
    name: str

    @computed_field  # type: ignore[misc]
    @property
    def person_at(self) -> str:
        return f"http://localhost:8000/people/{urllib.parse.quote(self.name)}"


class Person(BaseModel):
    name: str
    nickname: Optional[str] = None
    parent_of: Optional[list[NameAndRedirect]] = field(default_factory=list)
    child_of: Optional[list[NameAndRedirect]] = field(
        default_factory=list
    )  # from the example data, it's 0..1 parent, but it could be a list in the future
    friends_with: Optional[list[NameAndRedirect]] = field(default_factory=list)

    @computed_field  # type: ignore[misc]
    @property
    def firstname(self) -> str:  # Not resilient to name that are not "x y" format
        return f"{self.name.split()[0]}"

    @computed_field  # type: ignore[misc]
    @property
    def lastname(self) -> str:
        return f"{self.name.split()[-1]}"

    @computed_field  # type: ignore[misc]
    @property
    def person_at(self) -> str:
        return f"http://localhost:8000/people/{urllib.parse.quote(self.name)}"

    @computed_field  # type: ignore[misc]
    @property
    def ancestors_at(self) -> str:
        return f"http://localhost:8000/people/{urllib.parse.quote(self.name)}/ancestors"
