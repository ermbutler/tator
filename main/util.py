from collections import defaultdict
import logging
import os
import time
import subprocess
import json
import datetime
import shutil
import math
from typing import Dict

from progressbar import progressbar,ProgressBar
from dateutil.parser import parse
from boto3.s3.transfer import S3Transfer
from PIL import Image

from main.models import *
from main.models import Resource
from main.search import TatorSearch
from main.store import get_tator_store

from django.conf import settings
from django.db.models import F

from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk

logger = logging.getLogger(__name__)

""" Utility scripts for data management in django-shell """

def updateProjectTotals(force=False):
    projects=Project.objects.all()
    for project in projects:
        temp_files = TemporaryFile.objects.filter(project=project)
        files = Media.objects.filter(project=project, deleted=False)
        num_files = temp_files.count() + files.count()
        if force or num_files != project.num_files:
            project.num_files = num_files
            duration_info = files.values('num_frames', 'fps')
            project.duration = sum([info['num_frames'] / info['fps'] for info in duration_info
                                    if info['num_frames'] and info['fps']])
            logger.info(f"Updating {project.name}: Num files = {project.num_files}, "
                        f"Duration = {project.duration}")
        if not project.thumb:
            media = Media.objects.filter(project=project, media_files__isnull=False).first()
            if media:
                tator_store = get_tator_store(project.bucket, connect_timeout=1, read_timeout=1, max_attempts=1)
                if "thumbnail" in media.media_files and media.media_files["thumbnail"]:
                    src_path = media.media_files['thumbnail'][0]['path']
                    dest_path = f"{project.organization.pk}/{project.pk}/{os.path.basename(src_path)}"
                    tator_store.copy(src_path, dest_path)
                    project.thumb = dest_path
        users = User.objects.filter(pk__in=Membership.objects.filter(project=project)\
                            .values_list('user')).order_by('last_name')
        usernames = [str(user) for user in users]
        creator = str(project.creator)
        if creator in usernames:
            usernames.remove(creator)
            usernames.insert(0, creator)
        project.usernames = usernames
        project.save()

def waitForMigrations():
    """Sleeps until database objects can be accessed.
    """
    while True:
        try:
            list(Project.objects.all())
            break
        except:
            time.sleep(10)

INDEX_CHUNK_SIZE = 50000
CLASS_MAPPING = {'media': Media,
                 'localizations': Localization,
                 'states': State,
                 'treeleaves': Leaf,
                 'files': File}

def get_num_index_chunks(project_number, section, max_age_days=None):
    """ Returns number of chunks for parallel indexing operation.
    """
    count = 1
    if section in CLASS_MAPPING:
        qs = CLASS_MAPPING[section].objects.filter(project=project_number, meta__isnull=False)
        if max_age_days:
            min_modified = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
            qs = qs.filter(modified_datetime__gte=min_modified)
        count = math.ceil(qs.count() / INDEX_CHUNK_SIZE)
    return count

