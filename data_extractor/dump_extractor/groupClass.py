from baseClass import Container

class TypeSame(Container):

    def __ini__(self, type_id, snap):
        super().__init__(type_id, snap)

    def __str__(self):
        return f'<TypeSame:{self.id}>'

    def __repr__(self):
        return f'<TypeSame:{self.id}>'

    def __iter__(self):
        self._cursor = 0
        self._length = len(self.data)
        return self

    def __next__(self):
        if self._cursor < self._length:
            ret = self.data[self._cursor]
            self._cursor += 1
            return ret
        else:
            self._cursor = 0
            raise StopIteration   



class Molecule(Container):

    def __ini__(self, mol_id, snap):
        super().__init__(mol_id, snap)

    def __str__(self):
        return f'<Molecule: {self.id}>'

    def __repr__(self):
        return f'<Molecule: {self.id}>'

    def __iter__(self):
        self._cursor = 0
        self._length = len(self.data)
        return self

    def __next__(self):
        if self._cursor < self._length:
            ret = self.data[self._cursor]
            self._cursor += 1
            return ret
        else:
            self._cursor = 0
            raise StopIteration   


class Part(Container):

    def __init__(self, part_id, snap):
        super().__init__(part_id, snap)


    def __str__(self):
        return f'<Part: {self.id}>'

    def __repr__(self):
        return f'<Part: {self.id}>'

    def __iter__(self):
        self._cursor = 0
        self._length = len(self.data)
        return self

    def __next__(self):
        if self._cursor < self._length:
            ret = self.data[self._cursor]
            self._cursor += 1
            return ret
        else:
            self._cursor = 0
            raise StopIteration   