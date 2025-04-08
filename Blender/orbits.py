import bpy
import math

# Ay objesi
moon = bpy.data.objects.get("Moon")
if not moon:
    print("Moon objesi bulunamadı.")
else:
    # Var olan küreyi bul veya oluştur
    # Var olan küreyi bul veya oluştur
    orbiter = bpy.data.objects.get("Orbiter")
    if not orbiter:
        bpy.ops.mesh.primitive_uv_sphere_add(location=(1.5, 0, 0))
        orbiter = bpy.context.object
        orbiter.name = "Orbiter"
        orbiter.data.name = "Orbiter_Mesh"
        orbiter.scale = (0.1, 0.1, 0.1)  # Küçült
        print("Yeni orbiter küresi oluşturuldu.")
    else:
        orbiter.location = (1.5, 0, 0)
        orbiter.scale = (0.1, 0.1, 0.1)
        print("Var olan orbiter bulundu ve konumlandı.")

    # Materyal: Kırmızı
    if "RedOrbiterMaterial" in bpy.data.materials:
        red_mat = bpy.data.materials["RedOrbiterMaterial"]
    else:
        red_mat = bpy.data.materials.new(name="RedOrbiterMaterial")
        red_mat.diffuse_color = (1, 0, 0, 1)  # RGBA: Kırmızı

    # Materyali ata (önce eskiyi sil, sonra ekle)
    orbiter.data.materials.clear()
    orbiter.data.materials.append(red_mat)


    # Parent boşluğu (empty) oluştur
    orbit_empty = bpy.data.objects.get("Orbiter_Empty")
    if orbit_empty:
        bpy.data.objects.remove(orbit_empty, do_unlink=True)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    orbit_empty = bpy.context.object
    orbit_empty.name = "Orbiter_Empty"

    # Küreyi empty'nin child'ı yap (dönmesi için)
    orbiter.parent = orbit_empty

    # ---------- Animasyon ----------
    # 250 karelik animasyonda 0°'den 360°'ye Z rotasyonu
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 2500

    orbit_empty.rotation_euler = (0, 0, 0)
    orbit_empty.keyframe_insert(data_path="rotation_euler", frame=1)

    orbit_empty.rotation_euler = (0, 0, math.radians(360))
    orbit_empty.keyframe_insert(data_path="rotation_euler", frame=2500)

    # Döngü sürekli tekrar etsin
    action = orbit_empty.animation_data.action
    fcurve = action.fcurves.find("rotation_euler", index=2)  # Z ekseni
    if fcurve:
        modifier = fcurve.modifiers.new(type='CYCLES')  # Sonsuz döngü

    print("Orbiter küresi başarıyla yerleştirildi ve animasyon eklendi.")
    
    
        # ---------- Kamera etrafında dönen boşluk (empty) oluştur ----------
    camera = bpy.data.objects.get("Camera")
    if not camera:
        print("Camera objesi bulunamadı.")
    else:
        # Daha önce varsa sil
        cam_empty = bpy.data.objects.get("Camera_Orbit_Empty")
        if cam_empty:
            bpy.data.objects.remove(cam_empty, do_unlink=True)

        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        cam_empty = bpy.context.object
        cam_empty.name = "Camera_Orbit_Empty"

        # Kamera konumlandır (örneğin 1.85 birim uzaklıkta)
        camera.location = (1.85, 0, 0)
        camera.parent = cam_empty

        # Kamera animasyonu (daha yavaş)
        scene.frame_start = 1
        scene.frame_end = 10000  # Daha yavaş tur için yüksek kare sayısı

        cam_empty.rotation_euler = (0, 0, 0)
        cam_empty.keyframe_insert(data_path="rotation_euler", frame=1)

        cam_empty.rotation_euler = (0, 0, math.radians(360))
        cam_empty.keyframe_insert(data_path="rotation_euler", frame=5000)

        # Kamera için döngü modifiyeri
        action = cam_empty.animation_data.action
        fcurve = action.fcurves.find("rotation_euler", index=2)
        if fcurve:
            modifier = fcurve.modifiers.new(type='CYCLES')

        print("Kamera için yavaş yörünge animasyonu eklendi.")
        
                # Kamera her zaman Ay'a baksın
        track = camera.constraints.get("TrackTo")
        if not track:
            track = camera.constraints.new(type='TRACK_TO')
        track.name = "TrackTo"
        track.target = moon
        track.track_axis = 'TRACK_NEGATIVE_Z'
        track.up_axis = 'UP_Y'


