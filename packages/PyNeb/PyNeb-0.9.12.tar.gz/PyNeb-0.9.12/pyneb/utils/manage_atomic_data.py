import os
import pyneb as pn
import numpy as np
from misc import execution_path, parseAtom, roman_to_int, multi_split, int_to_roman
from init import ELEM_LIST, SPEC_LIST
from physics import _predefinedDataFileDict

class _ManageAtomicData(object):
    
    def __init__(self):
        self.log_ = pn.log_
        self.calling = '_ManageAtomicData'
        self._predefinedDataFileDict = _predefinedDataFileDict
        self.setDataFileDict()
        self.addDataFilePath()
        self.addDataFilePath('../atomic_data_fits/', inPyNeb=True)
        self.addDataFilePath('../atomic_data/', inPyNeb=True)
        self.addDataFilePath('./')
        self._RecombData = {}
        self.plot_path = execution_path('../plot/level_diagrams/')


    def getPredefinedDataFileDict(self, data_dict=None):
        """
        Retrieve a predefined dictionary of atomic data (either the default one [data_dict unspecified]
        or another one [identified by data_dict])
        
        Parameters:
           - data_dict    name of the dictionary 

        """
        
        if data_dict is None:
            return self._predefinedDataFileDict
        elif data_dict in self._predefinedDataFileDict:
            return self._predefinedDataFileDict[data_dict]
        else:
            self.log_.error('unknown DataFile dictionary {0}'.format(data_dict), calling=self.calling)
            return None


    def getAllPredefinedDict(self):
        """
        Return the labels of the available predefined dictionaries of atomic data

        """
        return pn.atomicData.getPredefinedDataFileDict().keys()

    
    def resetDataFileDict(self):
        """
        Reset the DataFileDict to the default value. This value is in defaultDict

        """
        self.setDataFileDict(self.defaultDict)


    def setDataFileDict(self, data_dict=None):
        """
        Use a dictionary for the atomic data (either predefined [string] or custom [dictionary]).
        
        Parameters:
           - data_dict    name of the dictionary 

        """
        if data_dict is None:
            self._DataFileDict = {}
            return None
        if type(data_dict) == type({}):
            for atom in data_dict:
                for data_type in data_dict[atom]:
                    self.setDataFile(data_dict[atom][data_type], atom, data_type)
            self.predefined = None
        elif data_dict in self.getPredefinedDataFileDict():
            self.setDataFileDict()
            self.setDataFileDict(self.getPredefinedDataFileDict(data_dict))
            self.predefined = data_dict
            self.log_.message('DataFileDict set to {0}.'.format(data_dict), calling=self.calling)
        else:
            self.log_.error('{0} is not a valid DataFileDict.'.format(data_dict), calling=self.calling)
 
            
    def addDataFilePath(self, fits_dir=None, inPyNeb=False):
        """
        Add a directory to the list of directories where atomic data files are searched for.
        
        Parameters:
           - fits_dir    directory
           - inPyNeb     Boolean.

        """
        if fits_dir is None:
            self._DataFilePaths = []
        else:
            try:
                if inPyNeb:
                    self._DataFilePaths.append(execution_path(fits_dir))
                else:
                    self._DataFilePaths.append(os.path.abspath(fits_dir))
            except:
                self.log_.warn('{0} could not be added to the path list', calling=self.calling)
 
 
    def removeDataFilePath(self, fits_dir=None):
        """
        Remove a directory from the list of directories where atomic data files are searched for.

        Parameters:
           - fits_dir    name of the directory to be removed

        """
        if fits_dir is None:
            pass
        else:
            try:
                self._DataFilePaths.remove(os.path.abspath(fits_dir))
            except:
                self.log_.warn('{0} could not be removed from the path list', calling=self.calling)
 
                
    def getAllDataFilePaths(self):
        """
        Return the list of directories where atomic data files are searched for.

        """
        return self._DataFilePaths
 
            
    def getDirForFile(self, data_file):
        """
        Return the first directory from getDataFilePaths() where a file is found.
        If nothing is found, return None.

        Parameters:
           - data_file    name of the file

        """
        for dir in self._DataFilePaths:
            if data_file in os.listdir(dir):
                return dir
        return None
 
    
    def printDirForAllFiles(self):
        """
        Print the directories where all the files defined in the dictionary of 
            atomic data files are located.

        """
        for atom in self._DataFileDict:
            atom_file = self.getDataFile(atom, 'atom', warn=False)
            if atom_file is not None:
                print('{0} atom from {1} in {2}'.format(atom, atom_file , self.getDirForFile(atom_file)))
            coll_file = self.getDataFile(atom, 'coll', warn=False)
            if coll_file is not None:
                print('{0} coll from {1} in {2}'.format(atom, coll_file , self.getDirForFile(coll_file)))
            rec_file = self.getDataFile(atom, 'rec', warn=False)
            if rec_file is not None:
                print('{0} rec from {1} in {2}'.format(atom, rec_file , self.getDirForFile(rec_file)))
 
 
    def getAllAvailableFiles(self, atom=None, data_type=None):
        """
        Scan every directory in the list of paths, printing all the *atom*.fits, *atom*.dat,
            *coll*.fits and *rec*.fits files
            
        Parameters:
           - atom        atom name
           - data_type   either 'rec', 'atom' or 'coll'

        """
        file_list = []
        if atom is not None:
            elem, spec = parseAtom(atom)
            elem = elem.lower()
            spec = int_to_roman(int(spec)).lower()
            atom_str = '{0}_{1}_'.format(elem, spec)
        else:
            atom_str = '.'
        if data_type is None:
            data_types = ['atom', 'coll', 'rec']
        else:
            data_types = [data_type]
        for dir in self._DataFilePaths:
            files = os.listdir(dir)
            for file in files:
                if (('.fits' in file) or ('.dat' in file) ) and (atom_str in file):
                    for dt in data_types:
                        if dt in file:
                            file_list.append(file)
        return file_list
    
    
    def getAllPossibleAtoms(self):
        """
        Return the list of all the possible collisional and recombination 
        atoms that can be built with the available datafiles (not all of 
        them necessarily included in the current atomic file dictionary) 
                    
        Parameters:
           - atom        atom name
           - data_type   either 'rec', 'atom' or 'coll'

        """
        atom_dict = {'atom':[], 'coll': [], 'rec': []}
        for path in self._DataFilePaths:
            files = os.listdir(path)
            for elem in ELEM_LIST:
                for spec in SPEC_LIST:
                    atom = elem + spec
                    atom_str = '{0}_{1}_'.format(elem.lower(), int_to_roman(int(spec)).lower())
                    for entry in files:
                        if (('.fits' in entry) or ('.dat' in entry) ) and (atom_str in entry):
                            if ('atom' in entry):
                                atom_dict['atom'].append(atom)
                            elif ('coll' in entry):
                                atom_dict['coll'].append(atom)
                            elif ('rec' in entry):
                                atom_dict['rec'].append(atom)
                            else:
                                pass
        coll_atom_list = list(set(atom_dict['atom']) & set(atom_dict['coll']))
        rec_atom_list = list(set(atom_dict['rec']))
        print 'Data for the following collisional atoms exist:', coll_atom_list
        print 'Data for the following recombination atoms exist:', rec_atom_list
        return [coll_atom_list, rec_atom_list] 
        
    
    def setDataFile(self, data_file=None, atom=None, data_type=None):
        """
        Associate an atomic data file to an atom and a type of data, which is one of 
            ('atom', 'coll', 'rec').

        Usage:
            pn.atomicData.setDataFile('cl_iii_atom_M83-KS86.fits')
            pn.atomicData.setDataFile('TEST.fits', 'O3', 'atom') # but the previous way 
                to name the files is preferred

        Parameters:
            - data_file    atomic data file. 
            - [atom]         selected atom
            - [data_type]    'atom', 'coll', 'rec'
            If atom and data_type not set, file format is assumed to be e.g. o_iii_coll_REF.fits

        """          
        if atom is None:
            strs = data_file.split('_')
            elem = strs[0].capitalize()
            spec = roman_to_int(strs[1])
            atom = elem + str(spec)
        else:
            elem, spec = parseAtom(atom)
        if data_type is None:
            strs = data_file.split('_')
            data_type = strs[2]
        if data_type not in ('atom', 'coll', 'rec'):
            self.log_.error('{0} is not a valid type'.format(data_type))
            return None
        if elem not in ELEM_LIST:
            self.log_.error('{0} is not a valid element'.format(elem))
            return None
        if atom not in self._DataFileDict:
            self._DataFileDict[atom] = {}
        if self.getDirForFile(data_file) is not None:
            self._DataFileDict[atom][data_type] = data_file
            # as something changed, predefined is not valid anymore
            self.predefined = None
            if data_type == 'rec':
                if atom in self._RecombData:
                    del self._RecombData[atom]
            self.log_.message('Adding {0} {1} data for {2}'.format(data_file, data_type, atom), calling=self.calling)
        else:
            self.log_.warn('File path of {0} not included in list. Run addDataFilePath first'.format(data_file),
                           calling=self.calling)
        if (atom == 'H1') and ('H1' in pn.atomicData._RecombData):
            del pn.atomicData._RecombData['H1']


    def getAllAtoms(self, coll=True, rec=False):
        """
        Return a list of all the atoms (e.g. 'O3') included in the adopted dictionary 
        and for which dataFiles are available (a subset of all the ions returned by
        the getAllPossibleIons() command)

        Parameters:
            - coll     if True (default) includes the Atom objects
            - rec     if True (not the default) includes the RecAtoms

        """
        to_return = []
        for atom in self._DataFileDict:
            if coll and ('atom' in self._DataFileDict[atom]):
                to_return.append(atom)
            if rec and ('rec' in self._DataFileDict[atom]):
                to_return.append(atom)
        return to_return
            

    def getDataFile(self, atom=None, data_type=None, warn=True):
        """
        Return the name of the atomic data file associated to an atom and a type of data, 
        which is one of ('atom', 'coll', 'rec').
            
        Parameters:
            - atom        selected atom
            - data_type   type of atomic data ('atom', 'coll', 'rec')
            - warn        warn if no associated data file is found
        
        """
        if atom is None:
            if data_type is None:
                return self._DataFileDict
            else:
                DFD = self._DataFileDict
                to_return = {}
                for at in DFD:
                    if data_type in DFD[at]:
                        to_return[at] = DFD[at][data_type]
                return to_return
        if data_type is None:
            return(self.getDataFile(atom, 'atom', warn=warn),
                   self.getDataFile(atom, 'coll', warn=warn),
                   self.getDataFile(atom, 'rec', warn=warn))
        if data_type not in ('atom', 'coll', 'rec'):
            if warn:
                self.log_.warn('{0} type unknown'.format(data_type), calling=self.calling)
            return None
        if atom not in self._DataFileDict:
            if warn:
                self.log_.warn('data for {0} not available'.format(atom), calling=self.calling)
            return None
        if data_type in self._DataFileDict[atom]:
            return self._DataFileDict[atom][data_type]
        else:
            if warn:
                self.log_.warn('{0} data not available for {1}'.format(data_type, atom), calling=self.calling)
            return None

        
    def getDataFullPath(self, atom, data_type=None, warn=True):
        """
        Return the full path of the atomic data file associated to an atom and a type of data, 
        which is one of ('atom', 'coll', 'rec').
        
        Parameters:
            - atom        selected atom
            - data_type   type of atomic data ('atom', 'coll', 'rec')
            - warn        warn if no associated data file is found
        
        """
        data_file = self.getDataFile(atom, data_type=data_type, warn=warn)
        data_path = self.getDirForFile(data_file)
        if data_file is None:
            return None
        else:
            return '{0}/{1}'.format(data_path, data_file)


    def scanDirForDataFiles(self, fits_dir):
        """
        Scan a directory and associate any file named x_i_type_ref.fits to the atom Xi (i in roman), 
        type being one of ('atom', 'coll', 'rec').
        The directory must have been registered before using addDataFilePath(fits_dir)

        Parameters:
            - fits_dir        directory name

        """
        for file_ in os.listdir(fits_dir):
            names = multi_split(file_, ['_', '.'])
            elem = names[0].title()            
            if elem in ELEM_LIST:
                spec = str(roman_to_int(names[1]))
                if spec in SPEC_LIST:
                    atom = elem + spec
                    if atom not in self._DataFileDict:
                        self._DataFileDict[atom] = {}
                    if names[2] in ('atom', 'coll', 'rec'):
                        self.setDataFile(atom, names[2], file_)
 
 
    def printAllSources(self, at_set=None, predef=None):
        """
        Print bibliographic sources for atomic data of a set of atoms.
        
        Usage:
        pn.atomicData.printAllSources(['O3', 'Ar4', 'S2'])
        pn.atomicData.printAllSources()

        Parameters: 
            - at_set   a list or tuple containing the atoms. If not set, 
                       print bibliographic sources for all the atoms in PyNeb's default dictionary
                       
        """        
        self.calling = 'printAllSources'
        if (type(at_set) == list) or (type(at_set) == tuple):
            at_dict = {}
            for item in at_set:
                at_dict[item] = pn.Atom(pn.utils.misc.parseAtom(item)[0], pn.utils.misc.parseAtom(item)[1])
        elif at_set is not None:
            pn.log_.error('The argument at_set must be a list or a tuple', calling=self.calling)
            return None
        elif (at_set is None) and (predef is None):
            at_dict = pn.getAtomDict()
        elif predef in pn.atomicData.getAllPredefinedDict():
            current = pn.atomicData.predefined
            pn.atomicData.setDataFileDict(predef)
            at_dict = pn.getAtomDict()
            pn.atomicData.setDataFileDict(current)
        else: 
            pn.log_.error('The argument predef must be the label of a predefined dictionary', calling=self.calling)
        
        for item in sorted(at_dict):                                                              
            at_dict[item].printSources()
    
    
    def printPoem(self, yr=0):
        """
        Print one of Wiese et al. spectroscopic poems
        
        Parameters:
            - yr     publication year. If no valid year is given, random print
 
        """
        if (yr == 96):
            print "********************************************"
            print ""
            print "We have used a near limitless data source,"
            print "It is the Opacity Project, of course."
            print "Its results are certainly fine"
            print "For most any LS-coupled line."        
            print ""
            print "            (Wiese, Fuhr & Deters 1996)"
            print ""
            print "********************************************"
        elif (yr == 66):
            print "********************************************"
            print ""
            print "If there is no other data source"
            print "Use the Coulomb approximation, of course."    
            print "The results should be certainly fine"
            print "For any moderately or highly excited line."
            print ""
            print "            (Wiese, Smith & Glennon 1966)" 
            print ""
            print "********************************************"
        else:
            rnd = np.random.rand()
            if (rnd < 0.5):
                self.printPoem(yr=66)
            else:
                self.printPoem(yr=96)
    
