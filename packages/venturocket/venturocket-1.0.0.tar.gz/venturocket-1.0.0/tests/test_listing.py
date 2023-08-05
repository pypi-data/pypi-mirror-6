from time import sleep
from venturocket.listing import ListingClient, Listing

__author__ = 'Joe Linn'

import unittest
from tests.basetest import BaseTest


class ListingClientTest(BaseTest):
    def setUp(self):
        super(ListingClientTest, self).setUp()
        self._client = ListingClient(self._key, self._secret)

    def test_storage(self):
        headline = "testing the python api client"
        listing = Listing("python_test_user", "provider", headline)
        listing.add_keyword("php", 400, 102)
        listing.add_location("94105")
        listing.add_listing_type("full-time")

        # create the listing
        listing_id = self._client.create_listing(listing)

        sleep(1)    # wait for VR to store the listing

        # retrieve the listing
        retrieved_listing = self._client.get_listing(listing_id)

        # ensure that the listing was stored properly
        self.assertEqual(headline, retrieved_listing['headline'])
        self.assertEqual(listing_id, retrieved_listing['listingId'])

        # modify the listing
        retrieved_listing['userType'] = "seeker"

        # store the modifications
        self._client.update_listing(listing_id, retrieved_listing)

        sleep(1)    # wait for VR to store the modifications

        # ensure that the modifications were stored
        self.assertEqual(retrieved_listing['userType'], self._client.get_listing(listing_id)['userType'])

        # disable the listing
        self._client.disable_listing(listing_id)

        sleep(1)    # wait for VR to disable the listing

        # ensure that the listing was disabled
        self.assertFalse(self._client.get_listing(listing_id)['enabled'])

    def test_matching(self):
        # create and store two listings which should match each other
        listing1 = Listing("test_match_1", "provider", "testing matching in python -- provider")
        listing1.add_keyword("python", 400, 500)
        listing1.add_listing_type("full-time")
        listing1.add_location("92109")

        listing2 = Listing("test_match_2", "seeker", "testing matching in python -- seeker")
        listing2.add_keyword("python", 500)
        listing2.add_listing_type("full-time")
        listing2.add_location("92109", 5, False)

        listing1_id = self._client.create_listing(listing1)
        listing2_id = self._client.create_listing(listing2)

        sleep(1)    # wait for storage

        # ensure that the two listings are matched
        listing1_matches = self._client.get_matches(listing1_id)
        listing2_matches = self._client.get_matches(listing2_id)

        match_found = False
        score = 0
        for match in listing1_matches:
            if match['listing']['listingId'] == listing2_id:
                match_found = True
                score = match['score']

        self.assertTrue(match_found)
        self.assertEqual(1.0, score)

        match_found = False
        for match in listing2_matches:
            if match['listing']['listingId'] == listing1_id:
                match_found = True
                self.assertEqual(score, match['score'])

        self.assertTrue(match_found)

        # disable both test listings
        self._client.disable_listing(listing1_id)
        self._client.disable_listing(listing2_id)

        sleep(1)    # wait for disabling

        # ensure that the disabled test listing is no longer among the match results
        listing1_matches = self._client.get_matches(listing1_id)
        match_found = False
        for match in listing1_matches:
            if match['listing']['listingId'] == listing2_id:
                match_found = True

        self.assertFalse(match_found)

if __name__ == '__main__':
    unittest.main()
