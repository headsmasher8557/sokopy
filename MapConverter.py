import Enum

convMap: dict[str, int] = {
    " ": Enum.TileType.EMPTY,
    "#": Enum.TileType.SOLID,
    "$": Enum.TileType.BOX,
    ".": Enum.TileType.GOAL,
    "*": Enum.TileType.BOX | Enum.TileType.GOAL,
    "@": Enum.TileType.PLAYER,
    "+": Enum.TileType.PLAYER | Enum.TileType.GOAL
}
def convert(data):
    maps = []
    curMap = []
    for line in data.split("\n"):
        if line == "": continue
        if line[0] == ";":
            # new level definition
            if len(curMap) > 0:
                maps.append(curMap) # add prev
            curMap = []
            continue
        # row definition
        row = []
        for ch in line:
            el = convMap[ch]
            if el:
                row.append(int(el))
            else:
                row.append(Enum.TileType.EMPTY)
        curMap.append(row)
    curMap.append(curMap) # add last map
    return maps

def convert_from_file(filename):
    f = open(filename, "rt")
    o = f.read()
    f.close()
    return convert(o)
