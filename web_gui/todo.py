"""Todo-flow DAG serialisation."""

from agent_team.context import get_context


def serialize_todo_flow() -> dict:
    flow = get_context().todo_flow
    if flow.plan is None:
        return {"tasks": [], "finished": True}
    tasks = []
    for t in flow.plan.tasks:
        tasks.append({
            "id": t.id,
            "uuid": t.uuid,
            "description": t.description,
            "status": t.status.value,
            "dependencies": t.dependencies,
            "result": t.result,
        })
    return {"tasks": tasks, "finished": flow.is_finished()}
