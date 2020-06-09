# Version: 3.0
# Data : 2019/03/21
# License : GPL
# USAGE: python3 polymer-generator.py



def backbone_generator():

    import configparser

    import os.path
    if not os.path.exists('polymer_init.ini'):
        raise IOError('sorry, you should generate init template first, by "polymer_generator.generate_lt()"')

    config = configparser.ConfigParser()
    config.read('polymer_init.ini')




    # define BOX properties
    box_x = int(config['DEFAULT']['box_x'])
    # box_y = int(config['DEFAULT']['box_y'])
    # box_z = int(config['DEFAULT']['box_z'])
    cell_x = 0
    cell_y = 0
    cell_z = 0

    # define CHAIN properties
    c_chain_length = int(config['BACKBONE']['c_chain_length'])
    c_bond_length = float(config['BACKBONE']['c_bond_length'])
    c_atom = config['BACKBONE']['c_atom']
    c_ID = config['BACKBONE']['c_ID']
    c_vector = c_bond_length * 0.707

    if config['BACKBONE']['isBranch'] == 'yes':

        # define branch properties
        b_chain_length = int(config['BRANCH']['b_chain_length'])
        b_bond_length = float(config['BRANCH']['b_bond_length'])
        b_point = list(map(int, config['BRANCH']['b_point'].split(',')))
        b_vector = b_bond_length * 0.707


        b_atom = config['BRANCH']['b_atom']
        b_ID = config['BRANCH']['b_ID']

    else:
        b_chain_length = 0
        b_point = []


    # define symbol
    right_curly_brace = '}'
    left_curly_brace = '{'

    # define lt file info
    if config['DEFAULT']['simple_name'] == 'yes':
        polymer_ltname = 'polymer.lt'
        Molecule_class = 'Polymer'
    else:
        polymer_ltname = f'polymer-{c_chain_length}-{b_chain_length}_{len(b_point)}.lt'
        Molecule_class = f'Polymer-{c_chain_length}-{b_chain_length}_{len(b_point)}'


    monomer_ltname = config['DEFAULT']['monomer_ltname']

    # counter of main chain
    c_index = 1
    b_index = 1

    # chain state, go along with x+ or x-
    mode = 'go'

    # cursor
    x_cursor = 0
    y_cursor = 0
    z_cursor = 0

    f = open(polymer_ltname, 'w')

    def branch_generator():

        nonlocal b_index, cell_x, cell_y, cell_z, b_chain_length
        b_v = b_vector
        x = x_cursor
        y = y_cursor
        z = z_cursor
        m = mode


        b = 1
        while b <= b_chain_length:
            if x >= 0 and x <= box_x:
                f.write(f'\tbra{b_index} = new {b_atom}.move({x}, {y:.2f}, {z:.2f})\n')
                b_index += 1
                b+=1
                if m == 'go':
                    x += b_v
                elif m == 'back':
                    x -= b_v
                if b_index % 2 == 0:
                    y += b_v
                else :
                    y -= b_v

            else:
                if m == 'go':
                    x -= b_v
                    m = 'back'
                elif m == 'back':
                    x += b_v
                    m = 'go'
                if b_index % 2 == 0:
                    y -= b_v
                else :
                    y += b_v

                # high position
                if b_index % 2 == 1:
                    if m == 'go':
                        x += b_v
                        y += b_v
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x += b_v
                        y += b_v

                    else:
                        x -= b_v
                        y += b_v
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x:.2f}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x -= b_v
                        y += b_v


                # low position
                else:
                    if m == 'back':
                        x += b_v
                        y += b_v
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x:.2f}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x -= b_v
                        y += b_v
                        if b > b_chain_length:
                            break
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x:.2f}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x -= b_v
                        y += b_v
                    else:
                        x -= b_v
                        y += b_v
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x:.2f}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x += b_v
                        y += b_v
                        if b > b_chain_length:
                            break
                        f.write(f'\tbra{b_index} = new {b_atom}.move({x:.2f}, {y:.2f}, {z:.2f})\n')
                        b_index += 1
                        b+=1
                        x += b_v
                        y += b_v



            cell_x = max(x, cell_x)
            cell_y = max(y, cell_y)
            cell_z = max(z, cell_z)


    f.write(f'import "{monomer_ltname}"\n')
    f.write(f'{Molecule_class} {left_curly_brace}\n\n')
    f.write(f'\n')
    f.write(f'\n')
    f.write(f'\tcreate_var {left_curly_brace}$mol{right_curly_brace}\n\n\n')

    while c_index <= c_chain_length:
        if x_cursor >= 0 and x_cursor <= box_x and c_index not in b_point:
            f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
            c_index += 1
            if mode == 'go':
                x_cursor += c_vector
            elif mode == 'back':
                x_cursor -= c_vector
            if c_index % 2 == 0:
                z_cursor += c_vector
            else :
                z_cursor -= c_vector

        else:

            if c_index in b_point:
                branch_generator()


            if mode == 'go':
                x_cursor -= c_vector
                mode = 'back'
            elif mode == 'back':
                x_cursor += c_vector
                mode = 'go'
            if c_index % 2 == 0:
                z_cursor -= c_vector
            else :
                z_cursor += c_vector

            # high position
            if c_index % 2 == 1:
                if mode == 'go':
                    x_cursor += c_vector
                    z_cursor += c_vector
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor += c_vector
                    z_cursor += c_vector
                else:
                    x_cursor -= c_vector
                    z_cursor += c_vector
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor -= c_vector
                    z_cursor += c_vector


            # low position
            else:
                if mode == 'back':
                    x_cursor += c_vector
                    z_cursor += c_vector
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor -= c_vector
                    z_cursor += c_vector
                    if c_index > c_chain_length:
                        break
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor -= c_vector
                    z_cursor += c_vector
                else:
                    x_cursor -= c_vector
                    z_cursor += c_vector
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor += c_vector
                    z_cursor += c_vector
                    if c_index > c_chain_length:
                        break
                    f.write(f'\tbone{c_index} = new {c_atom}.move({x_cursor:.2f}, {y_cursor:.2f}, {z_cursor:.2f})\n')
                    c_index += 1
                    x_cursor += c_vector
                    z_cursor += c_vector


        cell_x = max(x_cursor, cell_x)
        cell_y = max(y_cursor, cell_y)
        cell_z = max(z_cursor, cell_z)



    # --- topo ----
    c_index = 1
    f.write(f'\n\nwrite("Data Bond List") {left_curly_brace}\n\n')
    while c_index < c_chain_length:
        f.write(
            f'\t$bond:backbone{c_index}\t$atom:bone{c_index}/{c_ID}\t$atom:bone{c_index+1}/{c_ID}\n')
        c_index += 1

    # construct branch topo
    b_index = 1
    for _, bone in enumerate(b_point, 1):

        f.write(
            f'\t$bond:joint{_}\t$atom:bone{bone}/{c_ID}\t$atom:bra{b_index}/{b_ID}\n')

        while b_index < b_chain_length*_:
            f.write(
                f'\t$bond:brabone{b_index}\t$atom:bra{b_index}/{b_ID}\t$atom:bra{b_index+1}/{b_ID}\n')
            b_index += 1
    ##########################

        b_index += 1

    ##
    f.write(f'\t\n{right_curly_brace}')
    f.write(f'\n{right_curly_brace}')
    f.close()

    print(f'Summary:\n')
    print(f'File name: {polymer_ltname}\n')
    print(f'Molecule name: {Molecule_class}\n')
    print(f'\tmain chain length: {c_chain_length}\n')
    print(f'\tbranch chain length: {b_chain_length}\n')
    print(f'\tbranch chain number: {len(b_point)}\n')
    print(f'cell scale(appr.): ({cell_x:.2f}, {cell_y:.2f}, {cell_z:.3f})')



