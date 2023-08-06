import re
import gzip
import os
import numpy as np
import pyneb as pn
from pyneb.utils.misc import int_to_roman 
from pyneb.utils.physics import sym2name, vacuum_to_air

def conv_apap(str_in):
    """
    transform "1.3-01" into 1.3e-01 
    """
    a, b = re.split('\+|-',str_in)
    if '-' in str_in:
        return float(a) / 10**float(b)
    else:
        return float(a) * 10**float(b)

def apap2ascii(apap_file, max_levels=10):
    
    if max_levels is None:
        max_levels = np.Inf
        
    energy = []
    XJ = []
    if apap_file.split('.')[-1] == 'gz':
        f = gzip.open(apap_file)
    else:
        f = open(apap_file)
    foo = f.readline()
    while True:
        line = f.readline()
        if line[0:5] == "   -1":
            break
        lev = int(line[0:5])
        if lev <= max_levels:
            XJ.append(line[29:33])
            energy.append(line[34::])

    N_levels = len(energy)
    
    lev_i = []
    lev_j = []
    As = []
    Omegas = []
    
    temps_str = f.readline().split()[2::]
    temp_array = np.array([conv_apap(temp) for temp in temps_str])
    N_temp = len(temp_array)
    while True:
        line = f.readline()
        if line[0:4] == "  -1":
            break
        i = int(line[1:4])
        j = int(line[4:8])
        if (i <= max_levels) and (j <= max_levels):
            lev_i.append(i)
            lev_j.append(j)
            strg5 = line[8:8+(N_temp+1)*8].split()
            As.append(conv_apap(strg5[0]))
            Omegas.append([conv_apap(omega) for omega in strg5[1::]])
    f.close()
    
    lev_i = np.array(lev_i, dtype='int')
    lev_j = np.array(lev_j, dtype='int')        
    energy = np.array(energy, dtype='float') / 1e8 # cm-1 to A-1
#    tt = energy > 0
#    energy[tt] = 1./vacuum_to_air(1./energy[tt])    
    stat_weight = np.array(XJ, dtype='float') * 2 + 1
    As = np.array(As, dtype='float')
    Omegas = np.array(Omegas, dtype='float')

    A2d = np.zeros((N_levels, N_levels))
    for i, j, A in zip(lev_i, lev_j, As):
        A2d[i-1, j-1] = A
    Omega3d = np.zeros((N_levels, N_levels, N_temp))
    for i, j, Omega in zip(lev_i, lev_j, Omegas):
        Omega3d[i-1, j-1] = Omega
    
    atom = apap_file.split('#')[1].split('.')[0]
    spectrum = int(re.findall(r'\d+', atom)[0]) + 1
    ioniz = int_to_roman(spectrum).lower()
    elem = re.findall('[a-zA-Z]+', atom)[0]
    
    f_atom = open('{0}_{1}_atom_APAP14.dat'.format(elem, ioniz),'w')
    f_atom.write('Energy Stat_Weight Aij\n')
    str_ = '1/Ang         none'
    for i in np.arange(N_temp):
        str_ += '     1/s '
    str_ += '\n' 
    f_atom.write(str_)
    for i in np.arange(N_levels):
        str_ = '{0:.12f} {1:3d}'.format(energy[i], int(stat_weight[i]))
        str_ += ''.join(' {0:10.8e}'.format(A) for A in A2d[i])
        str_ += '\n'
        f_atom.write(str_)
    try:
        f_atom.write("*** ATOM {0}\n".format(sym2name[elem.capitalize]))
    except:
        pass
                     
    f_atom.write("""*** SPECTRUM {0}
*** N_LEVELS {1}
*** NOTE1 'Energy levels, As and Stats Weights'
*** SOURCE1 'http://www.apap-network.org/'
*** EUNIT 'VACUUM'
""".format(spectrum, N_levels))
    
        
    f_atom.close()
    
    f_coll = open('{0}_{1}_coll_APAP14.dat'.format(elem, ioniz),'w')
    
    str_ = '0   0 '
    str_ += ''.join(' {0:10.4e}'.format(T) for T in temp_array)
    str_ += '\n'
    f_coll.write(str_)
    for i in 1+np.arange(N_levels):
        for j in i+1+np.arange(N_levels-i):
            str_ = '{0} {1} '.format(i, j)
            str_ += ''.join(' {0:10.8e}'.format(O) for O in Omega3d[j-1, i-1])
            str_ += '\n'
            f_coll.write(str_)
    try:
        f_coll.write("*** ATOM {0}\n".format(sym2name[elem.capitalize()]))
    except:
        pn.log_.warn('No full name for element {0}'.format(elem.capitalize()))

    f_coll.write("""*** SPECTRUM {0}
*** N_LEVELS {1}
*** T_UNIT 'K'
*** NOTE1 'Collision strengths'
*** SOURCE1 'http://www.apap-network.org/'
""".format(spectrum, N_levels))
    
    f_coll.close()


def make_all(dir_ = '.', max_levels=8):
    file_liste = os.listdir('.')
    for file_ in file_liste:
        if file_[-1] == 'z':
            atom = file_.split('#')[1].split('.')[0]
            if atom == 'fe':
                apap2ascii(file_, 34)
            else:
                apap2ascii(file_, max_levels)
            print('{0} done'.format(file_))