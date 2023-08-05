#! /usr/bin/env python

"""
powder: a convenience script to simulate powder diffraction

by James Stroud

xprepx and ccp4 must be fully functional in your environment
python 2.4 or higher is recommended
"""

import os
import sys
import textwrap
import math
import itertools
import re
import time
import popen2

import ConfigParser as configparser

from cStringIO import StringIO
from optparse import OptionParser


ConfigParser = configparser.ConfigParser

# DEBUG = True

class PowderError(Exception): pass
class SettingsError(PowderError): pass

def doopts():
  program = os.path.basename(sys.argv[0])
  usg = """\
        usage: %s [-h | -t | [-c] settings.cfg] [-d]

          - Use the -d flag to debug, which doesn't run ccp4 or xprepx
          - Use the -t flag without a settings file name to print a
            new template for the settings file.
          - Use the -c flag with a settings file to get a
            conversion of 2-theta to resolution for the wavelength
            specified in the settings file.
          - Any header in the pdb file will be stripped, even
            the SCALE and ORIGIN cards.

          homepage: https://www.doe-mbi.ucla.edu/software/powder"""
  usg = textwrap.dedent(usg) % program
  parser = OptionParser(usage=usg)
  parser.add_option("-t", "--template", dest="template",
                    default=False, action="store_true",
                    help="print an example settings file",
                    metavar="TEMPLATE")
  parser.add_option("-c", "--chart", dest="chart",
                    default=False, action="store_true",
                    help="print chart of 2-theta to resolution",
                    metavar="TEMPLATE")
  parser.add_option("-d", "--debug", dest="debug",
                    default=False, action="store_true",
                    help="debug: don't run ccp4 or xprepx")
  return parser

def wait_exec(cmd, instr=None, poll_interval=0.1):
  # note capital letter in Popen3
  handle = popen2.Popen3(cmd)
  if instr is not None:
    handle.tochild.write(instr)
  output = []
  while True:
    s = handle.fromchild.read()
    output.append(s)
    time.sleep(poll_interval)
    process_code = handle.poll()
    if process_code != -1:
      output = "".join(output)
      break
  return output

def usage(parser):
  sys.stderr.write(parser.format_help())
  sys.stderr.write("\n")
  sys.exit()

def template(config):
  print "# settings file for powder"
  print
  print make_sample_config(config)
  sys.exit()

def get_cell(cell):
  return tuple([float(c) for c in cell.split()])

def get_res_limits(res_limits):
  lo, hi = [float(v) for v in res_limits.split()]
  if lo < hi:
    hi, lo = lo, hi
  return lo, hi

def flint(v):
  return int(math.floor(float(v)))
  
def res2twotheta(res, wl):
  return math.degrees(2.0 * math.asin(wl/(2.0 * res)))

def twotheta2res(twotheta, wl):
  return float(wl) / (2.0 * math.sin(math.radians(twotheta)/2.0))

def make_sample_config(config):
  rstr = []
  for key, (converter, example, default, help) in config:
    if help is not None:
      rstr.append("\n# %s" % help)
    rstr.append('%s = %s' % (key, example))
  return "\n".join(rstr)

def section2cfg(section, schema):
  """
  Pass in I{section} as a B{dict}.
  """
  cfg = {}
  for k in section:
    if k not in schema:
      msg = "Unknown setting: '%s'" % k
      raise SettingsError(msg)
  for k, (converter, example, default, help) in schema.items():
    v = section.get(k, default)
    if v is None:
      msg = "Settings file must specify value for '%s'." % k
      raise SettingsError, msg
    # probably should make this a converter
    if (converter == bool) and (v not in (True, False)):
      if v.lower() in ('yes', 'true'):
        v = True
      elif v.lower() in ('no', 'false'):
        v = False
      else:
        tmplt = '%s must be True, False, Yes, or No not "%s"'
        msg = tmplt % (k, v)
        raise SettingsError(msg)
    try:
      cfg[k] = converter(v)
    except ValueError, e:
      msg = "Bad value for setting '%s'." % k
      raise SettingsError(msg)
  return cfg
     
def config2cfg(c, schema):
  cfg = {}
  for name in c.sections():
    section = dict(c.items(name))
    cfg[name] = section2cfg(section, schema)
  return cfg

def make_defaults(schema):
  s = dict([(k,e) for (k,(c,e,d,h)) in schema.items()])
  return section2cfg(s, schema)