def buildSearchIndices(project_number, section, mode='index', chunk=None, max_age_days=None):
    """ Builds search index for a project.
        section must be one of:
        'index' - create the index for the project if it does not exist
        'mappings' - create mappings for the project if they do not exist
        'media' - create documents for media
        'states' - create documents for states
        'localizations' - create documents for localizations
        'treeleaves' - create documents for treeleaves
        'files' - create documents for files
    """
    project_name = Project.objects.get(pk=project_number).name
    logger.info(f"Building search indices for project {project_number}: {project_name}")

    if section == 'index':
        # Create indices
        logger.info("Building index...")
        TatorSearch().create_index(project_number)
        logger.info("Build index complete!")
        return

    if section == 'mappings':
        # Create mappings
        logger.info("Building mappings for media types...")
        for type_ in progressbar(list(MediaType.objects.filter(project=project_number))):
            TatorSearch().create_mapping(type_)
        logger.info("Building mappings for localization types...")
        for type_ in progressbar(list(LocalizationType.objects.filter(project=project_number))):
            TatorSearch().create_mapping(type_)
        logger.info("Building mappings for state types...")
        for type_ in progressbar(list(StateType.objects.filter(project=project_number))):
            TatorSearch().create_mapping(type_)
        logger.info("Building mappings for leaf types...")
        for type_ in progressbar(list(LeafType.objects.filter(project=project_number))):
            TatorSearch().create_mapping(type_)
        logger.info("Building mappings for file types...")
        for type_ in progressbar(list(FileType.objects.filter(project=project_number))):
            TatorSearch().create_mapping(type_)
        logger.info("Build mappings complete!")
        return

    class DeferredCall:
        def __init__(self, qs):
            self._qs = qs
        def __call__(self):
            for entity in self._qs.iterator():
                if not entity.deleted:
                    for doc in TatorSearch().build_document(entity, mode):
                        yield doc

    # Get queryset based on selected section.
    logger.info(f"Building documents for {section}...")
    qs = CLASS_MAPPING[section].objects.filter(project=project_number, meta__isnull=False)

    # Apply max age filter.
    if max_age_days:
        min_modified = datetime.datetime.now() - datetime.timedelta(days=max_age_days)
        qs = qs.filter(modified_datetime__gte=min_modified)

    # Apply limit/offset if chunk parameter given.
    if chunk is not None:
        offset = INDEX_CHUNK_SIZE * chunk
        qs = qs.order_by('id')[offset:offset+INDEX_CHUNK_SIZE]

    batch_size = 500
    count = 0
    bar = ProgressBar(redirect_stderr=True, redirect_stdout=True)
    dc = DeferredCall(qs)
    total = qs.count()
    bar.start(max_value=total)
    for ok, result in streaming_bulk(TatorSearch().es, dc(),chunk_size=batch_size, raise_on_error=False):
        action, result = result.popitem()
        if not ok:
            print(f"Failed to {action} document! {result}")
        bar.update(min(count, total))
        count += 1
        if count > total:
            print(f"Count exceeds list size by {total - count}")
    bar.finish()

def makeDefaultVersion(project_number):
    """ Creates a default version for a project and sets all localizations
        and states to that version. Meant for usage on projects that were
        not previously using versions.
    """
    project = Project.objects.get(pk=project_number)
    version = Version.objects.filter(project=project, number=0)
    if version.exists():
        version = version[0]
    else:
        version = make_default_version(project)
    logger.info("Updating localizations...")
    qs = Localization.objects.filter(project=project)
    qs.update(version=version)
    logger.info("Updating states...")
    qs = State.objects.filter(project=project)
    qs.update(version=version)

from pprint import pprint

def make_video_definition(disk_file, url_path):
        cmd = [
        "ffprobe",
        "-v","error",
        "-show_entries", "stream",
        "-print_format", "json",
        disk_file,
        ]
        output = subprocess.run(cmd, stdout=subprocess.PIPE, check=True).stdout
        video_info = json.loads(output)
        stream_idx=0
        for idx, stream in enumerate(video_info["streams"]):
            if stream["codec_type"] == "video":
                stream_idx=idx
                break
        stream = video_info["streams"][stream_idx]
        video_def = getVideoDefinition(
            url_path,
            stream["codec_name"],
            (stream["height"], stream["width"]),
            codec_description=stream["codec_long_name"])

        return video_def

def migrateVideosToNewSchema(project):
    videos = Media.objects.filter(project=project, meta__dtype='video')
    for video in progressbar(videos):
        streaming_definition = make_video_definition(
            os.path.join(settings.MEDIA_ROOT,
                         video.file.name),
            os.path.join(settings.MEDIA_URL,
                         video.file.name))
        if video.segment_info:
            streaming_definition['segment_info'] = video.segment_info
        if video.original:
            archival_definition = make_video_definition(video.original,
                                                        video.original)
        media_files = {"streaming" : [streaming_definition]}

        if archival_definition:
            media_files.update({"archival": [archival_definition]})
        video.media_files = media_files
        pprint(media_files)
        video.save()

def fixVideoDims(project):
    videos = Media.objects.filter(project=project, meta__dtype='video')
    for video in progressbar(videos):
        try:
            if video.original:
                archival_definition = make_video_definition(video.original,
                                                            video.original)
                video.height = archival_definition["resolution"][0]
                video.width = archival_definition["resolution"][1]
                video.save()
        except:
            print(f"Error on {video.pk}")

