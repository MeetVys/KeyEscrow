import os
from flask import Flask,render_template,jsonify,request,session
import ssl
import secrets
#os.environ['SSLKEYLOGFILE'] = '/home/sujeeth/network_security/key_escrow/sslkeylogfile'
app = Flask(__name__)
PORT = "5000"
URL = "0.0.0.0"

# Set up SSL/TLS context with keylog callback
context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
context.maximum_version = ssl.TLSVersion.TLSv1_2
context.minimum_version = ssl.TLSVersion.TLSv1_2
context.load_cert_chain(certfile='server.pem', keyfile='key.pem')

Admin_data_base = {
    'Admin_username': 'Admin_username_password'
}

# IP and List of strings "" : []
Keys_data_base = { 
    'Ip_address of server' : {'Ip_address_of_client': ['Testing keys']}
    
}

token_data_base =[]   # is for retrieving keys

@app.route('/' ,methods = ['GET'])
def index():
    return "Hello World"

# Define API endpoints

# Generating Tokens 
@app.route('/generatetokens', methods=['POST'])  # {'username' : val , 'password': val}
def generatetokens():
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
                'token' : token
            },200
        else :
            return "Password is Wrong",400
    else :
        return "User is not authenticated to access",400
    
    
@app.route('/keytoescrow', methods=['POST'])
# {'IP' : {'IP_addr': "session keys"}}   how server is sending the keys
def keytoescrow():
    ip_address_server = request.environ['REMOTE_ADDR']
    request_data = request.get_json()
    key_dict = request_data['IP']
    ip_addr_list = list(key_dict.keys())
    ip_addr = ip_addr_list[0] 
    session_keys = key_dict[ip_addr]
    if ip_address_server in Keys_data_base:
        if ip_addr in Keys_data_base[ip_address_server]:
            Keys_data_base[ip_address_server][ip_addr].append(session_keys)
        else :
            Keys_data_base[ip_address_server][ip_addr] = []
            Keys_data_base[ip_address_server][ip_addr].append(session_keys)
    else :
        t_list = []
        t_list.append(session_keys) 
        Keys_data_base[ip_address_server] = {ip_addr: t_list} 
    
    return jsonify(Keys_data_base),200

@app.route('/getkeys', methods=['POST'])
# Data Format {token : token, type:1 for whole server and 2 for client based , server_ip: IP , client_ip: iP }
def getkeys():
    global Keys_data_base
    request_data = request.get_json()
    auth_token = request_data['token']
    type = request_data['type']
    if auth_token in token_data_base:
        if type == 1:
            if request_data['server_ip'] in Keys_data_base:
                return jsonify(Keys_data_base[request_data['server_ip']]),200
            else :
                return jsonify({}),200
        elif type == 2 :
            if request_data['server_ip'] in Keys_data_base:
                if request_data['client_ip']  in Keys_data_base[request_data['server_ip']] :
                    return jsonify(Keys_data_base[request_data['server_ip']][request_data['client_ip']]),200
                else :
                    return jsonify({}),200
            else :
                return jsonify({}),200

        else :
            return "Invalid",400
    else :
        return "No Authorised for this data",400
    


if __name__ == '__main__':
    app.run(host= URL,port=PORT,debug=True,ssl_context=context)