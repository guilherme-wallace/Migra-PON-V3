# Migra-PON-V3

Script de automação para redes GPON, utilizado na migração de ONUs entre diferentes portas em OLTs.

## 🔧 Funcionalidades
- Coleta de dados de ONUs por SSH
- Extração automática de configurações
- Geração de comandos para desativação e reautorização
- Exportação de configurações em JSON e TXT
- Logging detalhado e modularização por função

## 📦 Tecnologias
- Python 3
- Paramiko (SSH)
- JSON / Regex
- Estrutura orientada a objetos

## 🧪 Como usar
 - Preencha os campos conforme necessário. 
 ### Variaveis que podem ser alteradas:
  - onu_ID = "ID inicial das ONUs" - default 0
  - ont_LIN_PROF = "Vlan Line profile"
  - ont_SRV_PROF = "Vlan service profile"
  - ont_native_vlan = "Vlan nativa da porta da ONU"
  - ont_vlan_service_port = "Vlan do service port"
  - ont_gem_PORT = "ID gemport"
  - ont_user_vlan = "Vlan do usuário"

  #### OBSERVAÇÕES:
   - Caso um campo esteja definido como None, o script usará o dado da autorização antiga ONU, ou seja, os dados que estão configurados antes da migração. 
   - Necessário ter dentro da pasta public uma arquivo em python chamado dadosConexaoOLTs.py onde terá os IPs e senhas para acesso as OLTs

```bash
git clone https://github.com/guilherme-wallace/Migra-PON-V3
cd Migra-PON-V3
python main.py
