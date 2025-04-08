import bpy

moon_obj = bpy.data.objects.get("Moon")
if moon_obj:
    # Silinecek nesneleri listeleyelim
    to_delete = []
    for child in moon_obj.children:
        if child.name.startswith("Meridian_") or child.name.startswith("Parallel_"):
            to_delete.append(child)
        elif child.type == 'FONT':
            # Font nesnelerinde, metin içeriğinde "°" karakteri varsa silinebilir
            if child.data.body.strip().endswith("°"):
                to_delete.append(child)
    
    # Belirlenen nesneleri silelim
    for obj in to_delete:
        bpy.data.objects.remove(obj, do_unlink=True)
    
    print("Tüm meridyen ve paralel çizgiler (etiketleriyle birlikte) silindi.")
else:
    print("'Moon' objesi bulunamadı.")