def parse_config(config_file, schema):
  if not os.path.exists(config_file):
    msg = 'Settings file "%s" does not exist.' % config_file
    raise SettingsError(msg)
  try:
    msg = 'Problem reading settings file "%s".' % config_file
    settings = open(config_file).read()
  except IOError:
    raise SettingsError(msg)
  settings = "[main]\n" + settings
  fp = StringIO()
  fp.write(settings)
  fp.reset()
  try:
    c = ConfigParser()
    c.readfp(fp)
  except configparser.Error, e:
    msg = 'Problem reading settings file "%s".' % config_file
    raise SettingsError(msg)
  return config2cfg(c, schema)

# (key, (converter, example, default, help))
# for defaults, use string representations or None if optional
# for help, use None if no help
config = [('pdb model', (str, 'my_model.pdb', None, None)),
          ('cell dimensions', (get_cell, '200 200 200', None, None)),
          ('res limits', (get_res_limits, '1000 4.0', None, None)),
          ('wavelength', (float, '1.54178', None, None)),
          ('postscript file', (str, 'my_powder.ps', None, None)),
          ('reset b-facs', (float, '-1', '-1',
                            "New B factor (-1 for no reset)")),
          ('mark interval', (flint, '2', '2',
                             '2-Theta Interval Marks')),
          ('title', (str, 'My Model', 'My Model',
                     'Title of simulation')),
          ('info', (str, 'info.txt', 'info.txt',
                    'Name of file that contains info about model')),
          ('simplify', (int, '1', 1,
                        'Amount to Simplify images for big models')),
          ('fast', (bool, 'True', True,
                    'skip steps where previous output exists')),
          ('clean up', (bool, 'True', True,
                       'Clean up sca and mtz files')),
          ('plot x units', (str, 'angstroms', 'angstroms',
                            'Units of x axis for plot')),
          ('side ps file', (str, 'side.ps', '.tmp.side.ps',
                       'Name of intermediate ps file for side view')),
          ('top ps file', (str, 'top.ps', '.tmp.top.ps',
                       'Name of intermediate ps file for top view')),
          ('spectrum file', (str, 'spectrum.yml', 'spectrum.yml',
                       'Name of file to store spectrum as yaml')),
          ('temp pdb file', (str, 'powder-tmp.pdb', '.tmp.pdb',
                             'Name of intermediate pdb file')),
          ('mtz file', (str, 'my_model.mtz', 'my_model.mtz',
                        'Output mtz File')),
          ('sca file', (str, 'my_model.sca', 'my_model.sca',
                        'Output Scalepack File')),
          ('molauto file', (str, 'my_mol.in', 'my_mol.in',
                            'Output file from molauto for molscript')),
          ('sfall', (str, 'sfall', 'sfall', 'Command to call sfall')),
          ('mtz2various', (str, 'mtz2various', 'mtz2various',
                           'Command to call mtz2various')),
          ('xprepx', (str, 'xprepx', 'xprepx',
                      'Command to call xprepx')),
          ('ps2pdf', (str, 'ps2pdf', 'ps2pdf',
                      'Command to call ps2pdf')),
          ('molauto', (str, 'molauto', 'molauto',
                      'Command to call molauto')),
          ('molscript', (str, 'molscript', 'molscript',
                         'Command to call molscript')),
          ('convert', (str, 'convert', 'convert',
                         'Command to convert image formats'))]

schema = dict(config)


sfall = """
        %(sfall)s xyzin %(temp pdb file)s HKLOUT %(mtz file)s << eof
        TITLE Calculate Fc from %(pdb model)s
        MODE sfcalc xyzin
        RESOLUTION %(lo res)s %(hi res)s
        SFSG 1
        SYMM 1
        eof
        """

mtz2v = """
        %(mtz2various)s HKLIN %(mtz file)s HKLOUT %(sca file)s << eof
        OUTPUT SCAL
        scale 0.01
        labin FP=FC SIGFP=PHIC
        end
        eof
        """

xprep = """
        echo '<pre>'
        %(xprepx)s << eof
        %(sca file)s
        d
        y
        p
        s
        i
        p1
        y
        a
        g
        %(wavelength)s
        0.0 %(hi 2-theta)s
        %(mark interval)s
        0.02 0.08
        90
        y
        raw_%(postscript file)s
        q
        eof
        echo '</pre>'
        """

