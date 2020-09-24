from collections import defaultdict

from ..models import Media
from ..search import TatorSearch
from ..schema import MediaCountSchema

from ._base_views import BaseDetailView
from ._media_query import get_media_queryset
from ._permissions import ProjectViewOnlyPermission

class MediaCountAPI(BaseDetailView):
    """ Retrieve number of media in a media list.

        This endpoint accepts the same query parameters as a GET request to the `Medias` endpoint,
        but only returns the next media ID from the media passed as a path parameter. This allows
        iteration through a media list without serializing the entire list, which may be large.
    """
    schema = MediaCountSchema()
    permission_classes = [ProjectViewOnlyPermission]
    http_method_names = ['get']

    def _get(self, params):
        """ Retrieve number of media in list of media.
        """
        response_data = []
        media_ids, media_count, _ = get_media_queryset(
            self.kwargs['project'],
            params,
        )
        return len(media_ids)
