"""OGRe Twitter Interface Tests

:class:`TwitterTest` -- Twitter interface test template

:meth:`TwitterTest.setUp` -- test initialization

:meth:`TwitterTest.test_sanitize_twitter` -- Twitter parameter preparation tests

:meth:`TwitterTest.test_twitter` -- Twitter API query tests

"""

import base64
import json
import os
import unittest
import urllib
from datetime import datetime
from mock import MagicMock, call
from snowflake2time import snowflake
from ogre import OGRe
from ogre.Twitter import *


class TwitterTest (unittest.TestCase):

    """Create objects that test the OGRe module.

    :meth:`TwitterTest.setUp` -- retriever and Twython Mock initialization

    :meth:`TwitterTest.test_sanitize_twitter` -- parameter cleansing tests

    :meth:`TwitterTest.test_twitter` -- API access and results-packaging tests

    """

    def setUp(self):
        """Prepare to run tests on the Twitter interface.

        Since OGRe requires API keys to run and they cannot be stored
        conveniently, this test module retrieves them from the OS;
        however, to prevent OGRe from actually querying the APIs
        (and subsequently retrieving unpredictable data),
        a MagicMock object is used to do a dependency injection.
        This relieves the need for setting environment variables
        (although they may be necessary in the future).
        Predictable results are stored in the data directory to be read
        during these tests.

        """
        self.retriever = OGRe(
            keys={
                "Twitter": {
                    "consumer_key": os.environ.get("TWITTER_CONSUMER_KEY"),
                    "access_token": os.environ.get("TWITTER_ACCESS_TOKEN")
                }
            }
        )
        self.api = MagicMock()
        with open("ogre/test/data/Twitter-response-example.json") as tweets:
            self.tweets = json.load(tweets)

    def test_sanitize_twitter(self):

        """Test the Twitter interface parameter sanitizer.

        These tests should verify that malformed or invalid data is detected
        before being sent to Twitter. They should also test that valid data is
        formatted correctly for use by Twython.

        """

        with self.assertRaises(ValueError):
            sanitize_twitter(keys={})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"invalid": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"consumer_key": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(keys={"consumer_key": "key", "invalid": None})
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys={
                    "consumer_key": "key",
                    "access_token": None
                }
            )
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ]
            )
        with self.assertRaises(ValueError):
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                location=(2, 1, 0, "km")
            )

        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("text",),
                keyword="test"
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("text",),
                "test -pic.twitter.com",
                15,
                None,
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image",),
                keyword="test"
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image",),
                "test  pic.twitter.com",
                15,
                None,
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                location=(0, 1, 2, "km")
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image", "text"),
                "",
                15,
                "0.0,1.0,2.0km",
                (None, None)
            )
        )
        self.assertEqual(
            sanitize_twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                interval=(0, 1)
            ),
            (
                self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                ("image", "text"),
                "test",
                15,
                None,
                (-5405765689543753728, -5405765685349449728)
            )
        )

    def test_twitter(self):

        """Test OGRe's access point to the Twitter API.

        These tests should make sure all input is validated correctly,
        and they should make sure that any relevant Twitter data is extracted
        and packaged in GeoJSON format correctly.

        The first two Tweets in the example Twitter response data
        must be geotagged, and the first one must an image entity attached.
        If any other geotagged data is included, this test will fail;
        however, it is a good idea to include non-geotagged Tweets
        to ensure that OGRe omits them in the returned results.

        """

        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=(),
                keyword="test"
            ),
            []
        )
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                keyword="test",
                quantity=0
            ),
            []
        )

        self.api.reset_mock()
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image", "text"),
                keyword="test",
                quantity=5,
                location=(4, 3, 2, "km"),
                interval=(1, 0),
                api=self.api
            ),
            []
        )
        self.api.assert_called_once_with(
            self.retriever.keychain[
                self.retriever.keyring["twitter"]
            ]["consumer_key"],
            access_token=self.retriever.keychain[
                self.retriever.keyring["twitter"]
            ]["access_token"]
        )
        self.api().search.assert_called_once_with(
            q="test",
            count=5,
            geocode="4.0,3.0,2.0km",
            since_id=-5405765689543753728,
            max_id=-5405765685349449728
        )

        self.api.reset_mock()
        self.api().search.return_value = self.tweets
        self.assertEqual(
            twitter(
                keys=self.retriever.keychain[
                    self.retriever.keyring["twitter"]
                ],
                media=("image", "text"),
                keyword="test",
                quantity=2,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                api=self.api
            ),
            [
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][0]
                                ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][0]
                                ["coordinates"]["coordinates"][1],
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][0]["text"],
                        "image": base64.b64encode(urllib.urlopen(
                            self.tweets["statuses"][0]
                                ["entities"]["media"][0]["media_url"]
                        ).read()),
                        "timestamp": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][0]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                },
                {
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            self.tweets["statuses"][1]
                                ["coordinates"]["coordinates"][0],
                            self.tweets["statuses"][1]
                                ["coordinates"]["coordinates"][1],
                        ]
                    },
                    "type": "Feature",
                    "properties": {
                        "source": "Twitter",
                        "text": self.tweets["statuses"][1]["text"],
                        "timestamp": datetime.utcfromtimestamp(
                            snowflake.snowflake2utc(
                                self.tweets["statuses"][1]["id"]
                            )
                        ).isoformat()+"Z"
                    }
                }
            ]
        )

        self.api.reset_mock()


if __name__ == "__main__":
    unittest.main()
