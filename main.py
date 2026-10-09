import fdf_creator
import chemical
import os

chemical.Obtain(fdf_creator.fdf_file)

chemical.psml_find(fdf_creator.fdf_file,os.getcwd())