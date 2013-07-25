import unittest

import Commodity

class TestCommodities(unittest.TestCase):
    def test_GetCommodities(self):
        dir = Commodity.CommodityDirector()
        dir.addCommodity('office supplies')
        self.assertTrue('office supplies' in dir.getCommodities())

from Transaction import *

import logging
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('/var/tmp/myapp.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

class TestTransactionDirector(TransactionDirector):
    "Just for test purposes"
    def populateRandomly(self,n):
        for i in range(n):
            self.transactions.append('{0}name'.format(i))

    def populateWithSomeNames(self):            
        self.addTransaction("Aloysius");
        self.addTransaction("Robert");
        self.addTransaction("Egbert");

class TestTransactions(unittest.TestCase):
    def test_GetTransactions(self):
        dir = TestTransactionDirector()
        dir.addTransaction('office supplies')
        self.assertTrue('office supplies' in dir.transactions)

    def test_CanPopulate(self):
        dir = TestTransactionDirector()
        dir.populateRandomly(4);
        self.assertTrue(len(dir.transactions) == 4)

if __name__ == '__main__':
    unittest.main()
