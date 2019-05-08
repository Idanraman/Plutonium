from sim.update import *
import copy

class Frame():
	def __init__(self):
		self.turn = 0
		self.last_alive = []
		self.budgets = []
		self.deposited = []
		self.halite = None
		self.ships = []
		self.dropoffs = []

	def width(self):
		return len(self.halite)

	def height(self):
		return len(self.halite[0])

	def players(self):
		return len(self.budgets)

	def total_halite(self):
		total = 0
		for x in range(self.width()):
			for y in range(self.width()):
				total += self.halite[x][y]
		return total

	def is_alive(self,pid):
		return self.last_alive[pid] == -1

	def kill(self,pid,turn_offset):
		t = self.turn + turn_offset
		if t < 0 : t = 0
		self.last_alive[pid] = t

	def death_time(self,pid):
		return self.last_alive[pid]

	def copy_frame(self):
		new_frame = copy.deepcopy(self)
		return new_frame

	def fix_inspiration(self,RADIUS, SHIPS_NEEDED):
		if self.ships == None:
			return
		map_width = self.width()
		map_height = self.height()

		xy_lookup = [[None for i in range(map_width)] for y in range(map_height)]

		for ship in self.ships:
			if ship == None:
				continue

			xy_lookup[ship.X][ship.Y] = ship

		for ship in self.ships:
			if ship == None:
				continue

			hits = 0

			for y in range(RADIUS):
				startx = y-RADIUS
				endx = RADIUS-y

				for x in range(endx):
					other_x = mod(ship.X + x, map_width)
					other_y = mod(ship.Y + y, map_height)

					other = xy_lookup[other_x][other_y]

					if other != None:
						if other.owner != ship.owner:
							hits+=1

					if y !=0:
						other_y = mod(ship.Y - y, map_height)

						other = xy_lookup[other_x][other_y]

						if other != None:
							if other.owner != ship.owner:
								hits+=1

			if hits >= SHIPS_NEEDED:
				ship.inspired = True
			else:
				ship.inspired = False

class Game():
	def __init__(self,constants):
		self.consts = constants
		self.frame = None
		self.update_from_moves = update_from_moves

	def use_frame(self,f):
		self.frame = f

	def bot_init_string(self):
		lines = []

		for pid in range(self.frame.players()):
			factory = self.frame.dropoffs[pid]
			x = factory.X
			y = factory.Y

			lines.append("%d %d %d" % (pid, x, y))

		lines.append("%d %d"% ( self.frame.width() , self.frame.height()))

		for y in range(self.frame.height()):
			elements = []
			for x in range(self.frame.width()):
				elements.append(str(self.frame.halite[x][y]))

			lines.append(str(' '.join(elements)))

		return "\n".join(lines)

	def get_rank(self,pid):
		money = self.frame.budgets[pid]
		la = self.frame.last_alive[pid]
		rank = 1
		for n in range(self.frame.players()):
			if n == pid:
				continue

			if self.frame.last_alive[n] > la and la !=-1:
				rank+=1
			elif self.frame.last_alive[n] == -1 and la !=-1:
				rank+=1
			elif self.frame.budgets[n] > money:
				rank+=1
		return rank

	def get_dropoffs(self):
		ret = self.frame.dropoffs.copy()
		return ret

	def budget(self,pid):
		return self.frame.budgets[pid]

	def is_alive(self,pid):
		return self.frame.is_alive(pid)

	def kill(self,pid,turn_offset):
		self.frame.kill(pid, turn_offset)

	def death_time(self,pid):
		return self.frame.death_time(pid)

class Dropoff():
	def __init__(self):
		self.fact = None
		self.owner = None
		self.sid = None
		self.X = None
		self.Y = None
		self.gathered = None

class Ship():
	def __init__(self):
		self.X = None
		self.Y = None
		self.owner = None
		self.sid = None
		self.halite = None
		self.inspired = None

class Position():
	def __init__(self):
		self.X = None
		self.Y = None

def mod(x,n):
	return (x % n + n) % n