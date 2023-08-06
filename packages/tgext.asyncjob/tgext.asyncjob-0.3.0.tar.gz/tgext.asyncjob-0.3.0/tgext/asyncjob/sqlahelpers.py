import time

def asyncjob_timed_query(query, retries=10, interval=6):
        counter = retries

        #this is just to wait a bit to give time to the database
        #to commit things. As it is an async job we don't really
        #need it to be fast, but waiting a bit might raise possibilities
        #to fetch data at first try.
        time.sleep(1)

        found = query.first()
        while not found and counter:
            time.sleep(interval)
            counter -= 1
            found = query.first()

        return query
