import paramiko
import time
import re
import os

def ssh_connect_and_execute_currentPort(hostnameOLTAntiga, username, password, pon_ANTIGA, delay=0.2, timeout=6, max_loops=20):
    commands_summary = [
        "enable",
        "config",
        f"display current-configuration port {pon_ANTIGA} | no-more"
    ]

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostnameOLTAntiga, username=username, password=password, timeout=timeout)
        ssh_shell = client.invoke_shell()

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
            #print(full_currentPort)

        # Filtra as linhas desejadas usando expressões regulares
        gpon_section = re.findall(r'\[gpon\][\s\S]*?#', full_currentPort)
        bbs_config_section = re.findall(r'\[bbs-config\][\s\S]*?#', full_currentPort)

        filtered_currentPort = gpon_section + bbs_config_section

        # Diretório de saída
        output_dir = 'src'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Salvando a saída completa em um arquivo
        full_currentPort_txt = os.path.join(output_dir, 'full_currentPort.txt')
        with open(full_currentPort_txt, 'w') as file:
            file.write(full_currentPort)

        # Salvando as seções filtradas
        filtered_currentPort_txt = os.path.join(output_dir, 'filtered_currentPort.txt')
        with open(filtered_currentPort_txt, 'w') as file:
            file.write('\n'.join(filtered_currentPort))

        print(f"As linhas filtradas foram salvas em '{filtered_currentPort_txt}'.")

    except paramiko.AuthenticationException:
        print("Erro de autenticação. Verifique o usuário e senha.")
    except paramiko.SSHException as ssh_exception:
        print(f"Erro de SSH: {ssh_exception}")
    except Exception as e:
        print(f"Erro ao conectar ou executar comandos: {e}")
    finally:
        client.close()
