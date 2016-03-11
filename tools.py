__author__ = 'alireza'




class Tools():

    def __init__(self):
        self.file = ""

    def offset_checker(self, offset, temp):
        if temp-offset >= 0:
            return temp-offset
        else:
            return 0

    def user_index_finder(self, user_ranks, player):
        j = -1
        for i in user_ranks:
            if i.id == player.id:
                return j + 1
            j = j + 1
        return j