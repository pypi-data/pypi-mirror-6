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

from __future__ import division
import numpy as np
from traits.api import (HasTraits,Str,Any,List,Instance,Bool,on_trait_change)
from utils import CVUError
import shell_utils

from color_map import set_lut
from mayavi import mlab
from mayavi.core.ui.api import MlabSceneModel

from chaco.api import (Plot,ArrayPlotData,ColorMapper,PlotGraphicsContext)
from chaco.tools.api import (ZoomTool,PanTool)
from color_axis import ColorfulAxis

import circle_plot

class DataView(HasTraits):	
	ds=Any						#symbolic reference to a dataset

	#the dataset keeps track of these and they are copied into the dataviews
	#where they are shown.

	#or, the dataset could just have a table listing what each viewport is
	#but i think this is considerably nicer

	current_subject=Str			#this is referred to as "cur_display_brain"
	current_parcellation=Str	#cur_display_parc, not so esoteric
	current_matrix_file=Str		#cur_display_mat, shows matrix file

	#there might be some traitsui information common to all views
	def __init__(self,ds,**kwargs):
		super(DataView,self).__init__(**kwargs)
		self.ds=ds
	
	def supply_adj(self): raise NotImplementedError()

	def error_dialog(self,str):
		return ds.error_dialog(str)
	
	def warning_dialog(self,str):
		return ds.warning_dialog(str)

	#abstract methods
	def draw_surfs(self): raise NotImplementedError()
	def draw_nodes(self): raise NotImplementedError()
	def draw_conns(self,new_edges=None): raise NotImplementedError()

	def snapshot(self): raise NotImplementedError()

	##END DATAVIEW

