import os
import json
import random
import datetime
import logging
import string
import functools
import datetime
from uuid import uuid1
from math import sin, cos, sqrt, atan2, radians

from django.core.files.uploadedfile import SimpleUploadedFile

from rest_framework import status
from rest_framework.test import APITestCase

from dateutil.parser import parse as dateutil_parse

from .models import User
from .models import Project
from .models import Membership
from .models import Permission
from .models import Algorithm
from .models import AlgorithmResult
from .models import JobResult
from .models import Package
from .models import EntityTypeMediaVideo
from .models import EntityTypeMediaImage
from .models import EntityTypeLocalizationBox
from .models import EntityTypeLocalizationLine
from .models import EntityTypeLocalizationDot
from .models import EntityTypeState
from .models import EntityTypeTreeLeaf
from .models import EntityMediaVideo
from .models import EntityMediaImage
from .models import EntityLocalizationBox
from .models import EntityLocalizationLine
from .models import EntityLocalizationDot
from .models import EntityState
from .models import LocalizationAssociation
from .models import TreeLeaf
from .models import MediaAssociation
from .models import AttributeTypeBool
from .models import AttributeTypeInt
from .models import AttributeTypeFloat
from .models import AttributeTypeEnum
from .models import AttributeTypeString
from .models import AttributeTypeDatetime
from .models import AttributeTypeGeoposition
from .models import AnalysisCount

logger = logging.getLogger(__name__)

def create_test_user():
    return User.objects.create(
        username="jsnow",
        password="jsnow",
        first_name="Jon",
        last_name="Snow",
        email="jon.snow@gmail.com",
        middle_initial="A",
        initials="JAS",
    )

def create_test_project(user):
    return Project.objects.create(
        name="asdf",
        creator=user,
    )

def create_test_membership(user, project):
    return Membership.objects.create(
        user=user,
        project=project,
        permission=Permission.FULL_CONTROL,
    )

def create_test_algorithm(user, name, project):
    return Algorithm.objects.create(
        name=name,
        project=project,
        user=user,
        setup=SimpleUploadedFile(name='setup.py', content=b'asdfasdf'),
        teardown=SimpleUploadedFile(name='teardown.py', content=b'asdfasdf'),
        image_name='asdf',
        username='jsnow',
        password='asdf',
        needs_gpu=False,
    )

def create_test_algorithm_result(user, name, project, algorithm):
    return AlgorithmResult.objects.create(
        algorithm=algorithm,
        user=user,
        started=datetime.datetime.now(datetime.timezone.utc),
        stopped=datetime.datetime.now(datetime.timezone.utc),
        result=JobResult.FINISHED,
        message="",
        setup_log=SimpleUploadedFile(name='setup.log', content=b'asdfasdf'),
        algorithm_log=SimpleUploadedFile(name='algorithm.log', content=b'asdfasdf'),
        teardown_log=SimpleUploadedFile(name='teardown.log', content=b'asdfasdf'),
    )

def create_test_package(user, name, project):
    return Package.objects.create(
        name=name,
        file=SimpleUploadedFile(name='asdf.zip', content=b'asdfasdf'),
        use_originals=False,
        creator=user,
        created=datetime.datetime.now(datetime.timezone.utc),
        project=project,
    )

def create_test_image_file():
    this_path = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(this_path, 'static', 'images',
                            'cvision_horizontal.png')
    return SimpleUploadedFile(name='test.png',
                              content=open(img_path, 'rb').read(),
                              content_type='image/png')

def create_test_video(user, name, entity_type, project):
    return EntityMediaVideo.objects.create(
        name=name,
        meta=entity_type,
        project=project,
        uploader=user,
        upload_datetime=datetime.datetime.now(datetime.timezone.utc),
        original='',
        md5='',
        file=SimpleUploadedFile(name='asdf.mp4', content=b'asdfasdf'),
        thumbnail=create_test_image_file(),
        thumbnail_gif=create_test_image_file(),
        num_frames=1,
        fps=30.0,
        codec='H264',
        width='640',
        height='480',
    )

def create_test_image(user, name, entity_type, project):
    return EntityMediaImage.objects.create(
        name=name,
        meta=entity_type,
        project=project,
        uploader=user,
        upload_datetime=datetime.datetime.now(datetime.timezone.utc),
        md5='',
        file=create_test_image_file(),
        thumbnail=create_test_image_file(),
        width='640',
        height='480',
    )

def create_test_box(user, entity_type, project, media, frame):
    x = random.uniform(0.0, float(media.width))
    y = random.uniform(0.0, float(media.height))
    w = random.uniform(0.0, float(media.width) - x)
    h = random.uniform(0.0, float(media.height) - y)
    return EntityLocalizationBox.objects.create(
        user=user,
        meta=entity_type,
        project=project,
        media=media,
        frame=frame,
        x=x,
        y=y,
        width=w,
        height=h,
    )
        