def clearOldFilebeatIndices():
    es = Elasticsearch([os.getenv('ELASTICSEARCH_HOST')])
    for index in es.indices.get('filebeat-*'):
        tokens = str(index).split('-')
        if len(tokens) < 3:
            continue
        dt = parse(tokens[2])
        delta = datetime.datetime.now() - dt
        if delta.days > 7:
            logger.info(f"Deleting old filebeat index {index}")
            es.indices.delete(str(index))

def make_sections():
    for project in Project.objects.all().iterator():
        es = Elasticsearch([os.getenv('ELASTICSEARCH_HOST')])
        result = es.search(index=f'project_{project.pk}',
                           body={'size': 0,
                                 'aggs': {'sections': {'terms': {'field': 'tator_user_sections',
                                                                 'size': 1000}}}},
                           stored_fields=[])
        for section in result['aggregations']['sections']['buckets']:
            Section.objects.create(project=project,
                                   name=section['key'],
                                   tator_user_sections=section['key'])
            logger.info(f"Created section {section['key']} in project {project.pk}!")

def make_resources():

    # Function to build resource objects from paths.
    def _resources_from_paths(paths):
        paths = [os.readlink(path) if os.path.islink(path) else path for path in paths]
        exists = list(Resource.objects.filter(path__in=paths).values_list('path', flat=True))
        needs_create = list(set(paths).difference(exists))
        paths = []
        return [Resource(path=p) for p in needs_create]

    # Function to get paths from media.
    def _paths_from_media(media):
        paths = []
        if media.file:
            paths.append(media.file.path)
        if media.media_files:
            for key in ['streaming', 'archival', 'audio', 'image', 'thumbnail', 'thumbnail_gif', 'attachment']:
                if key in media.media_files:
                    paths += [f['path'] for f in media.media_files[key]]
                    if key == 'streaming':
                        try:
                            paths += [f['segment_info'] for f in media.media_files[key]]
                        except:
                            logger.info(f"Media {media.id} does not have a segment file!")
        if media.original:
            paths.append(media.original)
        return paths

    # Create all resource objects that don't already exist.
    num_resources = 0
    path_list = []
    create_buffer = []
    for media in Media.objects.all().iterator():
        path_list += _paths_from_media(media)
        if len(path_list) > 1000:
            create_buffer += _resources_from_paths(path_list)
            path_list = []
        if len(create_buffer) > 1000:
            Resource.objects.bulk_create(create_buffer)
            num_resources += len(create_buffer)
            create_buffer = []
            logger.info(f"Created {num_resources} resources...")
    if len(path_list) > 0:
        create_buffer += _resources_from_paths(path_list)
        path_list = []
    if len(create_buffer) > 0:
        Resource.objects.bulk_create(create_buffer)
        num_resources += len(create_buffer)
        create_buffer = []
        logger.info(f"Created {num_resources} resources...")
    logger.info("Resource creation complete!")

    # Create many to many relations.
    Resource.media.through.objects.all().delete()
    num_relations = 0
    media_relations = []
    for media in Media.objects.all().iterator():
        path_list = _paths_from_media(media)
        path_list = [os.readlink(path) if os.path.islink(path) else path for path in path_list]
        for resource in Resource.objects.filter(path__in=path_list).iterator():
            media_relation = Resource.media.through(
                resource_id=resource.id,
                media_id=media.id,
            )
            media_relations.append(media_relation)
        if len(media_relations) > 1000:
            Resource.media.through.objects.bulk_create(media_relations)
            num_relations += len(media_relations)
            media_relations = []
            logger.info(f"Created {num_relations} media relations...")
    if len(media_relations) > 0:
        Resource.media.through.objects.bulk_create(media_relations)
        num_relations += len(media_relations)
        media_relations = []
        logger.info(f"Created {num_relations} media relations...")
    logger.info("Media relation creation complete!")

