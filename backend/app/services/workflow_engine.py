from datetime import datetime, timezone

from sqlalchemy import select

from app.models.execution import Execution, ExecutionLog
from app.models.workflow import Workflow
from app.services.log_stream import log_stream_manager


class WorkflowEngine:
    async def run(self, db, execution_id: int) -> dict:
        execution = (
            await db.execute(select(Execution).where(Execution.id == execution_id))
        ).scalar_one()
        workflow = (
            await db.execute(select(Workflow).where(Workflow.id == execution.workflow_id))
        ).scalar_one()

        execution.status = "running"
        execution.started_at = datetime.now(timezone.utc)
        await db.commit()

        await self._log(db, execution.id, "info", f"Starting workflow '{workflow.name}'")

        try:
            node_outputs: dict[str, dict] = {}
            for node in workflow.definition.get("nodes", []):
                node_type = node.get("type")
                node_id = node.get("id")
                config = node.get("config", {})
                await self._log(db, execution.id, "info", f"Executing node {node_id}:{node_type}")

                if node_type == "trigger":
                    node_outputs[node_id] = {"triggered": True}
                elif node_type == "action":
                    node_outputs[node_id] = {"status": "success", "config": config}
                elif node_type == "ai":
                    node_outputs[node_id] = {"ai_summary": "AI node executed", "task": config.get("task")}
                else:
                    node_outputs[node_id] = {"status": "skipped", "reason": "unknown node type"}

            execution.status = "success"
            execution.output_payload = {"node_outputs": node_outputs}
            execution.completed_at = datetime.now(timezone.utc)
            await db.commit()
            await self._log(db, execution.id, "info", "Workflow completed")
            return execution.output_payload
        except Exception as exc:
            execution.status = "failed"
            execution.error_message = str(exc)
            execution.completed_at = datetime.now(timezone.utc)
            execution.retries += 1
            await db.commit()
            await self._log(db, execution.id, "error", f"Execution failed: {exc}")
            raise

    async def _log(self, db, execution_id: int, level: str, message: str) -> None:
        log = ExecutionLog(execution_id=execution_id, level=level, message=message)
        db.add(log)
        await db.commit()
        await log_stream_manager.broadcast(
            execution_id,
            {"execution_id": execution_id, "level": level, "message": message},
        )


workflow_engine = WorkflowEngine()