class DVMayavi(DataView):
	scene=Instance(MlabSceneModel)	
	syrf_lh=Any		#mayavi.modules.surface
	syrf_rh=Any		#mayavi.modules.surface
	nodes_lh=Any	#mayavi.modules.glyph
	nodes_rh=Any	#mayavi.modules.glyph
	vectors=Any		#mayavi.modules.vectors
	txt=Any			#mayavi.modules.text3d
	
	thres=Any		#mayavi.filters.threshold
	surfs_cracked=Bool(False)

	def __init__(self,ds,engine=None,**kwargs):
		super(DVMayavi,self).__init__(ds,**kwargs)
		if engine is not None:
			self.scene=MlabSceneModel(engine=engine)
		else:
			self.scene=MlabSceneModel()

		#print 'INITIALIZE',self.scene

	@on_trait_change('scene:activated')
	def setup(self):
		try:
			mlab.figure(bgcolor=(.34,.34,.34),figure=self.scene.mayavi_scene)
		except Exception as e:
			print str(e)
			return 

		self.surfs_gen()
		self.nodes_gen()

		#If only the parcellation is loaded, the adj will be supplied later
		if self.ds.adj is not None: 
			self.supply_adj()

			#if adj exists (on init) we are the last thing to initialize,
			#so we should call display_all at the end.  if not, we delegate
			#that responsibility to somewhere where it makes more modular sense
			self.ds.display_all()

	def supply_adj(self):
		self.vectors_gen()	

		pck = self.scene.mayavi_scene.on_mouse_pick(self.leftpick_callback)
		pck.tolerance = .02
		self.scene.mayavi_scene.on_mouse_pick(self.rightpick_callback,
			button='Right')

	########################################################################
	# GEN METHODS
	########################################################################

	#access the sources via '.parent'
	def surfs_clear(self): 
		try:
			self.syrf_lh.parent.parent.parent.remove()
			self.syrf_rh.parent.parent.parent.remove()
		except (ValueError,AttributeError):
			self.ds.verbose_msg('failed to remove old surfaces')

	def surfs_gen(self):
		self.syrf_lh = mlab.triangular_mesh(
			self.ds.srf.lh_verts[:,0],self.ds.srf.lh_verts[:,1],
			self.ds.srf.lh_verts[:,2],self.ds.srf.lh_tris,
			opacity=self.ds.opts.surface_visibility,
			color=self.ds.default_glass_brain_color,)
		self.syrf_rh = mlab.triangular_mesh(
			self.ds.srf.rh_verts[:,0],self.ds.srf.rh_verts[:,1],
			self.ds.srf.rh_verts[:,2],self.ds.srf.rh_tris,
			opacity=self.ds.opts.surface_visibility,
			color=self.ds.default_glass_brain_color,)
		#some colors
		#(.4,.75,0) #DARKISH GREEN
		#(.82,1,.82) #LIGHTER GREEN
		#(.82,.82,.82) #GRAY

		self.surfs_cracked=False
		for surf in (self.syrf_lh,self.syrf_rh):
			surf.actor.actor.pickable=0
			set_lut(surf,self.ds.opts.scalar_map)

		self.ds.chg_lh_surfmask(); self.ds.chg_rh_surfmask()

	def cracked_surfs_gen(self): 
		tri_inds_l,tri_inds_r=[],[]
		#all lh nodes are assumed to start with l
		for l in self.ds.labv:
			if l[0]=='l':
				tris=self.ds.srf.lh_tris; tri_inds=tri_inds_l
			elif l[0]=='r':
				tris=self.ds.srf.rh_tris; tri_inds=tri_inds_r

			#get the triangles entirely contained in this set of vertices
			v_as_set=set(self.ds.labv[l])
			ts,=np.where([v_as_set.issuperset(tri) for tri in tris])
			tri_inds.extend(ts)

		self.syrf_lh=mlab.triangular_mesh(
			self.ds.srf.lh_verts[:,0],self.ds.srf.lh_verts[:,1],
			self.ds.srf.lh_verts[:,2],self.ds.srf.lh_tris[tri_inds_l],
			opacity=self.ds.opts.surface_visibility,
			color=self.ds.cvu.default_glass_brain_color,
			figure=self.scene.mayavi_scene)
		self.syrf_rh=mlab.triangular_mesh(
			self.ds.srf.rh_verts[:,0],self.ds.srf.rh_verts[:,1],
			self.ds.srf.rh_verts[:,2],self.ds.srf.rh_tris[tri_inds_r],
			opacity=self.ds.opts.surface_visibility,
			color=self.ds.cvu.default_glass_brain_color,
			figure=self.scene.mayavi_scene)

		self.surfs_cracked=True

		for surf in (self.syrf_lh,self.syrf_rh):
			surf.actor.actor.pickable=0
			set_lut(surf,self.ds.opts.scalar_map)

		self.ds.chg_lh_surfmask(); self.ds.chg_rh_surfmask()

	def nodes_clear(self): 
		try:
			self.nodes_lh.parent.parent.remove()
			self.nodes_rh.parent.parent.remove()
			self.txt.remove()
		except (ValueError,AttributeError):
			pass

	def nodes_gen(self): 
		#assumes that all LH nodes start with L.  This is not ideal.
		nodesource_lh = mlab.pipeline.scalar_scatter(
			self.ds.lab_pos[self.ds.lhnodes,0],
			self.ds.lab_pos[self.ds.lhnodes,1],
			self.ds.lab_pos[self.ds.lhnodes,2],
			figure=self.scene.mayavi_scene)
		self.nodes_lh=mlab.pipeline.glyph(nodesource_lh,
			scale_mode='none',scale_factor=3.0,mode='sphere',
			figure=self.scene.mayavi_scene)

		nodesource_rh=mlab.pipeline.scalar_scatter(
			self.ds.lab_pos[self.ds.rhnodes,0],
			self.ds.lab_pos[self.ds.rhnodes,1],
			self.ds.lab_pos[self.ds.rhnodes,2],
			figure=self.scene.mayavi_scene)
		self.nodes_rh=mlab.pipeline.glyph(nodesource_rh,
			scale_mode='none',scale_factor=3.0,mode='sphere',
			figure=self.scene.mayavi_scene)

		self.txt = mlab.text3d(0,0,83,'',scale=4.0,color=(.8,.6,.98,),
			figure=self.scene.mayavi_scene)
		self.txt.actor.actor.pickable=0

		for nodes in (self.nodes_lh,self.nodes_rh):
			nodes.glyph.color_mode='color_by_scalar'

		self.ds.chg_lh_nodemask(); self.ds.chg_rh_nodemask()
		self.draw_nodes()

	def vectors_clear(self):
		try:
			self.vectors.parent.parent.parent.remove()
			#TODO clearing old viewports and getting rid of them
			#needs to garbage collect explicitly
		except (ValueError,AttributeError):
			pass

	def vectors_gen(self): 
		vectorsrc=mlab.pipeline.vector_scatter(
			self.ds.starts[:,0],self.ds.starts[:,1],self.ds.starts[:,2],
			self.ds.vecs[:,0],self.ds.vecs[:,1],self.ds.vecs[:,2],
			figure=self.scene.mayavi_scene)

		vectorsrc.mlab_source.dataset.point_data.scalars=self.ds.adjdat

		#thresholding needs to be cleaned up a little bit.  the threshold
		#filter should only be set in draw_conns
		#reset_thresh should threshold cleanly such that its a valid value.
		#if its not a valid value, reset_thresh should error check it and set 
		#it to the min or max value that it can have (but print out a warning
		#saying it did so)
		self.ds.reset_thresh()

		self.thres=mlab.pipeline.threshold(vectorsrc,name='threshold',
			low=self.ds.thresval,up=np.max(self.ds.adjdat),
			figure=self.scene.mayavi_scene)	
		self.thres.auto_reset_lower=False
		self.thres.auto_reset_upper=False

		self.vectors=mlab.pipeline.vectors(self.thres,
			colormap=self.ds.opts.activation_map.cmap,
			line_width=self.ds.opts.conns_width,
			scale_mode='vector',figure=self.scene.mayavi_scene)
		self.vectors.glyph.glyph_source.glyph_source.glyph_type='dash'
		self.vectors.glyph.glyph.clamping=False
		self.vectors.actor.property.opacity=.3
		self.vectors.actor.actor.pickable=False

		set_lut(self.vectors,self.ds.opts.activation_map)
		self.ds.chg_conns_colors()
		self.ds.chg_lh_connmask(); self.ds.chg_rh_connmask()
		self.ds.chg_interhemi_connmask(); 

		self.ds.chg_conns_colorbar()

		#calling draw_conns is expensive and we want to avoid doing it
		#right after loading
		self.txt.set(text='')

	########################################################################
	# DRAW METHODS
	########################################################################

	def draw_surfs(self): 	
		srf_scalar=self.ds.scalar_display_settings.surf_color
		if (self.ds.display_mode=='scalar' and srf_scalar):
			colors_lh=np.zeros((len(self.ds.srf.lh_verts)),)
			colors_rh=np.zeros((len(self.ds.srf.rh_verts)),)
			for i,l in enumerate(self.ds.labv):
				#assumes that lh labels start with L and so on
				vertices=self.ds.labv[l]
				if l[0]=='l':
					colors_lh[vertices]=self.ds.node_scalars[srf_scalar][i]
				elif l[0]=='r':
					colors_rh[vertices]=self.ds.node_scalars[srf_scalar][i]
			self.syrf_lh.mlab_source.scalars=colors_lh
			self.syrf_rh.mlab_source.scalars=colors_rh
			
			for syrf in (self.syrf_lh,self.syrf_rh):
				syrf.actor.mapper.scalar_visibility=True

		else:
			for syrf in (self.syrf_lh,self.syrf_rh):
				syrf.actor.mapper.scalar_visibility=False
	
	def draw_nodes(self): 
		nc=self.ds.scalar_display_settings.node_color
		ns=self.ds.scalar_display_settings.node_size

		lhn=self.nodes_lh; lhn_ix=self.ds.lhnodes
		rhn=self.nodes_rh; rhn_ix=self.ds.rhnodes

		for nodes,ixes in ((lhn,lhn_ix),(rhn,rhn_ix)):
			nr=len(ixes)
			#set node size
			if self.ds.display_mode=='scalar' and ns:
				nodes.glyph.scale_mode='scale_by_vector'
				nodes.glyph.glyph.scale_factor=8
				nodes.mlab_source.dataset.point_data.vectors=(
					np.tile(self.ds.node_scalars[ns][ixes],(3,1)).T)
			else:
				nodes.glyph.scale_mode='data_scaling_off'
				nodes.glyph.glyph.scale_factor=3

		#set node color -- we dont care about ds.node_colors for mayavi
			if (self.ds.display_mode=='normal' or
					(self.ds.display_mode=='scalar' and not nc)):
				set_lut(nodes,self.ds.opts.default_map)
				nodes.mlab_source.dataset.point_data.scalars=np.tile(.3,nr)

			elif self.ds.display_mode=='scalar': #and nc must be true
				set_lut(nodes,self.ds.opts.scalar_map)
				nodes.mlab_source.dataset.point_data.scalars=(
					self.ds.node_scalars[nc][ixes])

			elif self.ds.display_mode=='module_single':
				set_lut(nodes,self.ds.opts.default_map)
				new_colors=np.tile(.3,self.ds.nr_labels)
				new_colors[self.ds.get_module()]=.8
				nodes.mlab_source.dataset.point_data.scalars=new_colors[ixes]

			elif self.ds.display_mode=='module_multi':
				new_colors=np.array(self.ds.module_colors[:self.ds.nr_modules])
				manager=nodes.module_manager.scalar_lut_manager
				#set the mayavi object to the dummy cmap that we hide from user
				#so that when changed notifications will work correctly
				manager.lut_mode='black-white'
				#now adjust its LUT manually
				manager.number_of_colors=self.ds.nr_modules
				manager.lut.table=new_colors	

				#set the mayavi scalars to be fractions between 0 and 1
				import bct
				nodes.mlab_source.dataset.point_data.scalars=(bct.ls2ci(
					self.ds.modules,zeroindexed=True)/self.ds.nr_modules)[ixes]

		mlab.draw()

	def draw_conns(self,new_edges=None):
		self.thres.set(lower_threshold=self.ds.thresval)
		lo=self.thres.lower_threshold; hi=self.thres.upper_threshold

		if new_edges is not None:
			new_starts=self.ds.lab_pos[new_edges[:,0]]
			new_vecs=self.ds.lab_pos[new_edges[:,1]] - new_starts

			self.vectors.mlab_source.reset(
				x=new_starts[:,0],y=new_starts[:,1],z=new_starts[:,2],
				u=new_vecs[:,0],v=new_vecs[:,1],w=new_vecs[:,2])

		if self.ds.curr_node is not None:
			self.vectors.actor.property.opacity=.75
			self.txt.set(text='  %s'%self.ds.labnam[self.ds.curr_node])
		else:
			self.vectors.actor.property.opacity=.3
			self.txt.set(text='')

		mlab.draw()

	########################################################################
	# DRAW HELPERS
	########################################################################

	def cleanup(self):
		self.surfs_clear()
		self.nodes_clear()
		self.vectors_clear()

	def set_colorbar(self,on,mayavi_obj,orientation='vertical'):
		if on:
			mlab.colorbar(object=mayavi_obj,orientation=orientation,title='')
		else:
			mayavi_obj.module_manager.scalar_lut_manager.show_scalar_bar=False

	def set_surf_render_style(self,style):
		#doesnt make sense to change the visualization if the surfaces are off
		self.ds.opts.lh_surfs_on=True
		self.ds.opts.rh_surfs_on=True

		if self.surfs_cracked:
			if style=='cracked glass':
				return
			else:
				self.surfs_clear()
				self.surfs_gen()
				self.draw_surfs()

		if style=='cracked_glass':
			self.surfs_clear()
			self.cracked_surfs_gen()
			self.draw_surfs()
		else:
			for syrf in [self.syrf_lh,self.syrf_rh]:
				if style=='contours':
					syrf.actor.property.representation='surface'
					syrf.enable_contours=True
					syrf.contour.number_of_contours=250	
					continue
				else:
					syrf.enable_contours=False
				if style=='glass':
					syrf.actor.property.representation='surface'
				elif style=='wireframe':
					syrf.actor.property.representation='wireframe'
				elif style=='speckled':
					syrf.actor.property.representation='points'

	########################################################################
	# CALLBACKS
	########################################################################

	#left mouse pick selects a single node, while right pick calls display_all
	def leftpick_callback(self,picker):
		for nodes in (self.nodes_lh,self.nodes_rh):
			if picker.actor in nodes.actor.actors:
				ptid=int(picker.point_id/nodes.glyph.glyph_source.glyph_source.
					output.points.to_array().shape[0])
				if ptid != -1 and nodes is self.nodes_lh:
					self.ds.display_node(self.ds.lhnodes[ptid])
				elif ptid != -1 and nodes is self.nodes_rh:
					self.ds.display_node(self.ds.rhnodes[ptid])

	def rightpick_callback(self,picker):
		self.ds.display_all()

	########################################################################
	# I/O
	########################################################################

	#takes a SnapshotParameters
	def snapshot(self,params):
		res=np.ceil(500*params.dpi/8000*111)	#TODO this resolution is too hi

		from mayavi import __version__ as mayavi_version
		if float(mayavi_version[:3]) >= 4.3:
			mlab.savefig(params.savefile,figure=self.scene.mayavi_scene,
				size=(res,res))
		else:
			self.hack_mlabsavefig(params.savefile,size=(res,res))

	#prior to mayavi 4.3, there was a bug that caused figures to be improperly 
	#tiled with magnification >=1. this is the workaround

	#in mayavi 4.4 offscreen rendering of text will be fixed
	def hack_mlabsavefig(self,fname,size):
		oldx,oldy=self.scene.scene_editor.get_size()

		curx,cury=self.scene.scene_editor.control.Parent.Parent.Size
		cury-=32 #the mayavi toolbar takes up 32 space, which is not what
				 #we are setting

		self.scene.scene_editor.set_size((curx,cury))
		self.txt.visible=False	#label visibility will be fixed in mayavi 4.4

		magnif_desired = max(size[0]//curx,size[1]//cury)+1
		newsize=(int(size[0]/magnif_desired),int(size[1]/magnif_desired))
		self.scene.scene_editor.set_size(newsize)
		from tvtk.api import tvtk
		filter=tvtk.WindowToImageFilter(read_front_buffer=True)
		filter.magnification=int(magnif_desired)
		self.scene.scene_editor._lift()
		filter.input = self.scene.scene_editor._renwin
		ex = tvtk.PNGWriter()
		ex.file_name = fname
		ex.input = filter.output
		self.scene.scene_editor._exporter_write(ex)

		#reset the old size
		self.scene.scene_editor.set_size((oldx,oldy))
		#restore the 3D region text if it was previously enabled
		self.txt.visible=self.ds.opts.show_floating_text

	#takes a MakeMovieParameters
	def make_movie(self,params):
		xs,ys=self.scene.scene_editor.control.GetScreenPositionTuple()		
		ys+=32 #the mayavi toolbar takes up 32 pixels
		xe,ye=tuple(self.scene.scene_editor(get_size()))

		cmd = ('ffmpeg -loglevel error -y -f x11grab -s %ix%i -r %i -b %i '
			'-i :0.0+%i,%i %s' % 
			(xe,ye,params.framerate,params.bitrate*1024,xs,ys,params.savefile))

		try:
			self.ffmpeg_process=shell_utils.sh_cmd_retproc(cmd)
			self.make_movie_animate(params.samplerate,params.anim_style)
		except CVUError as e:
			self.error_dialog(str(e))

	def make_movie_animate(self,samplerate,rotate_on):
		def anim():
			i=0
			while True:
				if rotate_on:
					self.scene.camera.azimuth(10)
					self.scene.render()
				yield
		animation=anim()
		fps_in=1000//samplerate
		self.animator=Animator(fps_in,animation.next)

	#this is a separate call, when the user is done recording and clicks
	#the button to stop the movie
	def make_movie_finish(self,params):
		if self.animator:
			self.animator.timer.Stop()
			del self.animator
		self.ffmpeg_process.communicate('q')
		if self.ffmpeg_process.returncode:
			self.error_dialog('ffmpeg failed with error code %s' %
				self.ffmpeg_process.returncode)
			del self.ffmpeg_process
			return
		del self.ffmpeg_process
		print "Movie saved successfully to %s" % params.savefile

	##END DVMAYAVI

class DVMatrix(DataView): 
	conn_mat=Any
	xa=Instance(ColorfulAxis)
	ya=Instance(ColorfulAxis)

	def __init__(self,ds,**kwargs):
		super(DVMatrix,self).__init__(ds,**kwargs)
		if self.ds.adj is not None: self.chaco_gen()
		else: self.empty_gen()

	def supply_adj(self):
		self.conn_mat.data.set_data('imagedata',self.ds.adj_thresdiag)

	########################################################################
	# GEN METHODS
	########################################################################

	def chaco_gen(self): 
		self.conn_mat=Plot(ArrayPlotData(imagedata=self.ds.adj_thresdiag))

		cm=ColorMapper.from_palette_array(self.ds.opts.connmat_map._pl(
			xrange(256)))
		self.conn_mat.img_plot('imagedata',name='connmatplot',colormap=cm)

		self.conn_mat.tools.append(ZoomTool(self.conn_mat))
		self.conn_mat.tools.append(PanTool(self.conn_mat))
		self.xa=ColorfulAxis(self.conn_mat,self.ds.node_colors,'x')
		self.ya=ColorfulAxis(self.conn_mat,self.ds.node_colors,'y')
		self.conn_mat.underlays=[self.xa,self.ya]
	
	def empty_gen(self):
		from chaco.api import Greys
		img = np.zeros((self.ds.nr_labels,self.ds.nr_labels))
		self.conn_mat=Plot(ArrayPlotData(imagedata=img))

		cm=ColorMapper.from_palette_array(self.ds.opts.connmat_map._pl(
			xrange(256)))
		self.conn_mat.img_plot('imagedata',name='connmatplot',colormap=cm)

		self.conn_mat.tools.append(ZoomTool(self.conn_mat))
		self.conn_mat.tools.append(PanTool(self.conn_mat))
		self.xa=ColorfulAxis(self.conn_mat,self.ds.node_colors,'x')
		self.ya=ColorfulAxis(self.conn_mat,self.ds.node_colors,'y')
		self.conn_mat.underlays=[self.xa,self.ya]

	########################################################################
	# DRAW METHODS
	########################################################################
		
	def draw_surfs(self): NotImplemented

	def draw_nodes(self):
		mat=self.ds.scalar_display_settings.connmat

		if self.ds.display_mode=='scalar' and mat:
			colors=list(self.ds.opts.scalar_map._pl(self.ds.node_scalars[mat]))
		else:
			colors=self.ds.node_colors

		self.xa.colors=colors; self.ya.colors=colors
		self.conn_mat.request_redraw()

	#FIXME listen to color changes directly from the GUI and then call
	#the dataset
	def draw_conns(self,new_edges=None): NotImplemented

	def center(self):
		for ax in (self.xa,self.ya):
			ax.mapper.range.high_setting=self.ds.nr_labels
			ax.mapper.range.low_setting=0


	########################################################################
	# I/O
	########################################################################
	
	#takes a SnapshotParameters
	def snapshot(self,params):
		gc=PlotGraphicsContext(self.conn_mat.outer_bounds,dpi=params.dpi)
		gc.render_component(self.conn_mat)
		gc.save(params.savefile)

	## END DVMATRIX

class DVCircle(DataView):
	circ=Any			#mpl.figure
	circ_data=List		#list(mpl.patch.pathpatch)

	def __init__(self,ds,**kwargs):
		super(DVCircle,self).__init__(ds,**kwargs)

		if self.ds.adj is not None: self.circ_gen()
		else: self.empty_gen()
		#self.empty_gen()

	def supply_adj(self):
		self.circ_gen(figure=self.circ)
		#self.empty_gen(figure=self.circ)
	
	########################################################################
	# GEN METHODS
	########################################################################

	def circ_gen(self,reqrois=(),figure=None):
		#if figure is not None: figure.clf(keep_observers=True)
		if figure is not None: figure.clf()

		self.circ=circle_plot.plot_connectivity_circle_cvu(
			np.reshape(self.ds.adjdat,(self.ds.nr_edges,)),
			self.ds.node_labels_numberless,
			indices=self.ds.edges.T,
			colormap=self.ds.opts.activation_map.cmap,
			fig=figure,
			n_lines=self.ds.nr_edges, #nr_edges is already bounded by soft_max
			node_colors=self.ds.node_colors,
			reqrois=reqrois,)
		self.circ_data=self.circ.get_axes()[0].patches

		self.draw_nodes()

	def empty_gen(self,figure=None):
		self.circ=circle_plot.plot_connectivity_circle_cvu(
			np.array(()),
			self.ds.node_labels_numberless,
			indices=np.array(((),())),
			colormap=self.ds.opts.activation_map.cmap,
			fig=figure,
			n_lines=None,
			node_colors=self.ds.node_colors,
			reqrois=(),)

	########################################################################
	# DRAW METHODS
	########################################################################

	def draw_surfs(self): NotImplemented

	def draw_nodes(self): 
		circ=self.ds.scalar_display_settings.circle

		if self.ds.display_mode=='scalar' and circ:
			colors=list(self.ds.opts.scalar_map._pl(self.ds.node_scalars[circ]))
		else:
			colors=self.ds.node_colors

		circ_path_offset=len(self.ds.adjdat)
		for n in xrange(self.ds.nr_labels):
			self.circ_data[circ_path_offset+n].set_fc(colors[n])
		
		self.circ.canvas.draw()
	
	#select_conns performs operations on us directly, so there is nothing left 
	#for us to do.  this breaks the design structure, in order to significantly 
	#reduce overhead on a costly and frequently run code segment

	#maybe it would be possible for select_conns to only examine and/or return
	#the ones that have changed and need to be updated
	def draw_conns(self,new_edges=None):
		self.circ.canvas.draw()

	########################################################################
	# CALLBACKS
	########################################################################

	def circle_click(self,event):
		if event.button==3:
			self.ds.display_all()
		#in principle, don't display node right here but wait for a pan.
		#this is complicated to implement, involving constantly checking
		#for motion and resetting the callbacks.  some of this logic is
		#written in mpleditor, but it isn't used because polar plots are
		#completely broken if you try to make them do this.

		#until mpl polar plots get real panning, just call to display node
		elif event.button==1 and (7 <= event.ydata <= 8):
			n=self.ds.nr_labels*event.xdata/(np.pi*2)+.5*np.pi/self.ds.nr_labels
	
			self.ds.display_node(int(np.floor(n)))

	def circle_mouseover(self,event,tooltip):
		if 7 <= event.ydata <= 8:
			n=self.ds.nr_labels*event.xdata/(np.pi*2)+.5*np.pi/self.ds.nr_labels

			tooltip.Enable(True)
			tooltip.SetTip(self.ds.labnam[int(np.floor(n))])
		else:
			tooltip.Enable(False)

	########################################################################
	# I/O
	########################################################################
	
	#takes a SnapshotParameters
	def snapshot(self,params):
		self.circ.savefig(params.savefile,dpi=params.dpi,facecolor='black')
	
	## END DVCIRCLE
