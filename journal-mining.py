import os
import scholar

querier = scholar.ScholarQuerier()
query = scholar.SearchScholarQuery()

# Set before = after to only get results from one year
pub_year = '2013'
query.set_timeframe(pub_year, pub_year)
querier.send_query(query)

articles = querier.articles
for art in articles:
    print(str(art.as_txt()) + '\n')