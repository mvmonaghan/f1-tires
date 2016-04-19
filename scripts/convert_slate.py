import slate
import re
import os
import pandas as pd

class TextGetter(object):
   """Get the text from a pdf document"""

   def __init__(self, fname):
       # self.text is a list of pages
       with open(fname) as f:
           self.raw_text = slate.PDF(f)
       valid_pages = self.get_valid_pages()
       self.clean_text = ' '.join([self.clean_page(p) for p in valid_pages])

   def get_valid_pages(self, invalid_phrases=None):
       '''Remove pages that contain invalid_phrases

       Input: invalid_phrases as a list'''
       inst_page = 'Instructions for Issuer'
       warn_page = 'This form is provided for informational purposes only'
       invalid_phrases_list = [inst_page, warn_page]
       if invalid_phrases:
           invalid_phrases_list += invalid_phrases
       valid_pages = []
       for page in self.raw_text:
           append_page = True
           for phrase in invalid_phrases_list:
               if phrase in page:
                   append_page = False
           if append_page:
               valid_pages.append(page)
       return valid_pages

   def clean_page(self, page):
       '''Page as str'''
       page = page.decode('ascii', 'ignore')
       page = re.sub('\n', ' ', page)
       return page

if __name__ == '__main__':
   fnames = os.listdir('data/forms')

   path = 'data/forms/'
   clean_fnames = []
   for fname in fnames:
       if '.pdf' in fname:
           clean_fnames.append(path + fname)


   start_index = sum(1 for line in open('data/corpus.csv'))
   # df = pd.read_csv('data/corpus.csv', '|,|', header=None)
   # df.columns = ['raw_text']
   # df['form'] = df['raw_text'].apply(lambda x: x.split('|')[0])
   # df['text'] = df['raw_text'].apply(lambda x: x.split('|')[-1])
   # df.drop('raw_text', inplace=True, axis=0)


   with open('data/corpus.csv', 'a') as f:
       for i, fname in enumerate(clean_fnames):
           print i, fname
           if i < start_index:
               continue

           t = TextGetter(fname)
           corpus_txt = fname.split('/')[-1][:-4] + '|,|' + t.clean_text + '\n'
           print 'Writing Corpus'

           f.write(corpus_txt)
