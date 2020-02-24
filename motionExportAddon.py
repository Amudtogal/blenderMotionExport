#!/usr/bin/python

# Blender Motion Tracking Addon 1.1
# © Simon Reichel 24/02/2020

import os
import numpy as np
import bpy
from bpy.props import BoolProperty as BoolProperty
from bpy.props import StringProperty as StringProperty

bl_info = {
    "name": "Export Motion Tracking Data",
    "category": "Import-Export",
    "description": "Use motion tracking data for scientific projects.",
    "author": "Simon Reichel",
    "version": (1, 1, 0),
    "blender": (2, 79, 0),
    "location": "This addon adds a new tab to the movie clip editor.",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "tracker_url": "https://github.com/BiYonic/blenderMotionExport/issues",
}


class ExportMarkerPanel(bpy.types.Panel):
    bl_label = "Marker"
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = "Tracking and Export"

    def draw(self, context):
        layout = self.layout
        sc = context.space_data
        clip = sc.clip

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("clip.add_marker_at_click", text="Add")
        row.operator("clip.delete_track", text="Delete")
        col.separator()
        if clip.tracking.tracks.active:
            col.prop(clip.tracking.tracks.active, 'name')

        selected = []
        tracks = clip.tracking.tracks
        for track in tracks:
            if track.select:
                selected.append(track)

        col.separator()
        # display marker distance as label
        if len(selected) == 2 and tracks.active:
            active_marker = selected[0] if tracks.active is selected[0] else selected[1]
            other_marker = selected[1] if tracks.active is selected[0] else selected[0]

            x_size = clip.size[0]
            y_size = clip.size[1]
            active_marker = active_marker.markers.find_frame(context.scene.frame_current)
            other_marker = other_marker.markers.find_frame(context.scene.frame_current)
            x = (active_marker.co.x - other_marker.co.x) * x_size
            y = (active_marker.co.y - other_marker.co.y) * y_size
            fulldistance = np.sqrt(x ** 2 + y ** 2)
            col.label("Marker distance:")
            col.label("{0:.2f} ({1:.2f}, {2:.2f})".format(fulldistance, x, y))
        else:
            col.label("Select two markers to show distance.")


class ExportTrackingPanel(bpy.types.Panel):
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_label = "Tracking"
    bl_category = "Tracking and Export"

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(text="Track:")

        props = row.operator("clip.track_markers", text="", icon='FRAME_PREV')
        props.backwards = True
        props.sequence = False
        props = row.operator("clip.track_markers", text="",
                             icon='PLAY_REVERSE')
        props.backwards = True
        props.sequence = True
        props = row.operator("clip.track_markers", text="", icon='PLAY')
        props.backwards = False
        props.sequence = True
        props = row.operator("clip.track_markers", text="", icon='FRAME_NEXT')
        props.backwards = False
        props.sequence = False

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Clear:")
        row.scale_x = 2.0

        props = row.operator("clip.clear_track_path", text="", icon='BACK')
        props.action = 'UPTO'

        props = row.operator("clip.clear_track_path", text="", icon='FORWARD')
        props.action = 'REMAINED'

        col = layout.column()
        row = col.row(align=True)
        row.label(text="Refine:")
        row.scale_x = 2.0

        props = row.operator("clip.refine_markers", text="", icon='LOOP_BACK')
        props.backwards = True

        props = row.operator("clip.refine_markers", text="", icon='LOOP_FORWARDS')
        props.backwards = False

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text="Merge:")
        row.operator("clip.join_tracks", text="Join Tracks")


class ExportDataPanel(bpy.types.Panel):
    bl_label = 'Export'
    bl_space_type = 'CLIP_EDITOR'
    bl_region_type = 'TOOLS'
    bl_category = 'Tracking and Export'

    # In andere Klasse kopieren
    bl_options = {'DEFAULT_CLOSED'}

    bpy.types.Scene.exp_path = StringProperty(
        name="Export Path",
        description="Path where data will be exported to",
        default="//",
        subtype='DIR_PATH')
    bpy.types.Scene.exp_subdirs = BoolProperty(
        name="Export Subdirectories",
        description="Markers will be exported to subdirectories",
        default=False)
    bpy.types.Scene.exp_logfile = BoolProperty(
        name="Write Logfile",
        description="Write logfile into export folder",
        default=False)

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.label("Export Path:")
        col.prop(context.scene, "exp_path", text="")
        col.separator()
        col.prop(context.scene, "exp_subdirs")
        col.prop(context.scene, "exp_logfile")
        col.separator()
        col.prop(context.scene, "frame_start")
        col.prop(context.scene, "frame_end")
        col.operator("scene.fullcliprange")
        col.separator()
        col.label("Export markers:")
        row = col.row(align=True)
        row.operator("scene.export_marker", text="Selected").selected_only = True
        row.operator("scene.export_marker", text="All")


