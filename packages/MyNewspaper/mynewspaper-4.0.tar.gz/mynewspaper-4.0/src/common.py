import os
import os.path
import logging


########################################################################
##### Globals
BASEPATH = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# enums
TOTAL, UNREAD, STARRED, LATER, ARCHIVED, MAX_STATE = range(6)
FEED_ARCHIVE, FEED_ENABLED, FEED_DISABLED, FEED_BROKEN = range(4)
FEED_STATES = ['archive', 'enabled', 'disabled', 'broken']
SORT_NONE, SORT_DATENEW_FEED, SORT_DATEOLD_FEED, SORT_FEED_DATENEW, SORT_FEED_DATEOLD = range(5)

# web
TIMEOUT_WEB = 60
NUMTHREADS_UPDATE_FEEDS = 25
NUMTHREADS_FETCH_ICONS = 25

# ui
DEFAULT_FAVICON = '/images/default_favicon.ico'
ART_STATE_ICONS = ('st_delete.png', 'st_unread.png', 'st_starred.png', 'st_later.png', 'st_archived.png')

# log
LOG_FILE = 'data/mynewspaper.log'
LOG_LEVEL = logging.INFO # logging.DEBUG
log = logging.getLogger('MyNewspaper')


########################################################################

