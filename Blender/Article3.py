import bpy
import math
import mathutils

def create_cylinder_between(p1, p2, radius=0.005, name="LineCylinder", color=(0.2, 0.5, 1.0, 1.0)):
    p1 = mathutils.Vector(p1)
    p2 = mathutils.Vector(p2)
    direction = p2 - p1
    length = direction.length
    midpoint = (p1 + p2) / 2

    # Silindir ekle
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=midpoint)
    obj = bpy.context.active_object
    obj.name = name

    # Yönünü hizala
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')

    # Malzeme
    mat = bpy.data.materials.get(f"{name}Material")
    if not mat:
        mat = bpy.data.materials.new(name=f"{name}Material")
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        for node in nodes:
            nodes.remove(node)

        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        output = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf.inputs["Base Color"].default_value = color
        mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    obj.data.materials.append(mat)
    return obj

def spherical_to_cartesian(lat_deg, lon_deg, radius=1.0):
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    x = radius * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lat)
    return (x, y, z)

# Nokta bilgileri (isim, lat, lon, renk)
points = [
    ("Ball Green", 40, 0, (0, 1, 0)),  
    ("Ball Yellow", -15, -60, (1, 1, 0))   
]

positions = {}  # Obje adlarıyla pozisyonları tutacağız

for name, lat, lon, color in points:
    # Eski nesne varsa sil
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    # Yeni konum
    pos = spherical_to_cartesian(lat, lon, radius=1.0)
    positions[name] = pos

    # Küçük bir UV Sphere oluştur
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=pos)
    dot = bpy.context.active_object
    dot.name = name  # Obje ismi ver

    # Malzeme oluştur
    mat = bpy.data.materials.get(f"{name}Material")
    if not mat:
        mat = bpy.data.materials.new(name=f"{name}Material")
        mat.diffuse_color = (*color, 1.0)
        mat.use_nodes = False
    dot.data.materials.append(mat)


#                               TOPLAR ARASI ÇİZGİ

# Eski çizgi varsa sil
line_name = "Line Blue"
if line_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[line_name], do_unlink=True)

# İki nokta arasında çizgi oluştur
p1 = positions["Ball Green"]
p2 = positions["Ball Yellow"]

create_cylinder_between(p1, p2, radius=0.007, name="Line Blue", color=(0.0, 0.3, 1.0, 1.0))



#                       KAMERA İLE ORTA NOKTA ARASI ÇİZGİ

cam_line_name = "Line Red"
if cam_line_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[cam_line_name], do_unlink=True)

# Orta nokta
v1 = mathutils.Vector(p1)
v2 = mathutils.Vector(p2)
midpoint = (v1 + v2) / 2

# Moon objesi
moon = bpy.data.objects.get("Moon")
if not moon:
    raise ValueError("Moon objesi sahnede bulunamadı.")
# Kamera objesi
camera = bpy.data.objects.get("Camera")
if not camera:
    raise ValueError("Camera objesi sahnede bulunamadı.")

moon_location = moon.location
cam_location = camera.location

# Kamera çizgisi: orta nokta → kamera
create_cylinder_between(moon_location, cam_location, radius=0.007, name="Line Red", color=(1, 0, 0, 1.0))




#                         PEMBE DÜZLEM – kırmızı çizgiye dik

# Eski düzlem varsa sil
plane_name = "Plane Pink"
if plane_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[plane_name], do_unlink=True)

# Kırmızı çizginin yön vektörü
direction = (cam_location - moon_location).normalized()

# Plane oluştur (bir yüzey)
bpy.ops.mesh.primitive_plane_add(size=2, location=midpoint)
plane = bpy.context.active_object
plane.name = plane_name

# Plane'in Z ekseni, çizgi yönüne dik olmalı → hizalama için quaternion kullan
# Plane'in yüzeyi Z ekseni boyunca dik çıkar, dolayısıyla onu çizgi yönüne dik çevirmeliyiz
plane.rotation_mode = 'QUATERNION'
# Düzlemin normali Z olduğu için: “Z yönü çizgiye dik olacak şekilde yönlen”
plane.rotation_quaternion = direction.to_track_quat('Z', 'Y')  # Z yönü çizgiye dik

