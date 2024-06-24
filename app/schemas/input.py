from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, computed_field


class PersonInput(BaseModel):
    firstname: str
    lastname: str
    nickname: Optional[str] = None

    @computed_field  # type: ignore[misc]
    @property
    def name(self) -> str:
        return f"{self.firstname} {self.lastname}"


class ChildInput(BaseModel):
    child_name: str


class FriendInput(BaseModel):
    friend_name: str
