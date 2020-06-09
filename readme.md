# 使用手册

本套件建议配合python交互模式或者jupyter notebook使用

|   |   |
|---|---|
|convertor|数据格式间转换工具|
|extractor|数据提取结构化工具|
|builder|模型生成工具|

## 起步

首先读取一个dump文件，然后指定读取的帧范围

```
dump = Dump('your/dump/path')
snaps = dump[10:1000:10]
```

snaps中包含有100个帧，每一个帧中包含了系统的所用信息。选择一个帧使用api以访问它

```
snaps[0].timestep  #当前时间步
snaps[-1].nofAtoms  #系统原子数

```

下一步是需要将所有粒子信息结构化，如按照分子链区分，按照类型区分

```
m = Molecules(snaps[-1])
ts = Typesames(snaps[-1])
```

同样，可以用api访问信息，用索引访问每一个分子或者类型组
```
molecule1 = m[0]
type1 = ts[0]
```

或者，可以传入一个函数，来定义如何对粒子进行划分

```
def ref(molecules):
    matrix = 160
    rod = 1
    graft = 8

    container = list()
    m0 = aux_replicate(molecules) # python的类是传址引用，因此需要复制一份

    m0.data = m0.data[:matrix] # 将前160条基体分子链分离出来

    container.append(Parts(m0, None, 'Matrix')) # 使用Parts类包装，等效于Molecule，存入临时容器

    for i in range(50): # 对剩余分子分组

        m0 = aux_replicate(molecules)


        m0.data = m0.data[matrix + i* (rod+graft) : matrix + (i+1)* (rod+graft)]

        container.append(Parts(m0, None, f'graft{i+1}'))

    return container # 返回装有Part容器的临时容器

p = Parts(molecules, ref, 'top')
p1 = p[0] # Matrix部分
```

# 计算
如计算type1 和type2之间的径向分布函数
```
center_atoms = typesames[1]
pair_atoms = typesames[2]

x, y = com_rdf(center_atoms, pair_atoms, bin=0.1, cutoff=2)
```

如果计算每一个分子的性质，那么构建函数的时候只需要着眼于当前分子，如

```
gys = aux_repeat(com_gyration, molecules) # com_gyration是计算一个分子的回转半径，repeat则是自动迭代容器中所有的分子
```

### model_builder

** 功能 **:
* 生成单链
* 生成支化链
* 生成石墨烯片

先生成配置文件模板, 修改参数后执行, 得到moltemplate的代码, 再使用moltemplate组装并生成所需的data.

#### polymer_generator.py
  
**Usage**
1. 新建.py文件或者使用python交互模式:
```
>>> import lammps_tools.model_builder.polymer_generator as pg
>>> pg.generate_lt()
```
生成模板文件monomer.lt, system.lt, polymer.ini, forcefield.lt
2. 按需修改模板
3. 运行
```
>>> pg.run()
```
4. 得到单个分子链文件. 同时输出这个链所占据的矩体尺寸, 方便在system.lt中移动生成
5. 写system.lt文件, 使用```moltemplate.sh system.lt ```生成文件

** 选项解释 **
[DEFAULT]
* 简易名字 := simple_name (yes/no). 
  ```
  指定yes文件名为'polymer.lt', 分子名'Polymer'; 
  文件名为: 'polymer-{main_chain_length}-{branch_length}\_{branch_number}.lt',
  分子名为 'Polymer-{main_chain_length}-{branch_length}_{(branch_number)}'
  ```

* 盒子尺寸 := box_*
* 单体文件 := monomer.ltname

[BACKBONE]
* 主链长 := c_chain_length
* 主链键长 := c_bond_length
* 主链元原子 := C_atom
* 主链原子ID := C_ID #当单体为多原子时起作用
* 是否有支链 := isBranch
```
C_atom inherits Forcefield{

    write("Data Atoms"){  ###保持元原子坐标在原点不变###
        $atom:C_ID     $mol:...    @atom:C     0    0    0    0
}}
```
[BRANCH]

* 支链长度 := b_chain_length
* 支链键长 := b_bond_length
* 支化点 := b_point = p1, p2, p3...
* 支链元原子 := b_atom
* 支链原子ID := b_ID

```
b_atom inherits Forcefield{

    write("Data Atoms"){
        $atom:B_ID     $mol:...    @atom:B     0    0    0    0   
    }
}
```

#### GP_generator.py
用法同上. 先使用generator_lt()生成配置文件模板, 再使用.run()执行.
** 编译树 **

monomer.lt -> polymer.lt --(fieldforce.lt)--> system.lt


### data_convertor
这一部分文件负责将LAMMPS的input data转换成其他格式文件.
#### lmp2xml
将data转换为XML. 
用法:
```
a = lmp2xml(fpath)
```
#### lmp2gsds
将data转换为GSD
```
b = lmp2gsd(fpath)
```
### utils
这一部分提供基本的数据处理.

#### discrete.py
提供了一个等宽分割的组件.
** Usage **
1. 实例化一个类, 传入需要处理的数据
``` d = Discrete(x, y) ```
2. 指定参数, 回收处理后的数据
``` x, y = equal_width_discrete(bin, ave=False, normalize=False) ```

** API **
* * class * Discrete(x, y=None)
传入x 或 x, y值, 如果y不指定则匹配生成与x等长元素为1的数列

* equal_width_discrete(bin, ave=False, normalize=False)
bin := 宽度
ave := 是否将每个bin中记录的数据加和平均
normalize := 是否对全体做归一化处理