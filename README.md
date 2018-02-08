# Political Science Paper Scraping (PSPS)
(p.s. excuse the pun)

Starting this as a fork of [scholar.py](https://github.com/ckreibich/scholar.py), a python script that scrapes google scholar data.  The goal is to amass the abstracts of many articles in different political journals, for later use in all kinds of data analysis.  As a basic example, what are the most common topics, keywords, etc.

Something to be careful of upfront - "Journal of Politics" also matches "Journal of Politics, Economics and Management".  So some post-request confirmation will need to done if we want to ensure that everything is labeled under the correct journal.

Note that in order to use this, you'll need a service account key file referencing your firebase project.