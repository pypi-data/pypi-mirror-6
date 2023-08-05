#!/usr/local/bin/python
#===============================================================================
# Copyright 2012 Jake Ross
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
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'


#============= enthought library imports =======================
from chaco.pdf_graphics_context import PdfPlotGraphicsContext
from pyface.constant import OK
from pyface.file_dialog import FileDialog
from pyface.image_resource import ImageResource
from traitsui.menu import Action
from traits.api import HasTraits, Instance, File
from traitsui.api import View, Item, Group, VGroup, UItem, ToolBar
#============= standard library imports ========================
import sys
import os
#============= local library imports  ==========================
#============= enthought library imports =======================
from src.bandwidth_highlighter import BandwidthHighlighter


class ImageProcessor(HasTraits):
    path = File
    highlighter = Instance(BandwidthHighlighter)

    def do_add_band(self):
        self.highlighter.add_band()

    def do_delete_band(self):
        self.highlighter.delete_band()

    def do_save(self):
        dlg = FileDialog(action='save as')
        if dlg.open() == OK:
            path = dlg.path

        if not path.endswith('.pdf'):
            path += '.pdf'

        gc = PdfPlotGraphicsContext(filename=path)
        pc = self.highlighter.container

        gc.render_component(pc, valign='center')
        gc.save()

        return gc

    def traits_view(self):
        sp=[os.path.join(os.path.dirname(__file__),'icons')]

        sa=Action(name='save',
                  action='do_save',
                  image=ImageResource(name='file_pdf.png',
                                      search_path=sp))
        aa=Action(name='add band',action='do_add_band',
                  image=ImageResource(name='add.png',
                                      search_path=sp))

        da = Action(name='delete band', action='do_delete_band',
                    image=ImageResource(name='delete.png',
                                        search_path=sp))

        tb=ToolBar(sa,aa, da)

        main_grp = Group(Item('path'))
        highlight_bands_grp = UItem('highlighter', style='custom')
        v = View(
            VGroup(main_grp,
                   Group(highlight_bands_grp,
                         layout='tabbed'
                   )
            ),
            resizable=True,
            width=800,
            height=800,

            toolbar=tb
        )
        return v

    def _highlighter_default(self):
        h = BandwidthHighlighter(path=self.path)
        self.on_trait_change(h.update_path, 'path')
        return h


if __name__ == '__main__':
    d = ImageProcessor()
    if len(sys.argv) > 1:
        path = os.path.join(os.getcwd(), sys.argv[1])
        d.path = path
    # d.path = '/Users/ross/Sandbox/archive/images/R2-03 closeup_1_BSE_1_zoomed.png'
    # d.path='/Users/argonlab2/Sandbox/R2-03 closeup_1_BSE_1 zoomed2.png'
    d.configure_traits()
#============= EOF =============================================
