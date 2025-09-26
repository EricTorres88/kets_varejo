CREATE TABLE IF NOT EXISTS cargos (
    id INT NOT NULL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Tabela de usuários (login)
CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    loja VARCHAR(100) NOT NULL,
    cargo_id INT NOT NULL,
    telefone VARCHAR(50) DEFAULT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cargo_id) REFERENCES cargos(id)
) ENGINE=InnoDB;


-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    telefone VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    preco DECIMAL(10,2) NOT NULL,
    estoque INT NOT NULL DEFAULT 0 CHECK (estoque >= 0),
    tamanho VARCHAR(10) NOT NULL
) ENGINE=InnoDB;

-- Tabela de vendas
CREATE TABLE IF NOT EXISTS vendas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    produto_id INT NOT NULL,
    situacao ENUM('Em aberto', 'Pago') NOT NULL DEFAULT 'Em aberto',
    valor DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('À vista', 'Débito', 'Crédito') NOT NULL,
    parcelas INT DEFAULT NULL, -- apenas se escolheu crédito
    data_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantidade_comprada INT NOT NULL DEFAULT 1,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
) ENGINE=InnoDB;

-- Tabela de fiado
CREATE TABLE IF NOT EXISTS fiado (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    venda_id INT NOT NULL, -- ligação com a venda
    cliente_id INT NOT NULL,
    produto_id INT NOT NULL,
    valor_devido DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('À vista', 'Débito', 'Crédito') NOT NULL,
    parcelas_total INT DEFAULT 1,
    parcelas_pagas INT DEFAULT 0,
    data_pagamento TIMESTAMP NULL DEFAULT NULL,
    FOREIGN KEY (venda_id) REFERENCES vendas(id),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
) ENGINE=InnoDB;

-- Tabela de despesas
CREATE TABLE IF NOT EXISTS despesas (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(100) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_vencimento DATE DEFAULT NULL,
    data_pagamento DATE NULL,
    estado ENUM('Pago', 'Em aberto') DEFAULT 'Em aberto'
) ENGINE=InnoDB;