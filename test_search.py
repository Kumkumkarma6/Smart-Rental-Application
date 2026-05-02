import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SearchingYourHome.settings')
django.setup()

from Room.ml import parse_search_text

test_queries = ['Pune 5000-10000', 'Mumbai', 'Delhi 3k-5k', 'Bangalore', 'Chennai 2000-4000', 'Hyderabad']
for query in test_queries:
    result = parse_search_text(query)
    print(f'Query: {query} -> State: {result["state"]}, Dist: {result["dist"]}, Rent: {result["min_rent"]}-{result["max_rent"]}')