# Malzeme oluştur ve ata (pembe renk)
mat = bpy.data.materials.get("PinkMaterial")
if not mat:
    mat = bpy.data.materials.new(name="PinkMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    output = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf.inputs["Base Color"].default_value = (1.0, 0.3, 0.6, 1.0)  # Pembe
    mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

plane.data.materials.append(mat)


#                     TOPLARDAN DÜZLEME DİK İNEN ÇİZGİLER

def project_point_onto_plane(point, plane_point, plane_normal):
    """Verilen noktayı bir düzleme dik izdüşümle yansıtır"""
    v = mathutils.Vector(point) - mathutils.Vector(plane_point)
    distance = v.dot(plane_normal)
    projected = mathutils.Vector(point) - distance * plane_normal
    return projected

# Her top için çizgi oluştur
for name in ["Ball Green", "Ball Yellow"]:
    p_top = mathutils.Vector(positions[name])
    p_plane = midpoint
    n_plane = direction.normalized()

    # Düzleme dik projeksiyon
    projected_point = project_point_onto_plane(p_top, p_plane, n_plane)

    # Renk
    color = (0, 1, 0, 1.0) if name == "Ball Green" else (1, 1, 0, 1.0)
    line_name = f"{name} To Plane"

    # Eski çizgi varsa sil
    if line_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[line_name], do_unlink=True)

    # Silindirik çizgi oluştur
    create_cylinder_between(p_top, projected_point, radius=0.005, name=line_name, color=color)


#                       KAHVERENGİ KAMERADA GÖRÜNEN MESAFE DOĞRUSU

# İzdüşüm noktalarını yeniden hesapla
proj_green = project_point_onto_plane(positions["Ball Green"], midpoint, direction.normalized())
proj_yellow = project_point_onto_plane(positions["Ball Yellow"], midpoint, direction.normalized())

# Çizgi ismi
black_line_name = "Line Black"
if black_line_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[black_line_name], do_unlink=True)

# Silindirik siyah çizgi
create_cylinder_between(proj_green, proj_yellow, radius=0.02, name=black_line_name, color=(0, 0, 0, 1.0))


# İzdüşüm noktalarına küçük siyah toplar (isimler benzersiz olsun)
for i, point in enumerate([proj_green, proj_yellow]):
    ball_name = f"Dot Black {i+1}"
    if ball_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[ball_name], do_unlink=True)

    # Küre oluştur
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=point)
    dot = bpy.context.active_object
    dot.name = ball_name

    # Siyah malzeme oluştur
    mat_name = "BlackDotMaterial"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.diffuse_color = (0, 0, 0, 1.0)
        mat.use_nodes = False
    dot.data.materials.append(mat)
    
   
   
   
# === Ball Green'den Plane Image düzlemine yeşil ışın ve top ===

green_ball = bpy.data.objects.get("Ball Green")
camera = bpy.data.objects.get("Camera")
plane = bpy.data.objects.get("Plane Image")

