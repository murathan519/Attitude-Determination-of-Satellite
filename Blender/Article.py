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
    ("Ball Green", 15, 10, (0, 1, 0)),  
    ("Ball Yellow", 5, -40, (1, 1, 0))   
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

# Kamera objesi
camera = bpy.data.objects.get("Camera")
if not camera:
    raise ValueError("Camera objesi sahnede bulunamadı.")
cam_location = camera.location

# Kamera çizgisi: orta nokta → kamera
create_cylinder_between(midpoint, cam_location, radius=0.007, name="Line Red", color=(1, 0, 0, 1.0))




#                         PEMBE DÜZLEM – kırmızı çizgiye dik

# Eski düzlem varsa sil
plane_name = "Plane Pink"
if plane_name in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects[plane_name], do_unlink=True)

# Kırmızı çizginin yön vektörü
direction = (cam_location - midpoint).normalized()

# Plane oluştur (bir yüzey)
bpy.ops.mesh.primitive_plane_add(size=0.6, location=midpoint)
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
create_cylinder_between(proj_green, proj_yellow, radius=0.005, name=black_line_name, color=(0, 0, 0, 1.0))


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
