#    (C) Roan LaPlante 2013 rlaplant@nmr.mgh.harvard.edu
#
#	 This file is part of cvu, the Connectome Visualization Utility.
#
#    cvu is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from matplotlib.colors import LinearSegmentedColormap
from mayavi.core import lut_manager
from pylab import get_cmap
from traits.api import (HasTraits,Enum,Bool,File,Range,Str,Instance,Property,Event,
	on_trait_change)

class CustomColormap(HasTraits):
	lut_list=lut_manager.lut_mode_list()
	lut_list.remove('black-white')
	lut_list.remove('blue-red')
	lut_list.append('custom_heat')

	imgs_path = 'cmap_images'

	map_type = Enum('default','scalar','activation','connmat')
	cmap = Enum(lut_list)
	reverse = Bool
	fname = File
	label = Str
	threshold = Range(0.0,0.5,0.2)
	_pl = Property(Instance(LinearSegmentedColormap))

	def __init__(self,type):
		self.map_type=type

	def _cmap_default(self):
		if self.map_type=='scalar': return 'BuGn'
		elif self.map_type=='activation': return 'YlOrRd'
		elif self.map_type=='connmat': return 'RdYlBu'
		else: return 'cool' #return default

	def _reverse_default(self):
		if self.map_type=='connmat': return True
		else: return False

	def _label_default(self):
		if self.map_type=='scalar': return 'Scalars Colormap'
		elif self.map_type=='activation': return 'Conns Colormap'
		elif self.map_type=='connmat': return 'Matrix Colormap'
		else: return 'Default Colormap'

	def _get__pl(self):
		'''return the LinearSegmentedColormap describing this CustomColormap'''
		if self.cmap=='file' and self.fname:
			return LinearSegmentedColormap.from_list('file',
				lut_manager.parse_lut_file(self.fname))	
		elif self.cmap=='custom_heat':
			return gen_heatmap(t=self.threshold,reversed=self.reversed)
		elif self.reverse:
			return get_cmap(self.cmap+'_r')
		else:
			return get_cmap(self.cmap)

#TODO THIS IS MONOLITHIC-DATASET CODE THAT SHOULD BE PORTED
def get_cmap_pl(map):
	'''From a CustomColormap instance, return a LinearSegmentedColormap
describing that CustomColormap'''
	if map.cmap=='file' and map.fname:
		return LinearSegmentedColormap.from_list('file',
			lut_manager.parse_lut_file(map.fname))
	elif map.cmap=='custom_heat':
		return gen_heatmap(t=map.threshold,reversed=map.reverse)
	elif map.reverse:
		return get_cmap(map.cmap+'_r')
	else:
		return get_cmap(map.cmap)

def gen_heatmap(t=.2,two_tailed=True,reversed=False):
	'''Generates a heatmap that has red-to-yellow at the top, blue-to-light-blue
at the bottom, and gray in the middle.  If the map is one-tailed, only the red
portion is displayed:

gen_heatmap(t=.2,two_tailed=True)
t -- the threshold used to start both tails of the heatmap.  This should be a
value between 0 and .5.  You are responsible for calculating the right value
from your statistics.

two-tailed -- if false, only the upper (red) part of the heatmap is shown'''

	#a very fancy algorithm to do things correctly when the map is inverted.
	#sorry about the readability
	def swapif(trip):
		if reversed: return ( 1-trip[0], trip[2], trip[1] )
		else: return trip

	def revif(tups):
		if reversed: l=list(tups); l.reverse(); return tuple(l)
		else: return tups

	if two_tailed and not reversed:
		cdict = {'red': revif(( swapif((0.0,0.0,0.6)),
							  	swapif((t  ,0.2,0.4)),
							  	swapif((1-t,0.4,1.0)),
							  	swapif((1.0,1.0,0.0)))),
				'green':revif(( swapif((0.0,0.0,1.0)),
								swapif((t  ,0.5,0.4)),
								swapif((1-t,0.4,0.0)),
								swapif((1.0,1.0,0.0)))),
				'blue': revif(( swapif((0.0,0.0,1.0)),
								swapif((t  ,1.0,0.4)),
								swapif((1-t,0.4,0.0)),
								swapif((1.0,0.5,0.0)))),}
	else:
		cdict = {'red': revif((	swapif((0.0,0.0,0.4)),
								swapif((1-t,0.4,1.0)),
								swapif((1.0,1.0,0.0)))),
				'green':revif(( swapif((0.0,0.0,0.4)),
								swapif((1-t,0.4,0.0)),
								swapif((1.0,1.0,0.0)))),
				'blue': revif(( swapif((0.0,0.0,0.4)),
								swapif((1-t,0.4,0.0)),
								swapif((1.0,0.5,0.0)))),}

	return LinearSegmentedColormap('heatmap_%.3f'%t,cdict,256)

def map_to_table(cmap,nvals=256):
	'''Takes a LinearSegmentedColormap, and returns a table of RGBA values
spanning that colormap.

	arguments:
	cmap - the LinearSegmentedColormap instance
	nvals- the number of values to span over.  The default is 256.'''

	return cmap(xrange(nvals),bytes=True)

def set_lut(mayavi_obj,map,use_vector_lut=False):
	'''Takes a mayavi object and a CustomColormap and sets the color LUT on thatobject to use the colormap referred to by the CustomColormap, handling all
edge cases

	arguments:
	mayavi_obj - the mayavi object.  This object MUST have a module_manager
		trait, which not all mayavi objects do.
	map - the CustomColormap instance
	use_vector_lut - if True, uses the vector_lut_manager instead of the
		scalar_lut_manager on the mayavi object.  Defaults to false.'''

	if use_vector_lut:
		lut_mgr=mayavi_obj.module_manager.vector_lut_manager
	else:
		lut_mgr=mayavi_obj.module_manager.scalar_lut_manager

	lut_mgr.number_of_colors = 256
	lut_mgr.file_name=map.fname	
	lut_mgr.reverse_lut=map.reverse

	if map.cmap=='custom_heat':
		lut_mgr.lut_mode='black-white' #this mode is not used and will always
									#trigger notifications when changed
		hmap = gen_heatmap(t=map.threshold)
		lut_mgr.lut.table = map_to_table(hmap)
	else:
		lut_mgr.lut_mode=map.cmap

