from datetime import datetime
from typing import Optional
from uuid import UUID

from theocraft_coop.root.connect_enums import UploadPurpose
from theocraft_coop.root.utils.base_schemas import AbstractModel


class Creator(AbstractModel):
    first_name: str
    last_name: str


class File(AbstractModel):
    purpose: UploadPurpose
    file_name: str
    creator_id: UUID
    link: str


class FileRead(File):
    id: UUID
    link_expiration: datetime
    date_created_utc: datetime
    creator: Optional[Creator] = None