def get_spectrum(psfile):
   """
   Returns the spectrum contained in the xprepx ps file as a
   list of (two-theta, normed intensity) pairs
   """
   xoff = 45
   yoff = 400
   spec_marker = '2 W C0'
   legend_marker = 'C0 45 700 545 700'
   end_marker = '(Simulated powder'
   xlines = open(psfile)
   for aline in xlines:
     if spec_marker in aline:
       break
   pts = []
   values = []
   for aline in xlines:
     if legend_marker in aline:
       pts.append(float(fx) - xoff)
       values.append(float(fy) - yoff)
       break
     sx, sy, fx, fy, _c = aline.split()
     pts.append(float(sx) - xoff)
     values.append(float(sy) - yoff)
   xlines.next()
   scale_tths = []
   scale_pts = []
   for aline in xlines:
     if end_marker in aline:
       break
     aline = xlines.next()
     twotheta, pt, center, _y, _c = aline.split()
     twotheta = float(twotheta[1:-1])
     center = float(center) - xoff
     scale_tths.append(twotheta)
     scale_pts.append(center)
   del_twoth = scale_tths[-1] - scale_tths[0]
   del_pt = scale_pts[-1] - scale_pts[0]
   twoth_per_pt = del_twoth / del_pt
   twoths = [(p * twoth_per_pt) for p in pts]
   maxval = max(values)
   values = [(v / maxval) for v in values]
   return zip(twoths, values)

def zapmsps(psfile):
  zapRE = re.compile("^\s*%|(?:showpage)")
  new_file = []
  for aline in psfile.splitlines():
    m = zapRE.search(aline)
    if m is None:
      new_file.append(aline)
  new_file.append("")
  return "\n".join(new_file)

def turn_molin(molin, turnstr="by rotation x 90.0"):
  new_file = []
  for aline in molin.splitlines():
    if "by centre position atom" in aline:
      aline = aline.replace(";", "\n    %s ;" % turnstr)
      #aline = aline + "\n\n     set segments 2;"
    new_file.append(aline)
  new_file.append("")
  new_molin = "\n".join(new_file)
  return new_molin

def run_molauto(cfg):
  if cfg['simplify'] > 1:
    nice = ''
  else:
    nice = '-nice'
  cmd = "%s %s %s" % (cfg['molauto'], nice, cfg['temp pdb file'])
  return wait_exec(cmd)

def run_molscript(cfg, molin):
  cmd = "%s <<eof\n%s\neof\n" % (cfg['molscript'], molin)
  return wait_exec(cmd)

def make_snap(molin, ps_file, cfg):
  sys.stderr.write('running molscript\n')
  molout = run_molscript(cfg, molin)
  open("%s.ps" % ps_file, 'w').write(molout)
  args = (cfg['convert'], ps_file, ps_file)
  wait_exec('%s %s.ps %s.png' % args)
  wait_exec('%s %s.png %s.ps.ps' % args)
  ps = open("%s.ps.ps" % ps_file).read()
  ps = zapmsps(ps)
  open(ps_file, "w").write(ps)

def simplify_molin(molin, cfg):
  simplification = cfg['simplify'] * 2
  output = []
  lines = iter(molin.splitlines())
  for i in xrange(11):
    output.append(lines.next())
  colors = []
  traces = []
  for line in lines:
    if not line.strip():
      break
    if 'plane' in line:
      colors.append(line.replace('plane', 'line'))
      trace = lines.next()
      if trace.strip():
        traces.append(trace)
      else:
        del(colors[-1])
  colors = colors[::simplification]
  firsts = traces[::simplification]
  lasts = traces[simplification-1::simplification]
  for color, first, last in itertools.izip(colors, firsts, lasts):
    start = first.split()[2]
    end = last.split()[-1]
    new = "   trace from " + start + " to " + end
    output.append(color)
    output.append(new)
  output.append("")
  output.append("end_plot")
  output = "\n".join(output) + "\n"
  open('test.in', 'w').write(output)
  return output

def make_snaps(cfg):
  if not (cfg['fast'] and os.path.exists(cfg['molauto file'])):
    sys.stderr.write('running molauto\n')
    molin = run_molauto(cfg)
    sys.stderr.write('writing molauto file\n')
    open(cfg['molauto file'], 'w').write(molin)
  else:
    sys.stderr.write('skipping molauto\n')
    molin = open(cfg['molauto file']).read()
  if cfg['simplify'] > 1:
    sys.stderr.write('simplifying molscript\n')
    molin = simplify_molin(molin, cfg)
  make_snap(molin, cfg['side ps file'], cfg)
  turned = turn_molin(molin)
  make_snap(turned, cfg['top ps file'], cfg)

