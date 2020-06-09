class lmp2xml:

    def __init__(self, fname):
        self.fname = fname
        self.data = dict()
        self.read_lmp()
        self.write_xml()

    def read_lmp(self):
        from lammps_tools.data_processing import data
        data = data.Data(self.fname)
        self.data = data.read_data()
        

    def write_xml(self):

        f = open(f'{self.fname}.xml', 'w')

        import contextlib
        @contextlib.contextmanager
        def add_label(lname, **kargs):
            label_name = lname
            for k,v in kargs.items():
                label_name += f' {k}="{v}"'
            f.write(f'<{label_name}>\n')
            try:
                yield
            finally:
                f.write(f'</{lname}>\n')

        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        with add_label('hoomd_xml', version=2.7):
            with add_label('configuration', time_step=0, dimensions=3, natoms=self.data['atoms']):
                with add_label('box', lx=self.data['xhi'], ly=self.data['yhi'], lz=self.data['zhi'], xy=0, yz=0):
                    with add_label('mass', num=self.data['atom_types']):
                        for i in self.data['Masses']:
                            f.write('\t'.join(i)+'\n')
                    
                    with add_label('position', num=self.data['atoms']):
                        for i in self.data['position']:
                            f.write('\t'.join(i)+'\n')
                    
                    with add_label('type', num=self.data['atoms']):
                        for i in self.data['atom_type_list']:
                            f.write(f'{i}\n')

                    with add_label('bond', num=self.data['bonds']):
                        for i in self.data['Bonds_xml']:
                            f.write(f'\t'.join(i)+'\n')

                    with add_label('angle', num=self.data['angles']):
                        for i in self.data['Angles_xml']:
                            f.write(f'\t'.join(i)+'\n')

                    with add_label('dihedrals', num=self.data['dihedrals']):
                        for i in self.data['Dihedrals_xml']:
                            f.write(f'\t'.join(i)+'\n')
