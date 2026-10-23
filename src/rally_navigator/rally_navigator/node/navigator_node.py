from rally_interfaces.msg import DriverStatus, Instruction, RaceMap
from rally_navigator.grid import Cell, GridMap
from rally_navigator.route import find_route, route_to_instructions
from rcl_interfaces.msg import SetParametersResult
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

MAP_TOPIC = '/race/map'
STATUS_TOPIC = '/miru/status'
INSTRUCTION_TOPIC = '/navigator/instruction'
INSTRUCTIONS_AHEAD_PARAM = 'instructions_ahead'

DEFAULT_INSTRUCTIONS_AHEAD = 2
MIN_INSTRUCTIONS_AHEAD = 1
MAX_INSTRUCTIONS_AHEAD = 5

TURN_NAMES = {
    Instruction.TURN_NONE: 'finish',
    Instruction.TURN_LEFT: 'belok kiri',
    Instruction.TURN_RIGHT: 'belok kanan',
}

class NavigatorNode:
    def __init__(self, node):
        self.node = node

        self.grid = None
        self.instructions = []
        self.last_status = None
        self.sent_count = 0

        # TODO: TASK A - Subscribe ke MAP_TOPIC callback on_map dengan QoS transient_local dan reliable
        map_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE)
        
        self.map_subscriber = self.node.create_subscription(RaceMap, MAP_TOPIC, self.on_map, map_qos)

        # TODO: TASK E - Buat publisher untuk INSTRUCTION_TOPIC dan subscriber untuk STATUS_TOPIC callback on_status
        self.instruction_publisher = self.node.create_publisher(Instruction, INSTRUCTION_TOPIC, 10)
        self.status_subscriber = self.node.create_subscription(DriverStatus, STATUS_TOPIC, self.on_status, 10)

        # TODO: TASK F - Daftarkan parameter INSTRUCTIONS_AHEAD_PARAM bawaan DEFAULT_INSTRUCTIONS_AHEAD dengan on_parameter_change.
        self.node.declare_parameter(INSTRUCTIONS_AHEAD_PARAM, DEFAULT_INSTRUCTIONS_AHEAD)
        self.node.add_on_set_parameters_callback(self.on_parameter_change)

        self.node.get_logger().info('navigator siap')

    # TODO: TASK A
    def on_map(self, msg):
        # Abaikan jika peta sudah ada, atau jika jumlah batunya tidak cocok dengan width*height, tampilkan log error.
        # Jika aman, simpan sebagai GridMap di self.grid, tampilkan log peta diterima, lalu panggil self.plan_route().
        if(self.grid is not None):
            return
        
        if(len(msg.rocks) != (msg.width * msg.height)):
            self.node.get_logger().error("Peta Rusak")
            return

        start_cell = Cell(msg.start_col, msg.start_row)
        finish_cell = Cell(msg.finish_col, msg.finish_row)
        self.grid = GridMap(msg.width, msg.height, msg.rocks, start_cell, finish_cell)
        rocks_total = sum(msg.rocks)
        self.node.get_logger().info(
            f'peta diterima: {msg.width}x{msg.height}, {rocks_total} batu, start ({msg.start_col}, {msg.start_row}), finis ({msg.finish_col}, {msg.finish_row})'
        )
        self.plan_route()

    # Provided, do not modify
    def plan_route(self):
        route = find_route(self.grid)
        if not route:
            self.node.get_logger().error('tidak ada rute dari start ke finish')
            return

        self.instructions = route_to_instructions(route)
        self.node.get_logger().info(
            f'rute {len(route) - 1} kotak, {len(self.instructions)} instruksi')

    # TODO: TASK E
    def on_status(self, msg):
        # Simpan laporan di self.last_status, lalu panggil self.send_instructions().
        self.last_status = msg
        self.send_instructions()

    def send_instructions(self):
        # Kirim instruksi mulai dari self.sent_count sampai done_id + DEFAULT_INSTRUCTIONS_AHEAD log tiap pengiriman
        # Jangan kirim jika rute belum ada, Miru belum lapor, atau belum ada subscriber (get_subscription_count() masih 0)
        if(not self.instructions or self.last_status is None or self.instruction_publisher.get_subscription_count() == 0):
            return
        
        instruction_ahead = self.node.get_parameter(INSTRUCTIONS_AHEAD_PARAM).value
        target_id_max = self.last_status.done_id + instruction_ahead
        total_instructions = len(self.instructions)
        
        while(self.sent_count < total_instructions and self.sent_count < target_id_max):
            instruction = self.instructions[self.sent_count]
            self.instruction_publisher.publish(instruction)
            
            turn_str = TURN_NAMES.get(instruction.turn, 'finish')
            self.node.get_logger().info(f'[navigator] kirim instruksi {instruction.id}: maju {instruction.distance}, {turn_str}')
            
            self.sent_count += 1

    # TODO: TASK F
    def on_parameter_change(self, parameters):
        # Tolak instructions_ahead di luar MIN_INSTRUCTIONS_AHEAD sampai MAX_INSTRUCTIONS_AHEAD, selain itu terima.
        for param in parameters:
            if(param.name == INSTRUCTIONS_AHEAD_PARAM):
                if(param.value < MIN_INSTRUCTIONS_AHEAD or param.value > MAX_INSTRUCTIONS_AHEAD):
                    return SetParametersResult(successful=False)
        
        return SetParametersResult(successful=True)
