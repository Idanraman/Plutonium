
'''
	This file is under the MIT License.

	Copyright (c) 2016 Michael Truell and Benjamin Spector

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in
	all copies or substantial portions of the Software.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
	THE SOFTWARE.
'''
import math, random
from sim.sim import *
from sim.mt19937 import Twister
#from mt19937_32 import mt19937_32

def rand_func():
	return(rand_creator.random32())


def urd():
	minor = rand_func() / 0xffffffffffffffff
	major = rand_func() / 0x100000000
	return major + minor


def map_gen_official(players, width, height, player_energy, seed):
	
	global rand_creator
	rand_creator = Twister(seed=seed)

	frame = Frame()

	for pid in range(players):
		frame.budgets.append(player_energy)
		frame.deposited.append(0)
		frame.last_alive.append( -1)

	frame.halite = [[0 for x in range(width)] for y in range(height)]

	tile_width = width
	tile_height = height

	tile_cols = 1
	tile_rows = 1

	if players > 1:
		tile_width = width / 2
		tile_cols = 2

	if players > 2:
		tile_height = height / 2
		tile_rows = 2

	if width % 2 == 1 and tile_cols >= 2 : tile_width += 1
	if height % 2 == 1 and tile_rows >=2 : tile_height += 1

	tile_width = int(tile_width)
	tile_height = int(tile_height)

	tile = make_tile(tile_width,tile_height)

	for y in range(tile_height):
		for x in range(tile_width):

			val = tile[y][x]

			frame.halite[x][y] = val

			if tile_cols > 1: frame.halite[width -1 -x][y] = val

			if tile_rows > 1:
				frame.halite[x][height - 1 - y] = val
				frame.halite[width - 1 - x][height - 1 - y] = val

	place_factories(frame, players, tile_width, tile_height)
	#print(frame.halite)
	return frame

def generate_smooth_noise(source_noise, wavelength):
	# source noise [[0]*8]*10 , wavelength = 2
	length = math.ceil(len(source_noise) / wavelength) # 10
	wide = math.ceil(len(source_noise[0]) / wavelength)

	mini_source = [[0 for x in range (wide)] for y in range (length)]
	#mini_source = [[0 for x in range (wide)] for y in range (length)]

	for y in range(len(mini_source)):
		for x in range(len(mini_source[0])):
			m = source_noise[wavelength * y][wavelength * x]
			mini_source[y][x] = m
	
	smoothed_source = [[0 for x in range (len(source_noise))] for y in range (len(source_noise[0]))]
	#smoothed_source = [[0 for x in range (len(source_noise[0]))] for y in range (len(source_noise))]
	for y in range(len(source_noise)):
		y_i = int(y / wavelength)
		y_f = int((y/wavelength+1) % len(mini_source))

		vertical_blend = y/wavelength - y_i

		for x in range(len(source_noise[0])):
			x_i = int(x/wavelength)
			x_f = int((x / wavelength + 1) % len(mini_source[0]))

			horizontal_blend = x/wavelength - x_i

			top_blend = (1-horizontal_blend) * mini_source[y_i][x_i] + horizontal_blend * mini_source[y_i][x_f]

			bottom_blend = (1 - horizontal_blend) * mini_source[y_f][x_i] + horizontal_blend * mini_source[y_f][x_f]

			smoothed_source[x][y] = (1 - vertical_blend) * top_blend + vertical_blend * bottom_blend

	return smoothed_source

def make_tile(tile_width,tile_height):

	tile = [[0 for y in range (tile_width)] for x in range (tile_height)]

	#tile = [[0 for x in range (tile_height)] for y in range (tile_width)]
	source_noise = [[0 for x in range (tile_height)] for y in range (tile_width)]
	region = [[0 for x in range (tile_height)] for y in range (tile_width)]

	FACTOR_EXP_1 = 2
	FACTOR_EXP_2 = 2
	PERSISTENCE = 0.7
	MAX_CELL_PRODUCTION = 1000
	MIN_CELL_PRODUCTION = 900

	for x in range(tile_height):
		for y in range(tile_width):
			source_noise[y][x] = math.pow(urd(), FACTOR_EXP_1)

	MAX_OCTAVE= int(math.floor(math.log(min(tile_width, tile_height),2))) +1
	amplitude= 1.0

	for octave in range(2,MAX_OCTAVE+1):
		smoothed_source = generate_smooth_noise(source_noise, int(round(math.pow(2,MAX_OCTAVE - octave))))
		for x in range(tile_height):
			for y in range(tile_width):
				region[y][x] += amplitude * smoothed_source[x][y]

		amplitude *= PERSISTENCE

	for x in range(tile_height):
		for y in range(tile_width):
			region[y][x] += amplitude * smoothed_source[x][y]

	max_value = 0

	for x in range(tile_height):
		for y in range(tile_width):
			region[y][x] = math.pow(region[y][x], FACTOR_EXP_2)
			if region[y][x] > max_value : max_value = region[y][x]

	actual_max = rand_func() % (1 + MAX_CELL_PRODUCTION - MIN_CELL_PRODUCTION) + MIN_CELL_PRODUCTION

	for x in range(tile_height):
		for y in range(tile_width):
			region[y][x] *= actual_max / max_value
			tile[x][y] = int(round(region[y][x]))

	rand_func()
	rand_func()
	return tile

def place_factories(frame, players, tile_width, tile_height):
	width = frame.width()
	height = frame.height()

	dx = 0.5 * tile_width
	dy = 0.5 * tile_height

	if tile_width>=16 and tile_width<=40 and tile_height>=16 and tile_height<=40:
		dx = int(8.0 + ((tile_width - 16) / 24.0) * 20.0)
		if players > 2:
			dy = int(8.0 + ((tile_height - 16) / 24.0) * 20.0)

	for pid in range(players):
		if pid ==0:
			x = dx
			y = dy
		elif pid == 1:
			x = width - 1 - dx
			y = dy
		elif pid == 2:
			x = dx
			y = height - 1 - dy
		elif pid == 3:
			x = width - 1 - dx
			y = height - 1 - dy

		factory = Dropoff()
		factory.fact = True
		factory.owner = pid
		factory.sid = -1
		factory.X = int(x)
		factory.Y = int(y)
		factory.gathered = 0

		frame.dropoffs.append(factory)
		frame.halite[int(x)][int(y)] = 0