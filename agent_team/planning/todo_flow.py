from typing import Optional, List
from agent_team.planning.plan import Plan
from agent_team.planning.task import Task, TaskStatus


class TodoFlow:
    """Execution engine for a task plan.

    Responsibilities:
    - Task lifecycle management (start / complete)
    - Automatic readiness calculation based on dependency completion
    - Plan revision (delegates graph mutations to Plan)

    All "completed" information is derived directly from task statuses —
    no redundant bookkeeping.
    """

    def __init__(self):
        self.plan: Optional[Plan] = None

    # -- plan lifecycle --------------------------------------------------------

    def set_plan(self, plan: Plan):
        self.plan = plan
        self._refresh_statuses()

    def reset(self):
        self.plan = None

    def revise_plan(
        self,
        new_tasks: List[Task] = None,
        add_dependencies: dict = None,
        deprecate_tasks: List[int] = None,
        remove_dependencies: dict = None,
    ):
        """Apply a batch of structural changes to the current plan.

        Order of operations: add tasks → deprecate → remove deps → add deps.
        Statuses are refreshed once at the end.
        """
        if self.plan is None:
            if new_tasks:
                self.plan = Plan(new_tasks)
            else:
                raise ValueError("No plan to revise and no new tasks provided")
        else:
            if new_tasks:
                self.plan.add_tasks(new_tasks)
            if deprecate_tasks:
                for task_id in deprecate_tasks:
                    self.plan.deprecate_task(task_id)
            if remove_dependencies:
                for task_id, dep_ids in remove_dependencies.items():
                    self.plan.remove_dependencies(task_id, dep_ids)
            if add_dependencies:
                for task_id, dep_ids in add_dependencies.items():
                    self.plan.add_dependencies(task_id, dep_ids)

        self._refresh_statuses()

    # -- task lifecycle --------------------------------------------------------

    def start_task(self, task_id: int):
        """Transition a task to IN_PROGRESS if all dependencies are met."""
        task = self._get_task_or_raise(task_id)
        unmet = self._unmet_dependencies(task)
        if unmet:
            desc = ", ".join(f"Task {t.id}" for t in unmet)
            raise RuntimeError(
                f"Task {task_id} cannot start — unmet dependencies: {desc}"
            )
        if task.status not in (TaskStatus.READY, TaskStatus.PENDING):
            raise RuntimeError(
                f"Task {task_id} cannot start from status '{task.status}'"
            )
        task.status = TaskStatus.IN_PROGRESS

    def complete_task(self, task_id: int, result=None):
        """Mark a task as done and refresh downstream readiness."""
        task = self._get_task_or_raise(task_id)
        if task.status != TaskStatus.IN_PROGRESS:
            raise RuntimeError(
                f"Task {task_id} is '{task.status}', expected 'in_progress'"
            )
        task.status = TaskStatus.DONE
        task.result = result
        self._refresh_statuses()

    # -- queries ---------------------------------------------------------------

    def get_next_task(self) -> Optional[Task]:
        """Return the first READY task, or None."""
        if self.plan is None:
            return None
        for task in self.plan.tasks:
            if task.status == TaskStatus.READY:
                return task
        return None

    def get_unmet_dependencies(self, task: Task) -> List[Task]:
        """Public accessor for unmet deps of a task."""
        return self._unmet_dependencies(task)

    def is_finished(self) -> bool:
        if self.plan is None:
            return True
        return all(t.is_terminal for t in self.plan.tasks)

    def summary(self, verbose: bool = False) -> str:
        if self.plan is None:
            return "No plan."
        lines = []
        for t in self.plan.tasks:
            line = f"[{t.status}] {t.description}"
            if verbose:
                unmet = self._unmet_dependencies(t)
                if unmet:
                    ids = ", ".join(str(d.id) for d in unmet)
                    line += f" (depends on: {ids})"
            lines.append(line)
        return "\n".join(lines)

    # -- private helpers -------------------------------------------------------

    def _get_task_or_raise(self, task_id: int) -> Task:
        if self.plan is None:
            raise ValueError("No plan exists")
        task = self.plan.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")
        return task

    def _unmet_dependencies(self, task: Task) -> List[Task]:
        """Return dependency tasks that are not yet DONE."""
        if self.plan is None:
            return []
        unmet = []
        for dep_id in task.dependencies:
            dep = self.plan.get_task(dep_id)
            if dep is not None and dep.status != TaskStatus.DONE:
                unmet.append(dep)
        return unmet

    def _refresh_statuses(self):
        """Recalculate READY / BLOCKED for all non-terminal, non-active tasks."""
        if self.plan is None:
            return
        completed = {t.id for t in self.plan.tasks if t.status == TaskStatus.DONE}
        for task in self.plan.tasks:
            if task.is_terminal or task.status == TaskStatus.IN_PROGRESS:
                continue
            if all(dep_id in completed for dep_id in task.dependencies):
                task.status = TaskStatus.READY
            else:
                task.status = TaskStatus.BLOCKED
    




