import os
import scholar
import time

# Rate limit parameter.
search_wait_time = 4
results_per_page = 10
start_offset = 0
max_start = 10
querier = scholar.ScholarQuerier()
query = scholar.SearchScholarQuery()

# Configure the query parameters.
pub_year = '2013'
pub_name = '"Journal Of Politics"'

# Set before = after to only get results from one year.
query.set_timeframe(pub_year, pub_year)  
query.set_pub(pub_name)
query.set_include_citations(False)
query.set_include_patents(False)

while start_offset < max_start:
    query.set_start(start_offset)
    print(f'Printing results from {start_offset} to {start_offset + results_per_page}')
    querier.send_query(query)
    articles = querier.articles
    print(f'number of articles is {len(articles)}')
    pdfs = list(filter(lambda x: x['url_pdf'] is not None, articles))
    print(f'filtered length is {len(pdfs)}')

    for art in articles:
        print(str(art.as_txt()) + '\n')

    time.sleep(search_wait_time)
    start_offset += results_per_page


