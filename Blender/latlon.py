import bpy
import math
from mathutils import Vector, Quaternion

# ---------- Fonksiyon: Etiketleri düzgün hizalamak için ----------
def orient_text_outward(text_obj, center_obj):
    outward = (text_obj.location - center_obj.location)
    if outward.length < 1e-6:
        return
    outward.normalize()
    quat = outward.to_track_quat('-Z', 'Y')
    rot_180_y = Quaternion((0, 1, 0), math.radians(180))
    final_quat = quat @ rot_180_y
    text_obj.rotation_quaternion = final_quat
    text_obj.rotation_euler = final_quat.to_euler()

# ---------- Ana obje: Moon ----------
moon_obj = bpy.data.objects.get("Moon")
if not moon_obj:
    print("Moon objesi bulunamadı.")
else:
    # ---------- Eski çizgileri ve yazıları temizle ----------
    for child in moon_obj.children:
        if child.name.startswith("Meridian_") or child.name.startswith("Parallel_"):
            bpy.data.objects.remove(child, do_unlink=True)
        elif child.type == 'FONT' and child.data.body.strip().endswith("°"):
            bpy.data.objects.remove(child, do_unlink=True)
        elif child.name.startswith("Moon_Marker_"):
            bpy.data.objects.remove(child, do_unlink=True)

    # ---------- Malzemeler ----------
    if "RedMaterial" in bpy.data.materials:
        red_mat = bpy.data.materials["RedMaterial"]
    else:
        red_mat = bpy.data.materials.new(name="RedMaterial")
        red_mat.diffuse_color = (1, 0, 0, 1)

    if "GreenMaterial" in bpy.data.materials:
        green_mat = bpy.data.materials["GreenMaterial"]
    else:
        green_mat = bpy.data.materials.new(name="GreenMaterial")
        green_mat.diffuse_color = (0, 1, 0, 1)

    if "BlueMaterial" in bpy.data.materials:
        blue_mat = bpy.data.materials["BlueMaterial"]
    else:
        blue_mat = bpy.data.materials.new(name="BlueMaterial")
        blue_mat.diffuse_color = (0, 0, 1, 1)

    # ---------- Ay yarıçapı ----------
    radius = moon_obj.dimensions[0] / 2
    text_offset = 0.05 * radius

    # ---------- Meridyenler ----------
    for angle in range(0, 360, 10):
        curve_data = bpy.data.curves.new(name=f"Meridian_{angle}", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='POLY')
        spline.use_cyclic_u = False
        num_points = 50
        spline.points.add(num_points - 1)
        for i in range(num_points):
            theta = math.pi * i / (num_points - 1)
            x = radius * math.sin(theta) * math.cos(math.radians(angle))
            y = radius * math.sin(theta) * math.sin(math.radians(angle))
            z = radius * math.cos(theta)
            spline.points[i].co = (x, y, z, 1)
        obj = bpy.data.objects.new(f"Meridian_{angle}", curve_data)
        bpy.context.collection.objects.link(obj)
        curve_data.bevel_depth = radius * 0.005
        obj.data.materials.append(red_mat)
        obj.parent = moon_obj

        # Etiket
        label_x = radius * math.cos(math.radians(angle))
        label_y = radius * math.sin(math.radians(angle))
        label_z = text_offset
        bpy.ops.object.text_add(location=(label_x, label_y, label_z))
        text = bpy.context.object
        text.data.body = f"{angle}°"
        text.data.align_x = 'CENTER'
        text.data.align_y = 'CENTER'
        text.data.size = radius * 0.1
        text.data.materials.append(green_mat)
        text.parent = moon_obj
        orient_text_outward(text, moon_obj)

    # ---------- Paraleller ----------
    for lat in range(-80, 90, 10):
        theta = math.radians(90 - lat)
        circle_radius = radius * math.sin(theta)
        z = radius * math.cos(theta)

        curve_data = bpy.data.curves.new(name=f"Parallel_{lat}", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='POLY')
        spline.use_cyclic_u = True
        num_points = 50
        spline.points.add(num_points)
        for i in range(num_points + 1):
            phi = 2 * math.pi * i / num_points
            x = circle_radius * math.cos(phi)
            y = circle_radius * math.sin(phi)
            spline.points[i].co = (x, y, z, 1)
        obj = bpy.data.objects.new(f"Parallel_{lat}", curve_data)
        bpy.context.collection.objects.link(obj)
        curve_data.bevel_depth = radius * 0.005
        obj.data.materials.append(red_mat)
        obj.parent = moon_obj

        # Etiket
        label_x = circle_radius + text_offset
        label_y = 0
        label_z = z
        bpy.ops.object.text_add(location=(label_x, label_y, label_z))
        text = bpy.context.object
        text.data.body = f"{lat}°"
        text.data.align_x = 'CENTER'
        text.data.align_y = 'CENTER'
        text.data.size = radius * 0.1
        text.data.materials.append(green_mat)
        text.parent = moon_obj
        orient_text_outward(text, moon_obj)

    # ---------- Koordinatla küp yerleştir ----------
    latitude_deg = 74.6     # ← burayı değiştirerek istediğin noktaya işaret koyabilirsin
    longitude_deg = 37.5

    lat_rad = math.radians(latitude_deg)
    lon_rad = math.radians(longitude_deg)

    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)

    position = Vector((x, y, z))
    bpy.ops.mesh.primitive_cube_add(size=radius * 0.01, location=position)
    cube = bpy.context.object
    cube.name = f"Moon_Marker_{latitude_deg}_{longitude_deg}"
    cube.data.name = cube.name
    cube.data.materials.append(blue_mat)

    outward = (position - moon_obj.location).normalized()
    cube.rotation_mode = 'QUATERNION'
    cube.rotation_quaternion = outward.to_track_quat('Z', 'Y')
    cube.parent = moon_obj

    print(f"Küp yerleştirildi: {latitude_deg}°, {longitude_deg}°")
    
    
        # ---------- Kamera: Ay'ı gözlemleyen uydu gibi konumlandır ----------
    # Kamera oluştur veya mevcutsa al
    camera = bpy.data.objects.get("Camera")
    if not camera:
        cam_data = bpy.data.cameras.new("Camera")
        camera = bpy.data.objects.new("Camera", cam_data)
        bpy.context.collection.objects.link(camera)

    # Kameranın hedef yüzey koordinatları
    target_lat = -62.0
    target_lon = 75.0
    surface_radius = radius  # Moon'un yüzeyi
    altitude = 0.75  # Yüzeyden yükseklik
    total_distance = surface_radius + altitude

    # Hedef noktanın dünya koordinatları
    lat_rad = math.radians(target_lat)
    lon_rad = math.radians(target_lon)
    x = total_distance * math.cos(lat_rad) * math.cos(lon_rad)
    y = total_distance * math.cos(lat_rad) * math.sin(lon_rad)
    z = total_distance * math.sin(lat_rad)
    cam_position = Vector((x, y, z))
    camera.location = cam_position

    # Kamerayı Moon merkezine döndür
    direction = moon_obj.location - camera.location
    direction.normalize()
    camera.rotation_mode = 'QUATERNION'
    camera.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

    print(f"Kamera yerleştirildi: {target_lat}°, {target_lon}°, {altitude} birim yukarıda")