def set_default_versions():
    memberships = Membership.objects.all()
    for membership in list(memberships):
        versions = Version.objects.filter(project=membership.project, number__gte=0).order_by('number')
        if versions.exists():
            versions_by_name = {version.name: version for version in versions}
            if str(membership.user) in versions_by_name:
                membership.default_version = versions_by_name[str(membership.user)]
            else:
                membership.default_version = versions[0]
            logger.info(f"Set default version for user {membership.user}, project "
                        f"{membership.project} to {membership.default_version.name}...")
            membership.save()
    logger.info(f"Set all default versions!")

def move_backups_to_s3():
    store = get_tator_store().store
    transfer = S3Transfer(store)
    bucket_name = os.getenv('BUCKET_NAME')
    num_moved = 0
    for backup in os.listdir('/backup'):
        logger.info(f"Moving {backup} to S3...")
        key = f'backup/{backup}'
        path = os.path.join('/backup', backup)
        transfer.upload_file(path, bucket_name, key)
        os.remove(path)
        num_moved += 1
    logger.info(f"Finished moving {num_moved} files!")


def fix_bad_archives(*, project_id_list=None, live_run=False, force_update=False):
    from pprint import pformat
    media_to_update = set()
    path_filename = "manifest_spec.txt"

    def _tag_needs_updating(path, store):
        return force_update or not store._object_tagged_for_archive(path)

    def _sc_needs_updating(path, store):
        return (
            force_update
            or store.head_object(path).get("StorageClass", "STANDARD") != store.get_archive_sc()
        )

    def _update_tag(path, store):
        if live_run:
            try:
                store._put_archive_tag(path)
            except:
                logger.warning(f"Tag operation on {path} failed", exc_info=True)
                return False
        else:
            media_to_update.add(f"{path}\n")

        return True

    def _archive_multi(multi, store):
        media_ids = multi.media_files.get("ids")
        if not media_ids:
            return "failed"

        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        media_qs = Media.objects.filter(pk__in=media_ids)
        for single in media_qs.iterator():
            single_success, single_sc_needs_updating, single_tag_needs_updating = _archive_single(
                single, store
            )
            success = success and single_success
            sc_needs_updating = sc_needs_updating or single_sc_needs_updating
            tag_needs_updating = tag_needs_updating or single_tag_needs_updating

        return success, sc_needs_updating, tag_needs_updating

    def _archive_single(single, store):
        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        for key in ["streaming", "archival", "audio", "image"]:
            if not (key in single.media_files and single.media_files[key]):
                continue

            for obj in single.media_files[key]:
                try:
                    path = obj["path"]
                except:
                    logger.warning(f"Could not get path from {key} in {single.id}", exc_info=True)
                    success = False
                    continue

                if not _sc_needs_updating(path, store):
                    continue

                sc_needs_updating = True
                if not _tag_needs_updating(path, store):
                    continue

                tag_needs_updating = True
                try:
                    success = _update_tag(path, store) and success
                except:
                    logger.warning(
                        f"Copy operation on {path} from {single.id} failed", exc_info=True
                    )
                    success = False

                if key == "streaming":
                    try:
                        success = _update_tag(obj["segment_info"], store) and success
                    except:
                        success = False

        return success, sc_needs_updating, tag_needs_updating

    logger.info(f"fix_bad_archives {'live' if live_run else 'dry'} run")

    archive_state_dict = {}
    project_qs = Project.objects.all()

    if project_id_list:
        project_qs = project_qs.filter(pk__in=project_id_list)

    for project in project_qs.iterator():
        tator_store = get_tator_store(project.bucket)
        proj_id = project.id
        logger.info(f"Analyzing project {proj_id}...")
        archived_media_qs = Media.objects.filter(project=project, archive_state="archived")
        media_count = archived_media_qs.count()
        if media_count < 1:
            logger.info(f"No archived media in project {proj_id}, moving on")
            continue

        archive_state_dict[proj_id] = {
            "correct_sc": 0,
            "successfully_archived": 0,
            "correct_tag": 0,
            "successfully_tagged": 0,
            "failed": 0,
        }
        idx = 0
        for media in archived_media_qs.iterator():
            idx += 1
            if idx % 250 == 0 or idx == media_count:
                logger.info(
                    f"Processed {idx} of {media_count} archived media for project {project.id}"
                )

            if not media.meta:
                logger.warning(f"No dtype for '{media.id}'")
                continue

            media_dtype = media.meta.dtype
            if media_dtype in ["image", "video"]:
                success, sc_needs_updating, tag_needs_updating = _archive_single(media, tator_store)
            elif media_dtype == "multi":
                success, sc_needs_updating, tag_needs_updating = _archive_multi(media, tator_store)
            else:
                logger.warning(
                    f"Unrecognized dtype '{media_dtype}' for media {media.id}, failed to archive"
                )
                continue

            if success:
                if tag_needs_updating:
                    archive_state_dict[proj_id]["successfully_tagged"] += 1
                else:
                    archive_state_dict[proj_id]["correct_tag"] += 1

                if sc_needs_updating:
                    archive_state_dict[proj_id]["successfully_archived"] += 1
                else:
                    archive_state_dict[proj_id]["correct_sc"] += 1
            else:
                archive_state_dict[proj_id]["failed"] += 1

    logger.info(f"fix_bad_archives stats:\n{pformat(archive_state_dict)}\n")
    if media_to_update:
        with open(path_filename, "w") as fp:
            fp.writelines(media_to_update)


