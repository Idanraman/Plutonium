from sim.constants import *
#from sim.sim import Dropoff

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

def string_to_dxdy(s):
	inter = {
	'e': [1,0],
	'w': [-1,0],
	's': [0,1],
	'n': [0,-1],
	'c': [0,0],
	'o': [0,0],
	'': [0,0],
	}
	return(inter[s])

def mod(x,n):
	return (x % n + n) % n

def update_from_moves(self,all_player_moves):
	players = self.frame.players()
	width = self.frame.width()
	height = self.frame.height()

	if self.frame.ships == None:
		self.frame.ships = []
	gens = [0] * players
	moves = [''] * len(self.frame.ships)
	fails = [''] * players
	#COMMNANDS STROCTURE: COMMANDS = {'g':'g','c':[12],'m':[<id>,'n']}
	for pid in range(len(all_player_moves)):
		print
		for command in all_player_moves[pid]:

			if command[0] not in ['g','m','c']:
				fails[pid] = "Bot %d sent unknown command %s" % (pid,command)
				continue

			if command[0] == "g":
				if gens[pid]:
					fails[pid] = "Bot %d sent 2 or more generate commands" % (pid)
					continue
				gens[pid] = 1
				continue

			if command[0] == "c" or command[0] == "m":
				sid = int(command[2])

				if sid >= len(self.frame.ships) or sid < 0 or self.frame.ships[sid] == None:
					fails[pid] = "Bot %d sent command for non-existent ship %d" % (pid,sid)
					continue

			ship = self.frame.ships[sid]

			if ship.owner != pid:
				fails[pid] = "Bot %d sent command for ship %d which doesn't belong to him" % (pid,sid)
				continue

			if moves[sid] != '':
				fails[pid] = "Bot %d sent 2 or more commands for ship %d" % (pid,sid)
				continue

			if command[0] == "c":
				for dropoff in self.frame.dropoffs:
					if dropoff.X == ship.X and dropoff.Y == ship.Y:
						fails[pid] = "Bot %d sent construct command from ship %d over a structure" % (pid,sid)

				moves[sid] = "c"
				continue

			direction = command[4]

			if direction not in ['n','s','e','w','o']:
				fails[pid] = "Bot %d sent unknown direction %s" % (pid,direction)
				continue
			moves[sid] = direction

	# ---------------------------------------------------------------------
	new_frame = self.frame.copy_frame()
	new_frame.turn += 1

	# Best just pretend ships with no move did in fact issue a "o" order...

	for ship in self.frame.ships:
		if ship == None:
			continue
		if moves[ship.sid] == '':
			moves[ship.sid] = 'o'

	# Budgets stuff

	for pid in range(players):
		if gens[pid]:
			new_frame.budgets[pid] -= NEW_ENTITY_ENERGY_COST

	for sid, move in enumerate(moves):

		if move == "c":
			ship = new_frame.ships[sid]

			pid = ship.owner

			new_frame.budgets[pid] -= DROPOFF_COST
			new_frame.budgets[pid] += ship.halite
			new_frame.budgets[pid] += new_frame.halite[ship.X][ship.Y]

	for pid in range(players):
		if new_frame.budgets[pid] < 0:
			fails[pid] =  "Bot %d went over budget" % (pid)

	# Print info on fails and kill player...

	for pid in range(players):
		if fails[pid] != '':
			print("%s\n" % (fails[pid]))

			if new_frame.is_alive(pid):
				new_frame.kill(pid, -2)

	# Clear gens / budgets of dead players...

	for pid in range(players):
		if new_frame.is_alive(pid) == False:
			gens[pid] = 0
			new_frame.budgets[pid] = 0

	# Clear all ships of dead players...
	for idx, pid in enumerate(new_frame.ships):
		if ship == None:
			continue
		if new_frame.is_alive(ship.owner) == False:
			new_frame.ships = None

	# All surviving moves are valid (I hope)...

	# Make dropoffs
	for sid , move in enumerate(moves):
		if move!= "c": continue

		ship = new_frame.ships[sid]
		if ship == None: continue

		dropoff = Dropoff()
		dropoff.fact = False
		dropoff.owner = ship.owner
		dropoff.sid = ship.sid
		dropoff.X = ship.X
		dropoff.Y = ship.Y
		dropoff.gathered = ship.halite + new_frame.halite[ship.X][ship.Y]

		new_frame.dropoffs.append(dropoff)
		new_frame.ships[ship.sid] = None

		new_frame.deposited[ship.owner] += ship.halite
		new_frame.deposited[ship.owner] += new_frame.halite[ship.X][ship.Y]

		new_frame.halite[ship.X][ship.Y] = 0

	# Move ships...

	ship_positions = {}
	#############################################################
	#try:
	#	for ship in new_frame.ships:
	#		print("x: " + str(ship.X) + " y: " + str(ship.Y) + " | ")
	#except:
	#	pass
	for sid , move in enumerate(moves):
		if new_frame.ships == None: continue
		if new_frame.ships[sid] == None: continue
		ship = new_frame.ships[sid]

		mcr = MOVE_COST_RATIO
		if ship.inspired: mcr = INSPIRED_MOVE_COST_RATIO

		if ship.halite >= (new_frame.halite[ship.X][ship.Y] / mcr): #We can move
			if move not in ['','o','c']:
				ship.halite -= int(new_frame.halite[ship.X][ship.Y] / mcr)

				dx , dy = string_to_dxdy(move)
				ship.X += dx
				ship.Y += dy
				ship.X = mod(ship.X, width)
				ship.Y = mod(ship.Y, height)

		try: ship_positions[(ship.X, ship.Y)].append(ship)
		except: ship_positions[(ship.X, ship.Y)] = [ship]

	#print(ship_positions)
	#Find places that want to spawn, so we can check for collisions...

	attempted_spawn_points = {}

	for pid in range(players):
		if gens[pid]:
			factory = new_frame.dropoffs[pid]
			x = factory.X
			y = factory.Y

			attempted_spawn_points[(x,y)] = True

	# Delete ships that collide...

	collision_points = {}

	for point, ships_here in ship_positions.items():

		x,y = point[0] , point[1]

		if len(ships_here) == 1 and (x,y) not in attempted_spawn_points:
			continue

		collision_points[(x, y)] = True

		wreckedsids = []

		for ship in ships_here:
			new_frame.ships[ship.sid] = None
			new_frame.halite[x][y] += ship.halite
			wreckedsids.append(ship.sid)

	# Deliveries

	for dropoff in new_frame.dropoffs:
		pid = dropoff.owner
		x = dropoff.X
		y = dropoff.Y
		if (x,y) in ship_positions:
			ships_here = ship_positions[(x, y)]
		else: ships_here = []

		# First, handle halite that is on the ground (due to collisions)...

		halite_on_ground = new_frame.halite[x][y]

		if halite_on_ground > 0:
			dropoff.gathered += halite_on_ground
			new_frame.budgets[pid] += halite_on_ground
			new_frame.deposited[pid] += halite_on_ground
			new_frame.halite[x][y] = 0


		if len(ships_here)==1 and (x, y) not in collision_points:
			if ships_here[0].owner == pid:
				sid = ships_here[0].sid
				dropoff.gathered += ships_here[0].halite
				new_frame.budgets[pid] += ships_here[0].halite
				new_frame.deposited[pid] += ships_here[0].halite
				new_frame.ships[sid].halite = 0

	# Gen
	for pid in range(players):
		if gens[pid]:
			factory = new_frame.dropoffs[pid]

			x = factory.X
			y = factory.Y

			try : ships_here = ship_positions[(x, y)]
			except: ships_here = []
			if len(ships_here) == 1:
				#print("it couldn't generate")
				continue

			sid = len(new_frame.ships)

			ship = Ship()
			ship.owner = pid
			ship.sid = sid
			ship.X = x
			ship.Y = y
			ship.halite = 0
			ship.inspired = False

			new_frame.ships.append(ship)

	# Mining

	ibm = INSPIRED_BONUS_MULTIPLIER

	if new_frame.ships != None:
		for sid, ship in enumerate(new_frame.ships):
			if ship == None: continue

			if sid >= len(self.frame.ships): break

			old_ship = self.frame.ships[sid]

			if old_ship.X == ship.X and old_ship.Y == ship.Y:

				exrat = EXTRACT_RATIO

				if ship.inspired: exrat = INSPIRED_EXTRACT_RATIO

				amount_to_mine = int((new_frame.halite[ship.X][ship.Y] + exrat - 1 ) / exrat)
				if amount_to_mine + ship.halite >= MAX_ENERGY:
					amount_to_mine = MAX_ENERGY - ship.halite

				ship.halite += amount_to_mine
				new_frame.halite[ship.X][ship.Y]-= amount_to_mine
				#new_frame.halite[ship.X][ship.Y] = int(new_frame.halite[ship.X][ship.Y])

				if ship.inspired:
					inspired_bonus = amount_to_mine * ibm
					if inspired_bonus + ship.halite >= MAX_ENERGY:
						inspired_bonus = MAX_ENERGY - ship.halite

					ship.halite += inspired_bonus

	#Fix inspiration for ships on new frame

	new_frame.fix_inspiration(INSPIRATION_RADIUS,INSPIRATION_SHIP_COUNT)
	self.frame = new_frame
	return(1,1)
