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

# Module imports
import csv
import time
from pathlib import Path
import argparse
import os

# Get terminal arguments (only to turn on printed progress updates)
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Turns on verbose output", action="store_true")
parser.add_argument("input", help="Name of the input file", default="log.csv")
parser.add_argument("output", help="Name of the output file", default="sessionization.txt")
args = parser.parse_args()

# Set working directory to this file's directory
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Define input CSV and inactivity_period paths
INPUT_PATH = Path("../input/") / args.input
OUTPUT_PATH = Path("../output/") / args.output
INACTIVITY_PATH = Path("../input/inactivity_period.txt")

# Define Session class
class Session(object):
    """
    Session object for maintaining information about individual sessions. Has methods for creating and updating each
    session.
    """
    def __init__(self, ip_address, start_time, doc_count):
        self.ip_address = ip_address
        self.start_time = start_time
        self.most_recent_time = start_time
        self.doc_count = doc_count

    def increment_doc_count(self, n=1):
        self.doc_count += n

    def update_time(self, t):
        self.most_recent_time = t

    def summary_str(self):
        out_str = ",".join([sess.ip_address, # IP address
                            int_to_time(sess.start_time), # Date/time of first request
                            int_to_time(sess.most_recent_time), # Date/time of last request
                            str(int(sess.most_recent_time - sess.start_time + 1)), # Duration in sec
                            str(sess.doc_count)]) # Document count
        return out_str + "\n"

# Define utility functions
def time_to_int(date, time_):
    """ Converts the date and time from the the log file into an easy-to-handle integer. """
    date = [int(e) for e in date.split("-")] # Elements of this list are year, month, day
    time_ = [int(e) for e in time_.split(":")] # Elements of this list are hour, minute, second
    t = (date[0], date[1], date[2], time_[0], time_[1], time_[2], 0, 0, -1)
    return time.mktime(t)

def int_to_time(t):
    """ Converts an integer representing the time since epoch to the format yyyy-mm-dd hh:mm:ss """
    t_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    return t_str


session_dict = {} # Dictionary of Session objects, indexed by IP address

# Open inactivity_period.txt and extract the inactivity period
with open(INACTIVITY_PATH, "r") as fo:
    inactivity_period = float(fo.read())
# Clear the output file
with open(OUTPUT_PATH, "w+") as fo:
    fo.write("")

# Open input file, initialize CSV reader
with open(INPUT_PATH, "r") as fo:
    reader = csv.DictReader(fo)
    # Start scanning through each line in the CSV
    i = 1
    previous_time = 0
    for row in reader:
        if args.verbose:
            print("Row {}".format(i))
            i += 1
        # The entries of each row are: ip, date, time, zone, cik, accession, extention, code, size, idx, norefer,
        # noagent, find, crawler, and browser
        # Read the line, extract the IP address and current time
        ip = row['ip']
        current_time = time_to_int(row['date'], row['time'])
        # If the IP matches one in the session dictionary, update the Session
        if ip in session_dict:
            session_dict[ip].increment_doc_count()
            session_dict[ip].update_time(current_time)
        # Otherwise create a new Session and add it to the dictionary
        else:
            session_dict[ip] = Session(ip, current_time, 1)

        # Iterate through all Sessions in session_dict to check for lapsed sessions
        if (current_time != previous_time):
            previous_time = current_time
            output_list = []
            for key in list(session_dict.keys()):
                sess = session_dict[key]
                # If Session has exceeded the inactivity_period
                if current_time - sess.most_recent_time > inactivity_period:
                    # Append entry to output list
                    output_list.append((sess.start_time, sess.summary_str()))
                    # Delete Session from session_dict
                    del session_dict[key]
            # Sort output list by start time, then write to file
            for _, e in sorted(output_list, key=lambda x: x[0]):
                with open(OUTPUT_PATH, "a+") as fo_out:
                    fo_out.write(e)
    # At end of input file, pretend all sessions have terminated
    output_list = []
    for key in session_dict:
        sess = session_dict[key]
        output_list.append((sess.start_time, sess.summary_str()))
    for _, e in sorted(output_list, key=lambda x: x[0]):
        with open(OUTPUT_PATH, "a+") as fo_out:
            fo_out.write(e)
