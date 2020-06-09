def GPbond_generator(f, LX, LZ):
    c = 0
    for j in range(LZ):
        for i in range(LX-1):
            f.write(f'\t$bond:GP-bond{c}\t$atom:Units[{i}][{j}]/GP0\t$atom:Units[{i+1}][{j}]/GP1\n')
            c+=1
            f.write(f'\t$bond:GP-bond{c}\t$atom:Units[{i}][{j}]/GP3\t$atom:Units[{i+1}][{j}]/GP2\n')
            c+=1
            if j+1 < LZ:
                f.write(f'\t$bond:GP-bond{c}\t$atom:Units[{i}][{j}]/GP3\t$atom:Units[{i}][{j+1}]/GP0\n')
                c+=1
    for j in range(LZ-1):
        f.write(f'\t$bond:GP-bond{c}\t$atom:Units[{LX-1}][{j}]/GP3\t$atom:Units[{LX-1}][{j+1}]/GP0\n')
        c+=1


def GPatom_generator():
    import configparser
    import os
    if not os.path.exists('GNP_init.ini'):
        raise IOError('sorry, you should generate init template first, via "GNP_generator.generate_lt()"')
        

    config = configparser.ConfigParser()
    config.read('GNP_init.ini')
    LX = int(config['DEFAULT']['LX'])
    LZ = int(config['DEFAULT']['LZ'])

    if LZ%2 == 0:
        print('Warning : LZ should be odd and even will round down')
        LZ -= 1

    LZ = (LZ+1)-1

    BOND_LENGTH = 1.48
    cos30 = 0.866
    sin30 = 0.5
    f = open(f'GNP-{LX}x-{LZ}z.lt', 'w')
    f.write('import "forcefield.lt"\n')
    f.write(f'Unit inherits Forcefield\n')
    f.write('{\n')
    f.write('\twrite("Data Atoms")\n\t{\n')
    f.write(f'\t\t$atom:GP0\t$mol:...\t@atom:GP\t0\t{BOND_LENGTH*cos30:.2f}\t0\t0\n')
    f.write(f'\t\t$atom:GP1\t$mol:...\t@atom:GP\t0\t0\t0\t{BOND_LENGTH*sin30:.2f}\n')
    f.write(f'\t\t$atom:GP2\t$mol:...\t@atom:GP\t0\t0\t0\t{BOND_LENGTH*(sin30+1):.2f}\n')
    f.write(f'\t\t$atom:GP3\t$mol:...\t@atom:GP\t0\t{BOND_LENGTH*cos30:.2f}\t0\t{BOND_LENGTH*2:.2f}\n')
    f.write('\t}\n\n')
    f.write('\twrite("Data Bond List")\n')
    f.write('\t{\n')
    f.write('\t\t$bond:GP-bond0\t$atom:GP0\t$atom:GP1\n')
    f.write('\t\t$bond:GP-bond1\t$atom:GP1\t$atom:GP2\n')
    f.write('\t\t$bond:GP-bond2\t$atom:GP2\t$atom:GP3\n')
    f.write('\t}\n')
    f.write('}\n\n\n\n')
    f.write('Sheet inherits Forcefield\n')
    f.write('{\n')
    f.write('\tcreate_var\t{$mol}\n')

    f.write(f'\tUnits = new Unit{[LX]}.move({BOND_LENGTH*cos30*2}, 0, 0){[LZ]}.move(0, 0, {BOND_LENGTH*3})\n')
    f.write('\twrite("Data Bond List")\n')
    f.write('\t{\n')
    GPbond_generator(f, LX, LZ)
    f.write('}}')


def run():
    GPatom_generator()
    print('successfully generate GNP .lt file')

def generate_lt():

    print('start generate template')
    with open('GNP_init.ini', 'w') as f:
        f.write(
            '''
[DEFAULT]
# define lt file info
monomer_ltname = monomer.lt

# Due to instinctinve defect, LZ is not the real ring number.
# The relation between LZ and Zrings is :
# Zrings = 2 * LZ - 1
# BUT Xrings IS NOT BE INFLENCED.
LX = 10
LZ = 6
                '''
            )
        print('ini file not exit but we created a template.')
        print('just modify it and rerun.')

    with open('GNP_system.lt', 'w') as f:
        f.write(
            '''
# - - System - -
import "GNP-11x-6z.lt"

write_once("Data Boundary") {
  0 200.0 xlo xhi
  0 80.0 ylo yhi
  0 200.0 zlo zhi
}

sys = new Sheet
            '''
        )

    with open('GNP_forcefield.lt', 'w') as f:
        f.write(
            '''
Forcefield
{

        write_once("In Init")
        {
                units   real
                atom_style      molecular
                bond_style      morse
                angle_style     cosine/squared
                dihedral_style  multi/harmonic
                pair_style      lj/cut 10.5
        }


        write_once("Data Masses")
        {
                @atom:GP        14.02

        }

        write_once("In Settings")
        {
                bond_coeff      @bond:GP-bond      114.5   2.1867  1.4810
                angle_coeff     @angle:GP-angle        67.2     120
                dihedral_coeff  @dihedral:GP-dihedral   6.0038  0       -6.0038    0       0
                pair_coeff      @atom:GP   @atom:GP   0.1480  3.6170  9.0425
        }

        write_once("Data Bonds By Type")
        {
              @bond:GP-bond      @atom:GP      @atom:GP

        }

        write_once("Data Angles By Type")
        {
              @angle:GP-angle      @atom:GP       @atom:GP       @atom:GP       @bond:*     @bond:*
        }

        write_once("Data Dihedrals By Type")
        {
                @dihedral:GP-dihedral      @atom:GP @atom:GP @atom:GP @atom:GP  @bond:*     @bond:*  @bond:*
        }



        write_once("Data Boundary")
        {
                0       100     xlo xhi
                0       100     ylo yhi
                0       100     zlo zhi
        }
}
            '''
        )