def create_test_line(user, entity_type, project, media, frame):
    x0 = random.uniform(0.0, float(media.width))
    y0 = random.uniform(0.0, float(media.height))
    x1 = random.uniform(0.0, float(media.width) - x0)
    y1 = random.uniform(0.0, float(media.height) - y0)
    return EntityLocalizationLine.objects.create(
        user=user,
        meta=entity_type,
        project=project,
        media=media,
        frame=frame,
        x0=x0, y0=y0, x1=x1, y1=y1,
    )
        
def create_test_dot(user, entity_type, project, media, frame):
    x = random.uniform(0.0, float(media.width))
    y = random.uniform(0.0, float(media.height))
    return EntityLocalizationDot.objects.create(
        user=user,
        meta=entity_type,
        project=project,
        media=media,
        frame=frame,
        x=x,
        y=y,
    )

def create_test_treeleaf(name, entity_type, project):
    return TreeLeaf.objects.create(
        name=name,
        meta=entity_type,
        project=project,
        path=''.join(random.choices(string.ascii_lowercase, k=10)),
    )
        
def create_test_attribute_types(entity_type, project):
    """Create one of each attribute type.
    """
    return {
        'bool': AttributeTypeBool.objects.create(
            name='bool_test',
            applies_to=entity_type,
            project=project
        ),
        'int': AttributeTypeInt.objects.create(
            name='int_test',
            applies_to=entity_type,
            project=project
        ),
        'float': AttributeTypeFloat.objects.create(
            name='float_test',
            applies_to=entity_type,
            project=project
        ),
        'enum': AttributeTypeEnum.objects.create(
            name='enum_test',
            choices=['enum_val1', 'enum_val2', 'enum_val3'],
            applies_to=entity_type,
            project=project
        ),
        'string': AttributeTypeString.objects.create(
            name='string_test',
            applies_to=entity_type,
            project=project
        ),
        'datetime': AttributeTypeDatetime.objects.create(
            name='datetime_test',
            use_current=False,
            applies_to=entity_type,
            project=project
        ),
        'geoposition': AttributeTypeGeoposition.objects.create(
            name='geoposition_test',
            applies_to=entity_type,
            project=project
        ),
    }

def random_datetime(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def random_latlon():
    return (random.uniform(-90.0, 90.0), random.uniform(-180.0, 180.0))

def latlon_distance(lat0, lon0, lat1, lon1):
    R = 6373.0 # Radius of earth in km
    rlat0 = radians(lat0)
    rlon0 = radians(lon0)
    rlat1 = radians(lat1)
    rlon1 = radians(lon1)
    dlon = rlon1 - rlon0
    dlat = rlat1 - rlat0
    a = sin(dlat / 2)**2 + cos(rlat0) * cos(rlat1) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

permission_levels = [
    Permission.VIEW_ONLY,
    Permission.CAN_EDIT,
    Permission.CAN_TRANSFER,
    Permission.CAN_EXECUTE,
    Permission.FULL_CONTROL
]

class PermissionCreateTestMixin:
    def test_create_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            self.membership.permission = level
            self.membership.save()
            if index >= permission_index:
                expected_status = status.HTTP_201_CREATED
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            endpoint = f'/rest/{self.list_uri}/{self.project.pk}'
            response = self.client.post(endpoint, self.create_json, format='json')
            self.assertEqual(response.status_code, expected_status)
            if hasattr(self, 'entities'):
                obj_type = type(self.entities[0])
            if expected_status == status.HTTP_200_OK:
                if isinstance(response.data['id'], list):
                    created_id = response.data['id'][0]
                else:
                    created_id = response.data['id']
                if hasattr(self, 'entities'):
                    self.entities.append(obj_type.objects.get(pk=created_id))
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

class PermissionListTestMixin:
    def test_list_patch_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            self.membership.permission = level
            self.membership.save()
            if index >= permission_index:
                expected_status = status.HTTP_200_OK
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            test_val = random.random() > 0.5
            response = self.client.patch(
                f'/rest/{self.list_uri}/{self.project.pk}'
                f'?type={self.entity_type.pk}',
                {'attributes': {'bool_test': test_val}},
                format='json')
            self.assertEqual(response.status_code, expected_status)
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

    def test_list_delete_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            self.membership.permission = level
            self.membership.save()
            if index >= permission_index:
                expected_status = status.HTTP_204_NO_CONTENT
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            response = self.client.delete(
                f'/rest/{self.list_uri}/{self.project.pk}'
                f'?type={self.entity_type.pk}')
            self.assertEqual(response.status_code, expected_status)
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

class PermissionDetailTestMixin:
    def test_detail_patch_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            self.membership.permission = level
            self.membership.save()
            if index >= permission_index:
                expected_status = status.HTTP_200_OK
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{self.entities[0].pk}',
                self.patch_json,
                format='json')
            self.assertEqual(response.status_code, expected_status)
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

    def test_detail_delete_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            self.membership.permission = level
            self.membership.save()
            if index >= permission_index:
                expected_status = status.HTTP_204_NO_CONTENT
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            test_val = random.random() > 0.5
            response = self.client.delete(
                f'/rest/{self.detail_uri}/{self.entities[0].pk}',
                format='json')
            self.assertEqual(response.status_code, expected_status)
            if expected_status == status.HTTP_204_NO_CONTENT:
                del self.entities[0]
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