def run():
    backbone_generator()

def generate_lt():

    with open('polymer_init.ini', 'w') as f:
        f.write(
                '''
[DEFAULT]
# if simple_name is specified, build file name as "polymer.lt" and molecule class name is "Polymer"
# or by the default rule:"polymer-${backbone_length}-${branch_length}_${branch_numbers}"
simple_name = yes

# define lt file info
monomer_ltname = monomer.lt

# define BOX properties
box_x = 200
box_y = 20
box_z = 20

[BACKBONE]
# define CHAIN properties
c_chain_length = 1000
c_bond_length = 1.53
c_atom = Monomer
C_ID = C

isBranch = no
[BRANCH]
# define branch properties
b_chain_length = 1000
b_bond_length = 1.53
b_point = 501, 1502, 2503, 3504, 4505
b_atom = Branch
b_ID = B



                '''
            )


    with open('system.lt','w') as f:
        f.write(
            '''
import "polymer.lt"



# Specify the periodic boundary conditions:

write_once("Data Boundary") {
  0 702 xlo xhi
  0 10 ylo yhi
  0 20 zlo zhi
}


s2 = new Polymer[5].move(0, 2, 0)






# ------------ Optional: ------------
# Now (for fun) shift some of the polymers
# in the x direction by a distance of 20.0
# Suppose we want to move the middle slice
# (which has constant Z).  We do that this way:
# polymers[1][*][*].move(20,0,0)
# more examples:
# polymers[*][1][*].move(0,0,20)
# polymers[*][*][1].move(0,20,0)
            '''
        )
    with open('monomer.lt','w') as f:
        f.write(
            '''
import "forcefield.lt"

Monomer inherits ForceField{

write("Data Atoms"){
    $atom:C     $mol:...    @atom:C     0.0     0.0000     0.0000   0.0000
}

}

Branch inherits ForceField{

    write("Data Atoms"){
        $atom:B     $mol:...    @atom:B     0   0   0   0
    }
}
            '''
        )
    with open('forcefield.lt','w') as f:
        f.write(
            '''

ForceField {


  write_once("In Init") {

    units           real
    atom_style      full
    bond_style      harmonic
    angle_style     harmonic
    dihedral_style  multi/harmonic
    pair_style      lj/cut 10.5
    boundary        p p p
  }

  write_once("Data Masses") {
    @atom:C     14.2
    @atom:B     14.2
  }


  write_once("In Settings") {

    pair_coeff    @atom:C  @atom:C       0.112    4.01    10.5
    pair_coeff    @atom:B  @atom:C       0.112    4.01    10.5
    pair_coeff    @atom:B  @atom:B       0.112    4.01    10.5

  }



  write_once("In Settings") {

    bond_coeff  @bond:backbone   350    1.53
    bond_coeff  @bond:brabone    350    1.53
    bond_coeff  @bond:joint      350    1.53
  }



  write_once("In Settings") {

    angle_coeff @angle:CCC   60    109.5
    angle_coeff @angle:CCB   60    109.5
    angle_coeff @angle:CBB   60    109.5
    angle_coeff @angle:BBB   60    109.5
  }

  write_once("In Settings") {
    dihedral_coeff @dihedral:CCCC   1.73    -4.49    0.776    6.99    0.0
    dihedral_coeff @dihedral:CCCB   1.73    -4.49    0.776    6.99    0.0
    dihedral_coeff @dihedral:CCBB   1.73    -4.49    0.776    6.99    0.0
    dihedral_coeff @dihedral:CBBB   1.73    -4.49    0.776    6.99    0.0
    dihedral_coeff @dihedral:BBBB   1.73    -4.49    0.776    6.99    0.0
  }

  ##############################################################
  ############-----AUTO BUILD------#############################
  ##############################################################

  # ---- 3-body angle (hinge) interactions: ----

  write_once("Data Bonds By Type"){

    @bond:backbone    @atom:C       @atom:C
    @bond:backbone    @atom:C       @atom:B
    @bond:backbone    @atom:B       @atom:B
  }

  # ---- 3-body angle (hinge) interactions: ----

  write_once("Data Angles By Type") {

    @angle:CCC  @atom:C   @atom:C   @atom:C    @bond:*   @bond:*
    @angle:CCB  @atom:C   @atom:C   @atom:B    @bond:*   @bond:*
    @angle:CBB  @atom:C   @atom:B   @atom:B    @bond:*   @bond:*
    @angle:BBB  @atom:B   @atom:B   @atom:B    @bond:*   @bond:*
  }


  # ---- 4-body dihedral interactions ----


  write_once("Data Dihedrals By Type") {
    # dihedralType atmType1 atmType2 atmType3 atmType4 bondType1 bType2 bType3
    @dihedral:CCCC @atom:C  @atom:C  @atom:C  @atom:C   @bond:* @bond:* @bond:*
    @dihedral:CCCB @atom:C  @atom:C  @atom:C  @atom:B   @bond:* @bond:* @bond:*
    @dihedral:CCBB @atom:C  @atom:C  @atom:B  @atom:B   @bond:* @bond:* @bond:*
    @dihedral:CBBB @atom:C  @atom:B  @atom:B  @atom:B   @bond:* @bond:* @bond:*
    @dihedral:BBBB @atom:B  @atom:B  @atom:B  @atom:B   @bond:* @bond:* @bond:*
  }




} # "ForceField"


            '''
        )
        
        print('successfully generate init template!')
