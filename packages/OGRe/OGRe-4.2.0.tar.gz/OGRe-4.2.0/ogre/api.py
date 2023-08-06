"""OGRe Query Handler

:class:`OGRe` -- retriever object template

:meth:`OGRe.fetch` -- method for making a retriever fetch data

:meth:`OGRe.get` -- alias of :meth:`OGRe.fetch`

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

    :meth:`fetch` -- method for retrieving data from a public source

    :meth:`get` -- backwards-compatible alias of :meth:`fetch`

    """

    def __init__(self, keys):
        """Instantiate an OGRe.

        :param keys: dictionaries containing API keys for public sources
        :type keys: dict

        .. note:: "Twitter" is currently the only supported source.

        Keys that a retriever object is instantiated with may be accessed later
        through the :attr:`keychain` attribute.

        .. note:: There is also a :attr:`keyring` attribute which maintains
                  a mapping of the lowercase version of each key to the
                  casing of the passed key. This enables you to pass a key with
                  a name stylized in the manner of your choosing (e.g. twitter,
                  Twitter, tWiTtEr, etc.)

        :raises: ValueError

        """
        self.keyring = {}
        for key, chain in keys.items():
            if key.lower() not in (
                "twitter"
            ):
                raise ValueError('Keys may include "Twitter" only.')
            self.keyring[key.lower()] = key
        self.keychain = keys

    def fetch(
        self,
        sources,
        media=("image", "sound", "text", "video"),
        keyword="",
        quantity=15,
        location=None,
        interval=None,
        api=None
    ):

        """Get geotagged data from public APIs.

        :param sources: public APIs to get content from (required)
        :type sources: tuple

        .. note:: "Twitter" is currently the only supported source.

        :param media: content mediums to get
        :type media: tuple

        .. note:: "image", "sound", "text", or "video" are supported mediums.

        :param keyword: term to search for
        :type keyword: str

        :param quantity: number of results to fetch
        :type quantity: int

        .. note:: The `quantity` parameter is satisfied on a best effort basis.
                  Fewer results may be returned due to lack of availability.

        :param location: latitude, longitude, radius, and unit
        :type location: tuple

        .. note:: "km" or "mi" are supported units.

        :param interval: earliest and latest moments (POSIX timestamps)
        :type interval: tuple

        .. note:: The order of earliest/latest moments does not matter.

        :param api: API access point (used for testing)
        :type api: callable

        :raises: ValueError

        :returns: GeoJSON FeatureCollection
        :rtype: dict

        """

        source_map = {"twitter": twitter}

        feature_collection = {
            "type": "FeatureCollection",
            "features": []
        }
        if media and quantity > 0:
            for source in sources:
                source = source.lower()
                if source not in source_map.keys():
                    raise ValueError('Source may be "Twitter".')
                for features in source_map[source](
                    keys=self.keychain[self.keyring[source]],
                    media=media,
                    keyword=keyword,
                    quantity=quantity,
                    location=location,
                    interval=interval,
                    api=api
                ):
                    feature_collection["features"].append(features)
        return feature_collection

    def get(
        self,
        sources,
        keyword="",
        what=("image", "sound", "text", "video"),
        when=None,
        where=None,
        how_many=15,
        api=None
    ):
        """Provide a backwards-compatible alias of :meth:`fetch`.

        .. deprecated: 4.1.0
           This method has been replaced by :meth:`fetch` which mirrors the
           interface used by individual source modules (e.g. :mod:`Twitter`).

        :param sources: corresponds directly
        :type sources: tuple

        :param keyword: corresponds directly
        :type keyword: str

        :param what: corresponds to `media`
        :type what: tuple

        :param when: corresponds to `interval`
        :type when: tuple

        :param where: corresponds to `location`
        :type where: tuple

        :param how_many: corresponds to `quantity`
        :type how_many: int

        :param api: corresponds directly
        :type api: callable

        :returns: GeoJSON FeatureCollection
        :rtype: dict

        """
        return self.fetch(
            sources=sources,
            media=what,
            keyword=keyword,
            interval=when,
            location=where,
            quantity=how_many,
            api=api
        )
