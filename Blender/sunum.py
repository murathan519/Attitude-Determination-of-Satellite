import bpy
import math
from mathutils import Vector, Quaternion

# Ay objesi
moon = bpy.data.objects.get("Moon")
if not moon:
    print("Moon objesi bulunamadı.")
else:
    # Önceki kamera çizgileri ve küreleri sil
    for obj in bpy.data.objects:
        if obj.name.endswith("_Line_Obj") or obj.name.startswith("Camera_Line_Hit_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Var olan küpü bul veya oluştur
    orbiter = bpy.data.objects.get("Orbiter")
    if not orbiter:
        bpy.ops.mesh.primitive_cube_add(location=(1.5, 0, 0))
        orbiter = bpy.context.object
        orbiter.name = "Orbiter"
        orbiter.data.name = "Orbiter_Mesh"
        orbiter.scale = (0.01, 0.01, 0.01)  # Daha küçük
        print("Yeni orbiter küpü oluşturuldu.")
    else:
        orbiter.location = (1.5, 0, 0)
        orbiter.scale = (0.01, 0.01, 0.01)
        print("Var olan orbiter bulundu ve konumlandı.")

    if "BlueOrbiterMaterial" in bpy.data.materials:
        blue_mat = bpy.data.materials["BlueOrbiterMaterial"]
    else:
        blue_mat = bpy.data.materials.new(name="BlueOrbiterMaterial")
        blue_mat.diffuse_color = (0, 0, 1, 1)

    orbiter.data.materials.clear()
    orbiter.data.materials.append(blue_mat)

    orbit_empty = bpy.data.objects.get("Orbiter_Empty")
    if orbit_empty:
        bpy.data.objects.remove(orbit_empty, do_unlink=True)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    orbit_empty = bpy.context.object
    orbit_empty.name = "Orbiter_Empty"
    orbiter.parent = orbit_empty

    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 2500

    orbit_empty.rotation_euler = (0, 0, 0)
    orbit_empty.keyframe_insert(data_path="rotation_euler", frame=1)
    orbit_empty.rotation_euler = (0, 0, math.radians(360))
    orbit_empty.keyframe_insert(data_path="rotation_euler", frame=2500)

    action = orbit_empty.animation_data.action
    fcurve = action.fcurves.find("rotation_euler", index=2)
    if fcurve:
        modifier = fcurve.modifiers.new(type='CYCLES')

    print("Orbiter küpü başarıyla yerleştirildi ve animasyon eklendi.")

    def create_camera(name, location):
        cam = bpy.data.objects.get(name)
        if not cam:
            bpy.ops.object.camera_add(location=location)
            cam = bpy.context.object
            cam.name = name
            print(f"Kamera '{name}' oluşturuldu.")
        else:
            print(f"Kamera '{name}' zaten var.")
        return cam

    camera1 = create_camera("Static_Camera_1", (2, 0, 0))
    camera2 = create_camera("Static_Camera_2", (0, 2, 0))

    # Mavi materyal (tüm çizgiler ve küreler için)
    blue_line_mat = bpy.data.materials.get("LineBlue")
    if not blue_line_mat:
        blue_line_mat = bpy.data.materials.new(name="LineBlue")
        blue_line_mat.diffuse_color = (0, 0, 1, 1)

    for cam in [camera1, camera2]:
        start = cam.location
        direction = (orbiter.location - start).normalized()
        end = start + direction * 1000

        curve_data = bpy.data.curves.new(name=f"{cam.name}_Line", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(1)
        spline.points[0].co = (*start, 1)
        spline.points[1].co = (*end, 1)
        curve_data.bevel_depth = 0.002

        curve_obj = bpy.data.objects.new(name=f"{cam.name}_Line_Obj", object_data=curve_data)
        curve_obj.data.materials.append(blue_line_mat)
        bpy.context.collection.objects.link(curve_obj)

        # Ay yüzeyi ile kesişim noktası hesapla
        moon_center = moon.location
        L = moon_center - start
        t_ca = L.dot(direction)
        d2 = L.length_squared - t_ca**2
        r2 = (moon.dimensions[0]/2)**2

        if d2 <= r2:
            t_hc = math.sqrt(r2 - d2)
            t = t_ca - t_hc
            hit_point = start + direction * t
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, location=hit_point)
            sphere = bpy.context.object
            sphere.name = f"Camera_Line_Hit_{cam.name}"
            sphere.data.materials.append(blue_line_mat)
            print(f"{cam.name} çizgisi için Ay yüzeyi kesişimi eklendi.")
