#Script desenvolvido por Guilherme Wallace Souza Costa (https://github.com/guilherme-wallace)

import paramiko
import time
import re
import os
import json
from route.dadosConexaoOLTs import *
from public.currentPort import *
from public.jsonONUs import *
from public.autorizaONU import *
from public.autofind import *
from public.ontSummary import *
from public.autorizaOLT import *

# Mapeamento das OLTs e seus IPs
olt_IPS = {
    "OLT-SEA01": ip_SEA01,
    "OLT-SEA03": ip_SEA03,
    "OLT-SEA04": ip_SEA04,
    "OLT-SEA05": ip_SEA05,
    "OLT-VTA01": ip_VTA01,
    "OLT-VTA02": ip_VTA02,
    "OLT-VVA01": ip_VVA01,
    "OLT-VVA03": ip_VVA03,
    "OLT-CCA01": ip_CCA01,
}
#------------------------------------------------------------------------------------------------------------
# Selecione a OLT Antiga
use_OLT_Antiga = "OLT-SEA01"
pon_ANTIGA = "0/18/3"

# Selecione a OLT Nova
use_OLT_Nova = "OLT-SEA05"

# Verifique as configurações das ONUs
# Deixew como None as configurações que não serão alteradas.

onu_ID = 0
ont_LIN_PROF = 1303
ont_SRV_PROF = 1303
ont_native_vlan = None
ont_vlan_service_port = 1303
ont_gem_PORT = 126
ont_user_vlan = None

#------------------------------------------------------------------------------------------------------------
hostnameOLTAntiga = olt_IPS.get(use_OLT_Antiga)
hostnameOLTNova = olt_IPS.get(use_OLT_Nova)

username = user
password = user_password

def main():    
    # Executa a função PEGA O CURRENTPORT
    ssh_connect_and_execute_currentPort(hostnameOLTAntiga, username, password, pon_ANTIGA)

    # Executando a função para criar o JSON
    json_onus_config(filtered_currentPort_path, onus_config_path)

    # Executando a função para buscar as ONUS para serem autorizadas
    ssh_connect_and_execute_autofind(hostnameOLTNova, username, password)
    
    # Executando a função para buscar summary das ONUs que serão autorizadas
    ssh_connect_and_execute_summary(hostnameOLTNova, username, password, autofind_onus_file, onus_config_file)

    # Executando a função para criar os comando de autorizar ONUs    
    authorize_onus(json_path, autofind_onus_path, autorizaONU_path, autorizaONUExcecao_path, pon_ANTIGA, start_id=onu_ID, lineprofile_id=ont_LIN_PROF, srvprofile_id=ont_SRV_PROF,
                   native_vlan=ont_native_vlan, service_port_id=None, vlan=ont_vlan_service_port, gemport=ont_gem_PORT, user_vlan=ont_user_vlan)
    
    # Executando a função que acessa as OLTs e autoriza as ONUs com novos dados.
    #execute_olt_commands_autorizaOLT(hostnameOLTAntiga, hostnameOLTNova, username, password)

main()
