import logging
import os
import json

from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings

from ..models import *
from ..cache import TatorCache

from .._permission_util import augment_permission, shift_permission, ColBitAnd

logger = logging.getLogger(__name__)


def _for_schema_view(request, view):
    """Returns true if permission is being requested for the schema view. This is
    necessary since there is no way to check project based permissions when
    no URL parameters are given.
    """
    return (
        view.kwargs == {}
        and isinstance(request.authenticators[0], SessionAuthentication)
        and request.META["HTTP_HOST"] in settings.ALLOWED_HOSTS
        and request.META["RAW_URI"].startswith("/schema/")
    )


### With fine-grained permissions enabled, we use the existance of permissions to determine access.
### a nuance is a given queryset (say all media) may be partially viewable to the user. This should be
### handled by the view itself.
class ProjectPermissionBase(BasePermission):
    """Base class for requiring project permissions."""

    def has_permission(self, request, view):
        # Get the project from the URL parameters
        if "project" in view.kwargs:
            project_id = view.kwargs["project"]
            project = get_object_or_404(Project, pk=int(project_id))
        elif "id" in view.kwargs:
            pk = view.kwargs["id"]
            obj = get_object_or_404(view.get_queryset(), pk=pk)
            project = self._project_from_object(obj)
            if project is None:
                raise Http404
        elif "uid" in view.kwargs:
            uid = view.kwargs["uid"]
            cache = TatorCache().get_jobs_by_uid(uid)
            if cache is not None and len(cache) == 1:
                project = get_object_or_404(Project, pk=cache[0]["project"])
            else:
                raise Http404
        elif "elemental_id" in view.kwargs:
            elemental_id = view.kwargs["elemental_id"]

            obj = view.get_queryset().filter(elemental_id=elemental_id)

            if not obj.exists():
                raise Http404
            obj = obj[0]
            project = self._project_from_object(obj)
            if project is None:
                raise Http404
        else:
            # If this is a request from schema view, show all endpoints.
            return _for_schema_view(request, view)

        return self._validate_project(request, project, view)

    def has_object_permission(self, request, view, obj):
        # Get the project from the object
        project = self._project_from_object(obj)
        return self._validate_project(request, project)

    def _project_from_object(self, obj):
        project = None
        if hasattr(obj, "project"):
            project = obj.project
        # Object is a project
        elif isinstance(obj, Project):
            project = obj
        return project

    def _validate_project(self, request, project, view):
        granted = False  # Always deny by default

        if isinstance(request.user, AnonymousUser):
            granted = False

        if request.method in ["GET", "HEAD", "PATCH", "DELETE", "PUT"]:
            ### GET, HEAD, PATCH, DELETE require permissions on the item itself
            perm_qs = view.get_queryset()
            perm_qs = augment_permission(request.user, perm_qs)
            model = view.get_queryset().model

            if perm_qs.exists():
                # See if any objects in the requested set DON'T have the required permission
                no_perm_qs = (
                    perm_qs.alias(
                        granted=ColBitAnd(
                            F("effective_permission"),
                            (self.required_mask),
                        )
                    )
                    .filter(granted=0)
                    .exists()
                )
                # If nothing is found, we have permission
                if not no_perm_qs:
                    granted = True
            if not perm_qs.exists() and request.method in ["GET", "HEAD", "PUT"]:
                ## If there are no objects to check or no permissions we have to go to the parent object
                ## If we are permissive (reading) we can see if the user has read permissions to the parent
                ## to avoid a 403, even if the set is empty
                proj_perm_qs = Project.objects.filter(pk=project.pk)
                proj_perm_qs = augment_permission(request.user, proj_perm_qs)
                proj_perm_qs = proj_perm_qs.alias(
                    granted=ColBitAnd(
                        F("effective_permission"),
                        (self.required_mask << shift_permission(model, Project)),
                    )
                )
                perm_qs = proj_perm_qs.filter(
                    granted__exact=(self.required_mask << shift_permission(model, Project))
                )

                if perm_qs.exists():
                    granted = True
        elif request.method in ["POST"]:
            ### POST gets permission from a model's parent object permission
            perm_qs = RowProtection.objects.filter(pk=-1)
            if hasattr(view, "get_parent_objs") is True:
                # TODO: Return parent objects and check permissions against those
                pass

            if not perm_qs.exists():
                ## If there are no permissions yet we have to go to the project object to confirm
                model = view.get_queryset().model
                proj_perm_qs = Project.objects.filter(pk=project.pk)
                proj_perm_qs = augment_permission(request.user, proj_perm_qs)
                proj_perm_qs = proj_perm_qs.alias(
                    granted=ColBitAnd(
                        F("effective_permission"),
                        (self.required_mask << shift_permission(model, Project)),
                    )
                )
                perm_qs = proj_perm_qs.filter(granted__gt=0)

                if perm_qs.exists():
                    granted = True
        else:
            assert False, f"Unsupported method={request.method}"

        return granted


