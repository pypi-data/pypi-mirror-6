__author__ = 'Joe Linn'

from venturocket.abstractclient import AbstractClient


class ListingClient(AbstractClient):
    def create_listing(self, listing):
        """
        Create a new listing
        :param listing: a dictionary or listing object
        :type listing: Listing or dict
        :return: the id of the newly created listing
        :rtype: str
        """
        if isinstance(listing, Listing):
            listing = listing.to_dict()
        return self._post("listing", data=listing)['listingId']

    def get_listing(self, listing_id):
        """
        Retrieve a listing by id
        :param listing_id: the id of the desired listing
        :type listing_id: str
        :return: a listing
        :rtype: dict
        """
        return self._get("listing/%s" % listing_id)

    def update_listing(self, listing_id, listing):
        """
        Update an existing listing
        :param listing_id: the id of the listing to be updated
        :type listing_id: str
        :param listing: either a dictionary or a Listing object
        :type listing: dict or Listing
        :return: the listing id of the updated listing
        :rtype: str
        """
        if isinstance(listing, Listing):
            listing = listing.to_dict()
        return self._put("listing/%s" % listing_id, data=listing)['listingId']

    def disable_listing(self, listing_id):
        """
        Disable a listing
        :param listing_id: the id of the listing to be disabled
        :type listing_id: str
        :return: the id of the disabled listing
        :rtype: str
        """
        return self._put("listing/%s/disable" % listing_id)["listingId"]

    def enable_listing(self, listing_id):
        """
        Enable a listing
        :param listing_id: the id of the listing to be enabled
        :type listing_id: str
        :return: the id of the enabled listing
        :rtype: str
        """
        return self._put("listing/%s/enable" % listing_id)["listingId"]

    def get_matches(self, listing_id):
        """
        Retrieve matches for a specific listing
        :param listing_id: the id of the listing for which to retrieve matches
        :type listing_id: str
        :return: a list of match objects. If no matches were found, the list will be empty.
        :rtype: list of dict
        """
        return self._get("listing/%s/matches" % listing_id)["matches"]


class Listing(object):
    def __init__(self, user_id, user_type, headline):
        super(Listing, self).__init__()
        self._params = {}
        self._locations = []
        self._keywords = []
        self._listing_types = []
        self.set_user_id(user_id).set_user_type(user_type).set_headline(headline)

    def set_user_id(self, user_id):
        """
        Set the user id for this listing
        :param user_id: arbitrary user id
        :type user_id: str
        :return:
        :rtype: self
        """
        return self._set_param('userId', user_id)

    def set_user_type(self, user_type):
        """
        Set the user type for this listing
        :param user_type:  must be either "provider" or "seeker"
        :type user_type: str
        :return:
        :rtype: self
        """
        if user_type != "provider" and user_type != "seeker":
            raise ValueError("user_type must be either 'provider' or 'seeker'. '%s' given." % user_type)
        return self._set_param("userType", user_type)

    def set_headline(self, headline):
        """
        Set the headline for this listing
        :param headline: 140 characters max
        :type headline: str
        :return:
        :rtype: self
        """
        return self._set_param("headline", headline)

    def set_telecommute(self, telecommute):
        """
        Set telecommuting options for this listing
        :param telecommute: "yes", "no", or "only". Defaults to "no" if omitted.
        :type telecommute: str
        :return:
        :rtype: self
        """
        valid_telecommute = [
            "yes",
            "no",
            "only"
        ]
        if telecommute not in valid_telecommute:
            raise ValueError("telecommute must be 'yes', 'no', or 'only'. %s given." % telecommute)
        return self._set_param("telecommute", telecommute)

    def add_location(self, zip_code, commute=0, relocate=False):
        """
        Add a location to this listing
        :param zip_code: a zip code
        :type zip_code: str
        :param commute: maximum commute radius in miles. Not used if user_type is "provider"
        :type commute: int
        :param relocate: true if willing to relocate to this location. Not used if user_type is "provider"
        :type relocate: bool
        :return:
        :rtype: self
        """
        self._locations.append({
            "zip": zip_code,
            "commute": commute,
            "relocate": relocate
        })
        return self

    def add_keyword(self, word, experience, range=0):
        """
        Add a keyword to this listing
        :param word: a valid keyword
        :type word: str
        :param experience: an integer value between 100 and 1000
        :type experience: int
        :param range: only used if user_type is "provider". experience + range cannot exceed 1000.
        :type range: int
        :return:
        :rtype: self
        """
        if experience < 100 or experience > 1000:
            raise ValueError("experience must be between 100 and 1000. %s given." % experience)
        if range < 0:
            raise ValueError("range cannot be negative. %s given." % range)
        if range + experience > 1000:
            raise ValueError("range + experience cannot exceed 1000. range: %s, experience: %s" % (range, experience))
        self._keywords.append({
            "word": word,
            "experience": experience,
            "range": range
        })
        return self

    def add_listing_type(self, listing_type):
        """
        Add a listing type to this listing
        :param listing_type: one of "contract", "full-time", "part-time", "contract-to-hire", or "internship"
        :type listing_type: str
        :return:
        :rtype: self
        """
        valid_types = [
            "contract",
            "full-time",
            "part-time",
            "contract-to-hire",
            "internship"
        ]
        if listing_type not in valid_types:
            raise ValueError("invalid listing_type given: %s" % listing_type)
        self._listing_types.append({
            "type": listing_type
        })
        return self

    def to_dict(self):
        """
        convert this listing object into a dict which can then be sent to the API
        :return:
        :rtype: dict
        """
        data = self._params
        data["locations"] = self._locations
        data["keywords"] = self._keywords
        data["listingTypes"] = self._listing_types
        return data

    def _set_param(self, key, value):
        """

        :param key:
        :type key: str
        :param value:
        :type value: str or list
        :return:
        :rtype: self
        """
        self._params[key] = value
        return self