"""OGRe Twitter Interface

:func:`twitter` : method for fetching data from Twitter

"""

import base64
import urllib
from datetime import datetime
from warnings import warn
from twython import Twython
from ogre.validation import sanitize
from snowflake2time.snowflake import *


def sanitize_twitter(
        keys,
        media=("image", "text"),
        keyword="",
        quantity=15,
        location=None,
        interval=None
):

    """Validate and prepare parameters for use in Twitter data retrieval.

    .. seealso:: https://dev.twitter.com/docs/api/1.1/get/search/tweets

    :param keys: Twitter API keys
    :type keys: dict

    .. note:: Twitter **requires** a "consumer_key" and "access_token".

    :param media: content mediums to get
    :type media: tuple

    .. note:: Twitter supports posts containing "image" and "text" only.

    :param keyword: search term(s)
    :type keyword: str

    .. note:: "Queries can be limited due to complexity." If this happens, no
              results will be returned. To avoid this, follow Twitter Best
              Practices including the following:
              "Limit your searches to 10 keywords and operators."

    .. seealso:: https://dev.twitter.com/docs/using-search

    :param quantity: number of results to fetch
    :type quantity: int

    .. note:: Twitter will return 15 results by default, and up to 100 can be
              requested in a single query. If a number larger than 100 is
              specified, the retriever will make multiple queries in an attempt
              to satisfy the requested `quantity`, but this is done on a
              best effort basis. Whether the specified number is returned or
              not depends on Twitter.

    :param location: latitude, longitude, radius, and unit
    :type location: tuple

    .. note:: Since OGRe only returns geotagged results, the larger the
              specified radius, the fewer results will be returned. This is
              because of the way Twitter satisfies geocoded queries. It uses
              so-called "fuzzy matching logic" to deduce the location of Tweets
              posted publicly but without location data. OGRe filters these out.

    :param interval: earliest and latest moments (POSIX timestamps)
    :type interval: tuple

    .. note:: "The Search API is not complete index of all Tweets,
               but instead an index of recent Tweets." Twitter's definition of
               "recent" is rather vague, but when an interval is not specified,
               "that index includes between 6-9 days of Tweets."

    :raises: ValueError

    :returns: Each passed parameter is returned (in order) in the proper format.
    :rtype: tuple

    """

    clean_keys = {}
    for key, value in keys.items():
        key = key.lower()
        if key not in (
            "consumer_key",
            "access_token"
        ):
            raise ValueError(
                'Valid Twitter keys are "consumer_key" and "access_token".'
            )
        if not value:
            raise ValueError("Twitter API keys are required.")
        clean_keys[key] = value
    if "consumer_key" not in clean_keys.keys() or \
       "access_token" not in clean_keys.keys():
        raise ValueError(
            'Twitter API keys must include a "consumer_key" and "access_token".'
        )

    clean_media, q, clean_quantity, clean_location, clean_interval = \
        sanitize(
            media=media,
            keyword=keyword,
            quantity=quantity,
            location=location,
            interval=interval
        )

    if clean_media is not None:
        if clean_media == ("image",):
            q += "  pic.twitter.com"
        elif clean_media == ("text",):
            q += " -pic.twitter.com"
    q = q.strip()

    geocode = None
    if location is not None and clean_location[2] > 0:
        geocode = \
            str(clean_location[0]) + "," +\
            str(clean_location[1]) + "," +\
            str(clean_location[2])+clean_location[3]

    period_id = (None, None)
    if interval is not None:
        period_id = (
            utc2snowflake(clean_interval[0]),
            utc2snowflake(clean_interval[1])
        )

    if q in ("", " -pic.twitter.com") and geocode is None:
        raise ValueError("Specify either a keyword or a location.")

    return (
        clean_keys,
        clean_media,
        q,
        clean_quantity,
        geocode,
        period_id
    )


def twitter(
        keys,
        media=("image", "text"),
        keyword="",
        quantity=15,
        location=None,
        interval=None,
        api=None
):

    """Fetch Tweets from the Twitter API.

    :param keys: API key and access token
    :type keys: dict

    .. note:: "consumer_key" and "access_token" are **required** keys.

    :param media: content mediums to get
    :type media: tuple

    .. note:: "text" or "image" are supported mediums.

    :param keyword: term to search for
    :type keyword: str

    :param quantity: quantity of results to fetch
    :type quantity: int

    .. note:: The `quantity` parameter is satisfied on a best effort basis.
              Fewer results may be returned due to lack of availability.

    :param location: latitude, longitude, radius, and unit
    :type location: tuple

    .. note:: "km" or "mi" are supported units.

    :param interval: earliest and latest moments (POSIX timestamps)
    :type interval: tuple

    .. note:: The order of earliest/latest moments does not matter.

    :param api: API access point (used for dependency injection)
    :type api: callable

    :raises: TwythonError

    :returns: GeoJSON Feature(s)
    :rtype: list

    """

    keychain, kinds, q, remaining, geocode, (since_id, max_id) = \
        sanitize_twitter(
            keys=keys,
            media=media,
            keyword=keyword,
            quantity=quantity,
            location=location,
            interval=interval
        )

    if not kinds or remaining < 1:
        return []

    if api is None:
        api = Twython

    total = remaining

    collection = []
    for i in range(0, 450):  # Twitter allows 450 requests every 15 minutes.
        count = min(remaining, 100)  # Twitter accepts a max count of 100.
        results = api(
            keychain["consumer_key"],
            access_token=keychain["access_token"]
        ).search(
            q=q,
            count=count,
            geocode=geocode,
            since_id=since_id,
            max_id=max_id
        )
        if "statuses" not in results.keys():
            # Query is too complex.
            # TODO Test overly complex queries.
            break
        for tweet in results["statuses"]:
            if tweet["coordinates"] is None:
                continue
            feature = {
                "type": "Feature",
                "geometry": tweet["coordinates"],
                "properties": {
                    "source": "Twitter",
                    "timestamp": datetime.utcfromtimestamp(
                        snowflake2utc(tweet["id"])
                    ).isoformat()+"Z"
                }
            }
            if "text" in kinds:
                feature["properties"]["text"] = tweet["text"]
            if "image" in kinds:
                if ("media" in tweet["entities"] and
                        tweet["entities"]["media"] is not None):
                    for entity in tweet["entities"]["media"]:
                        if entity["type"] == "photo":
                            feature["properties"]["image"] = base64.b64encode(
                                urllib.urlopen(entity["media_url"]).read()
                            )
                        else:
                            warn('New type "'+entity["type"]+'" detected.')
            collection.append(feature)
        if len(collection) < total:
            remaining = total-len(collection)
        else:
            break
        if "next_results" not in results["search_metadata"].keys():
            # All available results have been received.
            break
        max_id = int(
            results["search_metadata"]["next_results"]
            .split("max_id=")[1]
            .split("&")[0]
        )
    return collection
