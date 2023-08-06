""" Just some random dummy name generator,
	with a dummy user dictionary generator too!
	--------------------------------
	author: Shane Woodson
	version: 1.0.1
"""

import random

def generate_user_name():
	first_name = ''
	last_name = ''

	first_name_length = random.randrange(2,9)
	last_name_length = random.randrange(4,11)

	first_name_start_letters = 'ABCDEFGHJKLMNOPQRSTW'
	last_name_start_letters = 'ABCDEFGHJKLMNOPRSTVWYZ'

	return generate_name(first_name, first_name_start_letters, first_name_length).capitalize() + ' ' + generate_name(last_name, last_name_start_letters, last_name_length).capitalize()
	

def generate_name(name, letters, length):

	consonants = 'bcdfghjklmnpqrstvwxz'
	vowels = 'aeiou'
	rare_vowel = 'y'

	rare_roll = random.randrange(0,9)
	while len(name) <= length:
		if len(name) == 0:
			name += random.choice(letters)
		elif len(name) == 1:
			name += random.choice(vowels)
		elif len(name) == 2:
			if rare_roll > 3:
				name += random.choice(consonants)
			else:
				name += random.choice(vowels)
		elif len(name) == 3:
			name += random.choice(consonants)
		elif len(name) == 4:
			name += random.choice(vowels)
		elif len(name) >= 5:
			name += random.choice(consonants)
			name += random.choice(vowels)

		if len(name) == length and rare_roll == 0:
			name += rare_vowel

		if len(name) == length and name[-1] in 'cgjpquvxz':
			name = name[:-1] + chr(ord(name[-1])-1)

	return name

	
def generate_sample_users(num):
	user_dict = {}

	for i in range(0,num):
		user_id = hash(generate_user_name())
		user_dict[generate_user_name()] = {}
	return user_dict
