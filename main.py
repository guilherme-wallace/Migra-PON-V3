import paramiko
import time
import re
import os
import json
from route.dadosConexaoOLTs import *
from public.currentPort import *
from public.jsonONUs import *
from public.autorizaONU import *

# Mapeamento das OLTs e seus IPs
olt_IPS = {
    "OLT-SEA01": ip_SEA01,
    "OLT-SEA03": ip_SEA03,
    "OLT-VTA01": ip_VTA01,
    "OLT-VTA02": ip_VTA02,
    "OLT-VVA01": ip_VVA01,
    "OLT-VVA03": ip_VVA03,
    "OLT-CCA01": ip_CCA01,
}
#------------------------------------------------------------------------------------------------------------
#OBS: 1º adicione as ONUS que serão autorizadas, pelo comando display ont autofind all 

# Seleciona a OLT Antiga
use_OLT_Antiga = "OLT-SEA01"
pon_ANTIGA = "0/16/5"

# Seleciona a OLT Nova
use_OLT_Nova = "OLT-SEA03"
pon_nova = "0/1/4"

# Verifique as configurações da ONU
onu_ID = 0
ont_LIN_PROF = 1921
ont_SRV_PROF = 1921
ont_native_vlan = 1921
ont_vlan_service_port = 1501
ont_gem_PORT = 126
ont_user_vlan = 1921

#------------------------------------------------------------------------------------------------------------
# Arquivo contendo a lista de ONUs
onu_FILE = 'auto_find_onu_huawei.txt'

hostnameOLTAntiga = olt_IPS.get(use_OLT_Antiga)
hostnameOLTNova = olt_IPS.get(use_OLT_Nova)

# Dados de acesso SSH
username = user
password = user_password

def main():    
    #PEGA O CONFIGURAÇÕES DA PORTA------------------------------------------------------------------------------------------------------------

    # Executa a função PEGA O CURRENTPORT
    ssh_connect_and_execute_currentPort(hostnameOLTAntiga, username, password, pon_ANTIGA)

    # Executando a função para criar o JSON
    json_onus_config(filtered_currentPort_path, onus_config_path)

    # Executando a função para criar os comando de autorizar ONUs
    authorize_onus(json_path, autorizaONU_path, pon_nova, start_id=onu_ID, lineprofile_id=ont_LIN_PROF, srvprofile_id=ont_SRV_PROF, native_vlan=ont_native_vlan, service_port_id="", vlan=ont_vlan_service_port, gemport=ont_gem_PORT, user_vlan=ont_user_vlan)


main()

