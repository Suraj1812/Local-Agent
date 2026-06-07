import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from sqlalchemy.orm import Session

from agents.executor import ExecutorAgent
from agents.memory import MemoryAgent
from agents.planner import PlannerAgent
from database.models import Task
from services.conversations import add_message, ensure_conversation, serialize_conversation
from services.logging import log_event
from services.memory_store import long_term_memories, recent_messages
from services.ollama import ollama_service
from services.preferences import settings_out


class ManagerAgent:
    def __init__(self):
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.memory = MemoryAgent()

    async def run(self, db: Session, goal: str, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        final_event = None
        async for event in self.run_events(db, goal, conversation_id):
            if event.get("type") == "final":
                final_event = event["payload"]
        return final_event

    async def run_events(
        self, db: Session, goal: str, conversation_id: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        settings = settings_out(db)
        conversation = ensure_conversation(db, conversation_id, goal)
        add_message(db, conversation.id, "user", goal)
        log_event(db, "goal_received", goal, conversation_id=conversation.id)

        context = {
            "db": db,
            "goal": goal,
            "conversation_id": conversation.id,
            "settings": settings,
            "recent_messages": recent_messages(db, conversation.id, settings["memory_limit"]),
            "memories": long_term_memories(db, settings["memory_limit"]),
        }
        reasoning_steps = ["Goal received", "Memory loaded"]
        completed_tasks: List[Dict[str, Any]] = []

        yield {
            "type": "activity",
            "payload": {
                "current_goal": goal,
                "current_task": "Planning",
                "completed_tasks": [],
                "active_tool": None,
                "execution_progress": 10,
                "reasoning_steps": reasoning_steps,
                "status": "planning",
            },
        }

        plan = await self.planner.plan(goal, context)
        reasoning_steps.append("Plan created")
        yield {"type": "plan", "payload": plan}

        task_results = []
        total = max(len(plan), 1)
        for index, task in enumerate(plan, start=1):
            db_task = Task(
                conversation_id=conversation.id,
                goal=goal,
                title=task.get("title", "Agent task"),
                priority=task.get("priority", "medium"),
                status="in_progress",
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            log_event(db, "task_started", db_task.title, conversation_id=conversation.id, metadata={"task_id": db_task.id})

            yield {
                "type": "activity",
                "payload": {
                    "current_goal": goal,
                    "current_task": db_task.title,
                    "completed_tasks": completed_tasks,
                    "active_tool": None,
                    "execution_progress": int((index - 1) / total * 80) + 10,
                    "reasoning_steps": reasoning_steps,
                    "status": "executing",
                },
            }

            result = await self.executor.execute(task, context)
            db_task.status = "completed"
            db_task.result = result["response"]
            db.commit()
            task_results.append(result["response"])
            completed_tasks.append({**task, "status": "completed", "tool": result["tool"]})
            reasoning_steps.append(f"Completed: {task.get('title')}")
            log_event(
                db,
                "task_completed",
                db_task.title,
                conversation_id=conversation.id,
                metadata={"task_id": db_task.id, "tool": result["tool"]},
            )

            yield {
                "type": "activity",
                "payload": {
                    "current_goal": goal,
                    "current_task": task.get("title"),
                    "completed_tasks": completed_tasks,
                    "active_tool": result["tool"],
                    "execution_progress": int(index / total * 80) + 10,
                    "reasoning_steps": reasoning_steps,
                    "status": "executing",
                },
            }

        self.memory.store_goal(db, goal, plan, task_results)
        reasoning_steps.append("Memory updated")
        response = await self._final_answer(goal, plan, task_results, settings)

        activity = {
            "current_goal": goal,
            "current_task": None,
            "completed_tasks": completed_tasks,
            "active_tool": completed_tasks[-1]["tool"] if completed_tasks else None,
            "execution_progress": 100,
            "reasoning_steps": reasoning_steps,
            "status": "completed",
        }
        add_message(db, conversation.id, "assistant", response, {"plan": plan, "activity": activity})
        log_event(db, "response_returned", "Assistant response generated", conversation_id=conversation.id)

        final_payload = {
            "conversation": serialize_conversation(db, conversation),
            "response": response,
            "plan": plan,
            "activity": activity,
        }
        yield {"type": "final", "payload": final_payload}

    async def _final_answer(self, goal: str, plan: List[Dict[str, Any]], results: List[str], settings: Dict[str, Any]) -> str:
        joined_results = "\n\n".join(results)
        prompt = f"""
You are Manager Agent for a local autonomous assistant.
Write the final answer in markdown.
Goal: {goal}
Plan: {json.dumps(plan)}
Task results:
{joined_results}

Be useful and direct. Do not reveal hidden chain-of-thought.
"""
        try:
            return await ollama_service.generate(
                prompt,
                model=settings["model"],
                temperature=settings["temperature"],
            )
        except Exception:
            await asyncio.sleep(0.1)
            lines = [f"## Result for: {goal}", "", "Agent plan completed:"]
            lines.extend([f"- {task.get('title')} ({task.get('priority', 'medium')})" for task in plan])
            lines.extend(["", "### Output"])
            lines.extend([f"- {result}" for result in results])
            lines.append("")
            lines.append("Ollama is not reachable, so this answer used the local fallback path.")
            return "\n".join(lines)


manager_agent = ManagerAgent()