class PermissionListMembershipTestMixin:
    def test_list_not_a_member_permissions(self):
        self.membership.delete()
        url = f'/rest/{self.list_uri}/{self.project.pk}'
        if hasattr(self, 'entity_type'):
            url += f'?type={self.entity_type.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.membership.save()

    def test_list_is_a_member_permissions(self):
        self.membership.permission = Permission.VIEW_ONLY
        self.membership.save()
        url = f'/rest/{self.list_uri}/{self.project.pk}'
        if hasattr(self, 'entity_type'):
            url += f'?type={self.entity_type.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()

class PermissionDetailMembershipTestMixin:
    def test_detail_not_a_member_permissions(self):
        self.membership.delete()
        url = f'/rest/{self.detail_uri}/{self.entities[0].pk}'
        if hasattr(self, 'entity_type'):
            url += f'?type={self.entity_type.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.membership.save()

    def test_detail_is_a_member_permissions(self):
        self.membership.permission = Permission.VIEW_ONLY
        self.membership.save()
        url = f'/rest/{self.detail_uri}/{self.entities[0].pk}'
        if hasattr(self, 'entity_type'):
            url += f'?type={self.entity_type.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.membership.permission = Permission.FULL_CONTROL
        self.membership.save()


class AttributeMediaTestMixin:
    def test_media_with_attr(self):
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?media_id={self.media_entities[0].pk}'
            f'&type={self.entity_type.pk}&attribute=bool_test::true'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_multiple_media_with_attr(self):
        medias = random.choices(self.media_entities, k=3)
        medias = ','.join(map(lambda x: str(x.pk), medias))
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?media_id={medias}'
            f'&type={self.entity_type.pk}&attribute=bool_test::true'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class AttributeTestMixin:
    def test_query_no_attributes(self):
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(len(response.data), len(self.entities))
        this_ids = [e.pk for e in self.entities]
        rest_ids = [e['id'] for e in response.data]
        for this_id, rest_id in zip(sorted(this_ids), sorted(rest_ids)):    
            self.assertEqual(this_id, rest_id)

    def test_multiple_attribute(self):
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?type={self.entity_type.pk}&attribute=bool_test::true&attribute=int_test::0'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_count(self):
        test_vals = [random.random() > 0.5 for _ in range(len(self.entities))]
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{pk}', {
                    'attributes': {'bool_test': test_val},
                },
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?attribute=bool_test::true'
            f'&type={self.entity_type.pk}'
            f'&format=json'
            f'&operation=count'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], sum(test_vals))

    def test_count_by_attribute(self):
        test_vals = [random.choice(self.attribute_types['enum'].choices) for _ in range(len(self.entities))]
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{pk}',
                {'attributes': {'enum_test': test_val}},
                format='json')
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?format=json'
            f'&type={self.entity_type.pk}'
            f'&operation=attribute_count::enum_test'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for choice in self.attribute_types['enum'].choices:
            self.assertEqual(response.data.get(choice, 0), test_vals.count(choice))

    def test_pagination(self):
        test_vals = [random.random() > 0.5 for _ in range(len(self.entities))]
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'bool_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?format=json'
            f'&attribute=bool_test::true'
            f'&type={self.entity_type.pk}'
            f'&start=0'
            f'&stop=2'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), max(0, min(sum(test_vals), 2)))
        response1 = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?format=json'
            f'&attribute=bool_test::true'
            f'&type={self.entity_type.pk}'
            f'&start=1'
            f'&stop=4'
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data), max(0, min(sum(test_vals) - 1, 3)))
        if len(response.data) >= 2 and len(response1.data) >= 1:
            self.assertEqual(response.data[1], response1.data[0])

    def test_list_patch(self):
        test_val = random.random() > 0.5
        response = self.client.patch(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?type={self.entity_type.pk}',
            {'attributes': {'bool_test': test_val}},
            format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for entity in self.entities:
            response = self.client.get(f'/rest/{self.detail_uri}/{entity.pk}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['attributes']['bool_test'], test_val)

    def test_list_delete(self):
        test_val = random.random() > 0.5
        to_delete = [self.create_entity() for _ in range(5)]
        obj_ids = list(map(lambda x: str(x.pk), to_delete))
        for obj_id in obj_ids:
            response = self.client.get(f'/rest/{self.detail_uri}/{obj_id}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Update objects with a string so we know which to delete
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{obj_id}',
                {'attributes': {'string_test': 'DELETE ME!!!'}},
                format='json')
        response = self.client.delete(
            f'/rest/{self.list_uri}/{self.project.pk}'
            f'?type={self.entity_type.pk}'
            f'&attribute=string_test::DELETE ME!!!')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        for obj_id in obj_ids:
            response = self.client.get(f'/rest/{self.detail_uri}/{obj_id}')
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        for entity in self.entities:
            response = self.client.get(f'/rest/{self.detail_uri}/{entity.pk}')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_null_attr(self):
        test_vals = [random.random() > 0.5 for _ in range(len(self.entities))]
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'bool_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_null=bool_test::false'
            f'&type={self.entity_type.pk}', # needed for localizations
            format='json'
        )
        self.assertEqual(len(response.data), len(self.entities))
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_null=bool_test::true'
            f'&type={self.entity_type.pk}', # needed for localizations
            format='json'
        )
        self.assertEqual(len(response.data), 0)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_null=asdf::true'
            f'&type={self.entity_type.pk}', # needed for localizations
            format='json'
        )
        self.assertEqual(len(response.data), len(self.entities))
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_null=asdf::false'
            f'&type={self.entity_type.pk}', # needed for localizations
            format='json'
        )
        self.assertEqual(len(response.data), 0)
    
    def test_bool_attr(self):
        test_vals = [random.random() > 0.5 for _ in range(len(self.entities))]
        # Test setting an invalid bool
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'bool_test': 'asdfasdf'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'bool_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            # Do this again to test after the attribute object has been created.
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'bool_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(response.data['attributes']['bool_test'], test_val)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute=bool_test::true&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), sum(test_vals))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(test_vals) - sum(test_vals))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lt=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lte=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Bool is treated as a string
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(test_vals) - sum(test_vals))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=bool_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_int_attr(self):
        test_vals = [random.randint(-1000, 1000) for _ in range(len(self.entities))]
        # Test setting an invalid int
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'int_test': 'asdfasdf'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'int_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(response.data['attributes']['int_test'], test_val)
        for test_val in test_vals:
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute=int_test::{test_val}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([t == test_val for t in test_vals]))
        for lbound, ubound in [(-1000, 1000), (-500, 500), (-500, 0), (0, 500)]:
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=int_test::{lbound}&attribute_lt=int_test::{ubound}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([(t > lbound) and (t < ubound) for t in test_vals]))
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=int_test::{lbound}&attribute_lte=int_test::{ubound}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([(t >= lbound) and (t <= ubound) for t in test_vals]))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=int_test::1&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=int_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_float_attr(self):
        test_vals = [random.uniform(-1000.0, 1000.0) for _ in range(len(self.entities))]
        # Test setting an invalid float
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'float_test': 'asdfasdf'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'float_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(response.data['attributes']['float_test'], test_val)
        # Equality on float not recommended but is allowed.
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute=float_test::{test_val}&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for lbound, ubound in [(-1000.0, 1000.0), (-500.0, 500.0), (-500.0, 0.0), (0.0, 500.0)]:
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=float_test::{lbound}&attribute_lt=float_test::{ubound}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([(t > lbound) and (t < ubound) for t in test_vals]))
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=float_test::{lbound}&attribute_lte=float_test::{ubound}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([(t >= lbound) and (t <= ubound) for t in test_vals]))
        # Contains on float not recommended but is allowed.
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=float_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=float_test::false&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_enum_attr(self):
        test_vals = [random.choice(self.attribute_types['enum'].choices) for _ in range(len(self.entities))]
        # Test setting an invalid choice
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'enum_test': 'asdfasdf'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'enum_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(response.data['attributes']['enum_test'], test_val)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=enum_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=enum_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lt=enum_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lte=enum_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for _ in range(10):
            subs = ''.join(random.choices(string.ascii_lowercase, k=2))
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=enum_test::{subs}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([subs.lower() in t.lower() for t in test_vals]))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=enum_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_string_attr(self):
        test_vals = [''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 64)))
            for _ in range(len(self.entities))]
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(f'/rest/{self.detail_uri}/{pk}',
                                         {'attributes': {'string_test': test_val}},
                                         format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(response.data['attributes']['string_test'], test_val)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=string_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=string_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lt=string_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_lte=string_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for _ in range(10):
            subs = ''.join(random.choices(string.ascii_lowercase, k=2))
            response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=string_test::{subs}&type={self.entity_type.pk}&format=json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([subs.lower() in t.lower() for t in test_vals]))
        response = self.client.get(f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=string_test::0&type={self.entity_type.pk}&format=json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_datetime_attr(self):
        end_dt = datetime.datetime.now(datetime.timezone.utc)
        start_dt = end_dt - datetime.timedelta(days=5 * 365)
        test_vals = [
            random_datetime(start_dt, end_dt)
            for _ in range(len(self.entities))
        ]
        # Test setting an invalid datetime
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'datetime_test': 'asdfasdf'}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{pk}',
                {'attributes': {'datetime_test': test_val.isoformat()}},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            self.assertEqual(dateutil_parse(response.data['attributes']['datetime_test']), test_val)
        # Testing for equality not recommended, but it is allowed
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute=datetime_test::{test_val}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        delta_dt = datetime.timedelta(days=365)
        for lbound, ubound in [
                (start_dt, end_dt),
                (start_dt + delta_dt, end_dt - delta_dt),
                (start_dt + delta_dt, end_dt - 2 * delta_dt),
                (start_dt + 2 * delta_dt, end_dt - delta_dt),
            ]:
            lbound_iso = lbound.isoformat()
            ubound_iso = ubound.isoformat()
            response = self.client.get(
                f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=datetime_test::{lbound_iso}&'
                f'attribute_lt=datetime_test::{ubound_iso}&type={self.entity_type.pk}&'
                f'format=json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                len(response.data),
                sum([(t > lbound) and (t < ubound) for t in test_vals])
            )
            response = self.client.get(
                f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=datetime_test::{lbound_iso}&'
                f'attribute_lte=datetime_test::{ubound_iso}&type={self.entity_type.pk}&'
                f'format=json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(
                len(response.data),
                sum([(t >= lbound) and (t <= ubound) for t in test_vals])
            )
        # Contains on datetime not recommended but allowed
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=datetime_test::asdf&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=datetime_test::asdf&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_geoposition_attr(self):
        test_vals = [random_latlon() for _ in range(len(self.entities))]
        # Test setting invalid geopositions
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'geoposition_test': [-91.0, 0.0]}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.patch(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            {'attributes': {'geoposition_test': [0.0, -181.0]}},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for idx, test_val in enumerate(test_vals):
            pk = self.entities[idx].pk
            lat, lon = test_val
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{pk}',
                {'attributes': {'geoposition_test': [lat, lon]}},
                format='json',
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response = self.client.get(f'/rest/{self.detail_uri}/{pk}?format=json')
            self.assertEqual(response.data['id'], pk)
            attrs = response.data['attributes']['geoposition_test']
            self.assertEqual(response.data['attributes']['geoposition_test'], [lat, lon])
        # Equality on geoposition not recommended, but it is allowed
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_lt=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_lte=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_gt=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_gte=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Contains on geoposition not recommended, but it is allowed
        response = self.client.get(
            f'/rest/{self.list_uri}/{self.project.pk}?attribute_contains=geoposition_test::10::{lat}::{lon}&'
            f'type={self.entity_type.pk}&format=json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        test_lat, test_lon = random_latlon()
        for dist in [1.0, 100.0, 1000.0, 5000.0, 10000.0, 43000.0]:
            response = self.client.get(
                f'/rest/{self.list_uri}/{self.project.pk}?attribute_distance=geoposition_test::'
                f'{dist}::{test_lat}::{test_lon}&'
                f'type={self.entity_type.pk}&format=json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(len(response.data), sum([
                latlon_distance(test_lat, test_lon, lat, lon) < dist
                for lat, lon in test_vals
            ]))