def fix_bad_restores(
        *, media_id_list, live_run=False, force_update=False, restored_by_date=None
):
    from pprint import pformat
    update_sc = set()
    update_tag = set()
    archived_resources = set()
    sc_filename = "still_archived.json"
    tag_filename = "still_tagged.json"
    ar_filename = "archived_resources.json"

    def _tag_needs_updating(path, store):
        try:
            return force_update or store._object_tagged_for_archive(path)
        except:
            logging.warning(f"Could not detect object tags for {path}", exc_info=True)
            return False

    def _sc_needs_updating(path, store):
        return (
            force_update
            or store.head_object(path).get("StorageClass", "STANDARD") != store.get_live_sc()
        )

    def _update_sc(single, store):
        success = True
        if live_run:
            try:
                single.archive_state = "to_live"
                single.save()
            except:
                logger.warning(f"archive state update on {single.id} failed", exc_info=True)
                return False
        else:
            update_sc.add(f"{single.id}\n")

        return success

    def _check_and_update(file_info, store, has_segment_info):
        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        path_keys = ["path"]
        if has_segment_info:
            path_keys.append("segment_info")

        for path_key in path_keys:
            try:
                path = file_info[path_key]
            except:
                logger.warning(f"Could not get {path_key}", exc_info=True)
                success = False
                continue

            if _sc_needs_updating(path, store):
                sc_needs_updating = True
                archived_resources.add(path)

            if _tag_needs_updating(path, store):
                tag_needs_updating = True
                update_tag.add(f"{path}\n")

        return success, sc_needs_updating, tag_needs_updating

    def _archive_multi(multi, store):
        media_ids = multi.media_files.get("ids")
        if not media_ids:
            return "failed"

        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        media_qs = Media.objects.filter(pk__in=media_ids)
        for single in media_qs.iterator():
            single_success, single_sc_needs_updating, single_tag_needs_updating = _archive_single(
                single, store
            )
            success = success and single_success
            sc_needs_updating = sc_needs_updating or single_sc_needs_updating
            tag_needs_updating = tag_needs_updating or single_tag_needs_updating

        return success, sc_needs_updating, tag_needs_updating

    def _archive_single(single, store):
        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        if single.media_files:
            for key in ["streaming", "archival", "audio", "image"]:
                if key in single.media_files and single.media_files[key]:
                    for file_info in single.media_files[key]:
                        has_segment_info = key == "streaming"
                        bools = _check_and_update(file_info, store, has_segment_info)
                        success = success and bools[0]
                        sc_needs_updating = sc_needs_updating or bools[1]
                        tag_needs_updating = tag_needs_updating or bools[2]

            if sc_needs_updating:
              try:
                  success = _update_sc(single, store) and success
              except:
                  logger.warning(
                      f"Storage class operation on {path} from {single.id} failed", exc_info=True
                  )
                  success = False
        else:
            logger.warning(f"Media {single.id} has no media files")

        return success, sc_needs_updating, tag_needs_updating

    logger.info(f"fix_bad_restore {'live' if live_run else 'dry'} run")

    live_state_dict = {}
    tator_store_lookup = {}
    media_qs = Media.objects.filter(pk__in=media_id_list)
    media_count = media_qs.count()

    for idx, media in enumerate(media_qs.iterator()):
        proj_id = media.project.id
        if proj_id not in tator_store_lookup:
            tator_store_lookup[proj_id] = get_tator_store(media.project.bucket)
        if proj_id not in live_state_dict:
            live_state_dict[proj_id] = {
                "correct_sc": 0,
                "wrong_sc": 0,
                "correct_tag": 0,
                "wrong_tag": 0,
                "failed": 0,
            }

        if idx % 250 == 0 or idx == media_count:
            logger.info(f"Processed {idx} of {media_count} media")

        if not media.meta:
            logger.warning(f"No dtype for '{media.id}'")
            continue

        media_dtype = media.meta.dtype
        tator_store = tator_store_lookup[proj_id]
        if media_dtype in ["image", "video"]:
            success, sc_needs_updating, tag_needs_updating = _archive_single(media, tator_store)
        elif media_dtype == "multi":
            success, sc_needs_updating, tag_needs_updating = _archive_multi(media, tator_store)
        else:
            logger.warning(
                f"Unrecognized dtype '{media_dtype}' for media {media.id}, failed to archive"
            )
            continue

        if success:
            if tag_needs_updating:
                live_state_dict[proj_id]["wrong_tag"] += 1
            else:
                live_state_dict[proj_id]["correct_tag"] += 1

            if sc_needs_updating:
                live_state_dict[proj_id]["wrong_sc"] += 1
            else:
                live_state_dict[proj_id]["correct_sc"] += 1
        else:
            live_state_dict[proj_id]["failed"] += 1

    logger.info(f"fix_bad_restores stats:\n{pformat(live_state_dict)}\n")
    if update_sc:
        with open(sc_filename, "w") as fp:
            json.dump(list(update_sc), fp)
    if update_tag:
        with open(tag_filename, "w") as fp:
            json.dump(list(update_tag), fp)
    if archived_resources:
        with open(ar_filename, "w") as fp:
            json.dump(list(archived_resources), fp)


