# edgar-analytics: Insight data engineering coding challenge

### Outline
This program is a solution to the Insight coding challenge found
[here](https://github.com/InsightDataScience/edgar-analytics/blob/master/README.md#output-file).
The main objective is to summarize access to financial documents from a number of different users.
The program consists of a single Python script (sessionization.py), an input CSV (log.csv) and text document
(inactivity_period.txt), and an output text document (sessionization.txt).
The Python script contains a Session class, which contains all relevant information about each session (IP address,
time of first access, last time of access, number of documents accessed), and some methods for operating on this
class, including time conversions (times are stored as seconds elapsed since the Unix epoch).
The script points to the log.csv file, and iterates through each line, which corresponds to a single document request.
The IP address of the user and the time of access is extracted, then the IP is checked against a dictionary to see
if there are any existing sessions that need updating.
If there is no existing entry in the dictionary, a new one is made.
The program then checks to see if any of the existing sessions in the dictionary has exceeded the inactivity period,
and if so, appends the session to a list (deleting it from the dictionary), which is then sorted by the time of the
first request.
It then iterates through the list, writing a summary of each session to file.
If the end of the file is reached and some sessions still have not terminated, the same sorting/writing procedure is
performed, just without the check for inactivity.
Since there are multiple document requests per second, and time is effectively quantized at one second intervals,
the program only checks for inactivity whenever the time changes, which speeds up execution by roughly a factor of the
frequency of document requests.

### Some observations:
After looking at some real-world data from the SEC's website, I've noticed a couple things:
* Most users request a small number of documents per session (mostly just a single document)
    * But there is a decent fraction of users who request many tens or hundreds of documents per session
* The rate of document requests is fairly high (between 10-20/sec)
* The active session time is positively correlated with number of documents requested

### Downloading/running the program
Clone the repository with `git clone https://github.com/ecotner/edgar-analytics`, then run the script with ...