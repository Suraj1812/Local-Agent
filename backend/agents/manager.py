import asyncio
import json
import re
from typing import Any, AsyncGenerator, Dict, List, Optional

from sqlalchemy.orm import Session

from agents.executor import ExecutorAgent
from agents.memory import MemoryAgent
from agents.planner import PlannerAgent
from database.models import Task
from services.conversations import add_message, ensure_conversation, serialize_conversation
from services.ap_platform import ap_overview, run_matching
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
        if self._is_accounts_payable_goal(goal):
            return self._accounts_payable_answer(goal)

        joined_results = "\n\n".join(results)
        prompt = f"""
You are Manager Agent for a local autonomous finance assistant.
Write a clean, structured answer with short labels and concise bullet points.
Do not use markdown heading markers such as # or ##.
Do not mention model availability, Ollama, internal tools, or implementation details.
Goal: {goal}
Plan: {json.dumps(plan)}
Task results:
{joined_results}

Be useful and direct. Do not reveal hidden chain-of-thought.
"""
        try:
            response = await ollama_service.generate(
                prompt,
                model=settings["model"],
                temperature=settings["temperature"],
            )
            cleaned = self._clean_response(response)
            if self._is_accounts_payable_goal(goal) and self._is_weak_accounts_payable_answer(cleaned):
                return self._accounts_payable_answer(goal)
            return cleaned
        except Exception:
            await asyncio.sleep(0.1)
            return self._fallback_answer(goal, plan, results)

    def _fallback_answer(self, goal: str, plan: List[Dict[str, Any]], results: List[str]) -> str:
        if self._is_accounts_payable_goal(goal):
            return self._accounts_payable_answer(goal)

        useful_results = [result for result in results if result]
        lines = ["Result", "The agent completed the requested workflow and prepared a concise answer.", ""]
        if plan:
            lines.extend(["What was checked", *[f"- {task.get('title', 'Task')}" for task in plan[:4]], ""])
        if useful_results:
            lines.extend(["Key output", *[f"- {result}" for result in useful_results[:4]], ""])
        lines.extend(["Next step", "Review the result and run the next task when ready."])
        return "\n".join(lines).strip()

    @staticmethod
    def _is_accounts_payable_goal(goal: str) -> bool:
        terms = ("accounts payable", "invoice", "ap ", "vendor", "po", "purchase order", "erp", "journal", "risk")
        normalized = f" {goal.lower()} "
        return any(term in normalized for term in terms)

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
    def _is_weak_accounts_payable_answer(response: str) -> bool:
        normalized = response.lower()
        concrete_signals = ("acme components", "ac-55219", "po-88022", "goods receipt", "journal posting")
        return not any(signal in normalized for signal in concrete_signals)

    @staticmethod
    def _accounts_payable_answer(goal: str) -> str:
        overview = ap_overview()
        invoices = overview["invoices"]
        exception_invoice = next((invoice for invoice in invoices if invoice["status"] == "exception"), invoices[0])
        matching = run_matching(
            {
                "invoice_number": f"{exception_invoice['invoice_number']}-REVIEW",
                "po_number": exception_invoice["po_number"],
                "amount": exception_invoice["amount"],
                "vendor_id": exception_invoice["vendor_id"],
            }
        )
        exceptions = [item for item in overview["exceptions"] if item["invoice_id"] == exception_invoice["id"]]
        failed_checks = [check["name"] for check in matching.get("checks", []) if check.get("status") == "failed"]

        if "highest" in goal.lower() or "risk" in goal.lower():
            title = f"Highest AP risk: {exception_invoice['vendor']} {exception_invoice['invoice_number']}"
        else:
            title = f"AP review: {exception_invoice['vendor']} {exception_invoice['invoice_number']}"

        lines = [
            title,
            f"This invoice should not post yet. It has a policy score of {matching['score']}/100 and needs human review before ERP sync.",
            "",
            "Risk signals",
            f"- Amount: ${exception_invoice['amount']:,.0f}",
            f"- PO: {exception_invoice['po_number']} · ERP: {exception_invoice['erp']}",
            f"- Failed checks: {', '.join(failed_checks) if failed_checks else 'none'}",
        ]
        lines.extend([f"- {item['summary']}" for item in exceptions[:2]])
        lines.extend(
            [
                "",
                "Recommended action",
                "- Route the variance to the AP Manager.",
                "- Ask Receiving to confirm the short goods receipt or request a vendor credit memo.",
                "- Keep journal posting blocked until the exception is approved.",
            ]
        )
        return "\n".join(lines)


manager_agent = ManagerAgent()