def update_media_archive_state(
    media: Media,
    archive_state: str,
    restoration_requested: bool,
    **op_kwargs: dict,
) -> bool:
    """
    Attempts to update the archive state of all media associated with a video or image, except for
    thumbnails. If successful, the archive state of the media is changed according to the given
    arguments and True is returned.

    :param media: The media to update
    :type media: Media
    :param archive_state: The target for `media.archive_state`
    :type archive_state: str
    :param restoration_requested: The target for `media.restoration_requested`
    :type restoration_requested: bool
    :rtype: int
    """

    def _archive_state_comp(_media):
        """
        Compares the `archive_state` and `restoration_requested` values of the given media object
        against the desired target values. Returns `True` if they both match, `False` otherwise.
        """
        return (
            _media.archive_state == archive_state
            and _media.restoration_requested == restoration_requested
        )

    # Lookup table for operators based on the target `archive_state` and `restoration_requested`
    # values. `update_operator` must accept one string argument and return a boolean; `multi_test`
    # must accept an iterable and return a boolean
    operators_key = (archive_state, restoration_requested)
    one_in_false_out = lambda _in: False
    default = (one_in_false_out, one_in_false_out)
    update_operator, multi_test = {
        ("archived", False): (Resource.archive_resource, any),
        ("to_live", True): (Resource.request_restoration, all),
        ("live", False): (Resource.restore_resource, all),
    }.get(operators_key, default)

    success = []
    if media.media_files:
        for path in media.path_iterator(keys=["streaming", "archival", "audio", "image"]):
            success.append(update_operator(path, **op_kwargs))
    else:
        # If there are no media files, consider the noop update attempt successful
        success.append(True)

    success = all(success)
    if success:
        new_status_date = datetime.datetime.now(datetime.timezone.utc)
        media.archive_status_date = new_status_date
        media.archive_state = archive_state
        media.restoration_requested = restoration_requested
        media.save()

        # Check for multiviews containing this single and put them in the same state if they need
        # updating
        multi_qs = Media.objects.filter(meta__dtype="multi", media_files__ids__contains=media.id)
        for multi in multi_qs.iterator():
            if not _archive_state_comp(multi) and multi_test(
                _archive_state_comp(single)
                for single in Media.objects.filter(pk__in=multi.media_files["ids"])
            ):
                multi.archive_status_date = new_status_date
                multi.archive_state = archive_state
                multi.restoration_requested = restoration_requested
                multi.save()

    return success


