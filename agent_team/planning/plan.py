from typing import List, Optional
from .task import Task, TaskStatus


class Plan:
    """Task graph with O(1) lookup and structural validation.

    Manages the set of tasks and their dependency edges.  Every mutation
    re-validates the graph (dangling references, cycles) so the plan is
    always consistent.
    """

    def __init__(self, tasks: List[Task]):
        self._tasks: dict[int, Task] = {}
        for t in tasks:
            if t.id in self._tasks:
                raise ValueError(f"Duplicate task ID: {t.id}")
            self._tasks[t.id] = t
        self._validate()

    # -- read access -----------------------------------------------------------

    @property
    def tasks(self) -> List[Task]:
        """Ordered list view of all tasks (preserves insertion order)."""
        return list(self._tasks.values())

    @property
    def next_id(self) -> int:
        """Next available sequential task ID."""
        return max(self._tasks.keys(), default=0) + 1

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_task_by_uuid(self, uuid: str) -> Optional[Task]:
        for t in self._tasks.values():
            if t.uuid == uuid:
                return t
        return None

    # -- graph mutations -------------------------------------------------------

    def add_tasks(self, tasks: List[Task]):
        """Insert new tasks into the plan and re-validate."""
        for t in tasks:
            if t.id in self._tasks:
                raise ValueError(f"Duplicate task ID: {t.id}")
            self._tasks[t.id] = t
        self._validate()

    def deprecate_task(self, task_id: int):
        """Mark a task as deprecated and remove it from other tasks' deps."""
        task = self._get_or_raise(task_id)
        task.status = TaskStatus.DEPRECATED
        for t in self._tasks.values():
            if task_id in t.dependencies:
                t.dependencies.remove(task_id)

    def add_dependencies(self, task_id: int, dep_ids: List[int]):
        """Add dependency edges for *task_id* and re-check for cycles."""
        task = self._get_or_raise(task_id)
        for dep_id in dep_ids:
            if dep_id not in self._tasks:
                raise ValueError(f"Dependency target {dep_id} does not exist")
            if dep_id not in task.dependencies:
                task.dependencies.append(dep_id)
        self._check_cycles()

    def remove_dependencies(self, task_id: int, dep_ids: List[int]):
        """Remove dependency edges from *task_id*."""
        task = self._get_or_raise(task_id)
        task.dependencies = [d for d in task.dependencies if d not in dep_ids]

    # -- serialisation ---------------------------------------------------------

    def to_dict(self):
        return [t.to_dict() for t in self._tasks.values()]

    # -- internal --------------------------------------------------------------

    def _get_or_raise(self, task_id: int) -> Task:
        task = self._tasks.get(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found in plan")
        return task

    def _validate(self):
        """Check that every dependency ID references an existing task."""
        ids = set(self._tasks.keys())
        for t in self._tasks.values():
            for dep_id in t.dependencies:
                if dep_id not in ids:
                    raise ValueError(
                        f"Task {t.id} depends on non-existent task {dep_id}"
                    )
        self._check_cycles()

    def _check_cycles(self):
        """DFS-based cycle detection over non-terminal tasks."""
        active = {tid: t for tid, t in self._tasks.items() if not t.is_terminal}
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {tid: WHITE for tid in active}

        def _dfs(tid: int):
            color[tid] = GRAY
            for dep_id in active[tid].dependencies:
                if dep_id not in color:
                    continue  # terminal task — skip
                if color[dep_id] == GRAY:
                    raise ValueError(
                        f"Dependency cycle detected involving tasks {tid} and {dep_id}"
                    )
                if color[dep_id] == WHITE:
                    _dfs(dep_id)
            color[tid] = BLACK

        for tid in active:
            if color[tid] == WHITE:
                _dfs(tid)