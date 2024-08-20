""" Algorithm REST endpoints """

# pylint: disable=too-many-ancestors

import logging
import os
from django.db import transaction
from django.forms.models import model_to_dict
from django.conf import settings
from rest_framework.exceptions import PermissionDenied
import yaml

from ..models import Project
from ..models import Affiliation
from ..models import Algorithm
from ..models import Organization
from ..models import JobCluster
from ..models import database_qs
from ..schema import GroupListSchema, GroupDetailSchema
from ._base_views import BaseDetailView
from ._base_views import BaseListView
from ._permissions import OrganizationAdminPermission
from ..schema import parse

logger = logging.getLogger(__name__)


class GroupListAPI(BaseListView):
    """
    Retrieves job clusters and creates new job clusters
    """

    schema = GroupListSchema()
    permission_classes = [OrganizationAdminPermission]
    http_method_names = ["get", "post", "patch", "delete"]

    def _get(self, params: dict) -> dict:
        """
        Returns the full database entries of registered job clusters for the given organization
        """
        user = self.request.user
        org_id = params["id"]
        affiliations = Affiliation.objects.filter(user=user, permission="Admin")
        organization_ids = affiliations.values_list("organization", flat=True)
        if org_id not in organization_ids:
            raise PermissionDenied(
                f"User {user} does not have Admin permissions for organization {org_id}"
            )
        return list(
            JobCluster.objects.filter(organization__id=org_id).values(*JOB_CLUSTER_PROPERTIES)
        )

    def get_queryset(self):
        """
        Returns a queryset of organizations
        """
        return Organization.objects.all()

    def _post(self, params: dict) -> dict:
        """
        Registers a new job cluster using the provided parameters
        """
        organization = Organization.objects.get(pk=params["id"])

        return {"message": "Successfully registered job cluster.", "id": None}


class GroupDetailAPI(BaseDetailView):
    """
    Interact with a single job cluster
    """

    schema = GroupDetailSchema()
    permission_classes = [OrganizationAdminPermission]
    http_method_names = ["get", "patch", "delete"]

    def _delete(self, params: dict) -> dict:
        """
        Deletes the provided job cluster
        """

        # Grab the job cluster's object and delete it from the database
        grp_obj = Group.objects.get(pk=params["id"])
        grp_obj.delete()

        return {"message": "Job cluster deleted successfully!"}

    def _get(self, params):
        """Retrieve the requested algortihm entry by ID"""
        group = Group.objects.get(pk=params["id"])
        return model_to_dict(group, fields=["id", "name", "host", "port", "token", "cert"])

    @transaction.atomic
    def _patch(self, params) -> dict:
        """Patch operation on the job cluster entry"""
        pass

        return {"message": f"Group {params['id']} successfully updated!"}

    def get_queryset(self):
        """Returns a queryset of all job clusters"""
        params = parse(self.request)
        return self.filter_only_viewables(Group.objects.filter(pk=params["id"]))
