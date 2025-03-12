import bpy
import math

obj = bpy.data.objects.get("Moon")

if obj:
    start_frame = 1
    end_frame = 12000
    rotation_speed = 360 / (end_frame - start_frame)

    for frame in range(start_frame, end_frame + 1):
        obj.rotation_euler[2] = math.radians(rotation_speed * (frame - start_frame))
        obj.keyframe_insert(data_path="rotation_euler", index=2, frame=frame)

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
    bpy.ops.screen.animation_play()
else:
    print("'Moon' object cannot be found.")
