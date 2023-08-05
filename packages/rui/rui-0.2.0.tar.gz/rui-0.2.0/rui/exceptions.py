class DuplicateEntityError(Exception):
    def __init__(self, entity):
        self.entity = entity

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{0} already exists in world'.format(self.entity)


class DuplicateSystemError(Exception):
    def __init__(self, system):
        self.system = system

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{0} already exists in world'.format(self.system)


class UnmanagedEntityError(Exception):
    def __init__(self, entity):
        self.entity = entity

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '''{0} you were trying to use in world has not been
                added to world'''.format(self.entity)


class NonUniqueTagError(Exception):
    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '''Tag {0} you were trying to use in world has already been
                added to world'''.format(self.tag)
