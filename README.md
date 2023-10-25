# WordProcessor

An application that helps to analyze word frequency in the given list of urls.

## Problem Statement

Given the list of urls, the application should count the top 10 words from all of them
combined.

A valid word will:

1. Contain at least 3 characters.
2. Contain only alphabetic characters.
3. Be part of our bank of words (not all the words in the bank are valid according to the
   previous rules)
   The output should be pretty json printed to the stdout

## Documentation

### scripts/download_data.py

This is the script that downloads HTML page source for a given set of urls.

```console
(env) isshwarya@Isshwaryas-MBP WordProcessor % python scripts/download_data.py --help
usage: download_data.py [-h] [-o SAVE_DIR] [-f URL_LIST_FILE] [-r MAX_RETRIES] [-n NUM_THREADS] [-d]

A script to download HTML source for URLs

optional arguments:
  -h, --help            show this help message and exit
  -o SAVE_DIR, --save_dir SAVE_DIR
                        relative (to the cwd) directory path that should store HTML source files of the urls. Default: data/downloaded_files
  -f URL_LIST_FILE, --url_list_file URL_LIST_FILE
                        relative (to the cwd) file path for url list. Default: data/endg-urls
  -r MAX_RETRIES, --max_retries MAX_RETRIES
                        Max no.of retries on failures to get a response from the server to fetch URL source content. Default: 5
  -n NUM_THREADS, --num_threads NUM_THREADS
                        No.of worker threads to use. Default: 30
  -d, --debug           Enable debug messages
(env) isshwarya@Isshwaryas-MBP WordProcessor %

```

### scripts/word_analyzer.py

This is the script that analyzes word frequency from the given set of HTML files.

```console
(env) isshwarya@Isshwaryas-MBP WordProcessor % python scripts/word_analyzer.py --help
usage: word_analyzer.py [-h] [-p RELATIVE_DIR_PATH] [-w WORD_BANK_FILE_PATH] [-c COUNT] [-n NUM_THREADS] [-d]

Word frequency processor

optional arguments:
  -h, --help            show this help message and exit
  -p RELATIVE_DIR_PATH, --relative_dir_path RELATIVE_DIR_PATH
                        relative (to the cwd) directory path that contains html files. Default: data/downloaded_files
  -w WORD_BANK_FILE_PATH, --word_bank_file_path WORD_BANK_FILE_PATH
                        relative (to the cwd) file path for word bank. Default: data/word_bank.txt
  -c COUNT, --count COUNT
                        Count of top words needed. If not specified in the command line, checks for TOP_WORD_COUNT ENV variable. Default: 10
  -n NUM_THREADS, --num_threads NUM_THREADS
                        No.of worker threads to use. Default: 30
  -d, --debug           Enable debug messages
(env) isshwarya@Isshwaryas-MBP WordProcessor %

```

Logs for each execution can be found under

```console
<workspace>/logs/<timestamp_dir>/run.log
```

## Solution details

There are three possible ways to use the application.

### 1. Use the docker image with default url list file

To try out the application, it comes preloaded with the default url
list file (data/endg-urls) that lists 40000 urls. The image also contains a zip
file (data/downloaded_files.zip) that contains HTML page source for all these urls.

The below command starts the container in interactive mode

```console
>>> docker run -it isshwarya/word_processor:latest
```

To start in detached mode and view logs later

```console
>>> docker run -d isshwarya/word_processor:latest
320c85df517d2247dcd8a9b549ea67392fbe92aae213552e42e1c72f4ad66d42
>>>
>>> docker logs -f 320c85df517d2247dcd8a9b549ea67392fbe92aae213552e42e1c72f4ad66d42
<view console logs>
```

### 2. Use the docker image with custom url list file

To try with some other url list, you first need to download the page source
for those. You need Python3.8, pip and virtualenv to be already installed in your
system. Then follow the below steps.

1. First create virtual environment to run the application

```console
>>> mkdir ./env
>>> virtualenv ./env
>>> source ./env/bin/activate
```

2. Download or make the url list file available at \<workspace\>/data/endg-urls

3. Then run the script that downloads HTML page source for all those urls.

```console
>>> cd <workspace> && export PYTHONPATH=. && python scripts/download_data.py
```

    Note: Depending on the no.of urls to be fetched and the request limit
    imposed by the web server of the urls, the script might not be able
    to fetch data for all the URLs at one go.

    In that case, you can cron to run this script periodically - say, every
    20 min. runner.sh combines all the relevant commands together and you
    can simply make the cron to execute runner.sh

4. Mount the downloaded files to docker container and make it analyze the
   word frequency for your files.

```console
>>> docker run -it -v <workspace>/data/downloaded_files:/WordProcessor/data/downloaded_files isshwarya/word_processor:latest
```

Now the application will use the files from mounted directory instead of using
the preloaded source files.

### 3. Run locally without docker

This executes the application on your local machine directly.

1. First create virtual environment to run the application

```console
>>> mkdir ./env
>>> virtualenv ./env
>>> source ./env/bin/activate
```

2. Then run the application

```console
>>> cd <workspace>
>>> export PYTHONPATH=. && python scripts/download_data.py
```

## Sample output

```console
[
 [
    "the",
    853917
  ],
  [
    "and",
    390815
  ],
  [
    "that",
    222437
  ],
  [
    "for",
    183040
  ],
  [
    "you",
    162289
  ],
  [
    "with",
    133464
  ],
  [
    "its",
    84160
  ],
  [
    "but",
    83756
  ],
  [
    "will",
    81372
  ],
  [
    "can",
    73476
  ]
]
```

## Assumptions and TODOs

1. Fake user agent support can be added to handle the websites that applies request limits based on different useragents.

2. Only displayable content of the urls is considered for word frequency processing. Suggestions by the web page for further reads or user reviews posted on that page are not considered.
