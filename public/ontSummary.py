import paramiko
import time
import re
import json
import os

def ssh_connect_and_execute_summary(hostnameOLTAntiga, username, password, autofind_onus_file, onus_config_file, delay=0.2, timeout=6, max_loops=20):
    with open(autofind_onus_file, 'r') as file:
        autofind_onus = json.load(file)

    with open(onus_config_file, 'r') as file:
        onus_config = json.load(file)

    authorized_sns = {onu['sn_auth'] for onu in onus_config}

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostnameOLTAntiga, username=username, password=password, timeout=timeout)
        ssh_shell = client.invoke_shell()

        ont_summary_data = []
        processed_fsp = set() 

        for onu in autofind_onus:
            f_s_p = onu['F/S/P']
            sn = onu['Ont SN']

            if sn not in authorized_sns or f_s_p in processed_fsp:
                continue 

            commands_summary = [
                "enable",
                "config",
                f"display ont info summary {f_s_p} | no-more"
            ]

            full_currentPort = ""

            for command in commands_summary:
                ssh_shell.send(command + '\n')
                time.sleep(delay)

                output = ""
                loops = 0
                while loops < max_loops:
                    if ssh_shell.recv_ready():
                        chunk = ssh_shell.recv(4096).decode('utf-8')
                        output += chunk

                        if "{ <cr>||<K> }" in chunk:
                            ssh_shell.send('\n')
                            time.sleep(delay)

                    else:
                        time.sleep(0.5)

                    loops += 1

                full_currentPort += output

            processed_fsp.add(f_s_p)

            ont_info = re.findall(r'^\s*\d+\s+[A-F0-9]+\s+\S+\s+.*$', full_currentPort, re.MULTILINE)

            for info in ont_info:
                info_parts = re.split(r'\s+', info.strip(), maxsplit=5)
                ont_summary_data.append({
                    "F/S/P": f_s_p,
                    "ONT ID": info_parts[0],
                    "SN": info_parts[1],
                    "Type": info_parts[2],
                    "Distance": info_parts[3],
                    "Rx/Tx power": info_parts[4],
                    "Description": info_parts[5]
                })

        output_dir = 'src'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        ont_summary_json = os.path.join(output_dir, 'ontSummary.json')
        with open(ont_summary_json, 'w') as file:
            json.dump(ont_summary_data, file, indent=4)

        print(f"As informações das ONUs foram salvas em '{ont_summary_json}'.")

    except paramiko.AuthenticationException:
        print("Erro de autenticação. Verifique o usuário e senha.")
    except paramiko.SSHException as ssh_exception:
        print(f"Erro de SSH: {ssh_exception}")
    except Exception as e:
        print(f"Erro ao conectar ou executar comandos: {e}")
    finally:
        client.close()

autofind_onus_file = 'src/autofind_onus.json'
onus_config_file = 'src/onus_config.json'

