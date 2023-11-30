from uuid import UUID

from fastapi import HTTPException
from models import get_supabase_db
from modules.brain.dto.inputs import CreateBrainProperties
from modules.brain.entity.brain_entity import BrainEntity, BrainType
from repository.api_brain_definition.add_api_brain_definition import (
    add_api_brain_definition,
)
from repository.external_api_secret.create_secret import create_secret


def create_brain(brain: CreateBrainProperties, user_id: UUID) -> BrainEntity:
    if brain.brain_type == BrainType.API:
        if brain.brain_definition is None:
            raise HTTPException(status_code=404, detail="Brain definition not found")

        if brain.brain_definition.url is None:
            raise HTTPException(status_code=404, detail="Brain url not found")

        if brain.brain_definition.method is None:
            raise HTTPException(status_code=404, detail="Brain method not found")

    supabase_db = get_supabase_db()

    created_brain = supabase_db.create_brain(brain)

    if brain.brain_type == BrainType.API and brain.brain_definition is not None:
        add_api_brain_definition(
            brain_id=created_brain.brain_id,
            api_brain_definition=brain.brain_definition,
        )

        secrets_values = brain.brain_secrets_values

        for secret_name in secrets_values:
            create_secret(
                user_id=user_id,
                brain_id=created_brain.brain_id,
                secret_name=secret_name,
                secret_value=secrets_values[secret_name],
            )

    return created_brain
