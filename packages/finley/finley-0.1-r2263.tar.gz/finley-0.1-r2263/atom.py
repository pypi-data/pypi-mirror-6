# system modules
import math
import random
import types

# custom modules
import moremath

class atom: #isdoc #doc-contains: _comment, _idx, _atom_type, _label, _residue, _residue_id, _segment_name, _constrained, _charge, _mass, _psf_number, _pos, _charmm_idx
    def __str__(self): #isdoc
        prefix = 'atom' if self.get_name() is None else self.get_name()
        if self._pos is None:
            positions = '[no positions]'
        else:
            positions = '[x = {0:10f} y = {1:10f} z = {2:10f}]'.format(self._pos[0], self._pos[1], self._pos[2])
        return prefix + positions

    def __repr__(self): #isdoc
        return self.__str__()

    def __init__(self, box=None, label=None, idx=None): #isdoc
        if box is None:
            self._pos = None
        else:
            self.set_positions_by_box(self, box)
        self.set_label(label)
        self.set_name(idx)
        self.set_atom_type(None)
        self.set_comment(None)
        self._psf_number = None
        self._mass = None
        self._charge = None
        self._constrained = False
        self._segment_name = None
        self._residue_id = None
        self._charmm_idx = None

    def __sub__(self, other): #isdoc
        if self._pos is None:
            raise ValueError('No position specified.')
        if other._pos is None:
            raise ValueError('No position specified.')
        return math.sqrt(sum([(self._pos[i]-other._pos[i])**2 for i in range(3)]))

    def __add__(self, other): #isdoc
        if self._pos is None:
            raise TypeError('No position specified.')
        if type(other) == list:
            if len(other) == 3:
                self._pos = [sum(x) for x in zip(self._pos, other)]
            else:
                raise ArithmeticError('Unable to add different vectors of different lengths (lhs=%d, rhs=%d)' % (len(self._pos), len(other)))
        else:
            raise NotImplementedError()
        return self

    def __radd__(self, other): #isdoc
        return self + other

    def __deepcopy__(self, memo): #isdoc
        c = atom()
        c._pos = self._pos
        c._residue = self._residue
        c._label = self._label
        c._atom_type = self._atom_type
        c._idx = self._idx
        c._comment = self._comment
        c._psf_number = self._psf_number
        c._mass = self._mass
        c._charge = self._charge
        c._constrained = self._constrained
        c._segment_name = self._segment_name
        c._residue_id = self._residue_id
        c._charmm_idx = self._charmm_idx

        return c

    def set_residue(self, residue): #isdoc
        self._residue = residue
        return self

    def get_residue(self): #isdoc
        return self._residue

    def set_positions_by_box(self, box): #isdoc
        self._pos = [random.random()*box for i in range(3)]
        return self

    def set_positions(self, x, y=None, z=None): #isdoc
        # TODO: type checks
        if y is None and z is None and len(x) == 3:
            self._pos = list(x)
        else:
            self._pos = [x, y, z]
        return self

    def get_positions(self): #isdoc
        return self._pos

    def set_label(self, label): #isdoc
        if not type(label) in (str, types.NoneType):
            raise TypeError('Expected string or None as label, got %s.' % label)
        self._label = label
        return self

    def get_label(self): #isdoc
        return self._label

    def set_atom_type(self, atom_type): #isdoc
        if not type(atom_type) in (str, types.NoneType):
            raise TypeError('Expected string or None as atom type, got %s.' % atom_type)
        self._atom_type = str(atom_type)
        return self

    def get_atom_type(self): #isdoc
        return self._atom_type

    def set_name(self, idx): #isdoc
        self._idx = idx
        return self

    def get_name(self): #isdoc
        return self._idx

    def get_vector_to(self, other): #isdoc
        try:
            return map(lambda x: x[1]-x[0], zip(self._pos, other._pos))
        except:
            raise ValueError('No positional data defined.')

    def lj(self, other): #isdoc
        r = (self-other)**2
        if r < 0.1:
            return 1e6
        r = 1/r
        r *= r*r
        return (r*r-2*r)

    def set_comment(self, c): #isdoc
        if not type(c) in (str, types.NoneType):
            raise TypeError('Expected string or None as comment, got %s.' % c)
        self._comment = c
        return self

    def get_comment(self):  #isdoc
        return self._comment

    def translate(self, v): #isdoc
        self._pos = map(lambda x: sum(x), zip(self._pos, v))
        return self

    def rotate(self, n, angle): #isdoc
        self._pos = moremath.rotate_vector(self._pos, n, angle)
        return self

    def get_psf_number(self): #isdoc
        return self._psf_number

    def set_psf_number(self, n): #isdoc
        self._psf_number = int(n)
        return self

    def set_mass(self, n): #isdoc
        self._mass = n
        return self

    def get_mass(self): #isdoc
        return self._mass

    def set_charge(self, n): #isdoc
        self._charge = n
        return self

    def get_charge(self): #isdoc
        return self._charge

    def set_constrained(self, val): #isdoc
        self._constrained = bool(val)
        return self

    def is_constrained(self): #isdoc
        return self._constrained

    def set_segment_name(self, s): #isdoc
        self._segment_name = s
        return self

    def get_segment_name(self): #isdoc
        return self._segment_name

    def set_residue_id(self, i): #isdoc
        self._residue_id = int(i)
        return self

    def get_residue_id(self): #isdoc
        return self._residue_id

    def compatible_to(self, other): #isdoc
        if not isinstance(other, atom):
            return False

        checks = [atom.get_name, atom.get_residue, atom.get_segment_name]
        for check in checks:
            if not check(self) == check(other):
                return False
        return True

    def set_charmm_idx(self, idx): #isdoc
        self._charmm_idx = idx
        return self

    def get_charmm_idx(self): #isdoc
        return self._charmm_idx
        
