from abc import ABC, abstractmethod

from fastapi import Request

import coop_connect.services.cooperative_service as coop_service
from coop_connect.root.connect_exception import (
    ConnectNotFoundException,
    ConnectPermissionException,
)
from coop_connect.root.coop_enums import CooperativeUserRole, MembershipStatus, UserType
from coop_connect.root.dependencies import Current_User
from coop_connect.services.service_utils.exception_collection import NotFound


class PermissionsDependency:
    def __init__(self, permissions_classes: list):
        self.permissions_classes = permissions_classes

    def __call__(self, request: Request, current_user: Current_User):
        # 👆 ensures get_current_user resolves first
        for permission_class in self.permissions_classes:
            permission_class(request=request)


class UserBasePermission(ABC):

    user_role_error_msg = (
        "You dont have access to carry out this action. Please contact Support"
    )

    user_role = None

    @abstractmethod
    def has_required_permission(self, request: Request) -> bool: ...

    def __init__(self, request: Request):
        self.user_role = request.state.user.user_type

        if not self.has_required_permission(request=request):
            raise ConnectPermissionException(message=self.user_role_error_msg)


class CoopAdminorSuperAdminOnly(UserBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return self.user_role in [UserType.admin, UserType.coop_admin]


class CoopBasePermission(ABC):

    user_role_error_msg = (
        "You dont have access to this cooperative resource. Please contact your Admins"
    )

    coop_role = None

    coop_member_status = None

    edge_status = [
        MembershipStatus.INACTIVE,
        MembershipStatus.PENDING_APPROVAL,
        MembershipStatus.SUSPENDED,
        MembershipStatus.TERMINATED,
    ]

    @abstractmethod
    def has_required_permission(self, request: Request) -> bool: ...

    def __init__(self, request: Request):

        self.coop_role, self.coop_member_status = coop_service.get_coop_member_role(
            user_id=request.state.user.id,
            coop_id=request.path_params["coop_id"],  # extracted from router path
        )

        if not self.has_required_permission(request=request):
            raise ConnectPermissionException(message=self.user_role_error_msg)

    def is_active(self) -> bool:
        if self.coop_member_status in self.edge_status:

            raise ConnectNotFoundException(
                message="Your cooperative membership is not active"
            )
        return True


class CoopStaffOnly(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return (
            self.coop_role == CooperativeUserRole.STAFF
            and self.coop_member_status not in self.edge_status
        )


class CoopTresuserOnly(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return self.coop_role == CooperativeUserRole.TREASURER and self.is_active()


class CoopSecretaryOnly(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return self.coop_role == CooperativeUserRole.SECRETARY and self.is_active()


class CoopPresidentOnly(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return self.coop_role == CooperativeUserRole.PRESIDENT and self.is_active()


class CoopAccountantOnly(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return self.coop_role == CooperativeUserRole.ACCOUNTANT and self.is_active()


class CoopFinancialPerm(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return (
            self.coop_role
            in [
                CooperativeUserRole.TREASURER,
                CooperativeUserRole.ACCOUNTANT,
                CooperativeUserRole.PRESIDENT,
            ]
            and self.is_active()
        )


class CoopGeneralPerm(CoopBasePermission):
    def has_required_permission(self, request: Request) -> bool:
        return (
            self.coop_role
            in [
                CooperativeUserRole.STAFF,
                CooperativeUserRole.TREASURER,
                CooperativeUserRole.SECRETARY,
                CooperativeUserRole.PRESIDENT,
                CooperativeUserRole.ACCOUNTANT,
            ]
            and self.is_active()
        )


class CoopAllRoles(CoopBasePermission):

    def has_required_permission(self, request: Request) -> bool:
        return (
            self.coop_role
            in [
                CooperativeUserRole.STAFF,
                CooperativeUserRole.TREASURER,
                CooperativeUserRole.SECRETARY,
                CooperativeUserRole.PRESIDENT,
                CooperativeUserRole.ACCOUNTANT,
                CooperativeUserRole.MEMBER,
            ]
            and self.is_active()
        )
