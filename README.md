# CDDA tileset Text Fallback Fillers

Fallback images with text names and relevant JSON files CDDA tilesets.

### Using

* Get a decomposed version of a tileset. Ultica, current default CDDA tileset is available [here](https://github.com/I-am-Erk/CDDA-Tilesets/).
* Get the [`compose.py`](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/tools/gfx_tools/compose.py) script from CDDA
* [Set up your Python virtual environment](https://docs.python.org/3/tutorial/venv.html) and install `pyvips`.
* Put the `text_fallback_fillers` into a tileset directory that was designated for 32x32 fillers.
For Ultica it's `gfx/UltimateCataclysm/pngs_filler_32x32/`.
* Optional: remove 32x32 monster sprites from `text_fallback_fillers` and put vertical monsters from `tff_32x64` directory into a 32x64 tileset filler directory (`pngs_filler_tall_32x64`).
* Generate a game-compatible tileset with `compose.py`:
```sh
./Cataclysm-DDA/tools/gfx_tools/compose.py CDDA-Tilesets/gfx/UltimateCataclysm/
```


### Generating new


```sh
./Cataclysm-DDA/tools/json_tools/table.py -f csv --nonestring "" \
-t "AMMO,ARMOR,BATTERY,BIONIC_ITEM,BOOK,COMESTIBLE,ENGINE,field_type,GENERIC,GUN,GUNMOD,MAGAZINE,MONSTER,PET_ARMOR,TOOL,TOOL_ARMOR,TOOLMOD,trap,WHEEL" \
type id name color looks_like "copy-from" > tff-input.csv
cd CDDA-Tileset-TFF
./generate.py ../tff-input.csv
```
