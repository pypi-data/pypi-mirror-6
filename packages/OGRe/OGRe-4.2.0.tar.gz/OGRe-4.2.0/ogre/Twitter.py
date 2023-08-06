"""OGRe Twitter Interface

:func:`twitter` : method for fetching data from Twitter

"""

import base64
import hashlib
import logging
import sys
import urllib
from datetime import datetime
from time import time
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

    kinds = []
    if clean_media is not None:
        for clean_medium in clean_media:
            if clean_medium in ("image", "text"):
                kinds.append(clean_medium)
    kinds = tuple(kinds)

    if kinds == ("image",):
        q += "  pic.twitter.com"
    elif kinds == ("text",):
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

    if q in ("", "-pic.twitter.com") and geocode is None:
        raise ValueError("Specify either a keyword or a location.")

    return (
        clean_keys,
        kinds,
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

    qid = hashlib.md5(
        str(time.time()) +
        str(q) +
        str(remaining) +
        str(geocode) +
        str(since_id) +
        str(max_id)
    ).hexdigest()
    logging.basicConfig(
        filename="OGRe.log",
        level=logging.ERROR,
        format="%(asctime)s %(levelname)s:%(message)s",
        datefmt="%Y/%m/%d %H:%M:%S %Z"
    )
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    log.info(qid+" Request: Twitter")
    log.debug(
        qid+" Status:" +
        " keyword("+str(q)+")" +
        " quantity("+str(remaining)+")" +
        " location("+str(geocode)+")" +
        " interval("+str(since_id)+","+str(max_id)+")"
    )

    if api is None:
        api = Twython
    db = api(keychain["consumer_key"], access_token=keychain["access_token"])
    limits = db.get_application_rate_limit_status()
    maximum_queries =\
        limits["resources"]["search"]["/search/tweets"]["remaining"]
    if maximum_queries < 1:
        log.info(qid+" Failure: Queries are being limited.")
    else:
        log.debug(qid+" Status: "+str(maximum_queries)+" queries remain.")
    total = remaining

    collection = []
    for query in range(0, maximum_queries):
        count = min(remaining, 100)  # Twitter accepts a max count of 100.
        try:
            results = db.search(
                q=q,
                count=count,
                geocode=geocode,
                since_id=since_id,
                max_id=max_id
            )
        except:
            log.info(
                qid+" Failure: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                str(sys.exc_info()[1])
            )
            raise
        if "statuses" not in results.keys():
            log.info(
                qid+" Failure: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "The request is too complex."
            )
            break
        for tweet in results["statuses"]:
            if tweet["coordinates"] is None:
                continue
            feature = {
                "type": "Feature",
                "geometry": tweet["coordinates"],
                "properties": {
                    "source": "Twitter",
                    "time": datetime.utcfromtimestamp(
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
                        if entity["type"].lower() == "photo":
                            feature["properties"]["image"] = base64.b64encode(
                                urllib.urlopen(entity["media_url"]).read()
                            )
                        else:
                            log.warn(
                                qid+" Unrecognized Entity ("+entity["type"]+")"
                            )
            collection.append(feature)
        remained = remaining
        remaining = total-len(collection)
        log.debug(
            qid+" Status:" +
            " 1 query produced "+str(remained-remaining)+" results."
        )
        if remaining <= 0:
            log.info(
                qid+" Success: " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results."
            )
            break
        if "next_results" not in results["search_metadata"].keys():
            outcome = "Success" if len(collection) > 0 else "Failure"
            log.info(
                qid+" "+outcome+": " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "No retrievable results remain."
            )
            break
        max_id = int(
            results["search_metadata"]["next_results"]
            .split("max_id=")[1]
            .split("&")[0]
        )
        if query+1 >= maximum_queries:
            outcome = "Success" if len(collection) > 0 else "Failure"
            log.info(
                qid+" "+outcome+": " +
                str(query+1)+" queries produced " +
                str(len(collection))+" results. " +
                "No remaining results are retrievable."
            )
    return collection
