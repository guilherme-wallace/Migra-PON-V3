import json

def authorize_onus(json_path, autorizaONU_path, pon_nova, start_id=0, lineprofile_id=None, srvprofile_id=None,
                   native_vlan=None, service_port_id=None, vlan=None, gemport=None, user_vlan=None):    
    try:
        # Leitura do arquivo JSON com as ONUs
        with open(json_path, 'r') as file:
            onus = json.load(file)
        
        # Lista para armazenar comandos de autorização
        authorization_commands = []

        interfaceGPON_nova = "/".join(pon_nova.split("/")[0:2])
        gPON_nova = "/".join(pon_nova.split("/")[2:3])

        # Adiciona os comandos iniciais `enable` e `config` uma única vez
        authorization_commands.append("enable")
        authorization_commands.append("")
        authorization_commands.append("config")
        authorization_commands.append("")

        for onu in onus:
            # Definir o ID atual da ONU e incrementar o start_id
            ont_id = start_id
            start_id += 1
            
            # Verificação das palavras-chave na descrição
            if any(keyword in onu["desc"] for keyword in ["RDNT", "CORP", "ITX"]):
                print(f"A ONU com ID: {onu['ont_id']} respeitará o start_id mas não terá outras alterações devido à descrição: {onu['desc']}")
                modified_lineprofile_id = onu["lineprofile_id"]
                modified_srvprofile_id = onu["srvprofile_id"]
                modified_native_vlan = onu["native_vlans"]
                modified_service_ports = onu["service_ports"]
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
                    #f'service-port {sp_info["service_port_id"]} vlan {sp_info["vlan"]} gpon {pon_nova} ont {ont_id} gemport {sp_info["gemport"]} multi-service user-vlan {sp_info["user_vlan"]} tag-transform translate'
                    f'service-port vlan {sp_info["vlan"]} gpon {pon_nova} ont {ont_id} gemport {sp_info["gemport"]} multi-service user-vlan {sp_info["user_vlan"]} tag-transform translate'
                )

            # Adicionando comandos à lista
            for command in commands:
                authorization_commands.append(command)
                authorization_commands.append("")  # Linha em branco após cada comando

        # Salvando os comandos em um arquivo TXT
        with open(autorizaONU_path, 'w') as output_file:
            output_file.write("\n".join(authorization_commands))

        print(f"Comandos de autorização gerados para as ONUs e foram salvos em {autorizaONU_path}.")
    
    except Exception as e:
        print(f"Erro ao processar o arquivo JSON: {e}")

# Caminhos dos arquivos
autorizaONU_path = 'src/autorizaONU.txt'
json_path = 'src/onus_config.json'

