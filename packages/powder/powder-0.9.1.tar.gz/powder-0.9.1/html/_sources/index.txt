.. Created by phyles-quickstart.
   Add some items to the toctree.

======================
 powder Documentation
======================

A python package that simulates powder diffraction using CCP4 and xprepx.


The *powder* script glues together operations to simulate powder
diffraction using *xprepx* and *ccp4*.

The *powder* script installs to the ``bin/`` directory of your
Python install, which should be in your path.


Complete Instructions for *powder*
==================================

Prerequisits
------------

Before running powder, make sure that the following programs
and packages are available and in your path:

- *molscript* (including molauto)
- *sfall* (CCP4)
- *mtz2various* (CCP4)
- *xprepx* (by George Sheldrick)
- *ps2pdf*
- *convert* (ImageMagick)

You also need Python version 2.6 or 2.7.


Instructions
------------

Running *powder* requires only four easy steps.

1. Make a new directory and put your pdb file in it.
2. Make a template settings file in that directory::

     powder -t > settings.cfg

3. Edit *at least* the first five values in the settings
   file on the right hand side of the "=" signs.

   **Important** - Don't change the names on othe left
   of the "=" signs because the left hand side names have meaning.

4. Run *powder* with the config file you edited::

     powder settings.cfg

Notes
=====

- Run *powder* with no arguments for quick help::

      powder

- The powder diffraction and a postscript file will be made for
  you. The program that does the summation and averaging, *xprepx*,
  runs as an X-window. When the plot pops up, it is important to click
  in the plot window and hit ``<Enter>`` to make sure the postscript
  file is saved.
- A pdf file is now also made that summarizes the model and
  simulation. That file is named the same as the postscript output,
  except that the filename extension is ".pdf", of course.
  Contents of the file specified by the ``info`` setting
  will be inserted into this report.
- There is no need to edit the pdb file in most cases. The
  ``CRYST1`` card, which specifies the crystallographic symmetry, is
  created for you from the settings file and written to a new pdb file
  which is then used for the diffraction simulation.
- An exception to modifying pdb files is that NMR structures should be
  limited to one model only. NMR structures come from the PDB with
  more than one model included. The extra structures will influence
  the powder diffraction.
