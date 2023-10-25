"""
A script to download source HTML for the list of urls listed in a text file.
"""
import argparse
import concurrent.futures
import requests
import random
import os
import re
import threading
import time
from urllib.parse import urlparse

import lib.logger as logger
import lib.constants as constants


class PageSourceDownloader(object):
    def __init__(self, save_dir, url_list_file,
                 max_retries=constants.MAX_RETRIES_TO_GET_URL_CONTENT,
                 num_threads=constants.MAX_THREADS):
        """
        Constructor

        Args:
            save_dir(str): Directory where the source HTML for the files to be
                           stored
            url_list_file(str): Relative file path that contains list of urls to
                                be fetched
            max_retries(int): Max no.of retries to be done if HTTP GET for any
                              url fails without a response. Default: 5
            num_threads(int): No.of simultaneous worker threads to be used to
                              download all files. Default: 30
        """

        self.save_dir = save_dir
        self.url_list_file = url_list_file
        self.max_retries = max_retries
        # Number of concurrent threads to use
        self.num_threads = num_threads
        self.unexpected_status_code = False
        # Create the directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        self.duplicates = {}

    def download_url_and_save(self, url, index):
        """
        Given the url, downloads the page source and saves it to a file under
        output directory (specified to save_dir option during object creation).

        Args:
            url(str): URL
            index(int): identifier for logging purpose

        """

        if self.unexpected_status_code:
            # If any one thread has got an unexpected status code, the other
            # threads should not pick up any more new work.
            return
        failed = False
        ex = None
        name = threading.current_thread().name
        url = url.strip("/")
        file_name = f"{url.split('/')[-1]}.html"

        # check if its duplicate case
        # Eg:
        #  "https://www.engadget.com/2019/08/24/the-morning-after",
        #  "https://www.engadget.com/2019/08/23/the-morning-after",
        if file_name in self.duplicates:
            self.duplicates[file_name].append(url)
            rel_url_path = urlparse(url).path
            file_name = re.sub(r'\/', '-', rel_url_path)
        else:
            self.duplicates[file_name] = [url]

        output_file_path = os.path.join(
            self.save_dir, file_name)
        not_found_file_path = os.path.join(
            self.save_dir, f"NOT_FOUND_{file_name}")
        logger.DEBUG(f"checking if file {output_file_path} exists")
        if os.path.exists(output_file_path) or os.path.exists(not_found_file_path):
            # Already downloaded
            logger.DEBUG(f"{name} - Exists {index}. {url}")
            return
        for attempt in range(1, self.max_retries + 1):

            if failed:
                # need this condition to avoid sleep for the first attempt
                time.sleep(random.randint(0, 5))
            try:
                # Using fake user agents also didn't help to overcome
                # request limits.
                response = requests.get(url)

                if response.status_code == 200:
                    with open(output_file_path, 'w', encoding='utf-8') as file:
                        file.write(response.text)
                    logger.INFO(f"{name} - Downloaded {index}. {url}")
                elif response.status_code == 404:
                    with open(not_found_file_path, 'w', encoding='utf-8') as file:
                        file.write("")
                    logger.INFO(f"{name} - NOT FOUND {index}. {url}")
                else:
                    self.unexpected_status_code = True
                    logger.INFO(f"{name} - FAILED STATUS CODE "
                                f"{index}. {url} - {response.status_code}")

                failed = False
            except Exception as e:
                logger.DEBUG(
                    f"{name} - Error downloading {url}: {ex} - attempt {attempt}")
                failed = True
                ex = e

            if not failed:
                return
        # If it has reached here, then retries had been exhausted, but the action
        # was not completed
        logger.INFO(f"{name} - Error downloading {url}: {ex}")

    def begin_execution(self):
        """
        Method that starts execution by reading the urls file and then begins
        to download the source HTML for those
        """
        urls = []
        with open(self.url_list_file, "r") as file:
            data = file.read()
            urls = data.splitlines()

        logger.DEBUG("Total urls: %s" % len(urls))

        # Create a ThreadPoolExecutor with the specified number of threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Download all URLs concurrently and save to files
            executor.map(self.download_url_and_save,
                         urls, range(1, (len(urls)+1)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script to download HTML source for URLs")
    parser.add_argument("-o", "--save_dir",
                        help='relative (to the cwd) directory path that '
                             'should store HTML source files of the urls. '
                             f"Default: {constants.RELATIVE_HTML_DIR_PATH}",
                        type=str, default=constants.RELATIVE_HTML_DIR_PATH)
    parser.add_argument("-f", "--url_list_file",
                        help='relative (to the cwd) file path for url list. '
                             f'Default: {constants.RELATIVE_URL_LIST_FILE_PATH}',
                        type=str, default=constants.RELATIVE_URL_LIST_FILE_PATH)
    parser.add_argument("-r", "--max_retries",
                        help=f"Max no.of retries on failures to get a response "
                        "from the server to fetch URL source content. "
                             f"Default: {constants.MAX_RETRIES_TO_GET_URL_CONTENT}",
                             type=int, default=constants.MAX_RETRIES_TO_GET_URL_CONTENT)
    parser.add_argument("-n", "--num_threads",
                        help=f"No.of worker threads to use. "
                             f"Default: {constants.MAX_THREADS}",
                             type=int, default=constants.MAX_THREADS)
    parser.add_argument("-d", "--debug", help="Enable debug messages",
                        required=False, action='store_true')

    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logger.setup_logging(log_level="DEBUG")
    downloader = PageSourceDownloader(
        url_list_file=parsed_args.url_list_file,
        save_dir=parsed_args.save_dir,
        max_retries=parsed_args.max_retries,
        num_threads=parsed_args.num_threads
    )
    downloader.begin_execution()
