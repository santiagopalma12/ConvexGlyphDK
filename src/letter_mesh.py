def get_letter_grid(char):
    # 5x5 grids
    grids = {
        'A': [
            "  X  ",
            " X X ",
            "XXXXX",
            "X   X",
            "X   X"
        ],
        'B': [
            "XXXX ",
            "X   X",
            "XXXX ",
            "X   X",
            "XXXX "
        ],
        'C': [
            " XXX ",
            "X    ",
            "X    ",
            "X    ",
            " XXX "
        ],
        'D': [
            "XXXX ",
            "X   X",
            "X   X",
            "X   X",
            "XXXX "
        ],
        'E': [
            "XXXXX",
            "X    ",
            "XXXX ",
            "X    ",
            "XXXXX"
        ],
        'F': [
            "XXXXX",
            "X    ",
            "XXXX ",
            "X    ",
            "X    "
        ],
        'G': [
            " XXX ",
            "X    ",
            "X  XX",
            "X   X",
            " XXX "
        ],
        'H': [
            "X   X",
            "X   X",
            "XXXXX",
            "X   X",
            "X   X"
        ],
        'I': [
            "XXXXX",
            "  X  ",
            "  X  ",
            "  X  ",
            "XXXXX"
        ],
        'J': [
            "XXXXX",
            "   X ",
            "   X ",
            "X  X ",
            " XX  "
        ],
        'K': [
            "X   X",
            "X  X ",
            "XXX  ",
            "X  X ",
            "X   X"
        ],
        'L': [
            "X    ",
            "X    ",
            "X    ",
            "X    ",
            "XXXXX"
        ],
        'M': [
            "X   X",
            "XX XX",
            "X X X",
            "X   X",
            "X   X"
        ],
        'N': [
            "X   X",
            "XX  X",
            "X X X",
            "X  XX",
            "X   X"
        ],
        'O': [
            " XXX ",
            "X   X",
            "X   X",
            "X   X",
            " XXX "
        ],
        'P': [
            "XXXX ",
            "X   X",
            "XXXX ",
            "X    ",
            "X    "
        ],
        'Q': [
            " XXX ",
            "X   X",
            "X   X",
            "X  X ",
            " XX X"
        ],
        'R': [
            "XXXX ",
            "X   X",
            "XXXX ",
            "X  X ",
            "X   X"
        ],
        'S': [
            " XXX ",
            "X    ",
            " XXX ",
            "    X",
            " XXX "
        ],
        'T': [
            "XXXXX",
            "  X  ",
            "  X  ",
            "  X  ",
            "  X  "
        ],
        'U': [
            "X   X",
            "X   X",
            "X   X",
            "X   X",
            " XXX "
        ],
        'V': [
            "X   X",
            "X   X",
            "X   X",
            " X X ",
            "  X  "
        ],
        'W': [
            "X   X",
            "X   X",
            "X X X",
            "XX XX",
            "X   X"
        ],
        'X': [
            "X   X",
            " X X ",
            "  X  ",
            " X X ",
            "X   X"
        ],
        'Y': [
            "X   X",
            " X X ",
            "  X  ",
            "  X  ",
            "  X  "
        ],
        'Z': [
            "XXXXX",
            "   X ",
            "  X  ",
            " X   ",
            "XXXXX"
        ]
    }
    return grids.get(char.upper(), ["XXXXX"]*5)

def generate_polygon_mesh(char, scale=50):
    """
    Genera una lista de polígonos convexos (cuadrados) que forman la letra.
    Retorna: List[List[Tuple[float, float]]]
    """
    grid = get_letter_grid(char)
    polygons = []
    rows = len(grid)
    cols = len(grid[0])
    
    # Tamaño de cada "pixel" cuadrado
    pixel_size = scale / 5.0 
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != ' ':
                x = c * pixel_size
                y = r * pixel_size
                # Crear polígono cuadrado (convexo)
                poly = [
                    (x, y),
                    (x + pixel_size, y),
                    (x + pixel_size, y + pixel_size),
                    (x, y + pixel_size)
                ]
                polygons.append(poly)
    return polygons
