"""OGRe Twitter Interface Tests"""

import base64
import json
import os
import unittest
import urllib
from datetime import datetime
from mock import MagicMock, call
from snowflake2time import snowflake
from ogre import OGRe
from ogre.Twitter import twitter


class OGReTest (unittest.TestCase):

    """Create objects that test the OGRe module."""

    def setUp(self):
        """Prepare to run tests on OGRe.

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
        self.retriever = OGRe({
            "Twitter": {
                "consumer_key": os.environ.get("TWITTER_CONSUMER_KEY"),
                "access_token": os.environ.get("TWITTER_ACCESS_TOKEN")
            }
        })
        self.api = MagicMock()
        with open("ogre/test/data/Twitter-response-example.json") as tweets:
            self.tweets = json.load(tweets)

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

        with self.assertRaises(ValueError):
            twitter(self.retriever.keychain["Twitter"])
        with self.assertRaises(KeyError):
            twitter(
                {"invalid": "invalid"},
                keyword="test"
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=("malformed",)
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=("malformed", 0, 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(-100, 0, 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(100, 0, 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, "malformed", 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, -200, 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, 200, 0, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, 0, "malformed", "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, 0, -1, "km")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, 0, 0, "invalid")
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                locale=(0, 0, 0, 0)
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                period=("malformed",)
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                period=(-1, 1)
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                period=(1, -1)
            )
        with self.assertRaises(ValueError):
            twitter(
                self.retriever.keychain["Twitter"],
                medium=("invalid",)
            )
        with self.assertRaises(AttributeError):
            twitter(
                self.retriever.keychain["Twitter"],
                medium=(1,)
            )

        self.assertEqual(
            twitter(self.retriever.keychain["Twitter"], medium=()),
            []
        )

        self.api.reset_mock()
        self.assertEqual(
            twitter(
                self.retriever.keychain["Twitter"],
                keyword="test",
                locale=(0, 1, 2, "km"),
                period=(3, 4),
                medium=("image", "text"),
                api=self.api
            ),
            []
        )
        self.api.assert_called_once_with(
            self.retriever.keychain["Twitter"]["consumer_key"],
            access_token=self.retriever.keychain["Twitter"]["access_token"]
        )
        self.api().search.assert_called_once_with(
            q="test",
            count=100,
            geocode="0.0,1.0,2.0km",
            since_id=-5405765676960841728,
            max_id=-5405765672766537728
        )
        self.api.reset_mock()
        self.api().search.return_value = self.tweets
        self.assertEqual(
            twitter(
                self.retriever.keychain["Twitter"],
                keyword="test",
                locale=(0, 1, 2, "km"),
                period=(3, 4),
                medium=("image", "text"),
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
