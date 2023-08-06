"""OGRe Query Handler

:class:`OGRe` -- retriever object template

:func:`OGRe.get` -- method for making a retriever fetch data

"""

from ogre.Twitter import twitter


class OGRe:

    """Create objects that contain API keys and API access points.

    OGRe was made a class to avoid requiring API keys with every API call.
    Since this is a library meant for developers,
    it didn't seem appropriate to use a configuration file.
    Also, importing the keys from the OS environment subjects them to data leak.
    This way developers are responsible for keeping their keys safe.
    Twython, the Twitter API wrapper, also uses this scheme.

    :func:`get` -- method for retrieving data from a public source

    """

    def __init__(self, keys):
        """Instantiate an OGRe.

        :param keys: dictionaries containing API keys for public sources
        :type keys: dict

        .. note:: "Twitter" is the only supported source.

        """
        self.keychain = keys

    def get(
        self,
        sources,
        keyword="",
        what=None,
        when=None,
        where=None,
        api=None
    ):

        """Fetch geotagged data from public APIs.

        :param sources: public APIs to get content from (required)
        :type sources: tuple

        :param keyword: term to search for
        :type keyword: str

        :param what: content mediums to get
        :type what: tuple

        .. note:: "image", "sound", "text", or "video" are supported mediums.

        :param when: earliest and latest moments (POSIX timestamps)
        :type when: tuple

        :param where: latitude, longitude, radius, and unit
        :type where: tuple

        .. note:: "km" or "mi" are supported units.

        :param api: API access point (used for testing)
        :type api: callable

        :raises: AttributeError, ValueError

        :returns: GeoJSON FeatureCollection
        :rtype: dict

        """

        # TODO Verify Twitter accepts any constraint instead of a keyword.
        if keyword is "" and what is None and when is None and where is None:
            raise ValueError("Specify either a keyword or constraints.")

        medium = []
        if what is not None:
            for kind in what:
                kind = kind.lower()
                if kind not in (
                    "image",
                    "sound",
                    "text",
                    "video"
                ):
                    raise ValueError(
                        'Medium may be "image", "sound", "text", or "video".'
                    )
                if kind not in medium:
                    medium.append(kind)
        if not medium:
            medium = ("image", "sound", "text", "video")

        period = None
        if when is not None:
            if len(when) != 2:
                raise ValueError("usage: when=(earliest, latest)")
            since = float(when[0])
            if since < 0:
                raise ValueError("Earliest moment must be POSIX timestamps.")
            until = float(when[1])
            if until < 0:
                raise ValueError("Latest moment must be POSIX timestamps.")
            if since > until:
                since, until = until, since
            period = (since, until)

        locale = None
        if where is not None:
            if len(where) != 4:
                raise ValueError(
                    "usage: where=(latitude, longitude, radius, unit)"
                )
            latitude = float(where[0])
            if latitude < -90 or latitude > 90:
                raise ValueError("Latitude must be -90 to 90.")
            longitude = float(where[1])
            if longitude < -180 or longitude > 180:
                raise ValueError("Longitude must be -180 to 180.")
            radius = float(where[2])
            if radius < 0:
                raise ValueError("Radius must be positive.")
            unit = where[3].lower()
            if unit not in ("km", "mi"):
                raise ValueError('Unit must be "km" or "mi".')
            locale = (latitude, longitude, radius, unit)

        feature_collection = {
            "type": "FeatureCollection",
            "features": []
        }
        source_map = {"twitter": twitter}
        for source in sources:
            source = source.lower()
            if source not in source_map.keys():
                raise ValueError('Source may be "Twitter".')
            else:
                for feature in source_map[source](
                    self.keychain["Twitter"],
                    keyword,
                    locale,
                    period,
                    medium,
                    api
                ):
                    feature_collection["features"].append(feature)
        return feature_collection
