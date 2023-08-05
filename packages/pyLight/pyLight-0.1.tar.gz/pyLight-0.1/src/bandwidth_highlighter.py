#===============================================================================
# Copyright 2014 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#===============================================================================

#============= enthought library imports =======================
from traits.has_traits import HasTraits, on_trait_change
from traits.trait_types import Instance, Str, List
from traitsui.editors import ListEditor, InstanceEditor
from traitsui.group import VGroup, VSplit
from traitsui.item import UItem
from traitsui.view import View

from chaco.array_plot_data import ArrayPlotData
from chaco.default_colormaps import color_map_name_dict
from chaco.plot import Plot
from chaco.plot_containers import HPlotContainer
from chaco.tools.better_selecting_zoom import BetterSelectingZoom as ZoomTool
from chaco.tools.image_inspector_tool import ImageInspectorTool, ImageInspectorOverlay
from chaco.tools.pan_tool import PanTool

from enable.component import Component
from enable.component_editor import ComponentEditor

#============= standard library imports ========================
from numpy import array, where
#============= local library imports  ==========================
from src.band import Band
import Image


class BandwidthHighlighter(HasTraits):
    container = Instance(HPlotContainer)
    plot = Instance(Component)

    colormap_name_1 = Str('gray')

    path = Str
    # add_band = Button('Add band')
    highlight_bands = List(Band)

    def update_path(self, new):
        self.path = new

    def delete_band(self):
        self.highlight_bands.pop(-1)

    def add_band(self):
        self.highlight_bands.append(Band())

    def _path_changed(self):
        self._load_image(self.path)

    @on_trait_change('highlight_bands:[center,threshold,color, use]')
    def _refresh_highlight_bands(self, obj, name, old, new):
        if self.path:
            plot = self.oplot
            im = Image.open(self.path)
            rgb_arr = array(im.convert('RGB'))
            #            im_arr=array(im)
            gray_im = array(im.convert('L'))
            for band in self.highlight_bands:
                if band.use:
                    low = band.center - band.threshold
                    high = band.center + band.threshold

                    mask = where((gray_im > low) & (gray_im < high))
                    #                    print band.color[:3]
                    rgb_arr[mask] = band.color.toTuple()[:3]

            imgplot = plot.plots['plot0'][0]
            tools = imgplot.tools
            overlays = imgplot.overlays

            plot.delplot('plot0')
            plot.data.set_data('img', rgb_arr)
            img_plot = plot.img_plot('img', colormap=color_map_name_dict[self.colormap_name_1])[0]

            for ti in tools + overlays:
                ti.component = img_plot

            img_plot.tools = tools
            img_plot.overlays = overlays

            plot.request_redraw()

    def _load_image(self, path):
        self.container = self._container_factory()
        im = Image.open(path)
        #        oim = array(im)
        im = im.convert('L')
        odim = ndim = array(im)

        pd = ArrayPlotData()
        pd.set_data('img', odim)
        plot = Plot(data=pd, padding=[30, 5, 5, 30], default_origin='top left')
        img_plot = plot.img_plot('img',
                                 colormap=color_map_name_dict[self.colormap_name_1]
        )[0]
        self.add_inspector(img_plot)

        self.add_tools(img_plot)

        self.oplot = plot

        self.container.add(self.oplot)
        #        self.container.add(self.plot)
        self.container.request_redraw()

    def add_inspector(self, img_plot):
        imgtool = ImageInspectorTool(img_plot)
        img_plot.tools.append(imgtool)
        overlay = ImageInspectorOverlay(component=img_plot, image_inspector=imgtool,
                                        bgcolor="white", border_visible=True)

        img_plot.overlays.append(overlay)

    def add_tools(self, img_plot):
        zoom = ZoomTool(component=img_plot, tool_mode="box", always_on=False)
        pan = PanTool(component=img_plot, restrict_to_data=True)
        img_plot.tools.append(pan)

        img_plot.overlays.append(zoom)

    def _highlight_bands_default(self):
        return [Band(color='red'), Band(color='green'), Band(color='blue')]

    def traits_view(self):
        ctrl_grp = VGroup(
            # HGroup(UItem('add_band')),
            UItem('highlight_bands', height=115,editor=ListEditor(mutable=False,
                                                       style='custom',
                                                       editor=InstanceEditor())))
        v = View(
            VSplit(
            ctrl_grp,
            UItem('container',
                  editor=ComponentEditor(height=700))))
        return v

    def _container_factory(self):
        pc = HPlotContainer(padding=[5, 5, 5, 20])
        return pc

    def _container_default(self):
        return self._container_factory()

#============= EOF =============================================