# These map to the old permission system to make code work with both modes based on the setting of
# TATOR_FINE_GRAINED_PERMISSIONS environment variable
class ProjectViewOnlyPermission(ProjectPermissionBase):
    """Checks whether a user has view only access to a project. This
    is just to check whether a user is a member of a project.
    """

    message = "Not a member of this project."
    required_mask = PermissionMask.EXIST | PermissionMask.READ


class ProjectEditPermission(ProjectPermissionBase):
    """Checks whether a user has edit access to a project."""

    message = "Insufficient permission to modify this project."
    required_mask = (
        PermissionMask.EXIST | PermissionMask.READ | PermissionMask.CREATE | PermissionMask.MODIFY
    )


class ProjectTransferPermission(ProjectPermissionBase):
    """Checks whether a user has transfer access to a project."""

    message = "Insufficient permission to transfer media within this project."
    required_mask = PermissionMask.UPLOAD


class ProjectExecutePermission(ProjectPermissionBase):
    """Checks whether a user has execute access to a project."""

    message = "Insufficient permission to execute within this project."
    required_mask = PermissionMask.EXECUTE


class ProjectFullControlPermission(ProjectPermissionBase):
    """Checks if user has full control over a project."""

    message = "Insufficient permission to edit project settings."
    required_mask = PermissionMask.FULL_CONTROL


class PermalinkPermission(BasePermission):
    """
    1.) Let request through if project has anonymous membership
    2.) Let request through if requesting user any membership.
    Note: Because the lowest level of access allows READ the existence check for membership is sufficient.
    """

    def has_permission(self, request, view):
        try:
            media_id = view.kwargs.get("id")
            m = Media.objects.filter(pk=media_id)
            if not m.exists():
                return False  # If the media doesn't exist, do not authenticate
            project = m[0].project
            # Not all deployments have an anonymous user
            anonymous_user = User.objects.filter(username="anonymous")
            if anonymous_user.exists():
                anonymous_membership = Membership.objects.filter(
                    project=project, user=anonymous_user[0]
                )
                if anonymous_membership.exists():
                    return True
            if not isinstance(request.user, AnonymousUser):
                user_membership = Membership.objects.filter(project=project, user=request.user)
                if user_membership.exists():
                    return True
        except Exception as e:
            # This is an untrusted endpoint, so don't leak any exceptions to response if possible
            logger.error(f"Error {e}", exc_info=True)

        return False


