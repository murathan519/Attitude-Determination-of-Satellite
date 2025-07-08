import bpy
import math
import mathutils

# Silindirik çizgi oluşturma fonksiyonu
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

# Küresel koordinatı kartezyene çevirme
def spherical_to_cartesian(lat_deg, lon_deg, radius=1.0):
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    x = radius * math.cos(lat) * math.cos(lon)
    y = radius * math.cos(lat) * math.sin(lon)
    z = radius * math.sin(lat)
    return (x, y, z)

# Önce önceki çizgiler ve nokta varsa sil
for obj_name in ["Line Blue", "Line Red", "Hit Point"]:
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

# === YEŞİL ve SARI TOPLAR ===
points = [
    ("Ball Green", 15, 20, (0, 1, 0)),  
    ("Ball Yellow", 15, -10, (1, 1, 0))   
]

positions = {}

for name, lat, lon, color in points:
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)

    pos = spherical_to_cartesian(lat, lon, radius=1.0)
    positions[name] = pos

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=pos)
    dot = bpy.context.active_object
    dot.name = name

    mat = bpy.data.materials.get(f"{name}Material")
    if not mat:
        mat = bpy.data.materials.new(name=f"{name}Material")
        mat.diffuse_color = (*color, 1.0)
        mat.use_nodes = False
    dot.data.materials.append(mat)

# === KAMERA’DAN MOON’A IŞIN GÖNDERME ===

camera = bpy.data.objects.get("Camera")
moon = bpy.data.objects.get("Moon")

if not camera or not moon:
    raise ValueError("Camera veya Moon objesi sahnede bulunamadı.")

ray_origin = camera.location
ray_direction = -camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))  # lens yönü
    

# === KAMERA ARKASINA KÜP EKLE ===

# Eski küp varsa sahneden ve veriden tamamen sil
cube_name = "Camera Back Cube"
cube_obj = bpy.data.objects.get(cube_name)
if cube_obj:
    bpy.context.collection.objects.unlink(cube_obj)
    bpy.data.objects.remove(cube_obj, do_unlink=True)

# Kamera'nın -Z yönü (bakış yönünün tersi)
back_dir = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))  # arkaya doğru
cube_depth = 2.0
offset = back_dir.normalized() * (cube_depth / 2)
cube_location = camera.location + offset

# Küp oluştur
bpy.ops.mesh.primitive_cube_add(size=cube_depth, location=cube_location)
cube = bpy.context.active_object
cube.name = cube_name

# Kamera yönüne göre döndür
cube.rotation_mode = 'QUATERNION'
cam_forward = -camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, -1))
cube.rotation_quaternion = cam_forward.to_track_quat('Z', 'Y')

# Malzeme ata (gri)
mat = bpy.data.materials.get("BackCubeMaterial")
if not mat:
    mat = bpy.data.materials.new(name="BackCubeMaterial")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    for node in nodes:
        nodes.remove(node)
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    output = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    mat.node_tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
cube.data.materials.append(mat)


# === KÜP YÜZEYLERİNE PLANE EKLE ===

