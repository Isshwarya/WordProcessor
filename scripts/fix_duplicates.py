"""A temporary script used to fix duplicates"""

import os
import json

with open("data/endg-urls", "r") as file:
    data = file.read()
    urls = data.splitlines()

res = {}
duplicates = {}
for url in urls:
    url = url.strip("/")
    filename = url.split('/')[-1]
    if filename not in res:
        res[filename] = url
    else:
        if filename not in duplicates:
            duplicates[filename] = [res[filename], url]
        else:
            duplicates[filename].append(url)

print(json.dumps(duplicates, indent=2))

flat_list = []
for filename, url_list in duplicates.items():
    for url in url_list:
        flat_list.append(url)

print(json.dumps(flat_list, indent=2))
print(len(flat_list))
print(len(duplicates.keys()))

with open("data/duplicate_urls", "w", encoding='utf-8') as file:
    data = file.write(json.dumps(flat_list, indent=2))

for filename in duplicates.keys():
    filepath = os.path.join(os.getcwd(), "data",
                            "downloaded_files", f'{filename}.html')
    not_found_file_path = os.path.join(os.getcwd(), "data",
                                       "downloaded_files", f'NOT_FOUND_{filename}.html')
    print(f"Removing {filepath}")
    if os.path.isfile(filepath):
        os.remove(filepath)
    else:
        os.remove(not_found_file_path)
