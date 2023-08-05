                             Optimal Stellar Models (OSM)

OSM is a python program that implements the Levenberg-Marquardt method for the calculation of optimal stellar models with the CESTAM code. The minimization takes into account fundamental constraints as well as seismic constraints. Cross-correlations between the seismic constraints are also take into account in the minimization criterion. 

* Requirements:

- CESTAM (version 3.2 or newer) : a free code for the calculation of  the structures and evolutions of stars ;
- python-cestam, a Python library associated with CESTAM (developed by J. Marques), this module is included in the CESTAM package ;
- ADIPLS : a code for computing adiabatic stellar modes (http://astro.phys.au.dk/~jcd/adipack.n/) ;
- Python (2.7 or newer) , Numpy and Scipy. 

* Installation

You must first install CETSTAM and ADIPLS, please refer to their associated documentations. To install OSM in your home directory for you own use, type:
python setup.py install –-home=$HOME/

The components of the OSM library will be installed, depending on your architecture, in $HOME/lib/python or $HOME/lib64/python, while the osm.py executable will be installed in $HOME/bin/.

You can also install OSM as root for all the users, in that case type:
sudo python setup.py install


* Tutorial:

Please refer to the HTML documentation (index.html)


Copyright (c) 2012 R. Samadi (LESIA - Observatoire de Paris)

This is a free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with this code.  If not, see <http://www.gnu.org/licenses/>.