# Önceki Plane'leri sahneden ve Blender verisinden tamamen sil
for obj_name in ["Plane Perspective", "Plane Image"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        bpy.context.collection.objects.unlink(obj)
        bpy.data.objects.remove(obj, do_unlink=True)
        
# Küp boyutu
cube_size = cube.dimensions.x  # Küp eşkenar olduğu için x, y, z aynı

# Küpün orta noktası ve yönü
cube_center = cube.location
quat = cube.rotation_quaternion

# Küpün yerel -Z yönü (kamera tarafına bakan yüzey)
local_minus_z = mathutils.Vector((0, 0, -1))
face_persp_normal = quat @ local_minus_z
face_persp_center = cube_center + face_persp_normal * (cube_size / 2)

# Karşı yüz: +Z yönü (arkaya bakan)
face_image_normal = quat @ mathutils.Vector((0, 0, 1))
face_image_center = cube_center + face_image_normal * (cube_size / 2)

# Perspective yüzeyi
bpy.ops.mesh.primitive_plane_add(size=cube_size, location=face_persp_center)
plane_persp = bpy.context.active_object
plane_persp.name = "Plane Image"
plane_persp.rotation_mode = 'QUATERNION'
plane_persp.rotation_quaternion = quat

# Image yüzeyi
bpy.ops.mesh.primitive_plane_add(size=cube_size, location=face_image_center)
plane_image = bpy.context.active_object
plane_image.name = "Plane Perspective"
plane_image.rotation_mode = 'QUATERNION'
plane_image.rotation_quaternion = quat

# === Plane'leri küpün çocuğu yap ===

# Plane'leri ve küpü al
plane_image = bpy.data.objects.get("Plane Image")
plane_persp = bpy.data.objects.get("Plane Perspective")
cam = bpy.data.objects.get("Camera")
cube = bpy.data.objects.get("Camera Back Cube")

if cube and plane_image and plane_persp:
    plane_image.parent = cube
    plane_persp.parent = cube
    cam.parent = cube
    plane_image.matrix_parent_inverse = cube.matrix_world.inverted()
    plane_persp.matrix_parent_inverse = cube.matrix_world.inverted()
    cam.matrix_parent_inverse = cube.matrix_world.inverted()
else:
    print("Küp veya plane objeleri bulunamadı.")



# === SARI IŞIN: Ball Yellow'dan çıkan ve Camera objesinden geçen, Plane Image düzlemine çarpan ===

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

# Gerekli objeleri al
yellow_ball = bpy.data.objects.get("Ball Yellow")
camera = bpy.data.objects.get("Camera")
plane = bpy.data.objects.get("Plane Image")

if yellow_ball and camera and plane:
    ray_origin = yellow_ball.location
    ray_direction = (camera.location - ray_origin).normalized()
    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Eski sarı çizgi ve topu sil
        for obj_name in ["Line Yellow", "Ball Yellow Hit"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgiyi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Yellow", color=(1, 1, 0, 1))

        # Sarı top ekle
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        sphere = bpy.context.active_object
        sphere.name = "Ball Yellow Hit"

        mat = bpy.data.materials.get("Ball Yellow Material")
        if not mat:
            mat = bpy.data.materials.new(name="Ball Yellow Material")
            mat.diffuse_color = (1, 1, 0, 1)
            mat.use_nodes = False
        sphere.data.materials.append(mat)
    else:
        print("Sarı ışın Plane Image düzlemine çarpmadı.")
else:
    print("Ball Yellow, Camera veya Plane Image bulunamadı.")
    
    # === YEŞİL IŞIN: Ball Green'den çıkan ve Camera objesinden geçen, Plane Image düzlemine çarpan ===

green_ball = bpy.data.objects.get("Ball Green")

if green_ball and camera and plane:
    ray_origin = green_ball.location
    ray_direction = (camera.location - ray_origin).normalized()
    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Eski yeşil çizgi ve topu sil
        for obj_name in ["Line Green", "Ball Green Hit"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgiyi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Green", color=(0, 1, 0, 1))

        # Yeşil top ekle
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        sphere = bpy.context.active_object
        sphere.name = "Ball Green Hit"

        mat = bpy.data.materials.get("Ball Green Material")
        if not mat:
            mat = bpy.data.materials.new(name="Ball Green Material")
            mat.diffuse_color = (0, 1, 0, 1)
            mat.use_nodes = False
        sphere.data.materials.append(mat)
    else:
        print("Yeşil ışın Plane Image düzlemine çarpmadı.")
else:
    print("Ball Green, Camera veya Plane Image bulunamadı.")
   

# === KAMERA +Z YÖNÜNDEN MOON'A DOĞRU KIRMIZI IŞIN VE TOP ===

for obj_name in ["Line Red Forward", "Hit Pooint Forward"]:
    obj = bpy.data.objects.get(obj_name)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)


origin = camera.location
direction = mathutils.Vector((-1, 0, 0))  # +Z yönü
end_point = origin + direction * 100

def create_cylinder_between(p1, p2, radius=0.005, name="Line Red Forward", color=(1, 0, 0, 1)):
    p1 = mathutils.Vector(p1)
    p2 = mathutils.Vector(p2)
    direction = p2 - p1
    length = direction.length
    midpoint = (p1 + p2) / 2

    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=midpoint)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_mode = 'QUATERNION'
    obj.rotation_quaternion = direction.to_track_quat('Z', 'Y')

    # Malzeme
    mat = bpy.data.materials.get(name + "Mat")
    if not mat:
        mat = bpy.data.materials.new(name + "Mat")
        mat.diffuse_color = color
        mat.use_nodes = False
    obj.data.materials.append(mat)

    return obj

create_cylinder_between(origin, end_point)
 
    # === KIRMIZI IŞININ ARKA TARAFA UZATILMASI ===

plane = bpy.data.objects.get("Plane Image")  # Arka düzlem

if camera and plane:
    ray_origin = camera.location
    ray_direction = camera.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))  # -Z yönünün tersi = arkaya

    hit_point = intersect_ray_plane(ray_origin, ray_direction, plane)

    if hit_point:
        # Önceki objeleri sil
        for obj_name in ["Line Red Back", "Hit Point Back"]:
            obj = bpy.data.objects.get(obj_name)
            if obj:
                bpy.data.objects.remove(obj, do_unlink=True)

        # Çizgiyi oluştur
        create_cylinder_between(ray_origin, hit_point, radius=0.005, name="Line Red Back", color=(1, 0, 0, 1))

        # Kırmızı top ekle
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=hit_point)
        sphere = bpy.context.active_object
        sphere.name = "Hit Point Back"

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