def fixup_line(aline, reset_b):
  if not is_atom(aline):
    return aline
  # skip hydrogens with easy check then harder check
  try:
    if aline[76:78].upper() == ' H':
      return
  except IndexError:
    pass
  else:
    if aline[12].upper() == 'H' or aline[12:14].upper() == ' H':
      return
  # truncate charge information
  try:
    aline = aline[:78]
  except IndexError:
    pass
  else:
    aline = aline + '\n'
  if reset_b:
    aline = aline[:60] + reset_b + aline[66:]
  return aline

def is_atom(aline):
  return aline.startswith('ATOM') or aline.startswith('HETATM')

def is_marker(aline):
  return ( aline.startswith('TER') or
           aline.startswith('END') or
           aline.startswith('MASTER') )


def is_useful(aline):
  return is_atom(aline) or is_marker(aline)


def main(parser):
  options, args = parser.parse_args()
  if options.template:
    template(config)
  try:
    config_file = args[0]
  except IndexError:
    usage(parser)
  run(config_file, options)

def write_line(aline, reset_b, writer):
  aline = fixup_line(aline, reset_b)
  if aline is not None:
    writer(aline)


def run(config_file, options):
  cfg = make_defaults(schema)
  cfg['DEBUG'] = options.debug
  _cfg = parse_config(config_file, schema).values()[0]
  cfg.update(_cfg)
  
  cfg['lo res'], cfg['hi res'] = cfg['res limits']
  # cfg['lo 2-theta'] = res2twotheta(cfg['lo res'], cfg['wavelength'])
  cfg['hi 2-theta'] = res2twotheta(cfg['hi res'], cfg['wavelength'])

  if options.chart:
    header = " %8s | %8s  " % ("2-theta", "resolution")
    hline = "-" * len(header)
    rstr = []
    rstr.append(hline)
    rstr.append(header)
    rstr.append(hline)
    for i in itertools.count(1):
      twotheta = 0.5 * i
      resolution = twotheta2res(twotheta, cfg['wavelength'])
      rstr.append(" %8.2f | %8.2f" % (twotheta, resolution))
      if twotheta >= cfg['hi 2-theta']:
        rstr.append(hline)
        break
    print "\n".join(rstr)
    sys.exit()

  pdb_file = open(cfg['pdb model']).readlines()
  tmplt = ( 'CRYST1 %8.3f %8.3f %8.3f ' +
            ' 90.00  90.00  90.00 P 1           1\n' )
  cryst = tmplt % cfg['cell dimensions']
  new_pdb = open(cfg['temp pdb file'], 'w')
  do_cryst = True
  reset_b = cfg['reset b-facs']
  if reset_b > 0:
    reset_b = "%6.2f" % reset_b
  else:
    reset_b = False
  for aline in pdb_file:
    if do_cryst:
      if is_atom(aline):
        new_pdb.write(cryst)
        do_cryst = False
        write_line(aline, reset_b, new_pdb.write)
    elif is_useful(aline):
      write_line(aline, reset_b, new_pdb.write)

  new_pdb.close()

  def _do_cmd(command, cfg):
    command = textwrap.dedent(command) % cfg
    if cfg['DEBUG']:
      print
      print command
    else:
      os.system(command)

  if cfg['fast']:
    sys.stderr.write('#'*50 + '\n')
    sys.stderr.write('#' + 'WARNING'.center(48) + '#\n') 
    sys.stderr.write('#'*50 + '\n')
    sys.stderr.write('# using fast mode, may skip some steps...\n')
    sys.stderr.write('#'*50 + '\n')
  if not (cfg['fast'] and os.path.exists(cfg['mtz file'])):
    _do_cmd(sfall, cfg)
  else:
    sys.stderr.write('skipping sfall\n')
  if not (cfg['fast'] and os.path.exists(cfg['sca file'])):
    _do_cmd(mtz2v, cfg)
  else:
    sys.stderr.write('skipping mtz2various\n')
  if not (cfg['fast'] and
          os.path.exists("raw_" + cfg['postscript file'])):
    _do_cmd(xprep, cfg)
  else:
    sys.stderr.write('skipping xprep\n')

    
  make_snaps(cfg)

  if not cfg['DEBUG']:
    fix_ps(cfg)
    write_spectrum(cfg)

  if cfg['clean up']:
    if cfg['DEBUG']:
      print 'remove %s' % cfg['sca file']
      print 'remove %s' % cfg['mtz file']
    else:
      os.remove(cfg['sca file'])
      os.remove(cfg['mtz file'])

