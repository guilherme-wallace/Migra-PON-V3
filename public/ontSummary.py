import paramiko
import time
import re
import json
import os

def ssh_connect_and_execute_summary(hostnameOLTAntiga, username, password, autofind_onus_file, onus_config_file, delay=0.2, timeout=6, max_loops=20):
    # Carregar os arquivos JSON
    with open(autofind_onus_file, 'r') as file:
        autofind_onus = json.load(file)

    with open(onus_config_file, 'r') as file:
        onus_config = json.load(file)

    # Criar um dicionário de SNs autorizados
    authorized_sns = {onu['sn_auth'] for onu in onus_config}

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostnameOLTAntiga, username=username, password=password, timeout=timeout)
        ssh_shell = client.invoke_shell()

        ont_summary_data = []
        processed_fsp = set()  # Conjunto para rastrear os F/S/P já processados

        for onu in autofind_onus:
            f_s_p = onu['F/S/P']
            sn = onu['Ont SN']

            if sn not in authorized_sns or f_s_p in processed_fsp:
                continue  # Pula se SN não autorizado ou F/S/P já processado

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

            # Marcar o F/S/P como processado
            processed_fsp.add(f_s_p)

            # Extrair as informações de interesse usando regex
            ont_info = re.findall(
                r'(\d+)\s+(\w+)\s+([\w-]+)\s+(-?\d+\.?\d*/-?\d+\.?\d*)\s+(.*)',
                full_currentPort
            )

            for info in ont_info:
                ont_summary_data.append({
                    "F/S/P": f_s_p,
                    "ONT ID": info[0],
                    "SN": info[1],
                    "Type": info[2],
                    "Rx/Tx power": info[3],
                    "Description": info[4]
                })

        # Diretório de saída
        output_dir = 'src'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Salvando as informações em um arquivo JSON
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
