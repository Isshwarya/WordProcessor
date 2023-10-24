"""
A script to analyze word frequency of displayable content in HTML files
"""
import argparse
import json
import re
import os
# lxml quirk to explicitly import subpackage
import lxml.html
from collections import Counter
from bs4 import BeautifulSoup

import lib.constants as constants
import lib.logger as logger


class WordFrequencyProcessor(object):

    def __init__(self, html_files_dir_path, word_bank_file_path=None):
        """Constructor"""

        self.counter = Counter()
        self.html_files_dir_path = html_files_dir_path
        self.word_bank = []
        if word_bank_file_path:
            word_bank_file_path = os.path.join(
                os.getcwd(), word_bank_file_path)
            with open(word_bank_file_path, "r", encoding="utf-8") as file:
                self.word_bank = file.read().splitlines()

    def tokenize_and_clean(self, text):
        """
        Method to tokenize and clean text into words. Valid words are:
        1. Word length should be minimum of 3 letters.
        2. Word can have only alphabetic characters.
        3. Word should be part of word bank.

        Args:
            text(str): Text to be tokenized into words

        Returns: List of words
        """

        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        if self.word_bank:
            words = list(filter(lambda word: word in self.word_bank, words))
        return words

    def retrieve_text(self, html_content):
        parsed_html = lxml.html.fromstring(html_content)

        # Different HTML pages follow different structure but they typically
        # fall under one of the below expected structures. Whenever a new structure
        # is encountered, here is where th logic should be updated/

        # 1. Process by xpath
        elements = parsed_html.xpath('//div[@class="caas-content-wrapper"]')
        if len(elements) and len(elements) == 1:
            return elements[0].text_content()

        # 2. Process by another xpath
        elements = parsed_html.xpath('//section[@class="articles"]')
        if len(elements) and len(elements) == 1:
            return elements[0].text_content()

        # 3. Process by another xpath
        elements = parsed_html.xpath('//main[@class="W(100%)"]')
        if len(elements) and len(elements) == 1:
            return elements[0].text_content()

        # 4. Process using BeautifulSoap
        soup = BeautifulSoup(html_content, 'html.parser')
        all_text = soup.get_text()

        # 4a. Try regex1
        match = re.search(r'Read full article(.+)Latest Stories', all_text)
        if match:
            return match.group(1)

        # 4b. Try regex2
        pattern = re.compile(r'See all articles(.+)View All Comments', re.S)
        match = re.search(pattern, all_text)
        if match:
            return match.group(1)

        # Handle new patterns here as needed
        # ....

        # A fallback of considering the whole visible text (title + essay + reviews + extras)
        # can be considered to avoid unnecessary exception. When processing in 1000s, such
        # fallbacks for a few no.of files will not skew the result majorly.
        logger.DEBUG(f"---NONE OF THE MECHANISMS WORKED, FALLBACK USED---")
        return all_text

    def process_file_content(self, html_content):
        """
        This method accepts the html source file content, then extracts
        only the relevant content, then tokenize the content into words and
        finally calculates the word frequency.

        Args:
            html_content(str): HTML file content to be processed

        Returns: None

        """
        all_text = self.retrieve_text(html_content)
        # Tokenize and clean the text
        words = self.tokenize_and_clean(all_text)

        # Update the words in the counter
        self.counter.update(words)

    def process_all_files(self):
        """
        Process all the files by considering only the relevant content of our
        interest, tokenizing the words and then counting those.
        """
        # Iterate through the file paths and calculate word frequency
        logger.INFO(f"Processing all files under {self.html_files_dir_path}")
        file_paths = [f for f in os.listdir(self.html_files_dir_path)]
        for file_name in file_paths:
            full_path = os.path.join(self.html_files_dir_path, file_name)
            if not os.path.isfile(full_path):
                continue
            if file_name.startswith("NOT_FOUND_"):
                logger.DEBUG(f"Skipping {full_path}")
                continue

            logger.INFO(f"Handling {full_path}")
            with open(full_path, "r", encoding="utf-8") as file:
                self.process_file_content(html_content=file.read())

    def get_top_words(self, count):
        """
        Method to return the top words from the files processed

        Args:
            count(int): Count of top no.of words needed

        Returns:
            List of top (word, no_of_occurences) pairs

        """
        return self.counter.most_common(count)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Word frequency processor")
    parser.add_argument("-p", "--relative_dir_path",
                        help='relative (to the cwd) directory path that contains html files. '
                             f"Default: {constants.RELATIVE_HTML_DIR_PATH}",
                        type=str, default=constants.RELATIVE_HTML_DIR_PATH)
    parser.add_argument("-w", "--word_bank_file_path",
                        help='relative (to the cwd) file path for word bank. '
                             f'Default: {constants.RELATIVE_WORD_BANK_FILE_PATH}',
                        type=str, default=constants.RELATIVE_WORD_BANK_FILE_PATH)
    parser.add_argument("-c", "--count",
                        help=f"Count of top words needed. "
                             f"Default: {constants.TOP_WORD_COUNT}",
                             type=int, default=constants.TOP_WORD_COUNT)
    parser.add_argument("-d", "--debug", help="Enable debug messages",
                        required=False, action='store_true')

    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logger.setup_logging(log_level="DEBUG")
    html_files_dir_path = os.path.join(
        os.getcwd(), parsed_args.relative_dir_path)
    analyzer = WordFrequencyProcessor(html_files_dir_path=html_files_dir_path)
    analyzer.process_all_files()
    result = analyzer.get_top_words(count=parsed_args.count)

    logger.INFO("Top {count} words are: {data}".format(
        count=parsed_args.count,
        data=json.dumps(result, indent=2)
    ))