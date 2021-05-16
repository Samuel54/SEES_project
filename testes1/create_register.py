#!/usr/bin/env python3

import bcrypt
import os
import pickle
import base64

user_list = {}
with open('user_register.txt', 'wb+') as handle:
    pickle.dump(user_list, handle)
with open('user_register.txt', 'rb') as handle:
    user_list = pickle.loads(handle.read())

aux = 'Y'
while aux == 'Y' or aux == 'y':
    aux = input("Add  user? Y/N: ")
    if aux == 'Y' or aux == 'y':
        aux1 = 0
        while aux1 == 0:
            username = input("Please enter the @user name:")
            key_to_lookup = username
            if key_to_lookup in user_list:
                print("This user is already in use! Choose another one.")
            else:
                user_id = base64.b64encode(os.urandom(6))
                salt = bcrypt.gensalt()
                hashed_user_id = bcrypt.hashpw(user_id, salt)
                user_list[username] = hashed_user_id
                aux1 = 1
                print("Username saved")
                print("Your user ID is : ", user_id)
with open('user_register.txt', 'wb') as handle:
    pickle.dump(user_list, handle)


print(user_list)