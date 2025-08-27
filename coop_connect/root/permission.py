from abc import ABC, abstractmethod

from fastapi import Request

import coop_connect.services.cooperative_service as coop_service
from coop_connect.root.connect_exception import (
    ConnectNotFoundException,
    ConnectPermissionException,
)
from coop_connect.root.coop_enums import CooperativeUserRole, UserType
from coop_connect.root.dependencies import Current_User
from coop_connect.services.service_utils.exception_collection import NotFound


class PermissionsDependency:
    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request, current_user: Current_User):
        # 👆 ensures get_current_user resolves first
        for permission_class in self.permissions_classes:
            permission_class(request=request)


class CoopBasePermission(ABC):

    user_role_error_msg = (
        "You dont have access to this cooperative resource. Please cant your Admin"
    )

    coop_role = None

    @abstractmethod
    def has_required_permission(self, request: Request) -> bool: ...

    def __init__(self, request: Request):
        try:
            self.coop_role = coop_service.get_coop_member_role(
                user_id=request.state.user,
                coop_id=request.path_params["coop_id"],  # extracted from router path
            )

            if not self.has_required_permission(request=request):
                raise ConnectPermissionException(message=self.user_role_error_msg)

        except NotFound:
            raise ConnectNotFoundException(
                message="user is not a member of cooperative"
            )

        super().__init__()
