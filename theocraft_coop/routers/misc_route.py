from typing import List

from fastapi import (  # This imports FASTAPI Specific tools for all routers
    APIRouter,
    Body,
    Depends,
    UploadFile,
    status,
)

import theocraft_coop.root.connect_enums as misc_schema
import theocraft_coop.services.misc_service as misc_service
from theocraft_coop.root.dependencies import get_current_user
from theocraft_coop.schemas.user_schemas import UserProfile

api_router = APIRouter(prefix="/v1/misc", tags=["MISC Service"])


@api_router.post("/upload", status_code=status.HTTP_201_CREATED)  # response_model,
async def file_uploader(
    upload_files: List[UploadFile],
    purpose: misc_schema.UploadPurpose = Body(embed=True),
    current_user_profile: UserProfile = Depends(get_current_user),
):
    return await misc_service.file_uploader(
        files=upload_files, purpose=purpose, user_profile=current_user_profile
    )


@api_router.post("/delete-upload", status_code=status.HTTP_200_OK)  # response_model,
async def file_delete(
    uploaded_file: str = Body(embed=True),
    current_user_profile: UserProfile = Depends(get_current_user),
):
    return await misc_service.file_delete(uploaded_file=uploaded_file)
