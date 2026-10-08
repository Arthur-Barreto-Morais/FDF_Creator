"""
Informações que devem ser modificadas no arquivo FDF:
- label_name: Label do Arquivo
- num_atoms: Número de átomos
- num_species: Número de espécies químicas

"""
import os
import shutil
import argparse as arg
import periodictable
import subprocess

parser = arg.ArgumentParser()
parser.add_argument("-l", dest = "label", type = str, required = True)
parser.add_argument("-t", dest = "type", type = str, required = False, choices = ["opt","bands","phonons","dynamic"])
parser.add_argument("-n", dest = "num_atoms", type = int, required = False)
parser.add_argument("-el", dest = "elements", nargs ="+", required = False)
parser.add_argument("-Fin", dest = "Fin", type = str, required = False, default = "Ang", choices = ["Ang", "Fractional"])
parser.add_argument("-Fout", dest = "Fout", type = str, required = False, default = "Ang", choices = ["Ang", "Fractional"])
parser.add_argument("-cm", dest = "cell_move", type = str, required = False, default = "True", choices = ["True", "False"])
parser.add_argument("-bs", dest = "basis_size", type = str, required = False, default = "DZP")
parser.add_argument("-mesh", dest = "mesh_cutoff", type = float, required = False, default = 400.0)
parser.add_argument("-dc", dest = "dipole_correction", required = False, action = "store_true")
parser.add_argument("-s", dest = "spin_type", type = str, required = False, default = "non-polarized", choices = ["non-polarized", "polarized"])
parser.add_argument("-k", dest = "k_point", type = int, required = True)
parser.add_argument("-scf", dest = "scf_crit", type = float, required = False, default = 0.000001)
parser.add_argument("-run", dest = "run_type", type = str, required = False, default = "CG", choices = ["CG", "Broyden", "FIRE", "Verlet", "Nose", "FC"])
parser.add_argument("-steps", dest = "steps", type = int, required = False, default = 500)
parser.add_argument("-md", dest = "md_crit", type = float, required = False, default = 0.01)
parser.add_argument("-d3", dest = "Grimme_D3", required = False, action = "store_true")
parser.add_argument("-no_sv", dest = "save_dm", required = False, action = "store_false")
parser.add_argument
parser.add_argument
parser.add_argument
parser.add_argument


args = parser.parse_args()

label_name = args.label
fdf_file = label_name + ".fdf"

