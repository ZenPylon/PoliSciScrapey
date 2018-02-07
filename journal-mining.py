import os
import time

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import scholar

# Use a service account
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'scrapeymcscrapescrape',
})

db = firestore.client()

# Rate limit parameter.
search_wait_time = 4
results_per_page = 10
start_index = 0
search_offset = 0
max_start = 50
querier = scholar.ScholarQuerier()
query = scholar.SearchScholarQuery()

# Configure the query parameters.
pub_year = '2013'
pub_name = u'"Journal Of Politics"'

queries = db.collection('queries')

# Set before = after to only get results from one year.
query.set_timeframe(pub_year, pub_year)  
query.set_pub(pub_name)
query.set_include_citations(False)
query.set_include_patents(False)


existing_query = queries \
        .where(u'publication_title', u'==', pub_name) \
        .where(u'publication_year', u'==', int(pub_year)) \
        .get()

# If this query hasn't been run yet
if sum(1 for x in existing_query ) != 0:
    print(f'query for {pub_name} in {pub_year} already run (or in progress).  Skipping...')
else:
    print('marking query as started in firestore')
    # Create a document to mark this query
    query_doc_ref = queries.add({
        'completed': False,
        'created_at': int(time.time()),
        'publication_title': pub_name,
        'publication_year': int(pub_year),
        'start_index': int(start_index)
    })

    total_matches = 0
    matches_with_pdf = 0
    while search_offset < max_start:
        query.set_start(search_offset)
        querier.send_query(query)
        articles = querier.articles

        # If we reach the end of the results page    
        if len(articles) == 0:
            break
    
        # Fitler articles to include only those with pdf links and exact
        # publication matches
        articles = list(filter(lambda x: x['title'] == pub_name, articles))
        pdfs = list(filter(lambda x: x['url_pdf'] is not None, articles))
        total_matches += len(articles)
        matches_with_pdf += len(pdfs)

        print(f'Printing results from {search_offset} to {search_offset + results_per_page}')
        
        for pdf in pdfs:
            pdf['url_pdf']

        time.sleep(search_wait_time)
        search_offset += results_per_page
    
    # Mark our query as complete, and note the number of matches / pdfs
    query_doc_ref.update({
        'completed': True,
        'total_matches': total_matches,
        'matches_with_pdf': matches_with_pdf
    })

   
    

