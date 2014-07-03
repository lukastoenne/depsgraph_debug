### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import bpy
from bpy.types import AddonPreferences
from bpy.props import *

eval_mode_items = [
    ("EVAL_OLD", "Old", "Standard old depsgraph", 0),
    ("EVAL_NEW", "New", "New depsgraph", 14228),
    ("EVAL_SIM", "Simulate", "New depsgraph, simulated (no actual data changes)", 12345),
]
# all real values except 0
eval_modes_new = set(item[3] for item in eval_mode_items if item[3] != 0)

class DepgraphDebugPreferences(AddonPreferences):
    bl_idname = "depsgraph_debug"
    def eval_mode_get(self):
        dval = bpy.app.debug_value
        if dval in eval_modes_new:
            return dval
        else:
            return 0
    def eval_mode_set(self, value):
        if value in eval_modes_new:
            bpy.app.debug_value = value
        else:
            # only set to 0 if using a different mode,
            # allows using debug_value for other stuff too
            if bpy.app.debug_value in eval_modes_new:
                bpy.app.debug_value = 0
    depsgraph_eval_mode = EnumProperty(name="Eval Mode", description="Switch between depsgraph implementations", items=eval_mode_items, get=eval_mode_get, set=eval_mode_set)

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)


def get_prefs(context=bpy.context):
    return context.user_preferences.addons["depsgraph_debug"].preferences


def register():
    bpy.utils.register_class(DepgraphDebugPreferences)

def unregister():
    bpy.utils.unregister_class(DepgraphDebugPreferences)
