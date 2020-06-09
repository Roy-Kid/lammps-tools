# version: 0.0.3

class Snap:
    """Snap是整个程序基类。原因在于，所有的数据结构都有TIMESTEP，DATA这些数据，只不过在其上增加了功能，也就是说，dump里的数据永远要跟着数据结构走，子类和Snap的关系都是is-like-a的关系。实践证明，snap中的data就是得随着拆分而改变，否则后面处理起来处理的变量越来越多。如果需要全局怎么办，那就直接引用dump[][0]啊。

    其他派生的子类任何时候都应该接受Snap类作为数据结构，而不是单独传入数据。由此的蛋生鸡鸡生蛋的问题，解决之道在于只有完全信赖的Dump类可以直接向内部写入数据。
    """    

    def __init__(self, snap=None):
        
        if isinstance(snap, dict): 
            self._TIMESTEP = snap['TIMESTEP']
            self._NUMBER_OF_ATOMS = snap['NUMBER_OF_ATOMS']
            self._BOUNDARY_CONDITION_X = snap['BOUNDARY_CONDITION_X']
            self._BOUNDARY_CONDITION_Y = snap['BOUNDARY_CONDITION_Y']
            self._BOUNDARY_CONDITION_Z = snap['BOUNDARY_CONDITION_Z']
            self._XLO = snap['XLO']
            self._XHI = snap['XHI']
            self._YLO = snap['YLO']
            self._YHI = snap['YHI']
            self._ZLO = snap['ZLO']
            self._ZHI = snap['ZHI']
            self._HEADER = snap['HEADER']
            self._DATA = snap['DATA']
        
        else:
            self._TIMESTEP = snap.timestep
            self._NUMBER_OF_ATOMS = snap.nofAtoms
            self._BOUNDARY_CONDITION_X = snap.boundary_condition_x
            self._BOUNDARY_CONDITION_Y = snap.boundary_condition_y
            self._BOUNDARY_CONDITION_Z = snap.boundary_condition_z
            self._XLO = snap.xlo
            self._XHI = snap.xhi
            self._YLO = snap.ylo
            self._YHI = snap.yhi
            self._ZLO = snap.zlo
            self._ZHI = snap.zhi
            self._HEADER = snap.header
            self._DATA = snap.data

        self._DATA.sort(key=lambda atom: atom[0])

    def __iter__(self):
        self._cursor = 0
        self._length = len(self._DATA)
        return self

    def __next__(self):
        if self._cursor < self._length:
            ret = self._DATA[self._cursor]
            self._cursor += 1
            return ret
        else:
            self._cursor = 0
            raise StopIteration    

    def __getitem__(self, n):
        return self.data[n]

    @property
    def timestep(self):
        return self._TIMESTEP

    @property
    def nofAtoms(self):
        return self._NUMBER_OF_ATOMS
    
    @property
    def boundary_condition_x(self):
        return self._BOUNDARY_CONDITION_X
    @property
    def boundary_condition_y(self):
        return self._BOUNDARY_CONDITION_Y

    @property
    def boundary_condition_z(self):
        return self._BOUNDARY_CONDITION_Z

    @property
    def boundary_x(self):
        return self._XHI - self._XLO

    @property
    def boundary_y(self):
        return self._YHI - self._YLO

    @property
    def boundary_z(self):
        return self._ZHI - self._ZLO

    @property
    def xlo(self):
        return self._XLO

    @property
    def xhi(self):
        return self._XHI

    @property
    def ylo(self):
        return self._YLO
    
    @property
    def yhi(self):
        return self._YHI

    @property
    def zlo(self):
        return self._ZLO

    @property
    def zhi(self):
        return self._ZHI

    @property
    def header(self):
        return self._HEADER

    @property
    def data(self):
        return self._DATA

    @data.setter
    def data(self, data):
        self._DATA = data

    @property
    def length(self):
        return len(self._DATA)

    @property
    def ls(self):
        return f'contains {self.length} elements'

    def __str__(self):
        return f'<Snap at {self.timestep} TIMESTEP>'

    def __repr__(self):
        return f'<Snap at {self.timestep} TIMESTEP>'

    def __len__(self):
        return self.length

    

