"""OGRe Query Handler Tests"""

import json
import os
import unittest
from mock import MagicMock, call
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

    def test_get(self):

        """Test the main entry point to OGRe.

        These tests should make sure all input is validated correctly,
        and they should ensure that the retrieved results are packaged
        in a GeoJSON FeatureCollection object properly.

        """

        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",))
        with self.assertRaises(ValueError):
            self.retriever.get(("invalid",), keyword="test")
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), what=("invalid",))
        with self.assertRaises(AttributeError):
            self.retriever.get(("Twitter",), what=(1,))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), when=("malformed",))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), when=(-1, 1))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), when=(1, -1))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=("malformed",))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=("malformed", 0, 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(-100, 0, 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(100, 0, 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, "malformed", 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, -200, 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, 200, 0, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, 0, "malformed", "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, 0, -1, "km"))
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter",), where=(0, 0, 0, "invalid"))
        with self.assertRaises(AttributeError):
            self.retriever.get(("Twitter",), where=(0, 0, 0, 0))

        self.assertEqual(
            self.retriever.get((), keyword="test"),
            {
                "type": "FeatureCollection",
                "features": []
            }
        )
        self.assertEqual(
            self.retriever.get((), when=(0, 1)),
            self.retriever.get((), when=(1, 0))
        )

        self.api.reset_mock()
        self.api().search.return_value = self.tweets
        self.assertEqual(
            self.retriever.get(
                ("Twitter",),
                keyword="test",
                what=("image", "text"),
                when=(3, 4),
                where=(0, 1, 2, "km"),
                api=self.api
            ),
            {
                "type": "FeatureCollection",
                "features": twitter(
                    self.retriever.keychain["Twitter"],
                    keyword="test",
                    locale=(0, 1, 2, "km"),
                    period=(3, 4),
                    medium=("image", "text"),
                    api=self.api
                )
            }
        )
        self.api.reset_mock()


if __name__ == "__main__":
    unittest.main()