with open(fdf_file, 'w') as f:
    f.write(f"""####################Label of System#################### 
             
SystemName {label_name}     
SystemLabel {label_name}

#######################################################"""+"\n"+"\n")

    num_atoms = args.num_atoms if args.num_atoms is not None else "num_atoms"

    if args.elements is not None:
        elements = args.elements
        num_species = len(elements)
        species = "" 
        for i,element in enumerate(elements):
            species += f" {i+1} {periodictable.elements.symbol(element).number} {element}\n"
    else:
        num_species = "num_species"
        species = "\n"

    f.write(f"""####################Input Parameters####################        

NumberOfAtoms {num_atoms}
NumberOfSpecies {num_species}

%block ChemicalSpeciesLabel     
# Atomic_Index Atomic_Number Atomic_Symbol
# Example: 1 6 C 
{species}%endblock ChemicalSpeciesLabel

#Use only for needed species, like Li, Na, K...
#%block PAO.Polarization.Scheme
# Atomic_Symbol Polarization_Scheme
# Example: Li non-perturbative

#%endblock PAO.Polarization.Scheme
    
########################################################"""+"\n"+"\n")

    format_in = args.Fin
    format_out = args.Fout

    cell_move = args.cell_move

    f.write(f"""####################Structural Informations####################

#Format of the atomic coordinates input: Ang (Angstroms), Fractional (Fractional coordinates)
AtomicCoordinatesFormat {format_in}
#Format of the atomic coordinates output: Ang (Angstroms), Fractional (Fractional coordinates)
AtomCoorFormatOut {format_out}
#Atomic origin of the system.
AtomicCoordinatesOrigin 0.0 0.0 0.0

#Type of movement for the unitary cell: True (Cell can move), False (Cell is fixed)
MD.VariableCell {cell_move}

#Pensar nesse
MD.RelaxCellOnly false

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

###############################################################"""+"\n"+"\n")

    basis_size = args.basis_size

    mesh_cutoff = args.mesh_cutoff

    dipole_correction = str(args.dipole_correction) if args.dipole_correction is not None else "False"

    spin_type = args.spin_type

    k_point = args.k_point
    k_type = 0.5 if k_point % 2 == 0 else 0.0

    f.write(f"""####################Theoretical Informations####################

#Exchange-Correlation functional
XC.Functional GGA 
#Author of the Exchange-Correlation functional
XC.Authors PBE

#Type of basis set
PAO.BasisSize {basis_size}

#MeshCutoff intensity for the real space grid
MeshCutoff {mesh_cutoff} Ry

#Type of dipole correction: True (Dipole correction on), False (Dipole correction off)
#Use this in case of adsorption
Slab.DipoleCorrection {dipole_correction}  

#Type of spin polarization: non-polarized, polarized, non-collinear, spin-orbit. (Read Manual for more details)
Spin {spin_type}

#Monkhorst-Pack k-point sampling
%block kgrid_Monkhorst_Pack     
#Last value related to the k point value :0.5 (odd) or 0.0 (even)
# For 3D cells, also change the last line
{k_point} 0 0 {k_type}   
0 {k_point} 0 {k_type}   
0 0 1 0.0   
%endblock kgrid_Monkhorst_Pack  

################################################################"""+"\n"+"\n")

    scf_crit = args.scf_crit

    f.write(f"""####################SCF Informations####################

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
SCF.DM.Tolerance {scf_crit}

########################################################"""+"\n"+"\n")

    run_type = args.run_type
    steps = args.steps
    md_crit = args.md_crit

    f.write(f"""####################MD Informations####################

#MD - Molecular Dynamics

#
MD.TypeOfRun {run_type}

#
MD.Steps {steps}
MD.MaxDispl 0.1 Ang
MD.MaxForceTol {md_crit} eV/Ang
Target.Pressure 0 GPa

#######################################################"""+"\n"+"\n")

    grimme = str(args.Grimme_D3) if args.Grimme_D3 is not None else "False"

    f.write(f"""####################Grimmes-D3 Informations####################

DFTD3 {grimme}
DFTD3.UseXCDefaults {grimme}
DFTD3.BJdamping {grimme}

#DFTD3.Periodic ??????
###############################################################"""+"\n"+"\n")

    save_dm = str(args.save_dm) if args.save_dm is not None else "True"

    f.write(f"""####################Re-Run Output Informations####################

#
MD.UseSaveXV false

#
DM.UseSaveDM {save_dm}

#
MD.UseSaveCG false

#
UseSaveData false

###############################################################"""+"\n"+"\n")

    f.write(f"""####################Write Output Informations####################

#All informations about the output can be obtained in the manual.

#Increase the output informations
LongOutput true

------------------------Structure and Coordinates------------------------

#Write the {label_name}.xyz file
WriteCoor.Xmol true

#Write the {label_name}.xtl file (Fractional Format)
WriteCoorCerius true

#Write the MD animation, {label_name}.ANI file
WriteMDXmol true

#Write the initial structure in the output file
WriteCoorInitial true

#Write the structure at each step, {label_name}.Remember file
WriteCoorStep true

#Write all Molecular Dynamics (MD) informations:
# {label_name}.MD and {label_name}.MDE files
WriteMDHistory true

------------------------Forces and Orbitals------------------------

#Write the atomic forces, {label_name}.FA file
WriteForces true

#Write all the orbitals used in the calculation. {label_name}.ORB.INDX file
Write.OrbitalIndex false

#Write some orbital informations in the output file
WriteOrbMom false

------------------------Hamiltonian and Density Matrix (DM)------------------------

#Write the DM, {label_name}.DM file
Write.DM true

#Write the Hamiltonian and Overlap Matrices (HS), {label_name}.HSX file - Must be true for Bands and DOS calculations?
SaveHS false

------------------------Eigenvalues, Bands and Wavefunctions------------------------

#Write the Hamiltonian bands eigenvalues, {label_name}.bands file - Must be true for Bands calculations
WriteBands false

#Write the Hamiltonian eigenvalues, {label_name}.EIG file - Must be true for DOS accounts calculations
WriteEigenvalues false

#Write the Wavefunctions, {label_name}.WFSX file
WriteWaveFunctions false

------------------------Electronic Populations------------------------

#Write Mulliken population, values can be 0, 1, 2 or 3 (see manual)
WriteMullikenPop 1

#Write Hirshfeld population
Write.HirshfeldPop true

#Write Voronoi population
Write.VoronoiPop false

#Write the Crystal Orbital Overlap Population (COOP)/ Crystal Orbital Hamiltonian Population (COHP) informations:
#{label_name}.fullBZ.WFSX and {label_name}.HSX files
COOP.Write false

------------------------Others Write Options------------------------

#Write.Graphviz
#WriteKpoints 
#Write.DM.end.of.cycle
#Write.H 
#Write.H.end.of.cycle
#Write.HS.History
#WriteKBands

#WFS.Write.For.Bands

#SaveRho
#SaveDeltaRho
#SaveRhoXC
#SaveElectrostaticPotential
#SaveNeutralAtomPotential
#SaveTotalPotential
#SaveIonicCharge
#SaveTotalCharge

#SaveBaderCharge
#AnalyzeChargeDensityOnly
#SaveInitialChargeDensity

#Write.Denchar

#################################################################
    """)


#Para o futuro:
#BANDAS and DOS
#PHONONS
#OPTICAL
#Dynamic Simulations
#Adsorption (Li,Na,K)
#FatBands
#TRANSIESTA
#WORKFUNCTION
#DFT-U
#RT-TDDFT