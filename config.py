from user_config import GEOAPIFYKEY, DB_USER, DB_PWD
VALID_MATCH_TYPES = ['full_match', 'inner_part', 'match_by_street', 'match_by_city_or_disrict', 'match_by_postcode']
DB_SERVER = "localhost"  # TODO: when using docker change this
DB_PORT = "5432"
DB_NAME = "ske"
HQ_ADDRESS_TXT = '../data/headquarter.txt'
N_ENTRIES = 20 # Limit the number of rows to check, for quicker processing times.