- A text file will now be created that contains YAML
  (http://en.wikipedia.org/wiki/YAML) describing the spectrum as
  taken from the xprepx postscript output. The name of this file
  is specified by the ``spectrum file`` setting
  (default: ``spectrum.yml``). In YAML terms, the
  spectrum is stored as a top-level list of [2-theta, intensity] pairs.
  A python program can make a 2-D numpy array from the spectrum easily
  if numpy (http://numpy.scipy.org/) and pyYAML (http://pyyaml.org/)
  are installed.  For example, if the spectrum is stored in the
  file "``spectrum.yml``"::

      import numpy
      import yaml
      spec_ary = numpy.array(yaml.load(open('spectrum.yml')))
 
  More generally, the spectrum starts on the second line of the yaml
  file and each data line conforms to the following FORTRAN
  formatted read::

      REAL X, Y
      READ '(4X, F9.0, 2X, F9.0)', X, Y

Flags
=====

- The ``-d`` flag prevents powder from running xprepx and
  CCP4 programs for debugging.
- The ``-t`` flag will print a template file for editing (see
  the instructions).
- The ``-c`` flag with the config file will give a 2-theta -> resolution
  conversion for the wavelength specified in the config file. E.g.:

     powder -c settings.cfg
- The ``-h`` flag will print the usage and help notes.


Settings File
=============

The settings file is a standard *sectionless* config
file in the standard INI file format
(http://en.wikipedia.org/wiki/INI_file).

Examples of minimimal and complete settings files are at the
end of this manual.


Mandatory Settings
------------------

The "powder" script will fail if these minimal settings are not
included in the settings file.

   :pdb model:
       the name of the pdb file containing the model
       (e.g. ``my_model.pdb``)

   :cell dimensions:
       three numbers separated by spaces that
       specify the dimensions
       of the unit cell (e.g. ``250 250 250``)

   :res limits:
       two numbers separated by spaces that specify
       the low and high resolution
       limits over which to calculate the simulated
       powder diffraction spectrum (e.g. ``1000 4.0``)

   :wavelength:
       the wavelength of the simulated x-ray radiation
       (e.g. ``1.54178``)

   :postscript file:
       name of the output postscript file that
       shows the simulated spectrum
       (e.g. ``my_powder.ps``)

Optional Settings
-----------------

These settings are not necessary but are included for special cases,
like using non-standard versions of sfall, xprep, etc.

  :reset b-facs:
     a number that specifies a new b factor
     for all atoms in the model--if this
     number is negative, then no reset will be done
     (default: ``-1``)

  :mark interval:
     for the plotted spectrum, the interval
     between marks on the 2-theta axis (default: ``2``)

  :title:
     for the pdf report, the title will pe placed in the
     report above the simulated diffraction pattern
     (default: ``info.txt``)

  :info:
     name of info file that contains pre-formatted text
     that will be inserted into the pdf report
     (default: ``info.txt``)

  :clean up:
     if set to ``True``, then the mtz & sca files will be removed
     to save disk space
     (default: ``True``)

  :plot x units:
     if set to ``angstroms``, then theta angles along the
     x-axis are converted to angstroms instead of the *xprepx*
     default of degrees
     (default: ``angstroms``)

  :side ps file:
     name of an intermediate ps file showing a side view of the
     model--use it if you don't want a hidden file
     (default: ``.tmp.side.ps``)

  :top ps file:
     name of an intermediate ps file showing a top view of the
     model--use it if you don't want a hidden file
     (default: ``.tmp.top.ps``)

  :spectrum file:
     name of the yaml file in which the spectrum will be stored
     as a numerical 2-d array
     (default: ``spectrum.yml``)

  :temp pdb file:
     *powder* must create an intermediate pdb
     file (default: ``.tmp.pdb``)

  :mtz file:
     *powder* must create an intermediate mtz file
     (default: ``my_model.mtz``)

  :sca file:
     *powder* must also create an intermediate sca
     file that will also serve as the root name for
     the xprep prp results file (default: ``my_model.sca``)

  :sfall:
     command to call the *sfall* program from CCP4
     (default: ``sfall``)

  :mtz2various:
     command to call the *mtz2various* program from
     CCP4 (default: ``mtz2various``)

  :xprepx:
     command to call xprepx--if you have memory problems, use
     *bigxprepx*, i.e. ``/joule2/programs/xprep/bigxprepx``
     (default: ``xprepx``)

  :ps2pdf:
     command to convert postscript to pdf
     (default: ``ps2pdf``)

  :molauto:
     command to call *molauto* for making views of model
     (default: ``molauto``)

  :molscript:
     command to call *molscript* to make views of model
     (default: ``molscript``)

  :convert:
     command to convert different image formats
     (default: ``convert``)


Example Settings Files
======================

Minimal Settings File
---------------------

::

  # minimal settings file for powder

  pdb model = my_model.pdb
  cell dimensions = 200 200 200
  res limits = 1000 4.0
  wavelength = 1.54178
  postscript file = my_powder.ps


Complete Settings File
----------------------

::

  # complete settings file for powder

  pdb model = my_model.pdb
  cell dimensions = 200 200 200
  res limits = 1000 4.0
  wavelength = 1.54178
  postscript file = my_powder.ps

  # New B factor (-1 for no reset)
  reset b-facs = -1

  # 2-Theta Interval Marks
  mark interval = 2

  # Title of simulation
  title = My Model

  # Name of file that contains info about model
  info = info.txt

  # Clean up sca and mtz files
  clean up = True

  # Units of x axis for plot
  plot x units = angstroms

  # Name of intermediate ps file for side view
  side ps file = side.ps

  # Name of intermediate ps file for top view
  top ps file = top.ps

  # Name of file to store spectrum as yaml
  spectrum file = spectrum.yml

  # Name of intermediate pdb file
  temp pdb file = powder-tmp.pdb

  # Output mtz File
  mtz file = my_model.mtz

  # Output Scalepack File
  sca file = my_model.sca

  # Command to call sfall
  sfall = sfall

  # Command to call mtz2various
  mtz2various = mtz2various

  # Command to call xprepx
  xprepx = xprepx

  # Command to call ps2pdf
  ps2pdf = ps2pdf

  # Command to call molauto
  molauto = molauto

  # Command to call molscript
  molscript = molscript

  # Command to convert image formats
  convert = convert


.. toctree::
   :maxdepth: 2
   :numbered:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
