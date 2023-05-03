import requests

gen_token_Keyesc = "https://172.17.0.3:5000/generatetokens"
gen_token_server = "https://172.17.0.2:4000/generatetokens"

LI_URL = "https://172.17.0.2:4000/LI"

Get_Keys_URL = "https://172.17.0.3:5000/getkeys"

response = requests.post(gen_token_Keyesc,json={"username" : "Admin_username" , "password": "Admin_username_password"},verify=False)
if response.status_code ==200:
    response = response.json() 
    token_Keyes = response['token']
    print(token_Keyes)
else:   
    print ("Error in Generating Key Escrow Token")

response = requests.post(gen_token_server,json={"username" : "Admin_username" , "password": "Admin_username_password"},verify=False)
if response.status_code ==200:
    response = response.json() 
    token_server = response['token']
    print(token_server)
else :
    print ("Error in Generating Web Server Token")



while 1 : 
    print ("Press 1 for LI Utility")
    print ("Press 2 for Retrieve Keys from key escrow")
    x = input("Enter the number : ")
    if x == "1":
        print("Press 1 to Start LI for Whole Server")
        print("Press 2 to Start LI for particular client IP")
        print("Press 0 to Stop LI for Whole Server")
        print("Press 4 to Stop LI particular client IP")

        type_LI  = input("Enter Number: ")
        if type_LI.isdigit() :
            type_LI = int(type_LI)
            if type_LI ==0 or type_LI == 1: 
                response = requests.post(LI_URL,json={"token" : token_server, "type":type_LI , "client_ip": "127.0.0.122" },verify=False)
                print(response)
            elif type_LI  ==2 or type_LI ==4 :
                client_IP = input("Enter Client IP")
                response = requests.post(LI_URL,json={"token" : token_server, "type":type_LI , "client_ip": client_IP },verify=False)
                print(response)
            else :
                print("Invalid LI TYpe")

        else :
            print("Invalid LI Type")



    elif x == "2" :
        print("Press 1 to get Whole Server Keys")
        print("Press 2 to get Client Keys on a server")
        type_LI = input("Enter number")
        server_ip = input("Enter Server IP: ")
        if type_LI == "1":
            response = requests.post(Get_Keys_URL,json={"token" : token_Keyes, "type":1 , "server_ip": server_ip, "client_ip": "127.0.0.1" },verify=False)
            
            retrived_key_file = open("retrived_key_file.log", "w")
            retrived_key_file.truncate()
            response = response.json()
             
            client_as_keys = list(response)
            for item in client_as_keys:
                key_list_c = response[item]
                for key_val in key_list_c:
                    retrived_key_file.write(key_val)


            retrived_key_file.close()

        elif type_LI =="2" :
            client_IP = input("Enter Client IP: ")
            response = requests.post(Get_Keys_URL,json={"token" : token_Keyes, "type":2 , "server_ip": server_ip, "client_ip": client_IP},verify=False)
            retrived_key_file = open("retrived_key_file.log", "w")
            retrived_key_file.truncate()
            response = response.json() 
            for key_val in response:
                retrived_key_file.write(key_val)


            retrived_key_file.close()
        
        else :
            print("Invalid number")


    elif x == "3" :
        break
    else :
        print("Invalid")
