#!/usr/bin/env python3

import pickle
import bcrypt

# def register_client(username, onetimeID):

username = '@user1'
user_list = {}
with open('user_register.txt', 'rb') as handle:
    user_list = pickle.loads(handle.read())

print("The user list is :")
for key, value in user_list.items():
    print(key)


for key, value in user_list.items():
    if key == username:
        print("The user:" + " " + str(key) + " " + "as this hash value:" + " " + str(value))
        id = b'ZmLMGpQT'
        hashed = value
        #salt = bcrypt.gensalt()
        #hashed = bcrypt.hashpw(id, salt)

        if bcrypt.checkpw(id, hashed):
            print("match")
        else:
            print("does not match")




"""
# Extracting specific keys from dictionary
res = {key: user_list[key] for key in user_list.keys() & {username}}
# print result
print("The " + username + " filtered dictionary is : " + str(res))

"""