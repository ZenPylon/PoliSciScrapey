import os
import scholar

querier = scholar.ScholarQuerier()
query = scholar.SearchScholarQuery()

# Configure the query parameters
pub_year = '2013'
pub_name = '"Journal Of Politics"'

# Set before = after to only get results from one year
query.set_timeframe(pub_year, pub_year)  
query.set_pub(pub_name)
query.set_include_citations(False)
query.set_include_patents(False)
query.set_start(20)

querier.send_query(query)

articles = querier.articles
for art in articles:
    print(str(art.as_txt()) + '\n')