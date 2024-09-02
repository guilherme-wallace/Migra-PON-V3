import tkinter as tk
from tkinter import messagebox
from tkinter import *
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
    "OLT-VTA01": ip_VTA01,
    "OLT-VTA02": ip_VTA02,
    "OLT-VVA01": ip_VVA01,
    "OLT-VVA03": ip_VVA03,
    "OLT-CCA01": ip_CCA01,
}

# Dados de acesso SSH (estaticamente definidos)
username = user
password = user_password


def run_scriptAfter():
    try:
        # Coleta as entradas do usuário
        use_OLT_Antiga = olt_antiga_var.get()
        use_OLT_Nova = olt_nova_var.get()
        pon_ANTIGA = pon_antiga_var.get()
        onu_ID = int(onu_id_var.get())
        ont_LIN_PROF = None  # Configurações podem ser customizadas conforme necessário
        ont_SRV_PROF = None
        ont_native_vlan = None
        ont_vlan_service_port = None
        ont_gem_PORT = None
        ont_user_vlan = None

        hostnameOLTAntiga = olt_IPS.get(use_OLT_Antiga)
        hostnameOLTNova = olt_IPS.get(use_OLT_Nova)

        # Executa as funções principais
        
        messagebox.showinfo("Sucesso", "Script executado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

def run_scriptLate():
    try:
        # Coleta as entradas do usuário
        use_OLT_Antiga = olt_antiga_var.get()
        use_OLT_Nova = olt_nova_var.get()
        pon_ANTIGA = pon_antiga_var.get()
        onu_ID = int(onu_id_var.get())
        ont_LIN_PROF = None  # Configurações podem ser customizadas conforme necessário
        ont_SRV_PROF = None
        ont_native_vlan = None
        ont_vlan_service_port = int(vlan_service_port_var.get())
        ont_gem_PORT = None
        ont_user_vlan = None

        hostnameOLTAntiga = olt_IPS.get(use_OLT_Antiga)
        hostnameOLTNova = olt_IPS.get(use_OLT_Nova)

        # Executa as funções principais
        ssh_connect_and_execute_currentPort(hostnameOLTAntiga, username, password, pon_ANTIGA)
        json_onus_config(filtered_currentPort_path, onus_config_path)
        ssh_connect_and_execute_autofind(hostnameOLTNova, username, password)
        ssh_connect_and_execute_summary(hostnameOLTNova, username, password, autofind_onus_file, onus_config_file)
        authorize_onus(json_path, autofind_onus_path, autorizaONU_path, autorizaONUExcecao_path, pon_ANTIGA, start_id=onu_ID, 
                       lineprofile_id=ont_LIN_PROF, srvprofile_id=ont_SRV_PROF, native_vlan=ont_native_vlan, 
                       service_port_id=None, vlan=ont_vlan_service_port, gemport=ont_gem_PORT, user_vlan=ont_user_vlan)
        execute_olt_commands_autorizaOLT(hostnameOLTAntiga, hostnameOLTNova, username, password)
        
        messagebox.showinfo("Sucesso", "Script executado com sucesso!")

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

# Criação da interface gráfica
root = tk.Tk()
root.title("Migração de ONUs")

varRows = 0
# Labels e Caixas de Texto
tk.Label(root, text="OLT Antiga").grid(row= varRows + 1, column=0, padx=20, pady=10)
olt_antiga_var = tk.StringVar()
tk.Entry(root, textvariable=olt_antiga_var).grid(row= varRows + 1, column=1, padx=20, pady=10)

tk.Label(root, text="OLT Nova").grid(row= varRows + 2, column=0, padx=20, pady=10)
olt_nova_var = tk.StringVar()
tk.Entry(root, textvariable=olt_nova_var).grid(row= varRows + 2, column=1, padx=20, pady=10)

tk.Label(root, text="PON Antiga").grid(row= varRows + 3, column=0, padx=20, pady=10)
pon_antiga_var = tk.StringVar()
tk.Entry(root, textvariable=pon_antiga_var).grid(row= varRows + 3, column=1, padx=20, pady=10)

tk.Label(root, text="ONU ID").grid(row= varRows + 4, column=0, padx=20, pady=10)
onu_id_var = tk.StringVar()
tk.Entry(root, textvariable=onu_id_var).grid(row= varRows + 4, column=1, padx=20, pady=10)

#ont_LIN_PROF = None
tk.Label(root, text="Line profile").grid(row= varRows + 5, column=0, padx=20, pady=10)
LIN_PROF_var = tk.StringVar()
tk.Entry(root, textvariable=LIN_PROF_var).grid(row= varRows + 5, column=1, padx=20, pady=10)

#ont_SRV_PROF = None
tk.Label(root, text="Service profile").grid(row= varRows + 6, column=0, padx=20, pady=10)
SRV_PROF_var = tk.StringVar()
tk.Entry(root, textvariable=SRV_PROF_var).grid(row= varRows + 6, column=1, padx=20, pady=10)

#ont_native_vlan = None
tk.Label(root, text="Native VLAN").grid(row= varRows + 7, column=0, padx=20, pady=10)
native_vlan_var = tk.StringVar()
tk.Entry(root, textvariable=native_vlan_var).grid(row= varRows + 7, column=1, padx=20, pady=10)

#ont_vlan_service_port = None
tk.Label(root, text="VLAN Service Port").grid(row= varRows + 8, column=0, padx=20, pady=10)
vlan_service_port_var = tk.StringVar()
tk.Entry(root, textvariable=vlan_service_port_var).grid(row= varRows + 8, column=1, padx=20, pady=10)

#ont_gem_PORT = None
tk.Label(root, text="GEM Port").grid(row= varRows + 9, column=0, padx=20, pady=10)
gem_PORT_var = tk.StringVar()
tk.Entry(root, textvariable=gem_PORT_var).grid(row= varRows + 9, column=1, padx=20, pady=10)

#ont_user_vlan = None
tk.Label(root, text="User VLAN").grid(row= varRows + 10, column=0, padx=20, pady=10)
user_vlan_var = tk.StringVar()
tk.Entry(root, textvariable=user_vlan_var).grid(row= varRows + 10, column=1, padx=20, pady=10)


oltsName = 'Os nomes das OLTs são: \nOLT-SEA01 \nOLT-SEA03 \nOLT-VTA01 \nOLT-VTA02 \nOLT-VVA01 \nOLT-VVA03 \nOLT-CCA01'

#oltsName_txt = tk.Text(root,width=60,height=10)
#oltsName_txt.grid(row=0, rowspan=1, column=0, columnspan=1)
#oltsName_txt.insert(INSERT, oltsName)

# Botão de execução antes
#tk.Button(root, text="Executar Script Após a migração", command=run_scriptAfter).grid(row=10, column=0, columnspan=2, padx=20, pady=10)

# Botão de execução depois
tk.Button(root, text="Executar após a migração", command=run_scriptLate).grid(row= varRows + 11, column=0, columnspan=2, padx=20, pady=10)

# Iniciar o loop da interface gráfica
root.mainloop()
