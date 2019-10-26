# ImportVMFProps-zfbx
A helper blender plugin to import and place all props in a .vmf. Requires the use of zfbx for prop fbx creation.
This tool is to be used alongside zfbx. It is not perfect and requires changes but works well enough soo far.

## Requirements
You must use the tool [zfbx by Zak found here](https://forums.pixeltailgames.com/t/source-fbx-tool-and-bsp-proper-tool/2011) first. This will decompile your map into a base fbx of the world brushes and also fbx versions of all props and converted textures.

## How to use
- Use zfbx on your chosen map
- Install the plugin (blender 2.8 and higher)
- Go to File > Import > .vmf Props (zfbx)

- Navigate to the .vmf
- Before clicking import, paste the full path to the models directory made by zfbx. (This should contain folders named after props such as "props_c17")
- Click "Import Props" and wait. This can take a long time. Your blender will freeze but just be patient. If your PC is slow and has little ram it could crash with maps with many props
- Enjoy. Some props may not be rotated just right but this is something I will be working on.

## Current Issues
- All imported props have their own material instances. Future version will also fix this and make them share for easy editing.
- Slow. Can't do much about that.
- Only tested on Windows.
