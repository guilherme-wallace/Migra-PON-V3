# Migra-PON-V3

Script de automação para redes GPON, utilizado na migração de ONUs entre diferentes portas em OLTs.

## 🔧 Funcionalidades
- Coleta de dados de ONUs por SSH
- Extração automática de configurações
- Geração de comandos para desativação e reautorização
- Exportação de configurações em JSON
- Logging detalhado e modularização por função

## 📦 Tecnologias
- Python 3
- Paramiko (SSH)
- JSON / Regex
- Estrutura orientada a objetos

## 🧪 Como usar

 - Necessário ter dentro da pasta public uma arquivo em python chamado dadosConexaoOLTs.py onde terá os IPs e senhas para acesso as OLTs

```bash
git clone https://github.com/guilherme-wallace/Migra-PON-V3
cd Migra-PON-V3
python main.py
