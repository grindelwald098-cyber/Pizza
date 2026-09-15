from dataclasses import dataclass
from uuid import UUID


@dataclass
class UserPrincipal:
    id: UUID


@dataclass
class GuestPrincipal:
    id: UUID


Principal = UserPrincipal | GuestPrincipal