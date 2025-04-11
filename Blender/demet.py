import bpy
import math
from mathutils import Vector

# ---------- Ay objesini al ----------
moon = bpy.data.objects.get("Moon")
if not moon:
    print("Moon objesi bulunamadı.")
else:
        # ---------- Eski çizgiler ve işaretçi küreleri sil ----------
    for child in moon.children:
        if (
            child.name.startswith("Moon_Marker_") or
            child.name in {"Moon_Arc", "Moon_Marker_Line", "Camera_Line"}
        ):
            bpy.data.objects.remove(child, do_unlink=True)

    # ---------- Önceki işaretçileri sil ----------
    for child in moon.children:
        if child.name.startswith("Moon_Marker_"):
            bpy.data.objects.remove(child, do_unlink=True)

    # ---------- ENLEM / BOYLAM VERİLERİ ----------
    coords = [
        {"lat": 10, "lon": 10, "color": "RED"},   # İlk küre (kırmızı)
        {"lat": -10, "lon": -10, "color": "BLUE"} # İkinci küre (mavi)
    ]

    # ---------- Materyal oluştur (gerekirse) ----------
    def get_material(name, color):
        if name in bpy.data.materials:
            return bpy.data.materials[name]
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = color
        return mat

    red_mat = get_material("SmallRedMaterial", (1, 0, 0, 1))   # RGBA
    blue_mat = get_material("SmallBlueMaterial", (0, 0, 1, 1)) # RGBA

    # ---------- Yarıçap ayarı ----------
    moon_radius = moon.dimensions[0] / 2
    base_radius = moon_radius * 0.03
    small_radius = base_radius / 2

    # ---------- Küreleri yerleştir ----------
    for i, coord in enumerate(coords, start=1):
        lat_rad = math.radians(coord["lat"])
        lon_rad = math.radians(coord["lon"])

        x = moon_radius * math.cos(lat_rad) * math.cos(lon_rad)
        y = moon_radius * math.cos(lat_rad) * math.sin(lon_rad)
        z = moon_radius * math.sin(lat_rad)
        position = Vector((x, y, z))

        bpy.ops.mesh.primitive_uv_sphere_add(location=position, radius=small_radius)
        marker = bpy.context.object
        marker.name = f"Moon_Marker_{coord['lat']}_{coord['lon']}"
        marker.parent = moon

        # Materyal ata
        if coord["color"] == "RED":
            marker.data.materials.append(red_mat)
        elif coord["color"] == "BLUE":
            marker.data.materials.append(blue_mat)

        print(f"{coord['color']} küre yerleştirildi: Enlem {coord['lat']}°, Boylam {coord['lon']}°")


            # ---------- Küre yüzeyi boyunca eğri çizgi (arc) ----------
    if "GreenArcMaterial" in bpy.data.materials:
        arc_mat = bpy.data.materials["GreenArcMaterial"]
    else:
        arc_mat = bpy.data.materials.new(name="GreenArcMaterial")
        arc_mat.diffuse_color = (0, 1, 0, 1)

    if len(coords) >= 2:
        marker1 = bpy.data.objects.get(f"Moon_Marker_{coords[0]['lat']}_{coords[0]['lon']}")
        marker2 = bpy.data.objects.get(f"Moon_Marker_{coords[1]['lat']}_{coords[1]['lon']}")

        if marker1 and marker2:
            p1 = marker1.location.normalized()
            p2 = marker2.location.normalized()

            # Arayı böl
            arc_points = []
            segments = 64
            for i in range(segments + 1):
                t = i / segments
                # Küresel interpolasyon (slerp)
                interp = p1.lerp(p2, t)
                interp.normalize()
                arc_point = interp * moon_radius
                arc_points.append(arc_point)

            # Curve oluştur
            curve_data = bpy.data.curves.new("Moon_Arc_Curve", type='CURVE')
            curve_data.dimensions = '3D'
            spline = curve_data.splines.new('POLY')
            spline.points.add(len(arc_points) - 1)
            for i, pt in enumerate(arc_points):
                spline.points[i].co = (*pt, 1)

            curve_data.bevel_depth = moon_radius * 0.002
            curve_obj = bpy.data.objects.new("Moon_Arc", curve_data)
            curve_obj.data.materials.append(arc_mat)
            curve_obj.parent = moon
            bpy.context.collection.objects.link(curve_obj)

            print("Ay yüzeyi boyunca yeşil bir eğri çizildi.")

            # ---------- Sarı materyal oluştur ----------
    if "YellowMaterial" in bpy.data.materials:
        yellow_mat = bpy.data.materials["YellowMaterial"]
    else:
        yellow_mat = bpy.data.materials.new(name="YellowMaterial")
        yellow_mat.diffuse_color = (1, 1, 0, 1)  # RGBA: Sarı

    # ---------- Kamera objesi ve çizgi ----------
    camera = bpy.data.objects.get("Camera")
    if camera:
        cam_pos = camera.location
        moon_pos = moon.location
        direction = (moon_pos - cam_pos).normalized()
        hit_point = moon_pos - direction * moon_radius  # Ay yüzeyiyle temas noktası

        # Çizgiyi oluştur
        curve_data = bpy.data.curves.new(name="Camera_To_Moon_Line", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(1)
        spline.points[0].co = (*cam_pos, 1)
        spline.points[1].co = (*hit_point, 1)

        curve_data.bevel_depth = moon_radius * 0.002
        curve_obj = bpy.data.objects.new("Camera_Line", curve_data)
        curve_obj.data.materials.append(yellow_mat)
        curve_obj.parent = moon
        bpy.context.collection.objects.link(curve_obj)

        # Küçük sarı küre oluştur (öncekilerle aynı boyutta)
        bpy.ops.mesh.primitive_uv_sphere_add(location=hit_point, radius=small_radius)
        marker = bpy.context.object
        marker.name = "Moon_Marker_Camera_Hit"
        marker.data.materials.append(yellow_mat)
        marker.parent = moon

        print("Kameradan Ay'a sarı çizgi çizildi ve yüzeye küçük sarı küre yerleştirildi.")
    else:
        print("Camera objesi bulunamadı.")
        
        # ---------- Kameranın baktığı noktaya çizgi ----------
    if "Camera_Look_Line" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera_Look_Line"], do_unlink=True)

    if "CameraLookMaterial" in bpy.data.materials:
        look_mat = bpy.data.materials["CameraLookMaterial"]
    else:
        look_mat = bpy.data.materials.new(name="CameraLookMaterial")
        look_mat.diffuse_color = (1, 1, 0, 1)  # Sarı

    if camera:
        # Kameranın baktığı yön: local -Z ekseni
        look_dir = camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
        look_dir.normalize()

        # Ay yüzeyine çarpacağı nokta (kabaca Ay merkezine kadar gider ve durur)
        cam_to_moon = moon.location - camera.location
        proj_len = cam_to_moon.dot(look_dir)
        projected = camera.location + look_dir * proj_len

        # Bu vektörü normalize edip Ay yüzeyine yapıştıralım
        hit_point = moon.location + (projected - moon.location).normalized() * moon_radius

        # Çizgi oluştur
        curve_data = bpy.data.curves.new(name="Camera_Look_Curve", type='CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new(type='POLY')
        spline.points.add(1)
        spline.points[0].co = (*camera.location, 1)
        spline.points[1].co = (*hit_point, 1)

        curve_data.bevel_depth = moon_radius * 0.002
        curve_obj = bpy.data.objects.new("Camera_Look_Line", curve_data)
        curve_obj.data.materials.append(look_mat)
        curve_obj.parent = moon
        bpy.context.collection.objects.link(curve_obj)

        print("Kameranın baktığı noktaya sarı çizgi çizildi.")
        
        # ---------- Kameranın baktığı noktaya çizgi (pembe renkli) ----------

    # Eski çizgi ve işaretçiyi sil
    if "Camera_Look_Line" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera_Look_Line"], do_unlink=True)
    if "Moon_Marker_Camera_Look" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Moon_Marker_Camera_Look"], do_unlink=True)

    # PEMBE materyal oluştur
    if "PinkLookMaterial" in bpy.data.materials:
        pink_mat = bpy.data.materials["PinkLookMaterial"]
    else:
        pink_mat = bpy.data.materials.new(name="PinkLookMaterial")
        pink_mat.diffuse_color = (1, 0, 1, 1)  # RGBA: pembe

    if camera:
        from math import sqrt

        look_dir = camera.matrix_world.to_3x3() @ Vector((0, 0, -1))
        look_dir.normalize()
        origin = camera.location

        L = moon.location - origin
        t_ca = L.dot(look_dir)
        d2 = L.length_squared - t_ca**2
        r2 = moon_radius**2

        if d2 <= r2:
            t_hc = sqrt(r2 - d2)
            t = t_ca - t_hc
            hit_point = origin + look_dir * t

            # Çizgi oluştur
            curve_data = bpy.data.curves.new(name="Camera_Look_Curve", type='CURVE')
            curve_data.dimensions = '3D'
            spline = curve_data.splines.new(type='POLY')
            spline.points.add(1)
            spline.points[0].co = (*origin, 1)
            spline.points[1].co = (*hit_point, 1)

            curve_data.bevel_depth = moon_radius * 0.002
            curve_obj = bpy.data.objects.new("Camera_Look_Line", curve_data)
            curve_obj.data.materials.append(pink_mat)
            curve_obj.parent = moon
            bpy.context.collection.objects.link(curve_obj)

            # Pembe küre yerleştir
            bpy.ops.mesh.primitive_uv_sphere_add(location=hit_point, radius=small_radius)
            hit_marker = bpy.context.object
            hit_marker.name = "Moon_Marker_Camera_Look"
            hit_marker.data.materials.append(pink_mat)
            hit_marker.parent = moon

            print("Kamera yönü Ay yüzeyine doğru çizildi ve PEMBE işaretlendi.")
        else:
            print("Kamera yönü Ay yüzeyiyle kesişmiyor.")
            
        # ---------- Kameradan tüm işaretçilere (coords) çizgi ----------

    # Önceki çizgileri sil
    for obj in bpy.data.objects:
        if obj.name.startswith("Camera_To_Marker_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Materyal havuzu
    def ensure_material(name, rgba):
        if name in bpy.data.materials:
            return bpy.data.materials[name]
        mat = bpy.data.materials.new(name=name)
        mat.diffuse_color = rgba
        return mat

    color_materials = {
        "RED": ensure_material("CameraLine_Red", (1, 0, 0, 1)),
        "BLUE": ensure_material("CameraLine_Blue", (0, 0, 1, 1)),
        "GREEN": ensure_material("CameraLine_Green", (0, 1, 0, 1)),
        "YELLOW": ensure_material("CameraLine_Yellow", (1, 1, 0, 1)),
        "PINK": ensure_material("CameraLine_Pink", (1, 0, 1, 1))
    }

    if camera:
        for coord in coords:
            lat = coord["lat"]
            lon = coord["lon"]
            color = coord["color"]

            marker_name = f"Moon_Marker_{lat}_{lon}"
            marker_obj = bpy.data.objects.get(marker_name)

            if marker_obj and color in color_materials:
                curve_data = bpy.data.curves.new(name=f"Camera_To_{marker_name}", type='CURVE')
                curve_data.dimensions = '3D'
                spline = curve_data.splines.new(type='POLY')
                spline.points.add(1)
                spline.points[0].co = (*camera.location, 1)
                spline.points[1].co = (*marker_obj.location, 1)

                curve_data.bevel_depth = moon_radius * 0.002
                curve_obj = bpy.data.objects.new(f"Camera_To_Marker_{color}", curve_data)
                curve_obj.data.materials.append(color_materials[color])
                curve_obj.parent = moon
                bpy.context.collection.objects.link(curve_obj)

        print("Kameradan tüm işaretçilere çizgiler çizildi.")

        # ---------- Sarı toptan diğer markerlara yeşil yay (arc) çiz ----------
    arc_material = bpy.data.materials.get("GreenArcMaterial")
    if not arc_material:
        arc_material = bpy.data.materials.new(name="GreenArcMaterial")
        arc_material.diffuse_color = (0, 1, 0, 1)

    # Önceki yayları sil
    for obj in bpy.data.objects:
        if obj.name.startswith("Camera_Hit_Arc_to_"):
            bpy.data.objects.remove(obj, do_unlink=True)

    # Sarı top (kamera - Ay merkezine olan çizginin ucu)
    yellow_marker = bpy.data.objects.get("Moon_Marker_Camera_Hit")

    if yellow_marker:
        yellow_pos = yellow_marker.location.normalized()

        for coord in coords:
            marker_name = f"Moon_Marker_{coord['lat']}_{coord['lon']}"
            marker = bpy.data.objects.get(marker_name)

            if marker:
                target_pos = marker.location.normalized()

                arc_points = []
                segments = 64
                for i in range(segments + 1):
                    t = i / segments
                    interp = yellow_pos.lerp(target_pos, t)
                    interp.normalize()
                    arc_points.append(interp * moon_radius)

                # Curve oluştur
                curve_data = bpy.data.curves.new(name=f"Camera_Hit_Arc_to_{coord['color']}", type='CURVE')
                curve_data.dimensions = '3D'
                spline = curve_data.splines.new('POLY')
                spline.points.add(len(arc_points) - 1)
                for i, pt in enumerate(arc_points):
                    spline.points[i].co = (*pt, 1)

                curve_data.bevel_depth = moon_radius * 0.002
                curve_obj = bpy.data.objects.new(f"Camera_Hit_Arc_to_{coord['color']}", curve_data)
                curve_obj.data.materials.append(arc_material)
                curve_obj.parent = moon
                bpy.context.collection.objects.link(curve_obj)

        print("Sarı toptan kırmızı ve mavi toplara yeşil yaylar çizildi.")
    else:
        print("Sarı top (Moon_Marker_Camera_Hit) bulunamadı.")