elements = {
    1.008000: 'H', 
    12.011000: 'C', 
    14.007000: 'N', 
    15.999400: 'O', 
    15.999000: 'O', 
    30.974000: 'P',
    32.060000: 'S',
    18.998403: 'F'
    }

order_of_elements = 'H,He,Li,Be,B,C,N,O,F,Ne,Na,Mg,Al,Si,P,S,Cl,Ar,K,Ca,Sc,Ti,V,Cr,Mn,Fe,Co,Ni,Cu,Zn,Ga,Ge,As,Se,Br,Kr,Rb,Sr,Y,Zr,Nb,Mo,Tc,Ru,Rh,Pd,Ag,Cd,In,Sn,Sb,Te,I,Xe,Cs,Ba,La,Ce,Pr,Nd,Pm,Sm,Eu,Gd,Tb,Dy,Ho,Er,Tm,Yb,Lu,Hf,Ta,W,Re,Os,Ir,Pt,Au,Hg,Tl,Pb,Bi,Po,At,Rn,Fr,Ra,Ac,Th,Pa,U,Np,Pu,Am,Cm,Bk,Cf,Es,Fm,Md,No,Lr,Rf,Db,Sg,Bh,Hs,Mt,Ds,Rg,Cn,Uut,Fl,Uup,Lv,Uus,Uuo'.split(',')

def element_from_ordinal(no):
    try:
        no = int(no)
    except:
        raise TypeError('Ordinal not convertible to int.')
    
    if no < 1:
        raise ValueError('No such element.')
    if no > len(order_of_elements):
        raise ValueError('Unknown element.')

    return order_of_elements[no - 1]

def from_charmm_mass_definition(line): #isdoc
    try:
        parts = str(line).split()
    except:
        raise TypeError('Parameter not convertible to a string.')
    if len(parts) < 4:
        raise ValueError('Unable to parse line.')
    if parts[0] != 'MASS':
        raise ValueError('Line is no MASS definition.')

    try:
        mass = float(parts[3])
        label = elements[mass]
        idx = int(parts[1])
    except:
        raise ValueError('Unable to detect element label for mass %s' % parts[3])

    a = atom()
    a.set_atom_type(parts[2])
    a.set_label(label)
    a.set_mass(mass)
    a.set_charmm_idx(idx)
    comment = ' '.join(parts[4:]).strip()
    if len(comment) > 0:
        if not comment.startswith('!'):
            raise ValueError('Unable to parse what is supposed to be a comment.')
        comment = comment[1:]
    else:
        comment = ''
    a.set_comment(comment)

    return a

def from_pdb_line(line): #isdoc
    #ATOM     11  F3  LIG M   1       2.758   2.773   0.275  0.00  0.00      MOL  F

    if not line.startswith('ATOM') and not line.startswith('HETATM'):
        raise ValueError('Non-Atom line given.')

    try:
        label = line[76:78].strip()
    #    1/len(label)
    except:
        raise ValueError('Missing atom label.')

    try:
        residue = line[17:20].strip()
        1/len(residue)
    except:
        raise ValueError('Missing residue name.')

    c = atom(label=label)
    c.set_residue(residue)
    try:
        x = float(line[30:38])
        y = float(line[38:46])
        z = float(line[46:54])
    except:
        raise ValueError('Unable to convert atom coordinates.')

    c.set_positions(x, y, z)
    c.set_segment_name(line[72:76].strip())
    try:
        c.set_name(line[12:16].strip())
    except:
        raise ValueError('Unable to extract atom name.')

    return c

def from_psf_line(line): #isdoc
    #1 MOL      1        LIG      C1       CC33A  -0.270000       12.0107           0
    parts = line.strip().split()
    c = atom()
    c.set_residue(parts[3])
    c.set_name(parts[4])
    c.set_mass(float(parts[7]))
    c.set_charge(float(parts[6]))
    c.set_constrained(float(parts[8]))
    c.set_psf_number(int(parts[0]))
    c.set_segment_name(parts[1])
    c.set_residue_id(int(parts[2]))
    c.set_atom_type(parts[5])

    return c