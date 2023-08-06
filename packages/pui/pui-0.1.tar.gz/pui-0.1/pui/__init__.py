
class element(object):
    def __init__(self, tag):
        self.tag = tag
        self.offspring = list()

    def html(self):
        content = ''.join(sub.html() for sub in self.offspring)
        return self.tag + content

    def add(self, *things):
        for thing in things:
            self.offspring.append(thing)
        return self
