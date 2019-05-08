import json, os

PRETTYPRINT = False


class Replay(object):
	"""docstring for Replay"""
	def __init__(self, player_names, game, turns, seed):
		self.engine_version = "Plutonium Engine"
		self.contsants = game.contsants
		self.file_version = 3
		self.seed = seed
		self.num_players = game.frame.players()

		self.players = []
		self.full_frames = []
		self.stats = None
		self.production_map = None

		for pid in range(num_players):
			player = ReplayPlayer(names[pid],pid,game)
			self.players.append(player)

		self.production_map = ReplayMapFromFrame(game.frame)

	def dump(self,filename):
		outfile = open("guru99.txt","w+")

		enc = json.NewEn
		pass

class ReplayPlayer(object):
	def __init__(self,filename):
		pass

class CellUpdate(object):
	def __init__(self,filename):
		pass

class ReplayFrame(object):
	def __init__(self,filename):
		pass

class ReplayMove(object):
	def __init__(self,filename):
		pass

class ReplayStats(object):
	def __init__(self,filename):
		pass

class PlayerStats(object):
	def __init__(self,filename):
		pass

class EnergyHolder(object):
	def __init__(self,filename):
		pass

class ReplayMap(object):
	def __init__(self,filename):
		pass

class ReplayPlayer(object):
	def __init__(self):
		pass
