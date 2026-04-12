"""Automation engine API endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.services.automation_engine import TaskPriority, automation_engine

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(
    name: str,
    task_type: str = "command",
    priority: str = "medium",
    payload: dict | None = None,
) -> dict:
    """Create a new automation task."""
    task = automation_engine.create_task(
        name=name,
        task_type=task_type,
        user_id="demo-user",  # In production, from auth token
        payload=payload or {},
        priority=TaskPriority(priority),
    )
    return {
        "id": task.id,
        "name": task.name,
        "task_type": task.task_type,
        "status": task.status,
        "priority": task.priority,
        "created_at": task.created_at.isoformat(),
    }


@router.post("/tasks/{task_id}/execute")
async def execute_task(task_id: str) -> dict:
    """Execute an automation task."""
    try:
        task = await automation_engine.execute_task(task_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

    return {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "result": task.result,
        "error": task.error,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


@router.get("/tasks")
async def list_tasks() -> dict:
    """List all automation tasks."""
    tasks = automation_engine.get_user_tasks("demo-user")
    return {
        "tasks": [
            {
                "id": t.id,
                "name": t.name,
                "task_type": t.task_type,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ],
        "total": len(tasks),
    }


@router.post("/workflows", status_code=status.HTTP_201_CREATED)
async def create_workflow(
    name: str,
    description: str = "",
    trigger: str = "manual",
    steps: list[dict] | None = None,
) -> dict:
    """Create a new automation workflow."""
    workflow = automation_engine.create_workflow(
        name=name,
        description=description,
        user_id="demo-user",
        steps=steps or [],
        trigger=trigger,
    )
    return {
        "id": workflow.id,
        "name": workflow.name,
        "description": workflow.description,
        "trigger": workflow.trigger,
        "steps_count": len(workflow.steps),
        "is_active": workflow.is_active,
        "created_at": workflow.created_at.isoformat(),
    }


@router.get("/recommendations")
async def get_recommendations() -> dict:
    """Get AI-powered automation recommendations."""
    recommendations = automation_engine.generate_recommendations("demo-user")
    return {
        "recommendations": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "category": r.category,
                "confidence": r.confidence,
                "action_type": r.action_type,
                "suggested_config": r.suggested_config,
            }
            for r in recommendations
        ],
        "total": len(recommendations),
    }