def write_spectrum(cfg):
  spectrum = get_spectrum("raw_" + cfg['postscript file'])
  specfile = open(cfg['spectrum file'], 'w')
  specfile.write('model : "%s"\n' % cfg['pdb model'])
  specfile.write('spectrum :\n')
  specfile.write('  # [   2-theta, intensity ]\n')
  for t,v in spectrum:
    specfile.write('  - [ %9.6f, %9.7f ]\n' % (t,v))
  specfile.close()


def fix_ps(cfg):
  src = "raw_" + cfg['postscript file']
  degsRE = re.compile(r'(\(\d+\))')
  simstr = '(Simulated powder diffraction diagram) 25'
  ttstr = '2-theta -->'
  showpage = 'showpage'
  new_lines = []
  for aline in open(src):
    if cfg['plot x units'] == 'angstroms':
      parts = degsRE.split(aline)
      if len(parts) > 1:
        degs = float(parts[1][1:-1])
        if degs == 0:
          parts[1] = "(Inf)"
        else:
          reso = twotheta2res(degs, cfg['wavelength'])
          parts[1] = "(%s)" % round(reso, 2)
        aline = "".join(parts)
      if ttstr in aline:
        aline = aline.replace(ttstr, 'Resolution (Angstroms)')
    if simstr in aline:
      title = '(Simulated powder diffraction: %s) 22' % cfg['title']
      aline = aline.replace(simstr, title)
    if 'XSave save def' in aline:
      aline = "%s0.75 0.75 scale\n100 275 translate\n" % aline
    if showpage in aline:
      new_lines.append("-100 -275 translate\n")
      new_lines.append("1.33333333 1.33333333 scale\n")
      fontsize = 7
      spacing = fontsize * 0.17
      tmplt = "%s /Helvetica findfont exch scalefont setfont\n"
      bline = tmplt % (fontsize + spacing)
      new_lines.append(bline)
      xx = 55
      yy = 425
      bline = "%s %s moveto (%s) show\n" % (xx, yy, cfg['pdb model'])
      new_lines.append(bline)
      yy -= 25
      if os.path.exists(cfg['info']):
        tmplt = "%s /Helvetica findfont exch scalefont setfont\n"
        bline = tmplt % fontsize
        new_lines.append(bline)
        # spacing = 2
        for iline in open(cfg['info']):
          iline = iline.strip()
          if iline:
            if iline[0] == "~":
              iline = iline.replace("~", " ", 1)
            iline = iline.replace("(", "\\(")
            iline = iline.replace(")", "\\)")
            fmt = "%s %s moveto (%s) show\n" 
            bline = fmt % (xx, yy, iline)
            new_lines.append(bline)
            yy -= (fontsize + spacing)
      new_lines.append("375 215 translate 0.33 0.33 scale\n")
      if cfg['side ps file'] is not None:
        new_lines.append("(%s) run\n" % cfg['side ps file'])
      if cfg['top ps file'] is not None:
        new_lines.append("0 -620 translate\n")
        new_lines.append("(%s) run\n" % cfg['top ps file'])
    new_lines.append(aline)
  new_file = "".join(new_lines)
  if cfg['DEBUG']:
    psname = 'test.ps'
  else:
    psname = cfg['postscript file']
  psfile = open(psname, 'w')
  psfile.write(new_file)
  psfile.close()
  os.system('ps2pdf %s' % psname)

def graceful(e, parser):
  width = 65
  hline = "*" * width
  sys.stderr.write('\n' + hline + '\n')
  sys.stderr.write('ERROR'.center(65) + '\n')
  sys.stderr.write(hline + '\n\n')
  sys.stderr.write("  %s\n\n" % e)
  sys.stderr.write(hline + '\n\n')
  usage(parser)

def _powder():
  parser = doopts()
  try:
    main(parser)
  except PowderError, e:
    graceful(e, parser)

if __name__ == "__main__":
  _powder()
