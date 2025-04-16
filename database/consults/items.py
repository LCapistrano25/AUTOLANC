ITEMS_FOURMAQCONNECT = '''
    SELECT 
        INP.codigo AS "CODIGO",
        INP.origem AS "ORIGEM"
    FROM tb_itens_notas_fiscais AS INP
    INNER JOIN tb_notas_fiscais AS NF ON NF.id = INP.id_nota_fiscal
    WHERE NF.chave_acesso = %s
'''