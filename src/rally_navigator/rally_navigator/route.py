from collections import deque

from rally_interfaces.msg import Instruction
from rally_navigator.grid import Cell, DIRECTION_COL, DIRECTION_COUNT, DIRECTION_ROW, EAST

# Provided, do not modify
def trace_back(parent, finish):
    if finish not in parent:
        return []

    route = []
    cell = finish
    while cell is not None:
        route.append(cell)
        cell = parent[cell]
    route.reverse()
    return route

# TODO: TASK B
def find_route(grid):
    # Cari rute terpendek dari grid.start ke grid.finish dengan BFS, tetangga dicek berurutan
    # timur, utara, barat, selatan.
    # Return list kosong kalau tidak ada jalan.
    if not grid.inside(grid.start) or not grid.inside(grid.finish):
        return []

    # Ambil kotak dari pending. Untuk setiap tetangga yang di dalam grid yang bukan batu dan
    # belum dikunjungi, catat asalnya di parent lalu masukkan ke pending.
    parent = {grid.start: None}
    pending = deque([grid.start])
    # ... tulis pencariannya di sini ...
    while pending:
        current = pending.popleft()
        
        if(current == grid.finish):
            break
        
        for i in range(DIRECTION_COUNT):
            neighbor = Cell(current.col + DIRECTION_COL[i], current.row + DIRECTION_ROW[i])
            
            if(grid.inside(neighbor) and not grid.is_rock(neighbor) and neighbor not in parent):
                parent[neighbor] = current
                pending.append(neighbor)

    return trace_back(parent, grid.finish)

# TODO: TASK C
def route_to_directions(route):
    # Ubah rute (daftar kotak) jadi daftar arah tiap langkah: 0 timur, 1 utara, 2 barat, 3 selatan.
    directions = []
    
    for i in range(len(route) - 1):
        current_cell = route[i]
        next_cell = route[i+1]
        
        diff_col = next_cell.col - current_cell.col
        diff_row = next_cell.row - current_cell.row
        
        for direction_index in range(DIRECTION_COUNT):
            if(diff_col == DIRECTION_COL[direction_index] and diff_row == DIRECTION_ROW[direction_index]):
                directions.append(direction_index)
                break
        
    return directions

# TODO: TASK D
def directions_to_instructions(directions):
    # Gabungkan langkah lurus berturut-turut jadi satu instruksi, dan tutup tiap instruksi dengan belokannya.
    # Aturan khusus:
    # - Jika langkah pertama bukan ke timur, Miru harus belok dulu (instruksi pertama jaraknya 0).
    # - Putar balik ditulis dua belok kiri berturut-turut. 
    # - Instruksi terakhir tidak punya belokan (TURN_NONE).
    if not directions:
        return [Instruction(id=1, distance=0, turn=Instruction.TURN_NONE)]
    
    instructions = []
    
    current_facing = EAST
    current_distance = 0
    instruction_id = 1
    
    for step_direction in directions:
        if(step_direction == current_facing):
            current_distance += 1
        else:
            diff = (step_direction - current_facing) % DIRECTION_COUNT
            
            if(diff == 1):
                turn = Instruction.TURN_LEFT
            elif(diff == 3):
                turn = Instruction.TURN_RIGHT
            elif(diff == 2):
                instructions.append(Instruction(
                    id=instruction_id,
                    distance=current_distance,
                    turn=Instruction.TURN_LEFT
                ))
                instruction_id += 1
                
                current_distance = 0
                turn = Instruction.TURN_LEFT
                current_facing = step_direction
            
            instructions.append(Instruction(
                id=instruction_id,
                distance=current_distance,
                turn=turn
            ))
            
            instruction_id += 1
            current_distance = 1
            current_facing = step_direction

    instructions.append(Instruction(
        id=instruction_id,
        distance=current_distance,
        turn=Instruction.TURN_NONE
    ))
    
    return instructions
        

# Provided, do not modify
def route_to_instructions(route):
    return directions_to_instructions(route_to_directions(route))