class UserPermission(BasePermission):
    """1.) Reject all anonymous requests
    2.) Allow all super-user requests
    3.) Allow any cousin requests (users on a common project) (read-only)
    4.) Allow any request if user id = pk
    """

    def has_permission(self, request, view):
        if isinstance(request.user, AnonymousUser):
            # If user is anonymous but request contains a reset token and password, allow it.
            has_password = "password" in request.data
            has_token = "reset_token" in request.data
            has_two = len(list(request.data.values())) == 2
            is_patch = request.method == "PATCH"
            if has_password and has_token and has_two and is_patch:
                return True
            return False

        if _for_schema_view(request, view):
            return True

        user = request.user
        finger_user = view.kwargs.get("id")
        if user.is_staff:
            return True
        if user.id == finger_user:
            return True

        # find out if user is a cousin
        user_projects = Membership.objects.filter(user=user).values("project")
        cousins = Membership.objects.filter(project__in=user_projects).values("user").distinct()
        is_cousin = cousins.filter(user=finger_user).count() > 0
        if is_cousin and request.method == "GET":
            # Cousins have read-only permission
            return True

        return False


class UserListPermission(BasePermission):
    """1.) Reject anonymous GET requests
    2.) Allow any read-only requests
    3.) Always allow POST since permissions are determined in the endpoint
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        if isinstance(request.user, AnonymousUser):
            return False

        if _for_schema_view(request, view):
            return True

        if request.method == "GET":
            # All users have read-only permission, POST is validated by registration
            # token.
            return True

        return False


class ClonePermission(ProjectPermissionBase):
    """Special permission that checks for transfer permission in two
    projects.
    """

    message = "Insufficient permission to clone media between these projects."
    insufficient_permissions = [Permission.VIEW_ONLY, Permission.CAN_EDIT]

    def has_permission(self, request, view):
        if "project" in view.kwargs:
            src_project = view.kwargs["project"]
            src_project = get_object_or_404(Project, pk=int(src_project))
            dst_project = request.data["dest_project"]
            dst_project = get_object_or_404(Project, pk=int(dst_project))
        else:
            # If this is a request from schema view, show all endpoints.
            return _for_schema_view(request, view)

        return self._validate_project(request, src_project) and self._validate_project(
            request, dst_project
        )

    def has_object_permission(self, request, view, obj):
        return False


class OrganizationPermissionBase(BasePermission):
    """Base class for requiring organization permissions."""

    def has_permission(self, request, view):
        # Get the organization from the URL parameters
        if "organization" in view.kwargs:
            organization_id = view.kwargs["organization"]
            organization = get_object_or_404(Organization, pk=int(organization_id))
        elif "id" in view.kwargs:
            pk = view.kwargs["id"]
            obj = get_object_or_404(view.get_queryset(), pk=pk)
            organization = self._organization_from_object(obj)
            if organization is None:
                raise Http404
        else:
            # If this is a request from schema view, show all endpoints.
            return _for_schema_view(request, view)

        return self._validate_organization(request, organization)

    def has_object_permission(self, request, view, obj):
        # Get the organization from the object
        organization = self._organization_from_object(obj)
        return self._validate_organization(request, organization)

    def _organization_from_object(self, obj):
        organization = None
        if hasattr(obj, "organization"):
            organization = obj.organization
        # Object is a organization
        elif isinstance(obj, Organization):
            organization = obj
        return organization

    def _validate_organization(self, request, organization):
        granted = True

        if isinstance(request.user, AnonymousUser):
            granted = False
        else:
            # Find affiliation for this user and organization
            affiliation = Affiliation.objects.filter(user=request.user, organization=organization)

            # If user is not part of organization, deny access
            if affiliation.count() == 0:
                granted = False
            else:
                # If user has insufficient permission, deny access
                permission = affiliation[0].permission
                insufficient = permission in self.insufficient_permissions
                is_edit = request.method not in SAFE_METHODS
                if is_edit and insufficient:
                    granted = False
        return granted


class OrganizationMemberPermission(OrganizationPermissionBase):
    """Checks whether a user has member access to an organization. This
    is just to check whether a user is a member of an organization.
    """

    message = "Not a member of this organization."
    insufficient_permissions = []


class OrganizationAdminPermission(OrganizationPermissionBase):
    """Checks whether a user has admin access to an organization. This
    is just to check whether a user is a member of an organization.
    """

    message = "User does not have admin access to organization."
    insufficient_permissions = ["Member"]