class FullClipRangeOperator(bpy.types.Operator):
    """Select the whole frame range of the current clip"""
    bl_idname = "scene.fullcliprange"
    bl_label = "All frames"

    def execute(self, context):
        clip = bpy.data.movieclips[context.space_data.clip.name]

        context.scene.frame_start = clip.frame_start
        context.scene.frame_end = clip.frame_start + clip.frame_duration

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.space_data.clip


class ExportOperator(bpy.types.Operator):
    """Export the motion tracking data according to the settings."""
    bl_idname = "scene.export_marker"
    bl_label = "Export Tracking Markers"

    selected_only = BoolProperty(
        name="Selected Only",
        description="Export selected markers only",
        default=False)

    def execute(self, context):
        log = context.scene.exp_logfile
        path = bpy.path.abspath(context.scene.exp_path)
        subdirs = context.scene.exp_subdirs
        f_start = context.scene.frame_start
        f_end = context.scene.frame_end

        if not os.path.exists(path):
            os.makedirs(path)

        import time
        time_start = time.time()

        print("Writing log to {}.".format(os.path.join(path + "log.txt")))
        if log:
            log_file = open(os.path.join(path, "log.txt"), "w")
            log_file.write("Starting Export\n")
            log_file.write("Export path: {0}\n".format(path))
            log_file.write("Exporting from scene {0}\n".format(context.scene.name))
            log_file.write("Exporting from frame {0} to {1}\n".format(f_start, f_end))
            log_file.write("-----------------------------------------------------------\n\n")

        movieclips = []
        if self.selected_only:
            sc = context.space_data
            movieclips.append(sc.clip)
        else:
            movieclips = bpy.data.movieclips

        for clip in movieclips:
            x_size = clip.size[0]
            y_size = clip.size[1]

            if log:
                log_file.write("Starting movieclip {0} ({1} x {2} pixels)\n".format(
                    clip.name, x_size, y_size))

            if self.selected_only:
                tracks = [track for track in clip.tracking.tracks if track.select]
            else:
                tracks = clip.tracking.tracks

            for track in tracks:
                if log:
                    log_file.write("  Track {0} started ...\n".format(track.name))

                if not subdirs:
                    f_path = os.path.join(path, "{0}_{1}.csv".format(
                        clip.name.split(".")[0], track.name))
                else:
                    subpath = os.path.join(path, "{0}/".format(clip.name))
                    if not os.path.exists(subpath):
                        os.makedirs(subpath)
                    f_path = os.path.join(subpath, "{0}_{1}.csv".format(
                        clip.name.split(".")[0], track.name))

                print("Writing clip to {}.".format(f_path))
                export_file = open(f_path, 'w')
                export_file.write("frame;x;y\n")
                success = True
                i = f_start
                while i <= f_end:
                    marker = track.markers.find_frame(i)
                    if marker:
                        marker_x = round(marker.co.x * x_size)
                        marker_y = round(marker.co.y * y_size)
                        export_file.write("{0};{1};{2}\n".format(i, marker_x, marker_y))
                    else:
                        if log:
                            log_file.write("    Missing marker at frame {0}.\n".format(i))
                        success = False
                    i += 1

                export_file.close()
                if log:
                    log_file.write("  Finished Track {0} {1}...\n".format(
                        track.name, "successfully" if success else "with errors"))

            if log:
                log_file.write("Finished movieclip {0} in {1:.4f} s\n\n".format(
                    clip.name, time.time() - time_start))

        if log:
            log_file.write("-----------------------------------------------------------\n")
            log_file.write("Export finished ({0:.4f} s)".format(time.time() - time_start))
            log_file.close()

        self.report({'INFO'}, "Export done ({0:.4f} s)".format(time.time() - time_start))

        if len(movieclips) == 0:
            self.report({'INFO'}, "No clip opened...")

        return {"FINISHED"}


def register():
    bpy.utils.register_class(ExportOperator)
    bpy.utils.register_class(ExportMarkerPanel)
    bpy.utils.register_class(FullClipRangeOperator)
    bpy.utils.register_class(ExportTrackingPanel)
    bpy.utils.register_class(ExportDataPanel)


def unregister():
    bpy.utils.unregister_class(ExportOperator)
    bpy.utils.unregister_class(ExportMarkerPanel)
    bpy.utils.unregister_class(FullClipRangeOperator)
    bpy.utils.unregister_class(ExportTrackingPanel)
    bpy.utils.unregister_class(ExportDataPanel)


if __name__ == "__main__":
    register()
