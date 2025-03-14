import bpy
import math
import os
import time

obj = bpy.data.objects.get("Moon")

if obj:
    start_frame = 1
    end_frame = 12000
    rotation_speed = 360 / (end_frame - start_frame)

    output_dir = "E:\\Moon DEM\\Rendus"
    os.makedirs(output_dir, exist_ok=True)

    bpy.context.scene.render.image_settings.file_format = 'PNG'

    total_renders = 21
    render_interval_seconds = 25

    for i in range(total_renders):
        frame = start_frame + (i * 240)
        obj.rotation_euler[2] = math.radians(rotation_speed * (frame - start_frame))
        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)
        bpy.context.scene.frame_set(frame)
        render_filepath = os.path.join(output_dir, f"rendu_{i + 1}.png")
        bpy.context.scene.render.filepath = render_filepath
        bpy.ops.render.render(write_still=True)
        time.sleep(render_interval_seconds)

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    bpy.ops.screen.animation_play()
else:
    print("'Moon' object cannot be found.")
