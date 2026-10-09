"""
Informações que devem ser modificadas no arquivo FDF:
- label_name: Label do Arquivo
- num_atoms: Número de átomos
- num_species: Número de espécies químicas

"""

import argparse as arg
import periodictable

parser = arg.ArgumentParser(prog = "FDF_Creator", formatter_class = arg.RawDescriptionHelpFormatter, description = "Program used to create FDF files for SIESTA code at several configurations", epilog= """Some Examples: 
1: Run optimization with GrimmeD3 and Dipole Correction activated:
    -l Label -k K_Point -t opt -d3 -dc
    
2: Run bands with spin polarized optmization:
    -l Label -k K_Point -t band -s polarized
    """)

required = parser.add_argument_group("Required Configurations")

required.add_argument("-l", dest = "label", type = str, required = True, help = "Label of file")
required.add_argument("-k", dest = "k_point", type = int, required = True, help = "Quantity of K points in Monkhorst-Pack grid")

input = parser.add_argument_group("Important Configurations")

input.add_argument("-t", dest = "type", type = str, required = False, metavar = "TYPE", choices = ["opt","bands","phonons","dynamic"], help = "Some Pattern Configurations")
input.add_argument("-n", dest = "num_atoms", type = int, required = False, help = "Number of Atoms")
input.add_argument("-run", dest = "run_type", type = str, required = False, metavar = "RUN_TYPE", default = "CG", choices = ["CG", "Broyden", "FIRE", "Verlet", "Nose", "FC"], help = "Types of Run")
input.add_argument("-el", dest = "elements", nargs ="+", required = False, metavar = "ELEMENT", help = "Elements (In order)")

theoretical = parser.add_argument_group("Theoretical Configurations")

theoretical.add_argument("-bs", dest = "basis_size", type = str, required = False, default = "DZP", help = "Basis Size")
theoretical.add_argument("-s", dest = "spin_type", type = str, required = False, metavar = "SPIN_TYPE", default = "non-polarized", choices = ["non-polarized", "polarized"], help = "Type of Polarization")
theoretical.add_argument("-mesh", dest = "mesh_cutoff", type = float, required = False, default = 400.0, help = "Mesh Cutoff Value (Ry)")
theoretical.add_argument("-cm", dest = "cell_move", type = str, required = False, metavar = "CELL_MOVE", default = "True", choices = ["True", "False"], help = "Enable Cell Movement")

stored = parser.add_argument_group("Stored Configurations")

stored.add_argument("-d3", dest = "Grimme_D3", required = False, action = "store_true", help = "Enable Grimme D3(BJ) dispersion corrections")
stored.add_argument("-no_sv", dest = "save_dm", required = False, action = "store_false", help = "Do not save density matrix")
stored.add_argument("-dc", dest = "dipole_correction", required = False, action = "store_true", help = "Enable slab dipole correction")

criteria = parser.add_argument_group("Criteria Configurations")

criteria.add_argument("-scf", dest = "scf_crit", type = float, required = False, default = 0.000001, help = "Criteria of SCF")
criteria.add_argument("-md", dest = "md_crit", type = float, required = False, default = 0.01, help = "Criteria of MD")

simple = parser.add_argument_group("Simple Configurations")

simple.add_argument("-Fin", dest = "Fin", type = str, required = False, metavar = "FORMAT IN", default = "Ang", choices = ["Ang", "Fractional"], help = "Input Coordinate Format")
simple.add_argument("-Fout", dest = "Fout", type = str, required = False, metavar = "FORMAT OUT", default = "Ang", choices = ["Ang", "Fractional"], help = "Output Coordinate Format")
simple.add_argument("-steps", dest = "steps", type = int, required = False, default = 500, help = "Number of Steps in MD")

args = parser.parse_args()

label_name = args.label
fdf_file = label_name + ".fdf"

type = args.type

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
MD.VariableCell {cell_move if not type == "bands" else "False"}

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
#Position_x Position_y Position_z Atomic_Index Atomic_Number Atomic_Symbol
# Example: 0.000000 0.000000 0.000000 1 10 C

%endblock AtomicCoordinatesAndAtomicSpecies

###############################################################"""+"\n"+"\n")

    if type == "bands":
        f.write(f"""####################Bands and DOS Informations####################

#Specifies the scale of the k vectors in the band lines
BandLinesScale ReciprocalLatticeVectors

#High Simmetry Points/Path (HSP) for the bands calculations:
#More informations about HSP can be found in the wikipedia
%block BandLines
#k_point HSP_x HSP_y HSP_Z HSP_Symbol
# Example: 1 0.000 0.000 0.000 G #(Gamma)
%endblock BandLines

#These block are related with the Density of States (DOS) and Projected Density of States (PDOS)
%block ProjectedDensityOfStates
#Min_Energy Max_Energy Broadening Num_Points Unit
#We can start the line using EF (Fermi Energy) 
# Example: EF -10.00 10.00 0.0500 10000 eV  

%endblock ProjectedDensityOfStates

#These block are related with the Local Density of States (LDOS)
%block LocalDensityOfStates
#Min_Energy Max_Energy Unit
# Example: EF -2.0 2.0 eV
%endblock LocalDensityOfStates

##################################################################"""+"\n"+"\n")

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

#Choice of the type of calculation, see the manual for more information
MD.TypeOfRun {run_type}

#
MD.Steps {steps if not type == "bands" else 0}
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
LongOutput True

------------------------Structure and Coordinates------------------------

#Write the {label_name}.xyz file
WriteCoor.Xmol True

#Write the {label_name}.xtl file (Fractional Format)
WriteCoorCerius True

#Write the MD animation, {label_name}.ANI file
WriteMDXmol True

#Write the initial structure in the output file
WriteCoorInitial True

#Write the structure at each step in the output file
WriteCoorStep True

#Write all Molecular Dynamics (MD) informations:
# {label_name}.MD and {label_name}.MDE files
WriteMDHistory {"True" if type == "opt" else "False"}

------------------------Forces and Orbitals------------------------

#Write the atomic forces, {label_name}.FA file
WriteForces True

#Write all the orbitals used in the calculation. {label_name}.ORB.INDX file
Write.OrbitalIndex False

#Write some orbital informations in the output file
WriteOrbMom False

------------------------Hamiltonian and Density Matrix (DM)------------------------

#Write the DM, {label_name}.DM file
Write.DM True

#Write the Hamiltonian and Overlap Matrices (HS), {label_name}.HSX file - Must be true for Bands and DOS calculations?
SaveHS {"True" if type == "bands" else "False"}

------------------------Eigenvalues, Bands and Wavefunctions------------------------

#Write the Hamiltonian bands eigenvalues, {label_name}.bands file - Must be true for Bands calculations
WriteBands {"True" if type == "bands" else "False"}

#Write the Hamiltonian eigenvalues, {label_name}.EIG file - Must be true for DOS accounts calculations
WriteEigenvalues {"True" if type == "bands" else "False"}

#Write the Wavefunctions, {label_name}.WFSX file
WriteWaveFunctions {"True" if type == "bands" else "False"}

------------------------Electronic Populations------------------------

#Write Mulliken population, values can be 0, 1, 2 or 3 (see manual)
WriteMullikenPop 1

#Write Hirshfeld population
Write.HirshfeldPop True

#Write Voronoi population
Write.VoronoiPop True

#Write the Crystal Orbital Overlap Population (COOP)/ Crystal Orbital Hamiltonian Population (COHP) informations:
#{label_name}.fullBZ.WFSX and {label_name}.HSX files
COOP.Write False

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