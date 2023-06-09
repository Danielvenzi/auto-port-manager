import sqlite3
import os


# Cria o mini banco contendo as informações sobre o cliente
# nome
# grupo
# pb_key        - chave pública
# pv_key        - chave privada
# key_status    - status de criação da chave
# auth_status   - status da autenticação com um servidor
# id_hash       - hash usado para identificação do cliente no servidor
def create_config_db():
    conn = sqlite3.connect("./client_config.db")
    cursor = conn.cursor()
    cursor.execute("create table cliente (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nome TEXT, grupo TEXT, pb_key TEXT, pv_key TEXT, key_status TEXT, id_hash TEXT, auth_status TEXT);")
    cursor.execute("insert into cliente (nome, grupo, pb_key, pv_key, auth_status) values (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\");".format("mane", 
                                                                                                                                       "mane", 
                                                                                                                                       "./ssl_cliente/client.pub.key", 
                                                                                                                                       "./ssl_cliente/client.key",
                                                                                                                                       "0"))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_config_db()