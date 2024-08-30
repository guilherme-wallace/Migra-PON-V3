import paramiko
import time
import os

def ssh_connect_and_execute_commands(hostname, username, password, commands, delay=0.2, timeout=6, max_loops=20):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname, username=username, password=password, timeout=timeout)
        ssh_shell = client.invoke_shell()

        for command in commands:
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

            #print(output)

    except paramiko.AuthenticationException:
        print("Erro de autenticação. Verifique o usuário e senha.")
    except paramiko.SSHException as ssh_exception:
        print(f"Erro de SSH: {ssh_exception}")
    except Exception as e:
        print(f"Erro ao conectar ou executar comandos: {e}")
    finally:
        client.close()

def execute_olt_commands_autorizaOLT(hostnameOLTAntiga, hostnameOLTNova, username, password):
    # Diretórios e arquivos
    delete_commands_file = 'src/ontDelete.txt'
    authorize_commands_file = 'src/autorizaONU.txt'

    # Leitura dos comandos de remoção
    if os.path.exists(delete_commands_file):
        with open(delete_commands_file, 'r') as file:
            delete_commands = file.read().splitlines()
    else:
        print(f"Arquivo {delete_commands_file} não encontrado.")
        return

    # Leitura dos comandos de autorização
    if os.path.exists(authorize_commands_file):
        with open(authorize_commands_file, 'r') as file:
            authorize_commands = file.read().splitlines()
    else:
        print(f"Arquivo {authorize_commands_file} não encontrado.")
        return

    # Executando comandos na OLT antiga
    print(f"Executando comandos na OLT antiga: {hostnameOLTAntiga}")
    ssh_connect_and_execute_commands(hostnameOLTAntiga, username, password, delete_commands, delay=0.2, timeout=4, max_loops=6)

    # Executando comandos na OLT nova
    print(f"Executando comandos na OLT nova: {hostnameOLTNova}")
    ssh_connect_and_execute_commands(hostnameOLTNova, username, password, authorize_commands, delay=0.2, timeout=4, max_loops=6)