class ProjectDeleteTestCase(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.project = create_test_project(self.user)
        self.video_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.box_type = EntityTypeLocalizationBox.objects.create(
            name="boxes",
            project=self.project,
        )
        self.state_type = EntityTypeState.objects.create(
            name="state_type",
            project=self.project,
        )
        self.videos = [
            create_test_video(self.user, f'asdf{idx}', self.video_type, self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.boxes = [
            create_test_box(self.user, self.box_type, self.project, random.choice(self.videos), 0)
            for idx in range(random.randint(6, 10))
        ]
        self.associations = [
            MediaAssociation.objects.create()
            for _ in range(random.randint(6, 10))
        ]
        self.states = []
        for media_association in self.associations:
            for media in random.choices(self.videos):
                media_association.media.add(media)
            self.states.append(
                EntityState.objects.create(
                    meta=self.state_type,
                    project=self.project,
                    association=media_association,
                )
            )

    def test_delete(self):
        self.client.delete(f'/rest/Project/{self.project.pk}')

class AlgorithmLaunchTestCase(
        APITestCase,
        PermissionCreateTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.algorithm = create_test_algorithm(self.user, 'algtest', self.project)
        self.list_uri = 'AlgorithmLaunch'
        self.create_json = {
            'algorithm_name': self.algorithm.name,
            'media_ids': '1,2,3',
        }
        self.edit_permission = Permission.CAN_EXECUTE

class AlgorithmResultTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.algorithm = create_test_algorithm(self.user, 'algtest', self.project)
        self.list_uri = 'AlgorithmResults'
        self.entities = [
            create_test_algorithm_result(
                self.user, 'result1', self.project, self.algorithm
            ) for _ in range(random.randint(6, 10))
        ]

class AlgorithmTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.algorithm = create_test_algorithm(self.user, 'algtest', self.project)
        self.list_uri = 'Algorithms'
        self.entities = [
            create_test_algorithm(self.user, f'result{idx}', self.project)
            for idx in range(random.randint(6, 10))
        ]

class VideoTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entities = [
            create_test_video(self.user, f'asdf{idx}', self.entity_type, self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.media_entities = self.entities
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'EntityMedias'
        self.detail_uri = 'EntityMedia'
        self.create_entity = functools.partial(
            create_test_video, self.user, 'asdfa', self.entity_type, self.project)
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'video1', 'resourcetype': 'EntityMediaVideo'}

class ImageTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entity_type = EntityTypeMediaImage.objects.create(
            name="images",
            project=self.project,
            uploadable=False,
        )
        self.entities = [
            create_test_image(self.user, f'asdf{idx}', self.entity_type, self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.media_entities = self.entities
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'EntityMedias'
        self.detail_uri = 'EntityMedia'
        self.create_entity = functools.partial(
            create_test_image, self.user, 'asdfa', self.entity_type, self.project)
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'image1', 'resourcetype': 'EntityMediaImage'}

class LocalizationBoxTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionCreateTestMixin,
        PermissionListTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        media_entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entity_type = EntityTypeLocalizationBox.objects.create(
            name="boxes",
            project=self.project,
        )
        self.entity_type.media.add(media_entity_type)
        self.media_entities = [
            create_test_video(self.user, f'asdf{idx}', media_entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        self.entities = [
            create_test_box(self.user, self.entity_type, self.project, random.choice(self.media_entities), 0)
            for idx in range(random.randint(6, 10))
        ]
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'Localizations'
        self.detail_uri = 'Localization'
        self.create_entity = functools.partial(
            create_test_box, self.user, self.entity_type, self.project, self.media_entities[0], 0)
        self.create_json = {
            'type': self.entity_type.pk,
            'name': 'asdf',
            'media_id': self.media_entities[0].pk,
            'frame': 0,
            'x': 0,
            'y': 0,
            'width': 10,
            'height': 10,
            'bool_test': True,
            'int_test': 1,
            'float_test': 0.0,
            'enum_test': 'enum_val1',
            'string_test': 'asdf',
            'datetime_test': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'geoposition_test': [0.0, 0.0],
        }
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'box1', 'resourcetype': 'EntityLocalizationBox'}

class LocalizationLineTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionCreateTestMixin,
        PermissionListTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        media_entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entity_type = EntityTypeLocalizationLine.objects.create(
            name="lines",
            project=self.project,
        )
        self.entity_type.media.add(media_entity_type)
        self.media_entities = [
            create_test_video(self.user, f'asdf{idx}', media_entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        self.entities = [
            create_test_line(self.user, self.entity_type, self.project, random.choice(self.media_entities), 0)
            for idx in range(random.randint(6, 10))
        ]
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'Localizations'
        self.detail_uri = 'Localization'
        self.create_entity = functools.partial(
            create_test_line, self.user, self.entity_type, self.project, self.media_entities[0], 0)
        self.create_json = {
            'type': self.entity_type.pk,
            'name': 'asdf',
            'media_id': self.media_entities[0].pk,
            'frame': 0,
            'x0': 0,
            'y0': 0,
            'x1': 10,
            'y1': 10,
            'bool_test': True,
            'int_test': 1,
            'float_test': 0.0,
            'enum_test': 'enum_val1',
            'string_test': 'asdf',
            'datetime_test': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'geoposition_test': [0.0, 0.0],
        } 
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'line1', 'resourcetype': 'EntityLocalizationLine'}

class LocalizationDotTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionCreateTestMixin,
        PermissionListTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        media_entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entity_type = EntityTypeLocalizationDot.objects.create(
            name="lines",
            project=self.project,
        )
        self.entity_type.media.add(media_entity_type)
        self.media_entities = [
            create_test_video(self.user, f'asdf{idx}', media_entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        self.entities = [
            create_test_dot(self.user, self.entity_type, self.project, random.choice(self.media_entities), 0)
            for idx in range(random.randint(6, 10))
        ]
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'Localizations'
        self.detail_uri = 'Localization'
        self.create_entity = functools.partial(
            create_test_dot, self.user, self.entity_type, self.project, self.media_entities[0], 0)
        self.create_json = {
            'type': self.entity_type.pk,
            'name': 'asdf',
            'media_id': self.media_entities[0].pk,
            'frame': 0,
            'x': 0,
            'y': 0,
            'bool_test': True,
            'int_test': 1,
            'float_test': 0.0,
            'enum_test': 'enum_val1',
            'string_test': 'asdf',
            'datetime_test': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'geoposition_test': [0.0, 0.0],
        } 
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'dot1', 'resourcetype': 'EntityLocalizationDot'}

class StateTestCase(
        APITestCase,
        AttributeTestMixin,
        AttributeMediaTestMixin,
        PermissionCreateTestMixin,
        PermissionListTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        media_entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entity_type = EntityTypeState.objects.create(
            name="lines",
            project=self.project,
        )
        self.entity_type.media.add(media_entity_type)
        self.media_entities = [
            create_test_video(self.user, f'asdf', media_entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        media_associations = [
            MediaAssociation.objects.create()
            for _ in range(random.randint(6, 10))
        ]
        self.entities = []
        for media_association in media_associations:
            for media in random.choices(self.media_entities):
                media_association.media.add(media)
            self.entities.append(
                EntityState.objects.create(
                    meta=self.entity_type,
                    project=self.project,
                    association=media_association,
                )
            )
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'EntityStates'
        self.detail_uri = 'EntityState'
        self.create_entity = functools.partial(EntityState.objects.create,
            meta=self.entity_type, project=self.project, association=media_association)
        self.create_json = {
            'type': self.entity_type.pk,
            'name': 'asdf',
            'media_ids': [m.id for m in random.choices(self.media_entities)],
            'bool_test': True,
            'int_test': 1,
            'float_test': 0.0,
            'enum_test': 'enum_val1',
            'string_test': 'asdf',
            'datetime_test': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'geoposition_test': [0.0, 0.0],
        }
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'state1', 'resourcetype': 'EntityState'}

class TreeLeafTestCase(
        APITestCase,
        AttributeTestMixin,
        PermissionCreateTestMixin,
        PermissionListTestMixin,
        PermissionListMembershipTestMixin,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entity_type = EntityTypeTreeLeaf.objects.create(
            project=self.project,
        )
        self.entities = [
            create_test_treeleaf(f'leaf{idx}', self.entity_type, self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.attribute_types = create_test_attribute_types(self.entity_type, self.project)
        self.list_uri = 'TreeLeaves'
        self.detail_uri = 'TreeLeaf'
        self.create_entity = functools.partial(
            create_test_treeleaf, 'leafasdf', self.entity_type, self.project)
        self.create_json = {
            'type': self.entity_type.pk,
            'name': 'asdf',
            'path': 'asdf',
            'bool_test': True,
            'int_test': 1,
            'float_test': 0.0,
            'enum_test': 'enum_val1',
            'string_test': 'asdf',
            'datetime_test': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'geoposition_test': [0.0, 0.0],
        }
        self.edit_permission = Permission.FULL_CONTROL 
        self.patch_json = {'name': 'leaf1', 'resourcetype': 'TreeLeaf'}

class TreeLeafTypeTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entities = [
            EntityTypeTreeLeaf.objects.create(project=self.project)
            for _ in range(random.randint(6, 10))
        ]
        self.list_uri = 'TreeLeafTypes'

class EntityStateTypesTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.list_uri = 'EntityStateTypes'
        self.entities = [
            EntityTypeState.objects.create(
                name="lines",
                project=self.project,
            ),
            EntityTypeState.objects.create(
                name="boxes",
                project=self.project,
            ),
        ]
        
class EntityTypeMediaTestCase(
        APITestCase,
        PermissionDetailMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.detail_uri = 'EntityTypeMedia'
        self.entities = [
            EntityTypeMediaVideo.objects.create(
                name="videos",
                uploadable=True,
                keep_original=True,
                project=self.project,
            ),
            EntityTypeMediaImage.objects.create(
                name="images",
                uploadable=True,
                project=self.project,
            ),
        ]
        for entity_type in self.entities:
            create_test_attribute_types(entity_type, self.project)

class EntityTypeSchemaTestCase(
        APITestCase,
        PermissionDetailMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.detail_uri = 'EntityTypeSchema'
        self.entities = [
            EntityTypeMediaVideo.objects.create(
                name="videos",
                uploadable=True,
                keep_original=True,
                project=self.project,
            ),
            EntityTypeMediaImage.objects.create(
                name="images",
                uploadable=True,
                project=self.project,
            ),
        ]
        for entity_type in self.entities:
            create_test_attribute_types(entity_type, self.project)

class LocalizationAssociationTestCase(
        APITestCase,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        media_entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.media_entities = [
            create_test_video(self.user, f'asdf', media_entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        localization_type = EntityTypeLocalizationBox.objects.create(
            name="boxes",
            project=self.project,
        )
        self.localizations = [
            create_test_box(
                self.user, localization_type, self.project,
                random.choice(self.media_entities), random.randint(0, 1000)
            ) for _ in range(6, 10)
        ]
        self.entities = [
            LocalizationAssociation.objects.create()
            for _ in range(random.randint(6, 10))
        ]
        state_type = EntityTypeState.objects.create(
            name="lines",
            project=self.project,
        )
        self.states = [
            EntityState.objects.create(
                meta=state_type,
                project=self.project,
                association=entity,
            ) for entity in self.entities
        ]
        for entity in self.entities:
            for localization in random.choices(self.localizations):
                entity.localizations.add(localization)
        self.detail_uri = 'LocalizationAssociation'
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'color': 'asdf'}

class LocalizationTypesTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entities = [
            EntityTypeLocalizationBox.objects.create(
                name="box",
                project=self.project,
            ),
            EntityTypeLocalizationLine.objects.create(
                name="line",
                project=self.project,
            ),
            EntityTypeLocalizationLine.objects.create(
                name="line1",
                project=self.project,
            ),
        ]
        for entity_type in self.entities:
            create_test_attribute_types(entity_type, self.project)
        self.list_uri = 'LocalizationTypes'

class MembershipTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.list_uri = 'Memberships'

class PackageTestCase(
        APITestCase,
        PermissionDetailMembershipTestMixin,
        PermissionDetailTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entities = [
            create_test_package(self.user, f'asdf{idx}', self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.edit_permission = Permission.CAN_EDIT
        self.patch_json = {'name': 'asdfasdf'}
        self.detail_uri = 'Package'

class PackageCreateTestCase(
        APITestCase,
        PermissionCreateTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.list_uri = 'PackageCreate'
        self.create_json = {
            'package_name': 'asdf',
            'media_query': '?media_id=1,2,3',
        }
        self.edit_permission = Permission.CAN_TRANSFER

class PackagesTestCase(
        APITestCase,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entities = [
            create_test_package(self.user, f'asdf{idx}', self.project)
            for idx in range(random.randint(6, 10))
        ]
        self.list_uri = 'Packages'

class ProjectTestCase(APITestCase):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.entities = [
            create_test_project(self.user)
            for _ in range(random.randint(6, 10))
        ]
        memberships = [
            create_test_membership(self.user, entity)
            for entity in self.entities
        ]
        self.detail_uri = 'Project'
        self.patch_json = {
            'name': 'aaasdfasd',
            'section_order': ['asdf1', 'asdf2', 'asdf3']
        }
        self.edit_permission = Permission.FULL_CONTROL

    def test_detail_patch_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            obj = Membership.objects.filter(project=self.entities[0], user=self.user)[0]
            obj.permission = level
            obj.save()
            del obj
            if index >= permission_index:
                expected_status = status.HTTP_200_OK
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            response = self.client.patch(
                f'/rest/{self.detail_uri}/{self.entities[0].pk}',
                self.patch_json,
                format='json')
            self.assertEqual(response.status_code, expected_status)

    def test_detail_delete_permissions(self):
        permission_index = permission_levels.index(self.edit_permission)
        for index, level in enumerate(permission_levels):
            obj = Membership.objects.filter(project=self.entities[0], user=self.user)[0]
            obj.permission = level
            obj.save()
            del obj
            if index >= permission_index:
                expected_status = status.HTTP_204_NO_CONTENT
            else:
                expected_status = status.HTTP_403_FORBIDDEN
            test_val = random.random() > 0.5
            response = self.client.delete(
                f'/rest/{self.detail_uri}/{self.entities[0].pk}',
                format='json')
            self.assertEqual(response.status_code, expected_status)
            if expected_status == status.HTTP_204_NO_CONTENT:
                del self.entities[0]

    def test_delete_non_creator(self):
        other_user = User.objects.create(
            username="other",
            password="user",
            first_name="other",
            last_name="user",
            email="other.user@gmail.com",
            middle_initial="A",
            initials="OAU",
        )
        create_test_membership(other_user, self.entities[0])
        self.client.force_authenticate(other_user)
        response = self.client.delete(
            f'/rest/{self.detail_uri}/{self.entities[0].pk}',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class TranscodeTestCase(
        APITestCase,
        PermissionCreateTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.list_uri = 'Transcode'
        self.entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.create_json = {
            'type': f'{self.entity_type.pk}',
            'gid': str(uuid1()),
            'uid': str(uuid1()),
            'url': 'http://asdf.com',
            'name': 'asdf.mp4',
            'section': 'asdf section',
            'md5': '',
        }
        self.edit_permission = Permission.CAN_TRANSFER

class AnalysisCountTestCase(
        APITestCase,
        PermissionCreateTestMixin,
        PermissionListMembershipTestMixin):
    def setUp(self):
        self.user = create_test_user()
        self.client.force_authenticate(self.user)
        self.project = create_test_project(self.user)
        self.membership = create_test_membership(self.user, self.project)
        self.entity_type = EntityTypeMediaVideo.objects.create(
            name="video",
            project=self.project,
            uploadable=False,
            keep_original=False,
        )
        self.entities = [
            create_test_video(self.user, f'asdf{idx}', self.entity_type, self.project)
            for idx in range(random.randint(3, 10))
        ]
        self.analysis = AnalysisCount.objects.create(
            project=self.project,
            name="count_test",
            data_type=self.entity_type,
            data_filter={'attributes__enum_test': 'enum_val1'},
        )
        self.attribute_type = AttributeTypeEnum.objects.create(
            name='enum_test',
            choices=['enum_val1', 'enum_val2', 'enum_val3'],
            applies_to=self.entity_type,
            project=self.project,
        )
        self.list_uri = 'Analyses'
        self.create_json = {
            'resourcetype': 'AnalysisCount',
            'project': self.project.pk,
            'name': 'count_create_test',
            'data_type': self.entity_type.pk,
            'data_filter': {'attributes__enum_test': 'enum_val2'},
        }
        self.edit_permission = Permission.FULL_CONTROL
