import bcrypt

def gerar_hash(senha):
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode()

if __name__ == "__main__":
    senha = input("Digite a senha para gerar o hash seguro: ")
    hash_gerado = gerar_hash(senha)
    print("Hash gerado:")
    print(hash_gerado)