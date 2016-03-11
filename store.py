__author__ = 'alierza'

from flask import  json

class Store():
    def __init__(self):
        self.packages = None
        self.load_packages()


    def load_packages(self):
        with open("store.txt") as f:
            packages = f.read()
            self.packages = packages

    def get_packages(self):
        return self.packages

    def get_package_dicount(self,id):
        myPacks = self.packages.split('\n')
        myPack = myPacks[id - 1]
        myPack = myPack.split(":")
        return myPack[3]

    def get_package_price(self,id):
        myPacks = self.packages.split('\n')
        myPack = myPacks[id - 1]
        myPack = myPack.split(":")
        return myPack[1]

    def get_package_diamond(self,id):
        myPacks = self.packages.split('\n')
        myPack = myPacks[id - 1]
        myPack = myPack.split(":")
        return myPack[2]

