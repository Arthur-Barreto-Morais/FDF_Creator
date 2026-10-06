"""
Informações que devem ser modificadas no arquivo FDF:
- label_name: Label do Arquivo
- num_atoms: Número de átomos
- num_species: Número de espécies químicas

"""
import os
import shutil
import argparse as arg
import subprocess

label_name = "nome"
num_atoms = 10
num_species = 2
move_cell = "True"
dipole_correction = "True"
spin_type = "polarized"
k_point = 4

fdf_file = label_name + ".fdf"

with open(fdf_file, 'w') as f:
    f.write(f"""####################Label of System#################### 
             
SystemName {label_name}     
SystemLabel {label_name}

#######################################################

####################Input Parameters####################        

NumberOfAtoms {num_atoms}
NumberOfSpecies {num_species}

%block ChemicalSpeciesLabel     
# Atomic_Index Atomic_Number Atomic_Symbol
# Example: 1 6 C 

%endblock ChemicalSpeciesLabel

#Use only for needed species, like Li, Na, K...
#%block PAO.Polarization.Scheme
# Atomic_Symbol Polarization_Scheme
# Example: Li non-perturbative

#%endblock PAO.Polarization.Scheme
    
########################################################

####################Structural Informations####################

#Format of the atomic coordinates input: Ang (Angstroms), Fractional (Fractional coordinates)
AtomicCoordinatesFormat Ang 
#Format of the atomic coordinates output: Ang (Angstroms), Fractional (Fractional coordinates)
AtomCoorFormatOut Ang
#Atomic origin of the system.
AtomicCoordinatesOrigin 0.0 0.0 0.0

#Type of movement for the unitary cell: True (Cell can move), False (Cell is fixed)
MD.VariableCell {move_cell}

#Constrain atoms or/and cell-vectors:
%block Geometry.Constraints
# Examples
# 1- Constrain all Carbon atoms: Z 6
# 2- Constrain the cell-vector c: cell-vector c
# 3- Constrain the movement of one atom in the z-direction: atom 1 0. 0. 1.

%endblock Geometry.Constraints

#Cell vectors of the system
LatticeConstant 1.00 Ang
%block LatticeVectors

%endblock LatticeVectors

#Atomic coordinates, depends on the input format choice (Ang or Fractional)
%block AtomicCoordinatesAndAtomicSpecies
# Position_x Position_y Position_z Atomic_Index Atomic_Number Atomic_Symbol
# Example: 0.000000 0.000000 0.000000 1 10 C

%endblock AtomicCoordinatesAndAtomicSpecies

###############################################################

####################Theoretical Informations####################

#Exchange-Correlation functional
XC.Functional GGA 
#Author of the Exchange-Correlation functional
XC.Authors PBE

#Type of basis set
PAO.BasisSize DZP

#MeshCutoff intensity for the real space grid
MeshCutoff 400 Ry

#Type of dipole correction: True (Dipole correction on), False (Dipole correction off)
#Use this in case of adsorption
Slab.DipoleCorrection {dipole_correction}  

#Type of spin polarization: non-polarized, polarized, non-collinear, spin-orbit. (Read Manual for more details)
Spin {spin_type}
#Colocar o resto de spin

#Monkhorst-Pack k-point sampling
%block kgrid_Monkhorst_Pack     
#Last value related to the k point value :0.5 (odd) or 0.0 (even)
{k_point} 0 0 0.5   
0 {k_point} 0 0.5   
0 0 1 0.0   
%endblock kgrid_Monkhorst_Pack  

################################################################

####################SCF Informations####################

#SCF - Self Consistent Field

#All SCF parameters can be found in the manual, but this configuration is a good estimate for most systems.

#
SolutionMethod diagon
SCF.Mixer.Method pulay
OccupationFunction FD
ElectronicTemperature 300 K

#
MinSCFIterations 0
MaxSCFIterations 1000

#
SCF.Mixer.Weight 0.25
SCF.Mixer.History 10
SCF.Mixer.Restart 30
SCF.Mixer.Kick 100
SCF.Mixer.Kick.Weight 0.5

#
SCF.Mixer.Restart.Save 1
SCF.Mixer.Linear.After 0
SCF.Mixer.Linear.After.Weight 0.1

#
SCF.DM.Tolerance 0.000001

########################################################

####################MD Informations####################

#MD - Molecular Dynamics

#
MD.TypeOfRun

#
MD.Steps
MD.MaxDispl
MD.MaxForceTol
Target.Pressure 0 GPa

#######################################################

####################Grimmes-D3 Informations####################

DFTD3 true
DFTD3.UseXCDefaults true
DFTD3.BJdamping true

###############################################################

####################Old Output Informations####################

#
MD.UseSaveXV #false

#
DM.UseSaveDM #true

#
MD.UseSaveCG #false

#
UseSaveData #false

###############################################################

####################Write Output Informations####################

#Arrumar isso

LongOutput true
------------------------Coordenadas e Estrutura------------------------
WriteCoor.Xmol true
WriteMDXmol true
WriteCoorInitial true
WriteCoorStep true
WriteMDHistory true
Write.OrbitalIndex true
------------------------Forcas e k-points------------------------
WriteForces true
------------------------Hamiltoniano/ Matriz de densidade ------------------------
Write.DM true
Write.H false
SaveHS false
------------------------Autovalores, bandas e funcoes de onda------------------------
WriteKpoints false
WriteBands false
WriteKBandas false
WriteEigenvalues false
WriteWaveFunctions false
------------------------Populacao eletronica ------------------------
WriteMullikenPop 1
Write.HirshfeldPop true
Write.VoronoiPop false
COOP.Write false
WriteOrbMom true
#################################################################
    """)
