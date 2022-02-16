import logging
import os
import time
import subprocess
import json
import datetime
import shutil
import math

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
                tator_store = get_tator_store(project.bucket)
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
        *, project_id_list=None, live_run=False, force_update=False, restored_by_date=None
):
    from pprint import pformat
    media_to_update = set()
    path_filename = "still_archived.txt"

    def _tag_needs_updating(path, store):
        try:
            return force_update or store._object_tagged_for_archive(path)
        except:
            logging.warning(f"Could not detect object tags for {path}", exc_info=True)
            return False

    def _sc_needs_updating(path, store):
        return (
            force_update
            or store.head_object(path).get("StorageClass", "DEEP_ARCHIVE") != store.get_live_sc()
        )

    def _update_tag(path, store):
        if live_run:
            try:
                store.delete_all_tags(path)
            except:
                logger.warning(f"Tag operation on {path} failed", exc_info=True)
                return False
        else:
            media_to_update.add(f"{path}\n")

        return True

    def _update_sc(path, store):
        success = True
        if live_run:
            try:
                success = store.request_restoration(path, 30)
            except:
                logger.warning(f"restoration request on {path} failed", exc_info=True)
                return False
            if success:
                try:
                    success = store.restore_resource(path)
                except:
                    logger.warning(f"sc update on {path} failed", exc_info=True)
                    return False
        else:
            media_to_update.add(f"{path}\n")

        return success

    def _check_and_update(db_object, key, store, segment_info=False):
        success = True
        sc_needs_updating = False
        tag_needs_updating = False
        path_key = "segment_info" if segment_info else "path"
        try:
            path = db_object[path_key]
        except:
            logger.warning(f"Could not get {path_key}", exc_info=True)
            return False, False, False

        if _sc_needs_updating(path, store):
            sc_needs_updating = True
            try:
                success = _update_sc(path, store) and success
            except:
                logger.warning(
                    f"Storage class operation on {path} from {single.id} failed", exc_info=True
                )
                success = False

        if _tag_needs_updating(path, store):
            tag_needs_updating = True
            try:
                success = _update_tag(path, store) and success
            except:
                logger.warning(f"Tag operation on {path} from {single.id} failed", exc_info=True)
                success = False

        if key == "streaming" and (tag_needs_updating or sc_needs_updating):
            stream_stats = _check_and_update(db_object, path_key, store, segment_info=True)
            success = success and stream_stats[0]
            sc_needs_updating = sc_needs_updating or stream_stats[1]
            tag_needs_updating = tag_needs_updating or stream_stats[2]

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
                    for obj in single.media_files[key]:
                        bools = _check_and_update(obj, key, store)
                        success = success and bools[0]
                        sc_needs_updating = sc_needs_updating or bools[1]
                        tag_needs_updating = tag_needs_updating or bools[2]
        else:
            logger.warning(f"Media {single.id} has no media files")

        return success, sc_needs_updating, tag_needs_updating

    logger.info(f"fix_bad_restore {'live' if live_run else 'dry'} run")

    live_state_dict = {}
    project_qs = Project.objects.all()

    if project_id_list:
        project_qs = project_qs.filter(pk__in=project_id_list)

    for project in project_qs.iterator():
        tator_store = get_tator_store(project.bucket)
        proj_id = project.id
        logger.info(f"Analyzing project {proj_id}...")
        live_media_qs = Media.objects.filter(project=project, archive_state="live")
        if restored_by_date is not None:
            live_media_qs = live_media_qs.filter(archive_status_date__gte=restored_by_date)
        media_count = live_media_qs.count()
        if media_count < 1:
            logger.info(f"No archived media in project {proj_id}, moving on")
            continue

        live_state_dict[proj_id] = {
            "correct_sc": 0,
            "wrong_sc": 0,
            "correct_tag": 0,
            "wrong_tag": 0,
            "failed": 0,
        }
        idx = 0
        for media in live_media_qs.iterator():
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
    if media_to_update:
        with open(path_filename, "w") as fp:
            fp.writelines(media_to_update)
