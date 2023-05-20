import datetime
import glob
import gzip
import itertools
import json
import logging
import random
import time

from PIL import Image
import pysolr
from pysolr import SolrError
from tqdm.auto import tqdm

from mysql import MySQLClient
client = MySQLClient()

from solr import SolrClient
from config import *
from vectorizer.vectorizer import Vectorizer

class Indexer(SolrClient):
    def __init__(self):
        super().__init__()
        self.v = Vectorizer()
        self.max_index_size = 1200000
        self.post = 0

    def load_large_data(self, filepath):
        with gzip.open(filepath) as f:
            for line in tqdm(f, total=self.max_index_size, desc="parse wiki documents"):
                yield json.loads(line)

    def map_media(self, k) -> int:
        medias = {
            "dokujo-tsushin": 1,
            "it-life-hack": 2,
            "kaden-channel": 3,
            "livedoor-homme": 4,
            "movie-enter": 5,
            "peachy": 6,
            "smax": 7,
            "sports-watch": 8,
            "topic-news": 9
        }
        return medias.get(k)

    def save_index(self, data, collection):
        with open(f'index/index.{collection}.{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json', 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def create_index(self, collection, save:bool=True, filepath:str=None):
        col_info = COLLECTION.get(collection)
        if collection == 'wiki':
            return self.create_wiki_index(collection, filepath=filepath)
        elif col_info.get('result_type') == 'text' and col_info.get('w2v'):
            return self.create_text_index(collection, save)
        elif col_info.get('result_type') == 'text' and col_info.get('clip'):
            return self.create_clip_text_index(collection)
        elif col_info.get('result_type') == 'image':
            return self.create_img_index(collection, save)
        else:
            raise Exception('Invalid Collection')

    def create_text_index(self, collection, save:bool=True):
        rows = client.select()
        model = COLLECTION.get(collection).get('embedding_model')
        logging.info(f'vectorize {len(rows)} texts')
        data = [
            {
                'id': i,
                'media': self.map_media(row.get('media')),
                'url': row.get('url'),
                'title': row.get('title'),
                'body': row.get('body'),
                'vector': self.v.get_text_vector(model, row.get('body'))
            } for i, row in enumerate(tqdm(rows, total=len(rows), desc='[vectorizing]'))
        ]
        logging.info(f'finish vectorize {len(rows)} texts')

        if save:
            self.save_index(data, collection)

        return len(data)

    def create_img_index(self, collection, save:bool=True):
        ext = ['jpg', 'png', 'JPG', 'PNG', 'jfif']
        model = COLLECTION.get(collection).get('embedding_model')
        filepaths = list(itertools.chain.from_iterable([glob.glob(f'img/{collection}/**/*.{e}', recursive=True) for e in ext]))
        if len(filepaths) > self.max_index_size:
            filepaths = random.sample(filepaths, self.max_index_size)
        data = [
            {
                'id': i,
                'filepath': filepath,
                'vector': self.v.get_img_vector(model, Image.open(filepath))
            } for i, filepath in enumerate(tqdm(filepaths, total=len(filepaths), desc='[vectorizing]'))
        ]

        if save:
            self.save_index(data, collection)

        return len(data)

    def create_clip_text_index(self, collection, save:bool=True):
        logging.info(f'vectorize {collection} texts')
        rows = client.select()
        logging.info(f'vectorize {len(rows)} texts')
        model = COLLECTION.get(collection).get('embedding_model')

        if save:
            with open(f'index/index.{collection}.{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json', 'w') as f:
                for i, row in enumerate(tqdm(rows, total=len(rows), desc='[vectorizing]')):
                    data = {
                        'id': i,
                        'media': self.map_media(row.get('media')),
                        'url': row.get('url'),
                        'title': row.get('title'),
                        'body': row.get('body'),
                        'vector': self.v.get_text_vector(model, row.get('body'))
                    }
                    json.dump(data, f, ensure_ascii=False)
                    f.write('\n')
                    if i % 1000 == 0:
                        logging.info(f'{i} docs vectorized')

        logging.info(f'finish vectorize {collection} texts')
        return len(rows)

    def create_wiki_index(self, collection, filepath, save:bool=True):
        logging.info(f'vectorize {collection} texts')
        model = COLLECTION.get(collection).get('embedding_model')

        if save:
            with open(f'index/index.{collection}.{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.json', 'w') as f:
                for i, row in enumerate(self.load_large_data(filepath)):
                    if "index" not in row:
                        data = {
                            'id': i,
                            'media': row.get('media'),
                            'url': row.get('url'),
                            'title': row.get('title'),
                            'body': row.get('text'),
                            'vector': self.v.get_text_vector(model, row.get('text'))
                        }
                        json.dump(data, f, ensure_ascii=False)
                        f.write('\n')
                    if i % 10000 == 0:
                        logging.info(f'{i} docs vectorized')

        logging.info(f'finish vectorize {collection} texts')
        return i

    def _add(self, collection: str, data: list, commit :bool=True, max_post=60000):
        solr = pysolr.SolrCloud(self.zookeeper, collection=collection, timeout=30, retry_count=5, retry_timeout=0.2, always_commit=commit)
        solr.ping()

        # 大きすぎるとタイムアウトするので max_post 件ずつ送る
        for i in range(0, len(data), max_post):
            solr.add(data[i:i+max_post])
            time.sleep(2)

    def _add_large_index(self, collection, filepath, max_load_size=100):
        self.post = 0
        data = []
        for i, row in enumerate(self.load_large_data(filepath)):
            data += [row]
            if i % max_load_size == 0: # 一度に全件は Memory に載り切らないので分割して読み込み& post する
                self._add(collection, data, False)
                self.post += 1
                data = []
                if i >= self.max_index_size:
                    break # リソースの都合上これ以上はSolrにインデックスできない
        if self.post == 0: # 総ドキュメント数が max_index_size を下回った場合
            self._add(collection, data, False)

        solr = pysolr.SolrCloud(self.zookeeper, collection=collection, timeout=30, retry_count=5, retry_timeout=0.2, always_commit=False)
        solr.ping()
        solr.commit()

    def _add_wiki_org(self, collection, filepath):
        data = []
        for i, row in enumerate(self.load_large_data(filepath)):
            data += [{
                        'id': row.get('id'),
                        'media': row.get('media'),
                        'url': row.get('url'),
                        'title': row.get('title'),
                        'body': row.get('body'),
                    }]
            if i % 30000 == 0:
                self._add(collection, data, False)
                data = []
                if i >= self.max_index_size:
                    break # リソースの都合上これ以上はSolrにインデックスできない

        solr = pysolr.SolrCloud(self.zookeeper, collection=collection, timeout=30, retry_count=5, retry_timeout=0.2, always_commit=False)
        solr.ping()
        solr.commit()

    def add(self, collection, data:list=None, filepath:str=None):
        index_size = COLLECTION.get(collection).get('index_size')
        try:
            if data:
                self._add(collection, data)
            elif index_size == "large":
                self._add_large_index(collection, filepath=filepath)
            else:
                self._add(collection, self.create_index(collection))
        except SolrError as e:
            raise Exception(f':umbrella_with_rain_drops: failed!\n[ERROR]\n{e}')

        return ':100: success'
