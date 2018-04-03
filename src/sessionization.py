"""
21:31, 2 April, 2018
Author: Eric Cotner

Description:
EDGAR-analytics coding challenge for Insight Data Engineering program.

This script reads through the log.csv file line by line, and for each entry either creates or updates a Session class
based on the contents of that line. The Session class contains the ip address, start time of the session, and count of
webpages accessed during the session.
Since the ip address of each accessor is unique, this will be used as the key in a dictionary containing all the
currently active sessions.
***Or maybe I should use a min heap which is sorted according to how much time left until the end of the session?
If users frequently request documents multiple times, the dictionary approach is probably best. If they request
documents all at once, then the heap approach is likely best (the heap will have to be updated each time an individual
session is updated though, so this may complicate things).***

"""

class Session(object):
    def __init__(self, ip_address, start_time, doc_count):
        self.ip_address = ip_address
        self.start_time = start_time
        self.doc_count = doc_count

    def increment_doc_count(self, n=1):
        self.doc_count += n

    def session_len(self, current_time):
        dt = current_time - self.start_time
        return dt