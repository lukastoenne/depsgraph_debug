# ##### BEGIN GPL LICENSE BLOCK #####
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
from bpy_extras import image_utils
import sys
import os
import pipes
from subprocess import Popen, PIPE, STDOUT

class DepgraphGraphvizImage(bpy.types.Operator):
    """Show depgraph as image"""
    bl_idname = "scene.depgraph_graphviz_image"
    bl_label = "Graphviz"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        scene = context.scene
        source = scene.depgraph_graphviz()

        filename = os.path.join(bpy.app.tempdir, "blender_depgraph.png")
        imagename = bpy.path.basename(filename)

        process = Popen(["dot", "-T", "png:cairo", "-o", filename], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        dot_stdout = process.communicate(input=source.encode(encoding='UTF-8'))[0]

        if imagename in bpy.data.images:
            bpy.ops.image.reload()
            #bpy.data.images[imagename].reload()
            #bpy.data.images[imagename].update()
        else:
            image_utils.load_image(filename)

        print(source)
        return {'FINISHED'}


class DepgraphDebugPanel(bpy.types.Panel):
    """Debug tools for the depgraph"""
    bl_label = "Depgraph Debug"
    #bl_idname = "SCENE_PT_depgraph_debug"
    #bl_space_type = 'PROPERTIES'
    #bl_region_type = 'WINDOW'
    #bl_context = "scene"
    bl_idname = "IMAGE_PT_depgraph_debug"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.depgraph_graphviz_image")


def register():
    bpy.utils.register_class(DepgraphGraphvizImage)
    bpy.utils.register_class(DepgraphDebugPanel)

def unregister():
    bpy.utils.unregister_class(DepgraphGraphvizImage)
    bpy.utils.unregister_class(DepgraphDebugPanel)
