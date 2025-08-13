import logging
from typing import List

from fastapi import UploadFile

import theocraft_coop.database.db_handlers.file_db_handler as file_db_handler
import theocraft_coop.services.service_utils.uploader_utils as space_utils
from theocraft_coop.schemas.file_schemas import File, UploadPurpose
from theocraft_coop.schemas.user_schemas import UserProfile

LOGGER = logging.getLogger(__name__)


async def file_uploader(
    files: List[UploadFile], purpose: UploadPurpose, user_profile: UserProfile
):
    uploaded_resp = []
    for file in files:

        file_name = f"{purpose.value.lower()}/{str(user_profile.id)}-{file.filename.replace(' ', '_')}"

        await space_utils.file_uploader(file_name=file_name, data=file)

        link = await space_utils.get_presigned_url(file_name=file_name)

        uploaded_resp.append(
            File(
                purpose=purpose.value,
                file_name=file_name,
                creator_id=user_profile.id,
                link=link,
            )
        )

    return await file_db_handler.create_file(files=uploaded_resp)


async def file_delete(uploaded_file: str):
    file_name = uploaded_file.split("/")[-1]
    await space_utils.destroy_file(file_name=file_name)
    return {}
