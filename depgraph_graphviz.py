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
import subprocess
from subprocess import Popen, PIPE, STDOUT
import re

# if True: also output sequence of depsgraph build steps
DEBUG_BUILD = False

def write_graphviz(context, filename):
    scene = context.scene

    if DEBUG_BUILD:
        scene.depsgraph_rebuild(filename)
    else:
        scene.depsgraph_rebuild()

    graph = scene.depsgraph
    graph.debug_graphviz(filename)

def convert_graphviz(input_filename, output_filename):
    input_file = open(input_filename, 'r')
    output_file = open(output_filename, 'w')
    dot_process = Popen(["dot", "-T", "png:cairo"], stdin=input_file, stdout=output_file)
    dot_process.wait()
    input_file.close()
    output_file.flush()
    output_file.close()

def files_single(basename):
    valid = re.compile(r"%s$" % basename)
    files = os.listdir(bpy.app.tempdir)
    for filename in files:
        if valid.match(filename):
            yield os.path.join(bpy.app.tempdir, filename)

def files_numbered(basename):
    valid = re.compile(r"%s_(?P<number>[0-9]+)$" % basename)
    files = os.listdir(bpy.app.tempdir)
    for filename in files:
        match = valid.match(filename)
        if match:
            yield os.path.join(bpy.app.tempdir, filename), int(match.group('number'))

class DepgraphGraphvizImage(bpy.types.Operator):
    """Show depgraph as image"""
    bl_idname = "scene.depgraph_graphviz_image"
    bl_label = "Graphviz"

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        basename = "blender_depgraph"
        input_filename = os.path.join(bpy.app.tempdir, basename)
        output_filename = os.path.join(bpy.app.tempdir, basename + ".png")
        imagename = bpy.path.basename(output_filename)

        write_graphviz(context, input_filename)

        for filename in files_single(basename):
            convert_graphviz(filename, filename + ".png")
        
        for filename, number in files_numbered(basename):
            convert_graphviz(filename, filename + ".png")

        if imagename in bpy.data.images:
            bpy.ops.image.reload()
        else:
            image_utils.load_image(output_filename)

        return {'FINISHED'}


class DepgraphDebugPanel(bpy.types.Panel):
    """Debug tools for the depgraph"""
    bl_label = "Depgraph Debug"
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