class Container(Snap):
    """Container类同样完全继承了Snap的全部信息，同时创建一个self._container储存分类信息。传入snap之后，即刻将信息储存在self._DATA中。
    
    Args:
        ref (int): 指明分类依据
        Snap ([type]): Snap类提供了全部的系统信息
    """        
    def __init__(self, id, snap):
        if not isinstance(snap, Snap):
            raise TypeError('请传入一个Snap派生类。这个问题通常是dump实例指定snap后没有手动指定[0]造成')

        super().__init__(snap)    

        self._id = id

    def __getitem__(self, n):
        return self._DATA[n] 

    def __iter__(self):
        self._cursor = 0
        self._length = len(self._DATA)
        return self

    def __next__(self):
        if self._cursor < self._length:
            ret = self._DATA[self._cursor]
            self._cursor += 1
            return ret
        else:
            self._cursor = 0
            raise StopIteration  

    @property
    def id(self):
        return self._id

    @property
    def ls(self):
        return self._DATA

    @property
    def length(self):
        return len(self._DATA)


class Dump:
    def __init__(self, fpath):
        self._fpath = fpath
        try:
            self._dump = open(fpath)
        except FileNotFoundError as e:
            print(e, '文件不存在，请检查路径')
            raise


    def __getitem__(self, n):

        stack = list()

        if isinstance(n, int):
            if n >= 0:
                for j in self._read_data(self._fpath, n, n, 1):
                    stack.append(j)
                    return stack
            elif n < 0:
                raise TypeError(f'TIMESTEP 应该是一个整数{n}')

        elif isinstance(n, slice):

            start = n.start
            end = n.stop
            if n.step is None:
                stride = 1
            else:
                stride = n.step

            for j in self._read_data(self._fpath, start, end, stride):
                stack.append(j)
            return stack

        else:
            raise TypeError(f'类型不对兄弟，别搞我')

    def _read_data(self, fpath, start, end, stride):
        dump = open(fpath)
        line = dump.readline()
        while line.startswith('ITEM'):


            snap = dict()
            snap['DATA'] = list()

            if line.startswith('ITEM: TIMESTEP'):
                line = dump.readline()
                snap['TIMESTEP'] = int(line.split()[0])
                line = dump.readline()

            if line.startswith('ITEM: NUMBER OF ATOM'):
                line = dump.readline()
                snap['NUMBER_OF_ATOMS'] = int(line.split()[0])
                line = dump.readline()
            if line.startswith('ITEM: BOX'):
                snap['BOUNDARY_CONDITION_X'], snap['BOUNDARY_CONDITION_Y'], snap['BOUNDARY_CONDITION_Z'] = line.split()[-3:]
                line = dump.readline()
                snap['XLO'], snap['XHI'] = [float(i)
                                      for i in line.split()]
                line = dump.readline()
                snap['YLO'], snap['YHI'] = [float(i)
                                      for i in line.split()]
                line = dump.readline()
                snap['ZLO'], snap['ZHI'] = [float(i)
                                      for i in line.split()]
                line = dump.readline()

            # if line.startswith('ITEM: ATOMS'):
            #     snap['HEADER'] = line.split()[2:]

            #     # if out of the slice than jump over this snap;
            #     if snap['TIMESTEP'] < start or snap['TIMESTEP'] > end or (snap['TIMESTEP']-start)%stride != 0:
            #         line = dump.readline()
            #         while not line.startswith('ITEM: TIMESTEP'):
            #             line = dump.readline()
            #         continue

            #     for line in dump:
            #         if not line.startswith('ITEM'):
            #             snap['DATA'].append([float(i) for i in line.split()])                        
            #         else:
            #             break

            if line.startswith('ITEM: ATOMS'):
                snap['HEADER'] = line.split()[2:]
                if snap['TIMESTEP'] >= start and (snap['TIMESTEP']-start)%stride == 0:
                    if snap['TIMESTEP'] > end:
                        break
                    else:
                        for line in dump:
                            if not line.startswith('ITEM'):
                                snap['DATA'].append([float(i) for i in line.split()])
                            else:
                                break
                else: # 任何不符合要求的情况
                    line = dump.readline()
                    while not line.startswith('ITEM: TIMESTEP'):
                        line = dump.readline()
                    continue

                yield Snap(snap)

