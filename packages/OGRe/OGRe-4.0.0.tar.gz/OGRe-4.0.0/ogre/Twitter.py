"""OGRe Twitter Interface

:func:`twitter` : method for fetching data from Twitter

"""

import base64
import urllib
from datetime import datetime
from warnings import warn
from twython import Twython
from snowflake2time.snowflake import *


def twitter(
        keys,
        keyword="",
        locale=None,
        period=None,
        medium=("image", "text"),
        api=None
):

    """Fetch Tweets from the Twitter API.

    :param keys: API key and access token
    :type keys: dict

    .. note:: "consumer_key" and "access_token" are **required** keys.

    :param keyword: term to search for
    :type keyword: str

    :param locale: latitude, longitude, radius, and unit
    :type locale: tuple

    .. note:: "km" or "mi" are supported units.

    :param period: earliest and latest moments (POSIX timestamps)
    :type period: tuple

    :param medium: content mediums to get
    :type medium: tuple

    .. note:: "text" or "image" are supported mediums.

    :param api: API access point (used for dependency injection)
    :type api: callable

    :raises: AttributeError, KeyError, ValueError

    :returns: GeoJSON Feature(s)
    :rtype: list

    """

    coordinate = None
    if locale is not None:
        if len(locale) != 4:
            raise ValueError(
                "usage: locale=(latitude, longitude, radius, unit)"
            )
        latitude = float(locale[0])
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be -90 to 90.")
        longitude = float(locale[1])
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be -180 to 180.")
        radius = float(locale[2])
        if radius < 0:
            raise ValueError("Radius must be positive.")
        unit = locale[3]
        if unit not in ("km", "mi"):
            raise ValueError('Unit must be "km" or "mi".')
        coordinate = str(latitude)+","+str(longitude)+","+str(radius)+unit

    since = None
    until = None
    if period is not None:
        if len(period) != 2:
            raise ValueError("usage: period=(earliest, latest)")
        since = float(period[0])
        if since < 0:
            raise ValueError("Earliest moment must be POSIX timestamps.")
        until = float(period[1])
        if until < 0:
            raise ValueError("Latest moment must be POSIX timestamps.")
        since = utc2snowflake(since)
        until = utc2snowflake(until)

    media = []
    for kind in medium:
        kind = kind.lower()
        if kind not in ("image", "text"):
            raise ValueError('Medium may be "image" or "text".')
        if kind not in media:
            media.append(kind)
    if not media:
        return []
    if media == ["image"]:
        keyword += "  pic.twitter.com"
    elif media == ["text"]:
        keyword += " -pic.twitter.com"

    # TODO Verify Twitter accepts keyword="", medium=(text,) with a period.
    if keyword is "" and locale is None and period is None:
        raise ValueError("Specify either a keyword or constraints.")

    if api is None:
        api = Twython
    data = api(
        keys["consumer_key"],
        access_token=keys["access_token"]
    )
    results = data.search(
        q=keyword.strip(),
        count=100,
        geocode=coordinate,
        since_id=since,
        max_id=until
    )

    collection = []
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
        if "text" in media:
            feature["properties"]["text"] = tweet["text"]
        if "image" in media:
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
    return collection
