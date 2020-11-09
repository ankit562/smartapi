# package import statement
from smartapi import smartConnect as sc

# creating object of the class SmartConnect
obj = sc.SmartConnect()


# function to call the login api

def loginApiCall(clientcode, password):
    print(clientcode, password)
    login_response = obj.generateSession(clientcode, password)
    print("Logged in Successfully")
    return login_response


print(loginApiCall('D88311', 'Angel@444'))
