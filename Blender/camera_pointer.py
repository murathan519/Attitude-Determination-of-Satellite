import bpy
import math
from mathutils import Vector, Quaternion

# ---------- Kamera: Ay'ı gözlemleyen uydu gibi konumlandır ----------
    # Kamera oluştur veya mevcutsa al
camera = bpy.data.objects.get("Camera")
if not camera:
    cam_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(camera)
    
moon = bpy.data.objects.get("Moon")
if not moon:
    moon_data = bpy.data.cameras.new("Moon")
    moon = bpy.data.objects.new("Moon", moon_data)
    bpy.context.collection.objects.link(moon)

# Kameranın hedef yüzey koordinatları
target_lat = -47.0
target_lon = 90.0
surface_radius = 1  # Moon'un yüzeyi
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
direction = moon.location - camera.location
direction.normalize()
camera.rotation_mode = 'QUATERNION'
camera.rotation_quaternion = direction.to_track_quat('-Z', 'Y')

print(f"Kamera yerleştirildi: {target_lat}°, {target_lon}°, {altitude} birim yukarıda")