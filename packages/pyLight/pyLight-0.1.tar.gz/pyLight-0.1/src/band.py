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
from traits.api import HasTraits
from traitsui.api import View, Item

#============= standard library imports ========================
#============= local library imports  ==========================



from traits.has_traits import HasTraits
from traits.trait_types import Int, Bool
from traits.traits import Color
from traitsui.group import HGroup
from traitsui.item import UItem, Item
from traitsui.view import View

__author__ = 'ross'


class Band(HasTraits):
    center = Int(enter_set=True, auto_set=False)
    threshold = Int(enter_set=True, auto_set=False)
    color = Color
    use = Bool(False)

    def traits_view(self):
        v = View(HGroup(UItem('use'),
                        Item('center'), Item('threshold'),
                        UItem('color')))
        return v
#============= EOF =============================================