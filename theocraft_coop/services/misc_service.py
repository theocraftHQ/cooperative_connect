import logging
from typing import List

from fastapi import UploadFile

import theocraft_coop.services.service_utils.uploader_utils as space_utils
from theocraft_coop.root.connect_enums import UploadPurpose
from theocraft_coop.schemas.user_schemas import UserProfile

LOGGER = logging.getLogger(__name__)


async def file_uploader(
    files: List[UploadFile], purpose: UploadPurpose, user_profile: UserProfile
):
    uploaded_resp = []
    for file in files:
        uploaded_resp.append(
            await space_utils.file_uploader(
                file_name=f"{purpose.value}/{str(user_profile.id)}-{file.filename.replace(' ', '_')}",
                data=file,
            )
        )
    return uploaded_resp


async def file_delete(uploaded_file: str):
    file_name = uploaded_file.split("/")[-1]
    await space_utils.destroy_file(file_name=file_name)
    return {}
