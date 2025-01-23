CREATE TABLE produtos (
    id NUMBER PRIMARY KEY,
    nome VARCHAR (250) NOT NULL,
    categoria VARCHAR (250),
    preco NUMBER(10, 2) NOT NULL,
    quantidade NUMBER NOT NULL
);

CREATE TABLE tabela_vendas (
    id_venda NUMBER PRIMARY KEY,
    itens_venda VARCHAR2 (4000) NOT NULL,
    data_venda DATE NOT NULL
);

INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (1, 'Notebook Dell Inspiron', 'Computadores', 4500.00, 10);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (2, 'Smartphone Samsung Galaxy S23', 'Celulares', 4999.90, 15);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (3, 'Monitor LG Ultrawide 29"', 'Monitores', 1399.99, 8);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (4, 'Teclado Mecânico Redragon', 'Periféricos', 349.90, 20);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (5, 'Mouse Logitech G502', 'Periféricos', 299.99, 25);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (6, 'SSD Kingston 1TB', 'Armazenamento', 499.90, 12);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (7, 'Fone de Ouvido JBL Tune 710', 'Áudio', 379.90, 18);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (8, 'Smartwatch Apple Watch Series 9', 'Wearables', 3699.00, 5);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (9, 'Placa de Vídeo RTX 4060', 'Hardware', 2499.99, 7);
INSERT INTO produtos (id, nome, categoria, preco, quantidade) VALUES (10, 'Câmera GoPro Hero 11', 'Câmeras', 2799.90, 6);

ALTER TABLE tabela_vendas
MODIFY data_venda TIMESTAMP;

DESCRIBE tabela_vendas;

SELECT * from TABELA_VENDAS order by DATA_VENDA;

SELECT * FROM PRODUTOS order by id;

delete from TABELA_VENDAS where ID_VENDA = 2;


COMMIT;