from typing import Optional, List
from agent_team.planning.plan import Plan
from agent_team.planning.task import TaskStatus


class TodoFlow:

    def __init__(self):
        self.plan: Optional[Plan] = None
        self.completed_tasks = set()

    def set_plan(self, plan: Plan):
        self.plan = plan
        self._update_ready_tasks()

    def reset(self):
        self.plan = None
        self.completed_tasks = set()

    def revise_plan(
            self, 
            new_tasks: List, 
            add_dependencies: dict = None, 
            deprecate_tasks: List[int] = None, 
            remove_dependencies: dict = None
        ):
        """
        Insert new tasks into the plan and optionally update dependencies of existing tasks.
        
        Args:
            new_tasks: List of new Task objects to add to the plan
            deprecate_tasks: Optional list of task IDs to mark as deprecated (wrong or not needed anymore). 
                    The dependencies of the deprecated tasks will also be removed from other tasks.
            add_dependencies: Optional dict mapping existing task IDs to lists of new dependency IDs to add.
                    e.g., {2: [4, 5]} means task 2 should now also depend on tasks 4 and 5
            remove_dependencies: Optional dict mapping existing task IDs to lists of dependency IDs to remove.
                    e.g., {3: [1, 2]} means task 3 should no longer depend on tasks 1 and 2
        """

        if self.plan is None:
            self.plan = Plan(new_tasks)
        else:
            self.plan.tasks.extend(new_tasks)

        # Update dependencies of existing tasks if specified
        if add_dependencies:
            for task_id, new_deps in add_dependencies.items():
                task = self.plan.get_task(task_id)
                if task is None:
                    raise ValueError(f"Task {task_id} not found in plan")
                
                # Add new dependencies, avoiding duplicates
                for dep_id in new_deps:
                    if dep_id not in task.dependencies:
                        task.dependencies.append(dep_id)

        # Mark specified tasks as deprecated
        if deprecate_tasks:
            for task_id in deprecate_tasks:
                task = self.plan.get_task(task_id)
                if task is None:
                    raise ValueError(f"Task {task_id} not found in plan")
                task.status = TaskStatus.DEPRECATED
                # remove the dependencies of the deprecated task from other tasks
                for t in self.plan.tasks:
                    if task_id in t.dependencies:
                        t.dependencies.remove(task_id)

        # Remove specified dependencies from existing tasks if specified
        if remove_dependencies:
            for task_id, deps_to_remove in remove_dependencies.items():
                task = self.plan.get_task(task_id)
                if task is None:
                    raise ValueError(f"Task {task_id} not found in plan")
                
                # Remove specified dependencies
                task.dependencies = [dep for dep in task.dependencies if dep not in deps_to_remove]

        self._update_ready_tasks()
    

    def get_next_task(self):
        """Return the next ready task, or None if no tasks are ready."""

        if self.plan is None:
            return None

        for task in self.plan.tasks:
            if task.status == TaskStatus.READY:
                return task

        return None
        
    def get_unmet_dependencies(self, task):
        """Return a list of unmet dependencies for a given task."""
        unmet = []

        for dep_id in task.dependencies:
            dep = self.plan.get_task(dep_id)
            if dep.status != TaskStatus.DONE:
                unmet.append(dep)

        return unmet

    def start_task(self, task_id):
        """Mark a task as IN_PROGRESS if it's ready and all dependencies are met."""
        task = self.plan.get_task(task_id)
        if task is None:
            raise ValueError(f"Task {task_id} not found")

        # check dependencies
        unmet = self.get_unmet_dependencies(task)

        if unmet:
            descriptions = [f"'{t.description}'" for t in unmet]
            raise RuntimeError(
                f"Task '{task.description}' cannot start. "
                f"{len(unmet)} dependencies unfinished: "
                + ", ".join(descriptions)
            )

        if task.status not in [TaskStatus.READY, TaskStatus.PENDING]:
            raise RuntimeError(
                f"Task {task.id} '{task.description}' cannot start from status {task.status}"
            )

        task.status = TaskStatus.IN_PROGRESS


    def complete_task(self, task_id, result=None):

        task = self.plan.get_task(task_id)
        if task.status != TaskStatus.IN_PROGRESS:
            raise RuntimeError("Task must be IN_PROGRESS to complete")

        task.status = TaskStatus.DONE
        task.result = result
        self.completed_tasks.add(task.id)  # Store integer ID, not UUID
        self._update_ready_tasks()


    def _update_ready_tasks(self):
        """Update the status of tasks based on their dependencies."""

        if self.plan is None:
            return

        for task in self.plan.tasks:

            if task.status in [TaskStatus.DONE, TaskStatus.IN_PROGRESS, TaskStatus.DEPRECATED]:
                continue
            if all(dep in self.completed_tasks for dep in task.dependencies):
                task.status = TaskStatus.READY
            else:
                task.status = TaskStatus.BLOCKED


    def is_finished(self):
        """Check if all tasks in the plan are completed."""

        if self.plan is None:
            return True

        return all(t.status == TaskStatus.DONE or t.status == TaskStatus.DEPRECATED for t in self.plan.tasks)

    def summary(self, verbose=False):
        """Return a summary of the current plan and task statuses."""

        if self.plan is None:
            return "No plan."

        lines = []
        for t in self.plan.tasks:
            if verbose:
                unmet = self.get_unmet_dependencies(t)
                unmet_desc = ", ".join([f"{d.id}" for d in unmet])
                if unmet:
                    lines.append(
                        f"[{t.status}] {t.description} (depends on: {unmet_desc})"
                    )
                else:
                    lines.append(
                        f"[{t.status}] {t.description}"
                    )
            else:
                lines.append(
                    f"[{t.status}] {t.description}"
                )

        return "\n".join(lines)
    




