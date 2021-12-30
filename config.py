from user_config import GEOAPIFYKEY, DB_USER, DB_PWD
import os
dirpath = os.path.dirname(os.path.realpath(__file__))
VALID_MATCH_TYPES = ['full_match', 'inner_part', 'match_by_street', 'match_by_city_or_disrict', 'match_by_postcode']
DB_SERVER = "db"  # TODO: when using docker change this
DB_PORT = "5432"
DB_NAME = "ske"
HQ_ADDRESS_TXT = os.path.join(dirpath, 'data/headquarter.txt')
N_ENTRIES = 100 # Limit the number of rows to check, for quicker processing times.
LOG_CONF = os.path.join(dirpath, 'logging.conf')
UPLOAD_FOLDER = os.path.join(dirpath, 'uploads/')
