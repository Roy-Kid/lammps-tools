from baseClass import Container
from collections import defaultdict
from groupClass import Molecule, TypeSame

class Molecules(Container):

    id = 1

    def __init__(self, snap, ref=1, id = id):
        super().__init__(id, snap)
        self._ref = ref
        self._dechire(snap, self._ref)
        
        id += 1

    def _dechire(self, snap, ref):
        """用于拆分成Molecule的私有函数。
        
        Args:
            data (list): 排序好的数据
            snap (Snap): 原始数据传入
            ref (int): 指出mol-id的位置
        """        
        temp = defaultdict(list)

        for d in self.data:
            temp[int(d[ref])].append(d)
        
        self.data = list()
        for k,v in temp.items():
            snap.data = v
            mol = Molecule(k, snap)

            self.data.append(mol)      

    def __repr__(self):
        return f'<Molecules: {self.id}>'  

class TypeSames(Container):

    id = 1

    def __init__(self, snap, ref=2, id=id):
        super().__init__(id, snap)
        self._ref = ref
        self._dechire(snap)
        

        id += 1

    def _dechire(self, snap):
        """用于拆分成Molecule的私有函数。
        
        Args:
            data (list): 排序好的数据
            snap (Snap): 系统信息
            ref (int): type-id位置
        """        
        self.data = list() #清除全局data信息，装入容器
        temp = defaultdict(list)
        ref = self.ref

        for d in snap.data:
            temp[int(d[ref])].append(d)
        for k,v in temp.items():
            snap.data = v
            mol = TypeSame(k, snap)

            self.data.append(mol)        

    def __repr__(self):
        return f'<Typesomes: {self.id}>'  

    # def __iter__(self):
    #     self._cursor = 0
    #     self._length = len(self._container)
    #     return self

    # def __next__(self):
    #     if self._cursor < self._length:
    #         ret = self._container[self._cursor]
    #         self._cursor += 1
    #         return ret
    #     else:
    #         self._cursor = 0
    #         raise StopIteration   

    @property
    def ref(self):
        return self._ref

class Parts(Container):

    def __init__(self,  container, ref=None, id=id):
        # Container类需要传入一个snap来获取系统信息，但是通常这里传入的是snap的组合，把组合分成组合；因此随便传入一个，然后让_container里在储存parts，反复迭代。

        # 为什么这里的ref一开始none：这个parts是一个比较特殊的容器，它既是一个和Molecule平级的容器，又可以储存它本身。这一部分的功能为什么不交给part(Group)来做，因为group是为了储存一个原子单位而设计，而这里面最后要储存好多的Group子类。因此如果ref是位置参数的话，会陷入死循环，如果parts已经到了最底层，那么就不添加ref以跳出
        super().__init__(id, container)
        self._ref = ref
        self.data = list()


        if self._ref is not None:
            self._dechire(container, self._ref)
        else:
            """container（数据结构）.container（中的数据 ）
            """            
            self.data += container.data

       

    def _dechire(self, container, ref):
        self.data +=  ref(container)


    def __str__(self):
        return f'<Parts: {self.id}>'

    def __repr__(self):
        return f'<Parts: {self.id}>'    