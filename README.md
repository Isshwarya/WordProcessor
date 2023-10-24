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
```

### 2. Use the docker image with default url list file

To try with some other url list, you first need to download the page source
for those. You need Python3.8, pip and virtualenv to be already installed in your
system. Then follow the below steps.

1. First create virtual environment to run the application

```console
>>> mkdir ./env
>>> virtualenv ./env
>>> source ./env/bin/activate
```

2. Download or make the url list file available at data/endg-urls

3. Then run the script that downloads HTML page source for all those urls.

```console
>>> export PYTHONPATH=. && python scripts/download_data.py
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
>>> docker run -it -v /Users/$USER/WordProcessor/data/downloaded_files:/WordProcessor/data/downloaded_files isshwarya/word_processor:latest
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

1. Fake user agent support can be added for thr websites that applies request limits based on useragents

2. Only displayable content of the urls is considered for word processing. Suggestions by the web page for further reads or user reviews posted on that page are not considered.
