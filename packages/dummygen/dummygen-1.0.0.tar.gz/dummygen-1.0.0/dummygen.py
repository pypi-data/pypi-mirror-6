import random

def generate_user_name():
	first_name_length = random.randrange(3,9)
	last_name_length = random.randrange(4,11)
	letter_pool = 'abcdefghijklmnopqrstuvwxyz'
	first_name = ''
	last_name = ''
	while len(first_name) <= first_name_length:
		first_name += random.choice(letter_pool)
	while len(last_name) <= last_name_length:
		last_name += random.choice(letter_pool)

	return first_name.capitalize() + ' ' + last_name.capitalize()
	
	
def generate_sample_users(num):
	user_dict = {}

	for i in range(0,num):
		user_id = hash(generate_user_name())
		user_dict[generate_user_name()] = {}
	return user_dict


