class lmp2gsd:

    def __init__(self, fname):
        self.fname = fname
        self.data = dict()
        self.read_lmp()
        self.write_gsd()

    def read_lmp(self):
        from ..data_extractor import data
        data = data.Data(self.fname)
        self.data = data.read_data()

    def write_gsd(self):

        try:
            from gsd import hoomd
        except:
            raise('you should install dependency by "pip install gsd", more detail can refer to https://gsd.readthedocs.io/en/stable/')

        f = hoomd.open(name=f'{self.fname}.gsd', mode='wb')

        s = hoomd.Snapshot()
        
        s.configuration.step = 0
        s.configuration.dimensions = 3
        s.configuration.box = [self.data['xhi']*2, self.data['yhi']*2, self.data['zhi']*2, 0, 0, 0]


        s.particles.N = self.data['atoms']
        s.particles.mass = [14.01 for i in range(10)]
        s.particles.position = self.data['position']
        s.particles.types = ['Atom1']
        s.particles.typeid = self.data['Atom_type_list']

        s.bonds.N = self.data['bonds']
        s.bonds.group = self.data['Bonds_topo']
        s.bonds.types = ['Bond0']
        s.bonds.typeid = self.data['Bonds_type_list']

        s.angles.N = self.data['angles']
        s.angles.types = ['Angle0','Angle1']
        s.angles.typeid = self.data['Angles_type_list']
        s.angles.group = self.data['Angles_topo']

        s.dihedrals.N = self.data['dihedrals']
        s.dihedrals.types = ['Dihedral0','Dihedral1']
        s.dihedrals.typeid = self.data['Dihedrals_type_list']
        s.dihedrals.group = self.data['Dihedrals_topo']

        f.extend((s,))
