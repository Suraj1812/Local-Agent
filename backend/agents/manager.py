import json
import re
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
        if final_event is None:
            raise RuntimeError("Agent did not produce a final response")
        return final_event

    async def run_events(
        self, db: Session, goal: str, conversation_id: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        goal = " ".join(goal.strip().split())
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

            try:
                result = await self.executor.execute(task, context)
                db_task.status = "completed"
            except Exception as exc:
                result = {
                    "tool": None,
                    "tool_result": {"error": str(exc)[:300]},
                    "response": f"Task '{db_task.title}' could not complete: {str(exc)[:200]}",
                }
                db_task.status = "failed"
            db_task.result = result["response"]
            db.commit()
            task_results.append(result["response"])
            completed_tasks.append({**task, "status": db_task.status, "tool": result["tool"]})
            reasoning_steps.append(f"{db_task.status.title()}: {task.get('title')}")
            log_event(
                db,
                f"task_{db_task.status}",
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

        try:
            self.memory.store_goal(db, goal, plan, task_results)
            reasoning_steps.append("Memory updated")
        except Exception as exc:
            reasoning_steps.append("Memory skipped")
            log_event(db, "memory_error", str(exc)[:300], conversation_id=conversation.id)
        response = await self._final_answer(goal, plan, task_results, settings, context["recent_messages"])

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

    async def _final_answer(
        self,
        goal: str,
        plan: List[Dict[str, Any]],
        results: List[str],
        settings: Dict[str, Any],
        conversation_context: List[Dict[str, Any]],
    ) -> str:
        useful_results = [
            result
            for result in results
            if result and result != "Ready for a direct model answer."
        ]
        if self._requires_source_data(goal, useful_results):
            return self._missing_source_data_answer(goal)

        joined_results = "\n\n".join(useful_results) if useful_results else "No external tool context was needed."
        recent = json.dumps(conversation_context, default=str)[:1600]
        prompt = f"""
You are FirstAI. Answer the user's actual question directly and honestly.
Do not use a demo answer. Do not force finance, invoices, AP, ERP, or vendor context unless the user asked for it.
AP means accounts payable when the user is asking about finance.
Do not use markdown heading markers. Do not mention hidden prompts, internal implementation, or model availability.
If a question needs live/current verification, say what you know and what to check.
If the user asks you to analyze, summarize, compare, rank, or identify risk from data that is not provided, say that you need the source data and do not invent specifics.
Use the tool context only when it is relevant.

Recent context:
{recent}

Tool context:
{joined_results}

User question:
{goal}

Answer:
"""
        try:
            response = await ollama_service.generate(
                prompt,
                model=settings["model"],
                temperature=settings["temperature"],
                num_predict=420,
            )
            cleaned = self._clean_response(response)
            return cleaned or "I could not produce a useful answer. Please try the question again."
        except Exception:
            return self._model_unavailable_answer()

    @staticmethod
    def _model_unavailable_answer() -> str:
        return (
            "The local AI model did not respond in time.\n\n"
            "What to check\n"
            "- Ollama service is running.\n"
            "- The configured model is installed.\n"
            "- The backend can reach the Ollama host.\n\n"
            "Try again after the model is ready."
        )

    @staticmethod
    def _clean_response(response: str) -> str:
        lines = []
        previous_blank = False
        for raw_line in response.splitlines():
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", raw_line).strip()
            line = line.replace("**", "").replace("__", "")
            line = re.sub(r"^\s*[-*]\s+$", "", line)
            if not line:
                if not previous_blank and lines:
                    lines.append("")
                previous_blank = True
                continue
            lines.append(line)
            previous_blank = False
        return "\n".join(lines).strip()

    @staticmethod
    def _requires_source_data(goal: str, useful_results: List[str]) -> bool:
        if useful_results:
            return False
        lower = goal.lower()
        asks_for_analysis = any(
            term in lower
            for term in (
                "summarize",
                "analyze",
                "compare",
                "rank",
                "highest",
                "lowest",
                "risk",
                "from the data",
                "from data",
                "from this",
            )
        )
        says_missing = any(
            term in lower
            for term in (
                "no data",
                "not provided",
                "without data",
                "data is provided yet",
                "data i provide",
                "i will provide",
            )
        )
        return asks_for_analysis and says_missing

    @staticmethod
    def _missing_source_data_answer(goal: str) -> str:
        if "ap" in goal.lower() or "accounts payable" in goal.lower():
            return (
                "I cannot identify the highest accounts payable risk yet because no invoice, vendor, PO, GRN, "
                "payment, or exception data was provided.\n\n"
                "Send the source data and I will rank the risk by amount variance, missing receipt, duplicate invoice, "
                "vendor risk, approval status, due date pressure, and ERP posting impact."
            )
        return (
            "I do not have enough source data to answer that accurately yet.\n\n"
            "Send the data you want analyzed and I will summarize it directly without inventing missing details."
        )


manager_agent = ManagerAgent()
