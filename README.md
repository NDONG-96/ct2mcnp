# ct2mcnp
Conversion of DICOM CT inputs into formats compatible with MCNP:

# load 
load the scan.py and ct2mcnp.py files in your directori (/home/your_path_direcori) 

# compilation

1) import biblioteq ct2mcnp
2) define your DICOM CT path in variable path1
3) define your comout mcnp file in path2
4) define the position of your matrix of ct in mcnp geomety by transX, transY and transZ
   transX, transY and transZ repesente the deplacement of the corners of ct cub 

# example
from ct2mcnp import Ct2mcnp

path1 = "/home/examples/Patient/Abdomen/"
path2="/home/mcnp/mcnp.m"

transX=0
transY=0
transZ=0

Ct2mcnp(path1, path2, transX, transY, transZ).cell_card()


