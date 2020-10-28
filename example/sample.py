#package import statement
from smartapi import smartConnect as sc

#creating object of the class SmartConnect
obj=sc.SmartConnect()

#function to call the login api

def loginApiCall(clientcode,password):
    print(clientcode,password)
    loginResponse= obj.generateSession(clientcode,password)
    print("Loggedin Successfully")
    return loginResponse


print(loginApiCall('D88311','Angel@444'))

