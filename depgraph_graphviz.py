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
from bpy.types import PropertyGroup
from bpy.props import *
from bpy_extras import image_utils

import sys
import os
import pipes
import subprocess
from subprocess import Popen, PIPE, STDOUT
import re

def image_update(self, context=None):
    image = self.id_data

    suffix_fmt = "%%0%dd" % self.suffix_len
    filename = os.path.join(self.directory, self.basename + (suffix_fmt % self.index) + self.extension)
    image.filepath = filename

def index_get(self):
    return self.get('index', 0)

def index_set(self, value):
    if value < self.index_min:
        self['index'] = self.index_min
    elif value > self.index_max:
        self['index'] = self.index_max
    else:
        self['index'] = value

class DepsgraphDebugSequence(PropertyGroup):
    directory = StringProperty(name="Directory", description="Directory path of the image")
    basename = StringProperty(name="Base Name", description="Base name of the image files")
    extension = StringProperty(name="Extension", description="Filename extension")
    suffix_len = IntProperty(name="Suffix Length")

    index = IntProperty(name="Index", get=index_get, set=index_set, update=image_update)
    index_min = IntProperty(name="Index Minimum")
    index_max = IntProperty(name="Index Maximum")


def convert_graphviz(input_filename, output_filename):
    input_file = open(input_filename, 'r')
    output_file = open(output_filename, 'w')
    dot_process = Popen(["dot", "-T", "png:cairo"], stdin=input_file, stdout=output_file)
    dot_process.wait()
    input_file.close()
    output_file.flush()
    output_file.close()

def files_directory():
    return bpy.app.tempdir

def files_single(basename):
    valid = re.compile(r"%s$" % basename)
    files = os.listdir(files_directory())
    for filename in files:
        if valid.match(filename):
            yield os.path.join(bpy.app.tempdir, filename)

def graphviz_image_single(image, basename):
    for filename in files_single(basename):
        output_filename = "%s.png" % filename
        imagename = bpy.path.basename(output_filename)

        convert_graphviz(filename, output_filename)
        if imagename in bpy.data.images:
            bpy.ops.image.reload()
        else:
            image_utils.load_image(output_filename)
        break

def files_numbered(basename):
    valid = re.compile(r"%s_(?P<number>[0-9]+)$" % basename)
    files = os.listdir(files_directory())
    for filename in files:
        match = valid.match(filename)
        if match:
            yield os.path.join(bpy.app.tempdir, filename), match.group('number')

def graphviz_image_sequence(image, basename):
    settings = image.depsgraph_debug

    settings.directory = files_directory()
    settings.basename = "%s_" % basename
    settings.extension = ".png"

    first = True
    for filename, suffix in files_numbered(basename):
        index = int(suffix)
        if first:
            first = False
            settings.index_min = index
            settings.index_max = index
            settings.suffix_len = len(suffix)
        else:
            settings.index_min = min(settings.index_min, index)
            settings.index_max = max(settings.index_max, index)

        output_filename = "%s.png" % filename
        convert_graphviz(filename, output_filename)

    settings.index = settings.index_min
    image_update(settings)


class DepgraphGraphvizImage(bpy.types.Operator):
    """Show depgraph as image"""
    bl_idname = "scene.depgraph_graphviz_image"
    bl_label = "Graphviz"

    mode_items = [
        ("GRAPH", "Graph", "Show basic depsgraph structure"),
        ("EVAL", "Evaluate", "Evaluate the depsgraph and show each step"),
        ]
    mode = EnumProperty(name="Mode", items=mode_items, default='GRAPH')

    @classmethod
    def poll(cls, context):
        if context.scene is None:
            return False
        if context.space_data.type != 'IMAGE_EDITOR':
            return False
        if context.space_data.image is None:
            return False
        return True

    debug_basename = {
        'GRAPH'     : "blender_depgraph",
        'EVAL'      : "blender_depgraph_eval",
        }

    def execute(self, context):
        image = context.space_data.image

        basename = self.debug_basename[self.mode]
        input_filename = os.path.join(bpy.app.tempdir, basename)
        output_filename = os.path.join(bpy.app.tempdir, basename + ".png")
        imagename = bpy.path.basename(output_filename)

        scene = context.scene
        if self.mode == 'GRAPH':
            scene.depsgraph_rebuild()

            scene.depsgraph.debug_graphviz(input_filename)
            graphviz_image_single(image, basename)

        elif self.mode == 'EVAL':
            if not scene.depsgraph:
                scene.depsgraph_rebuild()

            scene.depsgraph.debug_simulate(input_filename)
            graphviz_image_sequence(image, basename)

        return {'FINISHED'}


class DepgraphDebugPanel(bpy.types.Panel):
    """Debug tools for the depgraph"""
    bl_label = "Depgraph Debug"
    bl_idname = "IMAGE_PT_depgraph_debug"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.operator("scene.depgraph_graphviz_image", text="Graph").mode = 'GRAPH'
        layout.operator("scene.depgraph_graphviz_image", text="Evaluate").mode = 'EVAL'

        image = context.space_data.image
        if image:
            layout.prop(image.depsgraph_debug, "index") 


def register():
    bpy.utils.register_class(DepsgraphDebugSequence)
    bpy.types.Image.depsgraph_debug = PointerProperty(type=DepsgraphDebugSequence)

    bpy.utils.register_class(DepgraphGraphvizImage)
    bpy.utils.register_class(DepgraphDebugPanel)

def unregister():
    del bpy.types.Image.depsgraph_debug
    bpy.utils.unregister_class(DepsgraphDebugSequence)
    
    bpy.utils.unregister_class(DepgraphGraphvizImage)
    bpy.utils.unregister_class(DepgraphDebugPanel)
