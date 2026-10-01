from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from shapely.ops import triangulate
import trimesh, numpy as np, os

W=512
tex=Image.new("RGB",(W,W),(244,244,240))
d=ImageDraw.Draw(tex)
d.ellipse((170,110,342,282), fill=(18,35,72))
d.polygon([(145,245),(205,205),(256,225),(307,205),(367,245),(335,420),(177,420)], fill=(24,55,120))
d.polygon([(205,250),(256,205),(307,250),(282,292),(230,292)], fill=(8,12,22))
d.line((315,145,390,390), fill=(205,25,35), width=18)
d.line((330,145,405,390), fill=(245,45,55), width=5)
d.polygon([(392,375),(420,430),(366,412)], fill=(180,20,30))
d.polygon([(150,330),(210,350),(185,385),(135,365)], fill=(210,25,40))
d.polygon([(362,330),(302,350),(327,385),(377,365)], fill=(210,25,40))
tex_path="/tmp/tee_texture.jpg"
tex.save(tex_path,quality=82,optimize=True)

def make_part(points, depth=.18):
    poly=Polygon(points); tris=triangulate(poly)
    verts=[]; faces=[]; uvs=[]
    minx,miny,maxx,maxy=poly.bounds
    def uv(x,y): return ((x-minx)/(maxx-minx or 1),(y-miny)/(maxy-miny or 1))
    for tri in tris:
        if not poly.covers(tri.representative_point()): continue
        coords=list(tri.exterior.coords)[:-1]
        base=len(verts)
        for x,y in coords: verts.append([x,y,depth/2]); uvs.append(uv(x,y))
        faces.append([base,base+1,base+2])
        base=len(verts)
        for x,y in coords:
            verts.append([x,y,-depth/2]); u=uv(x,y); uvs.append((u[0],1-u[1]))
        faces.append([base+2,base+1,base])
    ring=list(poly.exterior.coords)[:-1]
    for i,(x1,y1) in enumerate(ring):
        x2,y2=ring[(i+1)%len(ring)]
        base=len(verts); verts += [[x1,y1,depth/2],[x2,y2,depth/2],[x2,y2,-depth/2],[x1,y1,-depth/2]]
        u1,u2=uv(x1,y1),uv(x2,y2); uvs += [u1,u2,u2,u1]
        faces += [[base,base+1,base+2],[base,base+2,base+3]]
    m=trimesh.Trimesh(vertices=np.array(verts,float),faces=np.array(faces,int),process=False)
    m.visual=trimesh.visual.texture.TextureVisuals(uv=np.array(uvs))
    return m

body=[(-.95,1.25),(-.55,1.48),(-.25,1.25),(0,1.32),(.25,1.25),(.55,1.48),(.95,1.25),(.78,.78),(.72,-1.18),(0,-1.35),(-.72,-1.18),(-.78,.78)]
left=[(-.55,1.46),(-1.15,1.12),(-1.52,.65),(-1.38,.25),(-.98,.48),(-.68,.83)]
right=[(.55,1.46),(1.15,1.12),(1.52,.65),(1.38,.25),(.98,.48),(.68,.83)]
mat=trimesh.visual.material.PBRMaterial(baseColorTexture=Image.open(tex_path),roughnessFactor=.78,metallicFactor=0.0)
scene=trimesh.Scene()
for i,pts in enumerate((body,left,right)):
    m=make_part(pts); m.visual.material=mat
    scene.add_geometry(m,node_name=f"garment_part_{i}")
scene.export("assets/vastramm-tee-3d.glb")
print("generated",os.path.getsize("assets/vastramm-tee-3d.glb"))
