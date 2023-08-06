"""OGRe Query Handler Tests

:class:`OGReConstructorTest` -- retriever constructor test template

:meth:`OGReConstructorTest.test___init__` -- retriever creation tests

:class:`OGReTest` -- query handler test template

:meth:`OGReTest.setUp` -- query handler test preparation

:meth:`OGReTest.test_fetch` -- query handler tests

"""

import json
import os
import unittest
from mock import MagicMock, call
from ogre import OGRe
from ogre.Twitter import twitter


class OGReConstructorTest (unittest.TestCase):

    """Create objects that test the OGRe constructor.

    A separate class is required here because the constructor is used in the
    setUp method of future TestCase classes.

    :meth:`test___init__` -- retriever creation and key-handling tests

    """

    def test___init__(self):

        """Test key handling during OGRe construction.

        These tests should ensure that only valid keys are accepted
        and that the keyring is properly created.

        """

        with self.assertRaises(AttributeError):
            OGRe(keys={0: None})
        with self.assertRaises(ValueError):
            OGRe(keys={"invalid": None})
        with self.assertRaises(AttributeError):
            OGRe(keys={"Twitter": None, 0: None})
        with self.assertRaises(ValueError):
            OGRe(keys={"Twitter": None, "invalid": None})

        retriever = OGRe(
            keys={
                "Twitter": {
                    "consumer_key": "key",
                    "access_token": "token",
                }
            }
        )

        self.assertEqual(
            retriever.keyring,
            {"twitter": "Twitter"}
        )
        self.assertEqual(
            retriever.keychain,
            {
                "Twitter": {
                    "consumer_key": "key",
                    "access_token": "token",
                }
            }
        )


class OGReTest (unittest.TestCase):

    """Create objects that test the OGRe module.

    :meth:`setUp` -- query handler test preparation (always runs first)

    :meth:`test_fetch` -- query handling and packaging tests

    """

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

    def test_fetch(self):

        """Test the main entry point to OGRe.

        These tests should ensure that the retrieved results are packaged
        in a GeoJSON FeatureCollection object properly.

        """

        with self.assertRaises(ValueError):
            self.retriever.get(("invalid",),)
        with self.assertRaises(ValueError):
            self.retriever.get(("Twitter", "invalid"),)

        self.assertEqual(
            self.retriever.fetch(sources=()),
            {
                "type": "FeatureCollection",
                "features": []
            }
        )
        self.assertEqual(
            self.retriever.fetch(media=()),
            {
                "type": "FeatureCollection",
                "features": []
            }
        )
        self.assertEqual(
            self.retriever.fetch(quantity=0),
            {
                "type": "FeatureCollection",
                "features": []
            }
        )

        self.api.reset_mock()
        self.api().search.return_value = self.tweets
        self.assertEqual(
            self.retriever.fetch(
                sources=("Twitter",),
                media=("image", "text"),
                keyword="test",
                quantity=2,
                location=(0, 1, 2, "km"),
                interval=(3, 4),
                api=self.api
            ),
            {
                "type": "FeatureCollection",
                "features": twitter(
                    keys=self.retriever.keychain[
                        self.retriever.keyring["twitter"]
                    ],
                    media=("image", "text"),
                    keyword="test",
                    quantity=2,
                    location=(0, 1, 2, "km"),
                    interval=(3, 4),
                    api=self.api
                )
            }
        )
        self.api.reset_mock()


if __name__ == "__main__":
    unittest.main()
