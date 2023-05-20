from abc import abstractmethod
from abc import ABCMeta

import pysolr

class SolrClient(metaclass=ABCMeta):
    def __init__(self) -> None:
        super().__init__()
        self.zookeeper = pysolr.ZooKeeper("zookeeper1:2181")

class Searcher(SolrClient):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def search(self):
        pass
