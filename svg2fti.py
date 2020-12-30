import argparse
import xml.etree.ElementTree as ET

"""
svg2fti
@mach-kernel
"""

from ftibuilder.color import *
from ftibuilder.path import *

class FTIBuilder:
  def __init__(self, svg=None, num_samples=None, out=None, color_map=None):
    self.svg_et = ET.parse(svg)
    self.num_samples = num_samples
    self.out = out
    self.color_map = color_map

    self.fti_color = FTIColor(color_map)
    self.fti_paths = list(self.gen_fti_paths())

  def gen_fti_paths(self):
    for el in self.svg_et.findall('.//{http://www.w3.org/2000/svg}path'):
      yield FTIPath(
        svg_document=self.svg_et,
        svg_element=el,
        num_samples=self.num_samples,
        fti_color=self.fti_color
      )

  def write_fti(self):
    self.fix_scale()
    f = open(self.out, 'w')

    for num, fti_path in enumerate(self.fti_paths):

      f.write("#Path %d\n" % (num))
      f.write(fti_path.fti_begin_path);
      for vertex in fti_path.points:
        # reflect y
        f.write("vertex(%f,%f);\n" % (vertex.real, 100 - vertex.imag))
      f.write(fti_path.fti_end_path)

    f.close()

  """
  FTI only allows 100x100 so we are going to find the max of (max(real), max(imag)),
  then scale all points accordingly. Make smaller images larger and larger
  images fit on the canvas
  """
  def fix_scale(self):
    max_real, max_imag, max_final = 0, 0, 0

    for fti_path in self.fti_paths:
      for point in fti_path.points:
        max_real = max(max_real, point.real)
        max_imag = max(max_imag, point.imag)

    max_final = max(max_imag, max_real)
    scale = float(100) / max_final

    print(
      "SCALE ADJUSTMENT:\nmax_real %f\nmax_imag %f\nmax_final %f\nscale %f" % 
      (max_real, max_imag, max_final, scale)
    )

    for path in self.fti_paths:
      path.map_points(lambda p: p * scale)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='svg to SGI fti')
  parser.add_argument(
    '--svg',
    help='an svg',
    default=False,
    type=str,
    required=True
  )

  parser.add_argument(
    '--out',
    help='your output',
    default='out.fti',
    type=str,
    required=False
  )

  parser.add_argument(
    '--num_samples',
    help='fti does not support curves. higher is smoother.',
    default=50,
    type=int,
    required=False
  )

  parser.add_argument(
    '--color_map',
    help='json of sgi palette -> rgb',
    default='color_map.json',
    type=str,
    required=False
  )
  FTIBuilder(**vars(parser.parse_args())).write_fti()