from typing import List
from .task import Task


class Plan:

    def __init__(self, tasks: List[Task]):
        self.tasks = tasks

    def get_task_by_uuid(self, uuid):
        for t in self.tasks:
            if t.uuid == uuid:
                return t
        return None
    
    def get_task(self, id):
        for t in self.tasks:
            if t.id == id:
                return t
        return None

    def to_dict(self):
        return [t.to_dict() for t in self.tasks]