if green_ball and camera and plane:
    # Işın: Ball Green'den kameraya doğru
    ray_origin = green_ball.location
    ray_direction = (camera.location - ray_origin).normalized()

    def intersect_ray_plane(ray_origin, ray_direction, plane_obj):
        plane_point = plane_obj.location
        plane_normal = plane_obj.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))
        denom = ray_direction.dot(plane_normal)
        if abs(denom) < 1e-6:
            return None  # Paralel
        d = (plane_point - ray_origin).dot(plane_normal) / denom
        if d < 0:
            return None  # Geride kalıyor
        return ray_origin + ray_direction * d

    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Önceki objeleri sil
        for obj_name in ["Line Green Plane", "Ball Green Hit"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Green Plane", color=(0, 1, 0, 1))

        # Hit noktaya küçük yeşil top
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        hit_ball = bpy.context.active_object
        hit_ball.name = "Ball Green Hit"

        mat = bpy.data.materials.get("Ball Green Material")
        if not mat:
            mat = bpy.data.materials.new(name="Ball Green Material")
            mat.diffuse_color = (0, 1, 0, 1)
            mat.use_nodes = False
        hit_ball.data.materials.append(mat)

    else:
        print("Yeşil ışın Plane Image düzlemine çarpmadı.")
else:
    print("Ball Green, Camera veya Plane Image objesi eksik.")
    
    
    
# === Ball Yellow'dan Plane Image düzlemine sarı ışın ve top ===

yellow_ball = bpy.data.objects.get("Ball Yellow")
camera = bpy.data.objects.get("Camera")
plane = bpy.data.objects.get("Plane Image")

if yellow_ball and camera and plane:
    # Işın: Ball Yellow'dan kameraya doğru
    ray_origin = yellow_ball.location
    ray_direction = (camera.location - ray_origin).normalized()

    def intersect_ray_plane(ray_origin, ray_direction, plane_obj):
        plane_point = plane_obj.location
        plane_normal = plane_obj.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))
        denom = ray_direction.dot(plane_normal)
        if abs(denom) < 1e-6:
            return None
        d = (plane_point - ray_origin).dot(plane_normal) / denom
        if d < 0:
            return None
        return ray_origin + ray_direction * d

    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Önceki objeleri sil
        for obj_name in ["Line Yellow Plane", "Ball Yellow Hit"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgiyi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Yellow Plane", color=(1, 1, 0, 1))

        # Hit noktaya küçük sarı top
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        hit_ball = bpy.context.active_object
        hit_ball.name = "Ball Yellow Hit"

        mat = bpy.data.materials.get("Ball Yellow Material")
        if not mat:
            mat = bpy.data.materials.new(name="Ball Yellow Material")
            mat.diffuse_color = (1, 1, 0, 1)
            mat.use_nodes = False
        hit_ball.data.materials.append(mat)

    else:
        print("Sarı ışın Plane Image düzlemine çarpmadı.")
else:
    print("Ball Yellow, Camera veya Plane Image objesi eksik.")
    

    
# === YEŞİL ve SARI TOPLARIN Plane Image'deki versiyonları arasında siyah çizgi ===

green_hit = bpy.data.objects.get("Ball Green Hit")
yellow_hit = bpy.data.objects.get("Ball Yellow Hit")
camera = bpy.data.objects.get("Camera")

if green_hit and yellow_hit and camera:
    p_green = green_hit.location
    p_yellow = yellow_hit.location

    # Önce eski siyah çizgi varsa sil
    if "Line Black Plane" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Line Black Plane"], do_unlink=True)

    # Çizgi oluştur
    create_cylinder_between(p_green, p_yellow, radius=0.02, name="Line Black Plane", color=(0, 0, 0, 1))
else:
    print("Gerekli objelerden biri (Ball Green Hit, Ball Yellow Hit, Camera) bulunamadı.")
    
    
    
# === KIRMIZI IŞININ ARKA TARAFA UZATILMASI ===

plane = bpy.data.objects.get("Plane Image")  # Arka düzlem

if camera and plane:
    ray_origin = camera.location
    ray_direction = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))  # -Z yönünün tersi = arkaya

    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Önceki objeleri sil
        for obj_name in ["Line Red Back", "Red Ball Back"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgiyi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Red Back", color=(1, 0, 0, 1))

        # Kırmızı top ekle
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        sphere = bpy.context.active_object
        sphere.name = "Red Ball Back"

        mat = bpy.data.materials.get("HitMaterialBack")
        if not mat:
            mat = bpy.data.materials.new(name="HitMaterialBack")
            mat.diffuse_color = (1, 0, 0, 1)
            mat.use_nodes = False
        sphere.data.materials.append(mat)
    else:
        print("Kırmızı ışın Plane Image düzlemine çarpmadı.")
else:
    print("Camera veya Plane Image bulunamadı.")


for obj in bpy.data.objects:
    if obj.name.startswith("Line") and obj.type == 'MESH':
        # Eevee için gölgeyi kapat (Blender 3.6+)
        if hasattr(obj, "visible_shadow"):
            obj.visible_shadow = False

        # Cycles kullanıyorsan aşağıdaki satır da çalışır
        if hasattr(obj, "cycles_visibility"):
            obj.cycles_visibility.shadow = False
