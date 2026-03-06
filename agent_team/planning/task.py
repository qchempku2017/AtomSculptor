from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
import uuid


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"
    DEPRECATED = "deprecated"

    def __str__(self):
        return super().__str__()


@dataclass
class Task:
    description: str
    id: int
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[int] = field(default_factory=list)
    result: Optional[str] = None

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "dependencies": self.dependencies,
            "result": self.result,
        }