
from portfolio.services.codeforces import fetch_codeforces_data
from pprint import pprint

data = fetch_codeforces_data()
pprint(data)
