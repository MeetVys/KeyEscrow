import os
from flask import Flask,render_template,jsonify,request,session
import requests
import ssl
import secrets
import time

log_file = open("sslkeylogfile.log", "w")
log_file.truncate()
log_file.close()
URL_ESCROW = "https://127.0.0.1:5000/keytoescrow"

#os.environ['SSLKEYLOGFILE'] = '/home/sujeeth/network_security/key_escrow/sslkeylogfile'
app = Flask(__name__)

URL = "127.0.0.1"
PORT = "4000"

# Set up SSL/TLS context with keylog callback
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.maximum_version = ssl.TLSVersion.TLSv1_2
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.keylog_filename = 'sslkeylogfile.log'
context.load_cert_chain(certfile='server.pem', keyfile='key.pem')
sess = {}

num_of_entries = 1


Admin_data_base = {
    'Admin_username': 'Admin_username_password'
}
token_data_base =[]   # is for retrieving keys

IPs_to_LI = []  # IP address to be Legally introspected
type_LI = 0

def map_session_keys(sess,request):
    global num_of_entries
    time.sleep(1)
    with open("sslkeylogfile.log",'r') as fp:
        lines = fp.readlines()

    desired_lines = lines[num_of_entries - 1:]
    print ("Number of lines : ", len(lines), "num_entries: ", num_of_entries)
    for line in desired_lines:
        print("updates lins : ", num_of_entries+1)
        words = line.split() 
        if words[0] == "CLIENT_RANDOM":
            num_of_entries = num_of_entries +1 
            obj = {request.environ['REMOTE_ADDR']: line}
            print(obj)
            return obj
        else :
            num_of_entries = num_of_entries +1 
    return None

# Generating Tokens 
@app.route('/generatetokens', methods=['POST'])  # {'username' : val , 'password': val}
def generatetokens():
    global Admin_data_base
    global token_data_base
    obj = map_session_keys(sess,request)
    request_data = request.get_json()

    if 'username' in request_data:                  # If change in database check here
        username = request_data['username']
    else :
        return "Failed Username",400
    if 'password' in request_data:
        password = request_data['password']
    else :
        return "Failed Password",400
    if username in Admin_data_base:
        if Admin_data_base[username] == password:
            token = secrets.token_urlsafe(16)
            token_data_base.append(token)
            return {
                'token' : token,
                'length' : num_of_entries
            },200
        else :
            return "Password is Wrong",400
    else :
        return "User is not authenticated to access",400
    

@app.route('/LI', methods=['POST'])
# Data Format {token : token, type:1 for whole server and 2 for client based 3 stop, 4 purge the client ip, client_ip: iP }
def LI():
    obj = map_session_keys(sess,request)
    global type_LI
    global IPs_to_LI
    global token_data_base
    request_data = request.get_json()
    auth_token = request_data['token']
    type = request_data['type']
    if auth_token in token_data_base:
        if type == 1:
            type_LI = 1
            print("Type of LI" , type_LI)
            return "Started the LI for the whole Server",200
        elif type == 2 :
            type_LI =2 
            if request_data['client_ip'] not in IPs_to_LI:
                IPs_to_LI.append(request_data['client_ip'])
            print("Type of LI" , type_LI)
            return jsonify(IPs_to_LI) ,200
        elif type == 0 : 
            type_LI = 0 
            IPs_to_LI = []
            print("Type of LI" , type_LI)
            return jsonify(IPs_to_LI),200
        elif type == 4 :
            if type_LI == 2:
                if request_data['client_ip'] in IPs_to_LI:
                    IPs_to_LI.remove(request_data['client_ip'])
                    print("Type of LI" , type_LI)
                    return jsonify(IPs_to_LI),200
                else :
                    return "Ip was not in LI list",200
            else :
                return "It only works when type is set to 2",200
            
        else :
            return "Invalid",400
    else :
        return "No Authorised for this data",400


def sending_key_to_escrow(obj) :
    if obj is None:
        return
    data =  {'IP' : obj}
    response = requests.post(URL_ESCROW,json=data,verify=False)
    if response.status_code == 200  :
        obj = map_session_keys(sess,request)
        print("success in sending")
    else:
        print("something wring ")
    print(response.json())


@app.route('/')
def index():
    global type_LI
    global IPs_to_LI
    print(request.remote_addr)
    print (type_LI)
    obj = map_session_keys(sess,request)
    if type_LI == 1:
        sending_key_to_escrow(obj)
    elif type_LI ==2 :
        if request.remote_addr in IPs_to_LI:
            sending_key_to_escrow(obj)
    if obj is None:
        print( "Hell No None")
        return "Some how we have none"

    return obj

if __name__ == '__main__':
    app.run(host=URL,port=PORT,debug=True,ssl_context=context)

