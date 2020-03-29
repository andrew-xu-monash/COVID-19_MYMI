# TODO:
## - add referencing list as a variable into main dataframe

import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import glob
import json
import re

# defining file path for raw data
root_path = "C:\\Users\\Andrew\\PycharmProjects\\COVID-19-MYMI\\Data"
# defining file path for metadata
metadata_path = f'{root_path}\\all_sources_metadata_2020-03-13.csv'
# reading in metadata
meta_df = pd.read_csv(metadata_path, dtype={
    'pubmed_id': str,
    'Microsoft Academic Paper ID': str,
    'doi': str
})

# setting all_json as the a pattern in which all the files follows (via the glob.glob function)
all_json = glob.glob(f'{root_path}/**/*.json', recursive=True)

# reading in a single file for testing
with open(
        "C:\\Users\\Andrew\\PycharmProjects\\COVID-19-MYMI\\data\\0b0cc43d86df1f781f1b37dc2e1a5d8e0b12f7ae.json") as file:
    test_json = json.load(file)


# setting class for reading files
class FileReader:
    def __init__(self, file_path):
        with open(file_path) as file:
            content = json.load(file)
            self.paper_id = content['paper_id']
            self.abstract = []
            self.body_text = []
            # Abstract, need for loop to iterate through every word
            for entry in content['abstract']:
                self.abstract.append(entry['text'])
            # Body text, need for loop to iterate through every word
            for entry in content['body_text']:
                self.body_text.append(entry['text'])
            self.abstract = '\n'.join(self.abstract)
            self.body_text = '\n'.join(self.body_text)

    def __repr__(self):
        return f'{self.paper_id}: {self.abstract[:200]}... {self.body_text[:200]}...'


# Adding breaks within abstract & body text
def get_breaks(content, length):
    data = ""
    words = content.split(' ')
    total_chars = 0

    # add break every length characters
    for i in range(len(words)):
        total_chars += len(words[i])
        if total_chars > length:
            data = data + "<br>" + words[i]
            total_chars = 0
        else:
            data = data + " " + words[i]
    return data


from ast import literal_eval

# Defining empty dictionary
dict_ = {'paper_id': [], 'abstract': [], 'body_text': [], 'authors': [], 'title': [], 'journal': [],
         'abstract_summary': []}

# Iterating through every paper, for each paper, fill an entry within the dictionary
# enumerate() keeps a counter on the number of iterations
for idx, entry in enumerate(all_json):
    # Progress bar
    if idx % (len(all_json) // 10) == 0:
        print(f'Processing index: {idx} of {len(all_json)}')
    content = FileReader(entry)
    dict_['paper_id'].append(content.paper_id)
    dict_['abstract'].append(content.abstract)
    dict_['body_text'].append(content.body_text)

    # also create a column for the summary of abstract to be used in a plot
    if len(content.abstract) == 0:
        # no abstract provided
        dict_['abstract_summary'].append("Not provided.")
    elif len(content.abstract.split(' ')) > 100:
        # abstract provided is too long for plot, take first 300 words append with ...
        info = content.abstract.split(' ')[:100]
        summary = get_breaks(' '.join(info), 40)
        dict_['abstract_summary'].append(summary + "...")
    else:
        # abstract is short enough
        summary = get_breaks(content.abstract, 40)
        dict_['abstract_summary'].append(summary)

    # get metadata information
    meta_data = meta_df.loc[meta_df['sha'] == content.paper_id]

    try:
        # if more than one author
        authors = literal_eval(meta_data['authors'].values[0])
        if len(authors) > 2:
            # more than 2 authors, may be problem when plotting, so take first 2 append with ...
            dict_['authors'].append(". ".join(authors[:2]) + "...")
        else:
            # authors will fit in plot
            dict_['authors'].append(". ".join(authors))
    except Exception as e:
        # if only one author - or Null valie
        dict_['authors'].append(meta_data['authors'].values[0])

    # add the title information, add breaks when needed
    try:
        title = get_breaks(meta_data['title'].values[0], 40)
        dict_['title'].append(title)
    # if title was not provided
    except Exception as e:
        dict_['title'].append(meta_data['title'].values[0])

    # add the journal information
    dict_['journal'].append(meta_data['journal'].values[0])

df_covid = pd.DataFrame(dict_, columns=['paper_id', 'abstract', 'body_text', 'authors', 'title', 'journal',
                                        'abstract_summary'])

import re


def keyword_search(keyword, data):
    counter = 0
    for abstract in data["abstract"]:
        # pat = re.complie(r'[^a-zA-Z]+')
        # str = re.sub(pat, "", abstract).lower()
        str = abstract.lower()
        splits = str.split()
        for split in splits:
            if split == keyword:
                counter += 1
    return counter


print(f'There are {keyword_search("diagnosis", df_covid)} papers with the word "diagnosis" '
      f'within the abstract.')
print(f'There are {keyword_search("surveillance", df_covid)} papers with the word "surveillance" '
      f'within the abstract.')
