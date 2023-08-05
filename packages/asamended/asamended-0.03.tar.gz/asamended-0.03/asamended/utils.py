from operator import itemgetter


class OrderedSet(set):

    def sorted(self, sorter=itemgetter(0)):
        return sorted(self, key=sorter)
