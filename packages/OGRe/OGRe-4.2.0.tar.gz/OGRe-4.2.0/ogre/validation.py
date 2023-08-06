"""OGRe Parameter Validator

:func:`validate` -- check OGRe parameters for errors

:func:`sanitize` -- validate and cleanse OGRe parameters

"""


def validate(
    media=("image", "sound", "text", "video"),
    keyword="",
    quantity=15,
    location=None,
    interval=None,
):

    """Check common interface parameters for errors and validity.

    :param media: content mediums to get
    :type media: tuple

    .. note:: "image", "sound", "text", or "video" are valid mediums.

    :param keyword: search term(s)
    :type keyword: str

    :param quantity: number of results to fetch
    :type quantity: int

    .. note:: The `quantity` parameter must be positive.

    :param location: latitude, longitude, radius, and unit
    :type location: tuple

    .. note:: The `latitude`, `longitude`, and `radius` parameters should be
              floats or integers, and the `unit` parameters must be a string.
              "km" or "mi" are supported units.

    :param interval: earliest and latest moments (POSIX timestamps)
    :type interval: tuple

    .. note:: The `earliest` and `latest` parameters should be floats or
              integers and must be positive.

    :raises: ValueError

    """

    if media is not None:
        for medium in media:
            medium = medium.lower()
            if medium not in (
                "image",
                "sound",
                "text",
                "video"
            ):
                raise ValueError(
                    'Medium may be "image", "sound", "text", or "video".'
                )

    try:
        str(keyword)
    except:
        raise ValueError("Keyword must be a string.")

    if int(quantity) < 0:
        raise ValueError("Quantity must be positive.")

    if location is not None:
        if len(location) != 4:
            raise ValueError(
                "usage: where=(latitude, longitude, radius, unit)"
            )
        latitude = float(location[0])
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude must be -90 to 90.")
        longitude = float(location[1])
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude must be -180 to 180.")
        radius = float(location[2])
        if radius < 0:
            raise ValueError("Radius must be positive.")
        unit = location[3].lower()
        if unit not in ("km", "mi"):
            raise ValueError('Unit must be "km" or "mi".')

    if interval is not None:
        if len(interval) != 2:
            raise ValueError("usage: when=(earliest, latest)")
        since = float(interval[0])
        if since < 0:
            raise ValueError("Earliest moment must be POSIX timestamps.")
        until = float(interval[1])
        if until < 0:
            raise ValueError("Latest moment must be POSIX timestamps.")


def sanitize(
    media=("image", "sound", "text", "video"),
    keyword="",
    quantity=15,
    location=None,
    interval=None,
):

    """Validate and transform input to expected types.

    :param media: content mediums to get
    :type media: tuple

    .. note:: Duplicates are removed, and all mediums are made lowercase.

    :param keyword: search term(s)
    :type keyword: str

    :param quantity: number of results to fetch
    :type quantity: int

    :param location: latitude, longitude, radius, and unit
    :type location: tuple

    .. note:: The `unit` parameter is made lowercase.

    :param interval: earliest and latest moments (POSIX timestamps)
    :type interval: tuple

    .. note:: The `earliest` and `latest` parameters are put in ascending order.

    :returns: Each passed parameter is returned (in order) in the proper format.
    :rtype: tuple

    """

    validate(
        media=media,
        keyword=keyword,
        quantity=quantity,
        location=location,
        interval=interval
    )

    clean_media = []
    if media is not None:
        for medium in media:
            medium = medium.lower()
            if medium not in clean_media:
                clean_media.append(medium)

    clean_media = tuple(clean_media)
    clean_keyword = str(keyword)
    clean_quantity = int(quantity)

    clean_location = None
    if location is not None:
        latitude = float(location[0])
        longitude = float(location[1])
        radius = float(location[2])
        unit = location[3].lower()
        clean_location = (latitude, longitude, radius, unit)

    clean_interval = None
    if interval is not None:
        since = float(interval[0])
        until = float(interval[1])
        if since > until:
            since, until = until, since
        clean_interval = (since, until)

    return (
        clean_media,
        clean_keyword,
        clean_quantity,
        clean_location,
        clean_interval
    )
