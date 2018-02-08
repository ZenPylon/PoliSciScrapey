import os
import time
import wget

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import scholar

# Use a service account
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'projectId': 'scrapeymcscrapescrape',
    'storageBucket': 'scrapeymcscrapescrape.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

if not os.path.exists('./pdfs'):
    os.makedirs('./pdfs')
    
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
pub_name = u'"The Journal Of Politics"'

queries = db.collection('queries')
cluster_ids = db.collection('cluster_ids')

# Set before = after to only get results from one year.
query.set_timeframe(pub_year, pub_year)  
query.set_pub(pub_name)
query.set_include_citations(False)
query.set_include_patents(False)

existing_query = queries \
        .where(u'publication_name', u'==', pub_name) \
        .where(u'publication_year', u'==', int(pub_year)) \
        .get()

# If this query hasn't been run yet
if sum(1 for x in existing_query ) != 0:
    print(f'query for {pub_name} in {pub_year} already run (or in progress).  Skipping...')
else:
    print('marking query as started in firestore')

    # Create a document to mark this query
    query_doc_ref = queries.document()
    query_doc_ref.set({
        'completed': False,
        'created_at': int(time.time()),
        'end_index': int(max_start),
        'publication_name': pub_name,
        'publication_year': int(pub_year),
        'start_index': int(start_index)
    })

    total_matches = 0
    matches_with_pdf = 0
    total_errors = 0
    while search_offset < max_start:
        query.set_start(search_offset)
        querier.send_query(query)
        articles = querier.articles

        # If we reach the end of the results page    
        if len(articles) == 0:
            break

        # Fitler articles to include only those with pdf links and exact
        # publication matches
        
        # articles = list(filter(lambda x: x['title'] == pub_name, articles))
        pdf_articles = list(filter(lambda x: x['url_pdf'] is not None, articles))
        total_matches += len(articles)
        matches_with_pdf += len(pdf_articles)

        print(f'Printing results from {search_offset} to {search_offset + results_per_page}')

        for article in pdf_articles:
            cluster_id = str(article['cluster_id'])
            pdf_url = str(article["url_pdf"])
            local_path = f'pdfs/{cluster_id}.pdf'
            print(f'Downloading pdf from {pdf_url}')
            
            try:
                wget.download(pdf_url, local_path)

                print('\nSaving cluster id in firestore...')
                cluster_ids.document(cluster_id).set({
                    'created_at': int(time.time()),
                    'publication_name': pub_name,
                    'publication_year': int(pub_year),
                    'url': article['url_pdf']
                })
            
                print('Saving pdf file in Firebase Cloud Storage...')
                pdfblob = bucket.blob(f'pdf/{cluster_id}.pdf')
                pdfblob.upload_from_filename(local_path)

            except:
                print(f'error processing pdf:  {str(local_path)}')
                errors += 1

        time.sleep(search_wait_time)
        search_offset += results_per_page
        print('iteration complete, delaying before next iteration')
    
    # Mark our query as complete, and note the number of matches / pdfs
    query_doc_ref.update({
        'completed': True,
        'completed_at': int(time.time()),
        'total_errors': total_errors
        'total_matches': total_matches,
        'matches_with_pdf': matches_with_pdf
    })

   
    

