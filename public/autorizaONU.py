import json

def authorize_onus(json_path, autofind_onus_path, autorizaONU_path, autorizaONUExcecao_path, ont_pon_ANTIGA, start_id=0, lineprofile_id=None, srvprofile_id=None,
                   native_vlan=None, service_port_id=None, vlan=None, gemport=None, user_vlan=None):    
    try:
        with open(json_path, 'r') as file:
            onus = json.load(file)
        
        with open(autofind_onus_path, 'r') as file:
            autofind_onus = json.load(file)
        
        with open('src/ontSummary.json', 'r') as file:
            ont_summary = json.load(file)
        
        used_ont_ids = {int(onu["ONT ID"]) for onu in ont_summary}

        authorization_commands = ["enable", "", "config", ""]
        exception_commands = ["enable", "", "config", ""]
        delete_commands = ["enable", "", "config"]
        delete_Excecao_commands = ["enable", "", "config"]

        for onu in onus:
            matching_onu = next((a_onu for a_onu in autofind_onus if a_onu["Ont SN"] == onu["sn_auth"]), None)
            if not matching_onu:
                continue 

            pon_antiga = ont_pon_ANTIGA
            interfaceGPON_antiga = "/".join(pon_antiga.split("/")[0:2])
            gPON_antiga = "/".join(pon_antiga.split("/")[2:3])

            pon_nova = matching_onu["F/S/P"]
            interfaceGPON_nova = "/".join(pon_nova.split("/")[0:2])
            gPON_nova = "/".join(pon_nova.split("/")[2:3])

            while start_id in used_ont_ids:
                start_id += 1
            ont_id = start_id
            start_id += 1
            used_ont_ids.add(ont_id)
            
            if "RDNT" in onu["desc"]:
                print(f"A ONU com ID: {onu['ont_id']} descrição: {onu['desc']} é rede neutra, então suas configuração não foram modificadas.")
                modified_lineprofile_id = onu["lineprofile_id"]
                modified_srvprofile_id = onu["srvprofile_id"]
                modified_native_vlan = onu["native_vlans"]
                modified_service_ports = onu["service_ports"]
                save_path = authorization_commands
                delete_path = delete_commands
            elif any(keyword in onu["desc"] for keyword in ["CORP", "ITX", "WIFI", "EVNT"]):
                print(f"A ONU com ID: {onu['ont_id']} será salva em {autorizaONUExcecao_path} devido à descrição: {onu['desc']}")
                modified_lineprofile_id = onu["lineprofile_id"]
                modified_srvprofile_id = onu["srvprofile_id"]
                modified_native_vlan = onu["native_vlans"]
                modified_service_ports = onu["service_ports"]
                save_path = exception_commands
                delete_path = delete_Excecao_commands
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
                delete_path = delete_commands

            commands = [
                f"interface gpon {interfaceGPON_nova}",
                f'ont add {gPON_nova} {ont_id} sn-auth "{onu["sn_auth"]}" omci ont-lineprofile-id {modified_lineprofile_id} ont-srvprofile-id {modified_srvprofile_id} desc "{onu["desc"]}"'
            ]
            
            for vlan_info in modified_native_vlan:
                commands.append(f'ont port native-vlan {gPON_nova} {ont_id} eth 1 vlan {vlan_info["vlan"]} priority 0')

            commands.append("quit")

            for sp_info in modified_service_ports:
                commands.append(
                    f'\nservice-port vlan {sp_info["vlan"]} gpon {pon_nova} ont {ont_id} gemport {sp_info["gemport"]} multi-service user-vlan {sp_info["user_vlan"]} tag-transform translate'
                )

            for command in commands:
                save_path.append(command)
                save_path.append("") 

            delete_path.extend([
                f"\nundo service-port {sp_info['service_port_id']}" for sp_info in modified_service_ports
            ])
            delete_path.append("")  
            delete_path.append(f"interface gpon {interfaceGPON_antiga}")
            delete_path.append("")  
            delete_path.append(f"ont delete {gPON_antiga} {onu['ont_id']}")
            delete_path.append("")  
            delete_path.append(f"quit")

        if authorization_commands:
            with open(autorizaONU_path, 'w') as output_file:
                output_file.write("\n".join(authorization_commands))
        
        if exception_commands:
            with open(autorizaONUExcecao_path, 'w') as exception_file:
                exception_file.write("\n".join(exception_commands))

        if delete_commands:
            with open('ontDelete.txt', 'w') as delete_file:
                delete_file.write("\n".join(delete_commands))

        if delete_Excecao_commands:
            with open('ontDeleteExcecao.txt', 'w') as delete_Excecao_file:
                delete_Excecao_file.write("\n".join(delete_Excecao_commands))

        print(f"Comandos de autorização gerados e salvos em {autorizaONU_path} e {autorizaONUExcecao_path}. Comandos de remoção salvos em 'src/ontDelete.txt' e 'src/ontDeleteExcecao.txt'.")
    
    except Exception as e:
        print(f"Erro ao processar o arquivo JSON: {e}")

autorizaONU_path = 'autorizaONU.txt'
autorizaONUExcecao_path = 'autorizaONUExcecao.txt'
json_path = 'src/onus_config.json'
autofind_onus_path = 'src/autofind_onus.json'

