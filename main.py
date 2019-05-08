import json , time , os , sys
from subprocess import run, PIPE
from sim.sim import *
from sim.replay import *
from sim.mapgen import *
from sim.constants import *


def bot_handler(cmd, pid, io, pregame):
	bot_is_kill = False

	sys.stdout.flush()

# ----------------------------------------------------------------

class QuickGame():
	def __init__(self,width = 32, height = 32, players = 2, seed = ''):
		if seed == '':
			seed = int(time.time())
		self.turn = 0
		self.isdone = False
		self.seed = seed
		self.turns = turns_from_size(width, height)
		self.players = players
		if self.players < 1 or (self.players > 4):
			print("Bad number of players: %d\n" % (self.players))
			return()

		constants = [self.players, width, height, self.turns, self.seed]
		self.game = Game(constants)

		self.game.use_frame(map_gen_official(players, width, height, INITIAL_ENERGY, seed))

	def gameloop(self,move_strings = []):

		'''if self.turn == 0:
									move_strings = [{'g':'g'}]*self.players
								elif self.turn <= 400:
									move_strings = [{},{'m':[1,'n']}]
								else:
									move_strings = [{}]*self.players'''
		self.game.update_from_moves(self.game,move_strings)

		if self.turn < self.turns:
			self.turn +=1
			return self.isdone, self.game.frame
		else:
			return self.game_ending(move_strings)

	def game_ending(self,move_strings):
		self.isdone = True
		_ , rf = self.game.update_from_moves(self.game,move_strings)

		results = {'stats':{}}
		results['seed'] = self.seed
		results['time'] = 0

		for pid in range(self.players):
			rank = {
				'rank': self.game.get_rank(pid),
				'score': self.game.budget(pid)
			}
			results['stats'][pid] = rank

		return self.isdone, results

	def reset(self):
		pass


def main():
	start_time = time.time()
	width, height, sleep, seed, no_timeout, no_replay, viewer, folder, infile, inPNG, botlist = parse_args()

	provided_frame = None

	if infile != None: provided_frame = FrameFromFile(infile)
	elif inPNG != None: provided_frame = FrameFromPNG(inPNG)


	if provided_frame != None:
		width = provided_frame.width()
		height = provided_frame.height()

	turns = turns_from_size(width, height)

	players = len(botlist)

	if provided_frame != None and provided_frame.player() != players:
		print("Wrong number of bots (%d) given for this replay (need %d)\n" % ( players, provided_frame.Players()))
		return()


	if players < 1 or (players > 4 and provided_frame ==None):
		print("Bad number of players: %d\n" % (players))
		return()

	io_chans = ['']*players

	constants = [players, width, height, turns, seed]
	game = Game(constants)

	if provided_frame == None:
		game.use_frame(map_gen_official(players, width, height, INITIAL_ENERGY, seed))
	else:
		game.use_frame(provided_frame)

	json_blob = "im json blob"
	init_string = game.bot_init_string()

	for pid in range(players):
		pregame = "%s\n%d %d\n%s" % (json_blob, players, pid, init_string)
		bot_handler(botlist[pid], pid, io_chans[pid], pregame)

	if viewer:
		print(pregame)

	player_names = []
	for pid in range(players):
		player_names.append("")

	if viewer:
		print(player_names)

	if no_replay!= True:
		#replay = Replay(player_names, game, turns, seed)
		pass


	move_strings = [[],[]]

	for turn in range(turns+1):
		if turn == 0:
			print("pla!")
			move_strings = [['g'],['g']]
		elif turn <= 400:
			#move_strings = [['g'],['g']]
			move_strings = [['m 0 n'],['m 1 n']]
		else:
			move_strings = [[],[]]
		game.update_from_moves(game,move_strings)

		if turn < turns:
			for pid in range(players):
				if game.is_alive(pid): io_chans[pid] = ''

		received = [0]*players
		received_total = 0

		for pid in range(players):
			if game.is_alive(pid) == False or turn == turns:
				move_strings[pid] = []
				received[pid] = True
				received_total += 1


	_ , rf = game.update_from_moves(game,move_strings)

	if viewer == False:
		results = {'stats':{}}
		results['seed'] = seed
		results['time'] = 0

		for pid in range(players):
			rank = {
				'rank': game.get_rank(pid),
				'score': game.budget(pid)
			}
			results['stats'][pid] = rank

	print(results)



def parse_args():
	width, height, sleep, seed, no_timeout, no_replay, viewer, folder, infile, inPNG, botlist = [None]*11
	folder = "./"
	seed = int(time.time())
	args = sys.argv
	viewer = False
	dealt_with = [0]*len(args)
	dealt_with[0] = True
	botlist = []
	for n, arg in enumerate(args):
		if dealt_with[n]:
			continue

		if arg == "--width" or arg == "-w":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			width = args[n + 1]
			try: width = int(width)
			except:
				print("Couldn't understand stated width.\n")
				sys.exit()
			continue

		if arg == "--height" or arg == "-h":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			height = args[n+1]
			try: height = int(height)
			except:
				print("Couldn't understand stated height.\n")
				sys.exit()
			continue

		if arg == "--seed" or arg == "-s":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			seed = args[n+1]
			try: seed = int(seed)
			except:
				print("Couldn't understand stated seed.\n")
				sys.exit()
			continue

		if arg == "--sleep":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			sleep = args[n+1]
			try: sleep = int(sleep)
			except:
				print("Couldn't understand stated sleep.\n")
				sys.exit()
			continue

		if arg == "--file" or arg == "-f":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			infile = args[n+1]
			continue

		if arg == "--png" or arg == "-g":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			inPNG = args[n+1]
			continue

		if arg == "--replay-directory" or arg == "-i":
			dealt_with[n] = True
			dealt_with[n + 1] = True
			folder = args[n+1]
			continue

		if arg == "--viewer" or arg == "-u":
			dealt_with[n] = True
			viewer = True
			continue

		if arg == "--no-timeout":
			dealt_with[n] = True
			no_timeout = True
			continue

		if arg == "--no-replay":
			dealt_with[n] = True
			no_replay = True
			continue

		if arg == "--no-compression": # We already don't...
			dealt_with[n] = True
			continue

		if arg == "--results-as-json": # We already do...
			dealt_with[n] = True
			continue

		if arg == "--no-logs": # We already don't...
			dealt_with[n] = True
			continue

	for n, arg in enumerate(args):
		if dealt_with[n]:
			continue

		if len(arg) > 0 and arg[0] == '-':
			print("Couldn't understand flag %s (not implemented)\n" % (arg))
			sys.exit()

	for n, arg in enumerate(args):
		if dealt_with[n]:
			continue
		botlist.append(arg)

	if width == 0 and height > 0: width = height
	if height == 0 and width > 0: height = width

	if width < 2 or width > 128 or height <2 or height > 128:
		width = sim.SizeFromSeed(seed)
		height = width

	return (width, height, sleep, seed, no_timeout, no_replay, viewer, folder, infile, inPNG, botlist)

def turns_from_size(width,height):
	size = width
	if height > size: size = height
	return int(((size * 25) / 8) + 300)



main()