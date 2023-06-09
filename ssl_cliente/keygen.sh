#!/bin/bash

# Script que faz a criação das chaves usadas para o processo de autenticação via JWT com o servidor

# Chaves para o JWT
ssh-keygen -t rsa -b 4096 -m PEM -f ./client.key
openssl rsa -in ./client.key -pubout -outform PEM -out ./northbound.key.pub