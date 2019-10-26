bl_info = {
    "name": "Import .vmf Props (zfbx)",
    "category": "Import",
    "blender": (2, 80, 0),
    "author": "Robert Straub (robertstraub.co.uk)",
    "version": (0, 0, 4),
    "location": "File > Import",
    "description": "Import all converted prop fbx's from zfbx using the source .vmf",
}

import bpy
import re
import os
import math

class Entity():
    origin = ["0.0","0.0","0.0"]
    classname = ""
    model = ""
    angles = ["0.0","0.0","0.0"]
    parentname = ""
    id = ""

def ReadEntities(data):
    # Using the vmf data we need to:
    # 1, Parse all entities
    # 2, Find all props/entities with the model property
    # 3, Locate model fbx and import, then restore transforms
    # Done?
    
    entities = []
    depth = 0
    readingEntity = False
    skipline = False
    skipblock = False
    skipblockindex = 0
    currentLine = 0

    currentEntity = 0

    print("Begining parse of file data.")
    for line in data:
        line = line.replace('\n', '')
        currentLine += 1
        if skipline:
            skipline = False
            continue

        if '{' in line and "material" not in line:
            depth += 1
        
        if '}' in line and "material" not in line:
            depth -= 1
            if depth == 0:
                #We cant be reading an entity as it must have closed if we had one.
                if readingEntity:
                    currentEntity += 1
                    readingEntity = False

        #If we are meant to be skipping this block
        if skipblock:
            # Stop skipping if we hit the end brace and we go back to the index we began on.
            if '}' in line:
                if depth == skipblockindex:
                    skipblock = False
                    print(f"Ended block skip at: {currentLine}.")
                    continue
            else: 
                continue

        #Check if we can skip here to allow skipblock to end if needed.
        if '}' in line and depth == 0: continue

        #Check the line to handle it correctly
        if depth == 0:
            #We are waiting for a new block
            if line == "world":
                print(f"Hit world block! {currentLine}")
                skipblock = True
                skipblockindex = depth
                continue
            elif line == "entity":
                print(f"Hit entity block! {currentLine}")
                depth += 1
                skipline = True
                readingEntity = True
                #Make a new entity object
                entities.append(Entity())
                continue
            else:
                print(f"Line unrecognised:[{line}]")
        elif depth == 1:
            if readingEntity:
                #Begin reading the entity properties
                #Check if this line is an internal block we skip for now
                if(("solid" in line and '"' not in line) or ("connections" in line and '"' not in line)):
                    skipblock = True
                    skipblockindex = depth
                    print(f"Beginning skipping as we hit solid or connections {currentLine}")
                    continue

                keyval = ExtractKeyValue(line)
                if(keyval[0] == "origin"):
                    #Extract and store the position data
                    originvals = keyval[1].split(" ")
                    entities[currentEntity].origin = []
                    for i in range(3):
                        entities[currentEntity].origin.append(keyval[(i+1)])
                elif(keyval[0] == "classname"):
                    entities[currentEntity].classname = keyval[1]
                elif(keyval[0] == "model"):
                    entities[currentEntity].model = keyval[1]
                elif(keyval[0] == "angles"):
                    #Extract and store the rotation data
                    entities[currentEntity].angles = [3]
                    for i in range(3):
                        entities[currentEntity].angles.append(keyval[(i+1)])
                elif(keyval[0] == "id"):
                    entities[currentEntity].id = keyval[1]
                elif(keyval[0] == "parentname"):
                    entities[currentEntity].parentname = keyval[1]

    # End of parsing all entities?
    print(f"Entity count: {entities.__len__()}. Current Line: {currentLine}.")

    return entities;

def ExtractKeyValue(line):
    #regex was being stupid and cus python is weaklytyped i cba to fix it.
    #reextract = re.findall('"(.+?)"', line)
    #if(reextract):
    #    toreturn.append(reextract[0].group(1))
    #    toreturn.append(reextract[1].group(1))
    modifline = line.replace("	", "") # Remove Tab
    modifline = modifline.replace('"', "")# Remove quotes
    return modifline.split(" ")
            
def ReadFile(context, filepath, setting):
    f = open(filepath, 'r', encoding='utf-8')
    data = f.readlines()
    print(f"Read {data.__len__()} lines from {filepath}")

    allEntities = ReadEntities(data)   
    f.close()

    fbxpath = setting
    fbxpath = fbxpath.replace("\\", "/")

    count = 0
    collectionmade = False

    for ent in allEntities:
        if("prop" in ent.classname and not ent.model == ""):
            count += 1
            propmodelsuffix = ent.model;
            propmodelsuffix = propmodelsuffix.replace("models/", "")
            propmodelsuffix = propmodelsuffix.replace("\\", "/");
            propmodelsuffix = propmodelsuffix.replace(".mdl", ".fbx")

            modelpath = f"{fbxpath}/{propmodelsuffix}"

            if not os.path.exists(modelpath):
                print("Skipped an entity as its model wasnt found!")
                print(ent.id + ": " + modelpath)
                continue

            bpy.ops.import_scene.fbx(filepath = modelpath)
            importedFBX = bpy.context.selected_objects[:]

            newPropFbx = None
            if importedFBX.__len__() == 1:
                newPropFbx = importedFBX[0]
            else:
                cob = importedFBX[0]
                # Loop till we get the top most object.
                while(True):
                    if(cob.parent == None):
                        newPropFbx = cob
                        break
                    else:
                        cob = cob.parent

            names = propmodelsuffix.replace(".fbx", "")
            newPropFbx.name = f"{ent.id}: {names}"
            
            #Scale down the world positions.
            scale = 0.01

            newPropFbx.location = float(ent.origin[0]) * scale, float(ent.origin[1]) * scale, float(ent.origin[2]) * scale
            newPropFbx.rotation_euler = (float(ent.angles[0])+ 90) * (math.pi / 180), float(ent.angles[1]) * (math.pi / 180), (float(ent.angles[2])+ 90) * (math.pi / 180)

            #if not collectionmade:
            #    bpy.ops.collection.create(name="Imported Props")
            #    collectionmade = True
            #
            #bpy.ops.collection.objects_add_active(collection = "Imported Props")

    return {'FINISHED'}

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    """Import fbx props using a .vmf"""
    bl_idname = "import_vmf.import_props"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Props"

    # ImportHelper mixin class uses this
    filename_ext = ".vmf"

    filter_glob: StringProperty(
        default="*.vmf",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: StringProperty(
        name="Model FBX Directory",
        description="Location of the converted prop mdl's from zfbx",
        default="PATH HERE!",
    )

    def execute(self, context):
        return ReadFile(context, self.filepath, self.use_setting)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text=".vmf Props (zfbx)")


def register():
    bpy.utils.register_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportSomeData)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()
