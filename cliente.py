import requests
import os
import sqlite3
import jwt
from flask import jsonify


# Coleta as informações necessárias para autenticação no servidor
def get_auth_info():
    conn = sqlite3.connect("./cliente_db/client_config.db")
    cursor = conn.cursor()
    cursor.execute("select nome, grupo, pb_key, auth_status from cliente where id=1;")
    result = cursor.fetchall()
    conn.close()

    auth_status = result[0][3]

    result = {"nome":result[0][0],
              "grupo":result[0][1],
              "pb_key":result[0][2],
              }

    # Verifica se a autenticação já foi feita com um servidor
    if auth_status == "0":
        return False, result
    else:
        return True, result
    
# Coleta as informações necessárias para a alocação de porta dedicada no servidor
def get_port_info():
    conn = sqlite3.connect("./cliente_db/client_config.db")
    cursor = conn.cursor()
    cursor.execute("select nome, grupo, id_hash from cliente where id=1;")
    result = cursor.fetchall()
    conn.close()

    result = {"nome":result[0][0],
              "grupo":result[0][1],
              "id_hash":result[0][2],
              }
    
    return result


# Função que gera o JWT enviado durante alocação de porta dedicada
def generate_jwt(token_info):

    # Lê o arquivo da chave privada usada para criar o JWT
    priv_key = ""
    with open(str("./ssl_cliente/client.key"), 'rb') as file:
        priv_key = file.read()
        file.close()

    jwt_token = jwt.encode(token_info, priv_key, algorithm="RS256")
    # Cria o JSON usado para alocação de porta
    jwt_json = jsonify({"jwt":jwt_token})

    return jwt_json


# Atualize os campos id_hash e auth_status do banco de dados após autenticação
def update_auth_db(id_hash):
    conn = sqlite3.connect("./cliente_db/client_config.db")
    cursor = conn.cursor()
    cursor.execute("insert into cliente (id_hash, auth_status) values (\"{}\",\"{}\");".format(id_hash, "1"))
    conn.commit()
    conn.close()

# Função para autenticação com o servidor
def auth_to_server(addr, port, cliente_info):

    try:
        # Envia a requisição POST para o servidor contendo as informações do usuário que está se autenticando
        response = requests.post("http://"+addr+":"+port+"/auth", json=cliente_info)
        response = requests.get_json(force=True)

        # Verifica se o processo de autenticação foi bem sucedido
        if response["status"] == "Success":
            # Atualiza o banco de dados com o novo id_hash
            update_auth_db(response["id_hash"])
            return True
        else:
            print("Error - {}".format(response))

    except requests.HTTPError as err:
        print(err)
    except requests.ConnectionError as err:
        print(err)
    except requests.ConnectTimeout as err:
        print(err)
    except requests.Timeout as err:
        print(err)

    return False

# Após autenticação recebe os dados da porta dedicada do servidor
def get_port_from_server(addr, port, port_info):

    # Cria o JWT usado
    jwt_json = generate_jwt(port_info)

    try:
        # Envia a requisição POST para o servidor contendo as informações do usuário que está se autenticando
        response = requests.post("http://"+addr+":"+port+"/allocate", json=jwt_json)
        response = requests.get_json(force=True)

        # Verifica se o processo de autenticação foi bem sucedido
        if response["status"] == "Success":
            # Retorna a porta usada para comunicação dedicada
            return True, int(response["port"])

    except requests.HTTPError as err:
        print(err)
    except requests.ConnectionError as err:
        print(err)
    except requests.ConnectTimeout as err:
        print(err)
    except requests.Timeout as err:
        print(err)

    return False, None


def allocate_port():
    port_info = get_port_info()

    # Verifica se o processo de alocação de porta foi bem sucedido
    status, dedicated_port = get_port_from_server(addr, port, port_info)
    if status:
        print("Tá aqui sua porta dedicada: {}".format(dedicated_port))
        # TODO comunicação com a porta
    else:
        print("Algum erro na alocação da porta, lado do servidor")

if __name__ == "__main__":

    # Informações hardcoded no banco de dados (checar o código generate_client_db.py)
    #nome_cliente = "mane"
    #grupo_cliente = "mane"

    addr = "127.0.0.1"
    port = 8080

    auth_status, cliente_info = get_auth_info()

    # Verifica se o cliente já está previamente autenticado
    if auth_status:
        allocate_port()
    else:
        # Realiza autenticação no servidor
        if auth_to_server(addr, port, cliente_info):
            allocate_port()
        else:
            print("Erro durante a autenticação no servidor")