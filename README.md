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

### Performance
After looking at the SEC data, it seems apparent that most users only make a single request, so that the number of
active sessions is never very high - assuming new sessions are started at the rate inactive ones end, there are typically
only tens of active sessions at once, meaning searching through a data structure is not so performance-critical.
I considered using a min heap as a priority queue at first so that finding inactive sessions would be O(1) time, but
then adding/updating sessions to the heap would be O(log k) (where k is the number of active sessions).
Using a dictionary instead has O(1) add/update complexity, but O(k) to find inactive sessions.
Since we only look for inactive sessions once per second, but add/update sessions for every data entry (roughly k times
per second), the heap has total time complexity of O(k*log k), whereas the dictionary method has O(k), so it scales
a bit better (though for only 10-20 requests per second the speedup is likely negligible).

The speed of the script is pretty quick; this can get through roughly one hour's worth of logs (from the SEC) in
a couple seconds, so it should have no trouble streaming data in real-time.

### Downloading/running the program
Clone the repository with `git clone https://github.com/ecotner/edgar-analytics`, `cd` into the directory, then run 
the script with `./run.sh` or `python3.6 ./src/sessionization.py` with the optional `-v` flag to turn on printing of
progress updates.
If you want to use your own log file, just replace the one at `input/log.csv`, and you can update the value in
`inactivity_period.txt` to change the number of seconds elapsed before considering a session inactive.
Make sure you have Python 3.6 installed; all modules used should be in the standard library.

To run the program on some real SEC data, download and extract some of the data from the SEC website, from the root
of the repository run:
```bash
cd input
wget http://www.sec.gov/dera/data/Public-EDGAR-log-file-data/2017/Qtr2/log20170630.zip
unzip log20170630.zip
mv log20170630.csv log.csv
```
Then execute the `run.sh` script. **Be warned, the files from the SEC are typically multiple GB.**