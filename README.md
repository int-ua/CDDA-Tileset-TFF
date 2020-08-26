# CDDA tileset Text Fallback Fillers

32x32 images with text names and relevant JSON files for using as a fallback in CDDA tilesets.

### How to

1. Put the `text_fallback_fillers` inside a directory in a decomposed tileset that was designated for fillers.
For Ultica it's `gfx/UltimateCataclysm/pngs_fillerhoder_32x32/`.
2. Generate a game-compatible tileset with `compose.py`:
```sh
./Cataclysm-DDA/tools/gfx_tools/compose.py CDDA-Tilesets/gfx/UltimateCataclysm/
```


### Generate new

0. [Set up your Python virtual environment](https://docs.python.org/3/tutorial/venv.html) and install `requirements.txt`.
1.
```sh
./Cataclysm-DDA/tools/json_tools/table.py -f csv --nonestring "" \
-t "AMMO,ARMOR,BATTERY,BIONIC_ITEM,BOOK,COMESTIBLE,ENGINE,field_type,GENERIC,GUN,GUNMOD,MAGAZINE,MONSTER,PET_ARMOR,TOOL,TOOL_ARMOR,TOOLMOD,trap,WHEEL" \
type id name color looks_like "copy-from" > tff-input.csv
cd CDDA-Tileset-TFF
./generate.py ../tff-input.csv
```