def get_clones(media: Media, filter_dict: Dict[str, str] = None) -> Dict[int, Dict[str, set]]:
    """
    Gets the exhaustive list of clone ids of the given media. If a `filter_dict` argument is given,
    it is used to filter media from the results to determine the subset of clones that match. The
    return value is a dictionary with the keys being single media ids (i.e. the given media's id for
    a single type or the media ids that compose a multiview) and the value being another dict, with
    three keys:

    - `all`: contains the set of all integer media ids of all clones of the given media.
    - `original`: contains the set of integer media ids of the original clones. For a single media,
      e.g. `media.meta.dtype` is `video` or `image`, `original` will contain exactly one element.
      For multiviews, i.e. `media.meta.dtype` is `multi`, `original` will contain the same number of
      elements as `media.media_files`.
    - `remaining`: contains the set of integer media ids that are clones of the given media object
      that do match the `filter_dict` arguments, if given, otherwise it is empty

    :param media: The media to find clones of.
    :type media: Media
    :param filter_dict: If specified, it is the keyword arguments to pass to the `exclude` operation
                        on the clones' queryset and will populate the `remaining` set.
    :type filter_dict: dict
    :rtype: dict
    """

    def _find_multi_clones(media: Media, return_dict: Dict[int, Dict[str, set]]) -> None:
        """
        Checks the given multiview's individual media for clones.
        """
        # If media.media_files is empty or none, there is nothing to check
        if media.media_files:
            # Get the queryset of all single media ids in the multiview
            single_qs = Media.objects.filter(pk__in=media.media_files["ids"])

            # Find the set of clones for each
            for obj in single_qs.iterator():
                _find_single_clones(obj, return_dict[obj.id])

    def _find_single_clones(media: Media, clone_dict: Dict[str, set]) -> None:
        """
        Checks the given media for clones and applies `filter_dict`, if set. Starts with the first
        entry of `keys` and moves on if the key is not found in `media.media_files`. For clones that
        match the `filter_dict`, if set, this will update the `clone_dict["remaining"]` set with
        their integer ids.
        """
        original_media_ids = set()

        for key in ["streaming", "archival", "audio", "image"]:
            # If the given key does not exist in `media_files` or the list of files is empty, move
            # on to the next key, if any
            if not (key in media.media_files and media.media_files[key]):
                continue

            # Collect all paths for this key
            paths = [obj["path"] for obj in media.media_files[key]]

            # Update the set of original_media_ids with the part of the path that is the media id to
            # which this object was originally uploaded
            original_media_ids.update(int(path.split("/")[2]) for path in paths)

            # Shared base queryset
            media_qs = Media.objects.filter(resource_media__path__in=paths)
            media_dict["all"].update(list(media_qs.values_list("id", flat=True)))

            # Apply filter_dict, if given
            if filter_dict:
                media_qs = media_qs.exclude(**filter_dict)
                media_dict["remaining"].update(list(media_qs.values_list("id", flat=True)))

        n_original_ids = len(original_media_ids)
        if n_original_ids != 1:
            logger.error(
                f"Found {n_original_ids} original clones of {media.id}: {original_media_ids}"
            )

        media_dict["original"].update(original_media_ids)

    # Set up the return dict
    return_value = defaultdict(lambda: {"all": set(), "original": set(), "remaining": set()})

    dtype = getattr(media.meta, "dtype", None)

    if dtype in ["image", "video"]:
        _find_single_clones(media, return_value[media.id])
    elif dtype == "multi":
        _find_multi_clones(media, return_value)
    else:
        logger.error(f"Expected dtype in ['multi', 'image', 'video'], got '{dtype}'")

    return dict(return_value)
