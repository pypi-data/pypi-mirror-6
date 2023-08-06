import logging
import sys

logging.basicConfig()
logger = logging.getLogger(__name__)

try:
    from suds.client import Client
except ImportError:
    logger.error('Error importing suds client. Please download it from (https://fedorahosted.org/suds/).')


class SermonAudioAPI(object):
    #URL for the sermon audio wsdl
    api_wsdl_url = 'http://web4.sa-media.com/SASoapAPI/service.asmx?WSDL'

    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password

        self.client = self._get_client()

    @classmethod
    def _get_client(self):
        """Create the SUDS Client

           Looks at self.api_wsdl_url
        """
        return Client(self.api_wsdl_url)

    @classmethod
    def _get_sermons(self, result):
        """Returns a list of sermons

           Makes sure that the result is in the expected format.
        """
        if str(result.__class__) == 'suds.sudsobject.ArrayOfSermon':
            return result[0]
        else:
            return []

    @classmethod
    def _get_speakers(self, result):
        """Returns a list of speakers from a result

           Makes sure that the result is in the expected format.
        """
        if str(result.__class__) == 'suds.sudsobject.ArrayOfString':
            return result[0]
        else:
            return []

    @classmethod
    def _get_string_array_items(self, result):
        if str(result.__class__) == 'suds.sudsobject.ArrayOfString':
            return result[0]
        else:
            return []

    def get_sermon_list(self, category, search_term):
        """ Returns a list of sermons base on search criteria.

            Keyword Arguments:
            Valid search categories are:
            cagetory -- Must be one of the following
                1. speaker
                2. eventtype
                3. series
                4. year
            search_term -- Your search term
        """
        search_categories = ['speaker', 'eventtype', 'series', 'year']

        if category not in search_categories:
            logging.debug('Invalid category specified (%s)' % (category))
            return []

        try:
            result = self.client.service.SermonList(self.username, self.password, category, search_term)

            return self._get_sermons(result)
        except:
            logging.error('Get sermon list exception for category (%s) and item (%s)' % (category, item))
            return []

        return result

    def get_sermon_info(self, sermon_id):
        """ Returns the information for a single sermon

            Keyword Arguments
            sermon_id -- The id of the sermon you want
        """
        if not sermon_id:
            logging.debug('Could not get sermon info because no sermon id was specified.')
            return []

        try:
            result = self.client.service.GetSermonInfo(self.username, self.password, sermon_id)

            if str(result.__class__) == 'suds.sudsobject.SermonSingle':
                return result
            else:
                logging.debug('Get sermon info did not return proper result')
                return []
        except:
            logging.error('Get sermon info exception for sermon id (%s)' % (sermon_id))
            return []

    @classmethod
    def newest_sermons_by_speaker(self, speaker):
        """Returns a list of sermons

           Keyword arguments:
           speaker -- a name of a preacher
        """
        if not speaker:
            logging.debug('Could not get sermons by speaker because no speaker was specified.')
            return []

        try:
            result = self._get_client().service.NewestSermonsBySpeaker(speaker)

            sermons = self._get_sermons(result)

            return sermons
        except:
            logging.error('Call newest_sermons_by_speaker exception for speaker (%s)' % (speaker))
            return []

    @classmethod
    def newest_sermons_by_member_id(self, member_id):
        """Returns a list of sermons

           Keyword arguments:

           member_id -- the name of a member
        """

        if not member_id:
            logging.debug('Call newest_sermons_by_member_id did not have a member_id specified')
            return []

        try:
            result = self._get_client().service.NewestSermonsByMemberID(member_id)

            sermons = self._get_sermons(result)

            return sermons
        except:
            logging.error(
                'Call newest_sermons_by_member_id exception for member id (%s) (%s)' % (member_id, sys.exc_info()[0]))
            return []

    @classmethod
    def get_event_types(self):

        try:
            result = self._get_client().service.GetEventTypes()

            events = self._get_string_array_items(result)

            return events
        except:
            logging.error('Call get_event_types exception')
            return []

    @classmethod
    def get_languages(self):

        try:
            result = self._get_client().service.GetLanguages()

            languages = self._get_string_array_items(result)

            return languages
        except:
            logging.error('Call get_languages exception')
            return []

    @classmethod
    def get_newest_series_by_member_id(self, member_id):
        """ Returns a list of series

            Keyword arguments:

            member_id -- the name of a member
        """
        if not member_id:
            logging.debug('Call get_newest_series_by_member_id did not have member id specified')
            return []

        try:
            result = self._get_client().service.GetNewestSeriesByMemberID(member_id)

            if str(result.__class__) == 'suds.sudsobject.ArrayOfString':
                return result[0]
            else:
                return []
        except:
            logging.error('Call get_newest_series_by_member_id exception for member id (%s)' % (member_id))
            return []

    @classmethod
    def get_series_by_member_id(self, member_id):
        """ Returns a list of the series for the specified member

            Keyword arguments:

            member_id -- the name of a member
        """

        if not member_id:
            logging.debug('Call get_series_by_member_id did not have a member id specified')
            return []

        try:
            result = self._get_client().service.GetNewestSeriesByMemberID(member_id)

            if str(result.__class__) == 'suds.sudsobject.ArrayOfString':
                return result[0]
            else:
                return []
        except:
            logging.error('Call get_series_by_member_id exception for member id (%s)' % (member_id))

    @classmethod
    def get_speakers_by_member_id(self, member_id):

        if not member_id:
            logging.debug('Call get_speakers_by_member_id did not have a member id specified')
            return []

        try:
            result = self._get_client().service.GetSpeakersByMemberID(member_id)

            speakers = self._get_speakers(result)

            return speakers
        except:
            logging.error('Call get_speakers_by_member_id exception for member id (%s)' % (member_id))
            return []

    @classmethod
    def get_speakers_by_keyword(self, keyword):
        """Returns a list of speakers for a given keyword

           Keyword Arguments:
           keyword -- A string search term ('love')
        """

        if not keyword:
            logging.debug('Call get_speakers_by_keyword did not have a keyword specified')
            return []

        try:
            result = self._get_client().service.GetSpeakersByKeyword(keyword)

            speakers = self._get_string_array_items(result)

            return speakers
        except:
            logging.error('Call get_speakers_by_keyword exception for keyword (%s)' % (keyword))
            return []

    def get_favorite_broadcasters(self):
        return Exception('Not Implemented Yet')

    def get_favorite_sermons(self):
        return Exception('Not Implemented Yet')

    def get_favorite_speakers(self):
        return Exception('Not Implemented Yet')

    def submit_sermon(self):
        return Exception('Not Implemented Yet')

    def update_sermon(self):
        return Exception('Not Implemented Yet')
