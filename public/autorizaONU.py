import json

def authorize_onus(json_path, autofind_onus_path, autorizaONU_path, autorizaONUExcecoo_path, ont_pon_ANTIGA, start_id=0, lineprofile_id=None, srvprofile_id=None,
                   native_vlan=None, service_port_id=None, vlan=None, gemport=None, user_vlan=None):    
    try:
        # Leitura do arquivo JSON com as ONUs e do arquivo autofind
        with open(json_path, 'r') as file:
            onus = json.load(file)
        
        with open(autofind_onus_path, 'r') as file:
            autofind_onus = json.load(file)
        
        # Listas para armazenar comandos de autorização
        authorization_commands = ["enable", "", "config", ""]
        exception_commands = ["enable", "", "config", ""]
        delete_commands = ["enable", "", "config", ""]
        
        # Iterar sobre as ONUs no arquivo de configuração
        for onu in onus:
            # Verificar se a ONU está no arquivo autofind
            matching_onu = next((a_onu for a_onu in autofind_onus if a_onu["Ont SN"] == onu["sn_auth"]), None)
            if not matching_onu:
                continue  # Pular a ONU se não estiver no autofind

            pon_antiga = ont_pon_ANTIGA
            interfaceGPON_antiga = "/".join(pon_antiga.split("/")[0:2])
            gPON_antiga = "/".join(pon_antiga.split("/")[2:3])

            # Definir PON nova baseada no arquivo autofind
            pon_nova = matching_onu["F/S/P"]
            interfaceGPON_nova = "/".join(pon_nova.split("/")[0:2])
            gPON_nova = "/".join(pon_nova.split("/")[2:3])

            # Definir o ID atual da ONU e incrementar o start_id
            ont_id = start_id
            start_id += 1
            
            # Verificação das palavras-chave na descrição
            if any(keyword in onu["desc"] for keyword in ["RDNT", "CORP", "ITX"]):
                print(f"A ONU com ID: {onu['ont_id']} será salva em {autorizaONUExcecoo_path} devido à descrição: {onu['desc']}")
                modified_lineprofile_id = onu["lineprofile_id"]
                modified_srvprofile_id = onu["srvprofile_id"]
                modified_native_vlan = onu["native_vlans"]
                modified_service_ports = onu["service_ports"]
                save_path = exception_commands
            else:
                modified_lineprofile_id = lineprofile_id or onu["lineprofile_id"]
                modified_srvprofile_id = srvprofile_id or onu["srvprofile_id"]
                modified_native_vlan = [{"vlan": native_vlan or vlan_info["vlan"]} for vlan_info in onu["native_vlans"]]
                modified_service_ports = [{
                    "service_port_id": service_port_id or sp_info["service_port_id"],
                    "vlan": vlan or sp_info["vlan"],
                    "gemport": gemport or sp_info["gemport"],
                    "user_vlan": user_vlan or sp_info["user_vlan"]
                } for sp_info in onu["service_ports"]]
                save_path = authorization_commands

            # Gerando comandos para autorizar a ONU
            commands = [
                f"interface gpon {interfaceGPON_nova}",
                f'ont add {gPON_nova} {ont_id} sn-auth "{onu["sn_auth"]}" omci ont-lineprofile-id {modified_lineprofile_id} ont-srvprofile-id {modified_srvprofile_id} desc "{onu["desc"]}"'
            ]
            
            # Adicionando comandos para native-vlans
            for vlan_info in modified_native_vlan:
                commands.append(f'ont port native-vlan {gPON_nova} {ont_id} eth 1 vlan {vlan_info["vlan"]} priority 0')

            commands.append("quit")

            # Adicionando comandos para service-ports
            for sp_info in modified_service_ports:
                commands.append(
                    f'service-port vlan {sp_info["vlan"]} gpon {pon_nova} ont {ont_id} gemport {sp_info["gemport"]} multi-service user-vlan {sp_info["user_vlan"]} tag-transform translate'
                )

            # Adicionando comandos à lista correspondente (normal ou exceção)
            for command in commands:
                save_path.append(command)
                save_path.append("")  # Linha em branco após cada comando

            # Gerando comandos para deletar a ONU e adicionar ao arquivo ontDelete.txt
            delete_commands.extend([
                f"undo service-port {sp_info['service_port_id']}" for sp_info in modified_service_ports
            ])
            delete_commands.append("")  # Linha em branco após cada comando
            delete_commands.append(f"interface gpon {interfaceGPON_antiga}")
            delete_commands.append("")  # Linha em branco após cada comando
            delete_commands.append(f"ont delete {gPON_antiga} {ont_id}")
            delete_commands.append("")  # Linha em branco após cada comando

        # Salvando os comandos no arquivo principal
        if authorization_commands:
            with open(autorizaONU_path, 'w') as output_file:
                output_file.write("\n".join(authorization_commands))
        
        # Salvando os comandos no arquivo de exceção
        if exception_commands:
            with open(autorizaONUExcecoo_path, 'w') as exception_file:
                exception_file.write("\n".join(exception_commands))

        # Salvando os comandos no arquivo ontDelete.txt
        if delete_commands:
            with open('src/ontDelete.txt', 'w') as delete_file:
                delete_file.write("\n".join(delete_commands))

        print(f"Comandos de autorização gerados e salvos em {autorizaONU_path} e {autorizaONUExcecoo_path}. Comandos de remoção salvos em 'src/ontDelete.txt'.")
    
    except Exception as e:
        print(f"Erro ao processar o arquivo JSON: {e}")

# Caminhos dos arquivos
autorizaONU_path = 'src/autorizaONU.txt'
autorizaONUExcecoo_path = 'src/autorizaONUExcecoo.txt'
json_path = 'src/onus_config.json'
autofind_onus_path = 'src/autofind_onus.json'
