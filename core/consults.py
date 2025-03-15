INVOICES = ''' 
    SELECT 
        chave_acesso AS CHAVE,
        F.numero AS NUMERO_FILIAL,
        F.nome AS NOME_FILIAL,
        O.numero AS OPERACAO,
        NT.conferente AS CONFERENTE,
        NT.codigo_vendedor AS VENDEDOR,
        CC.numero AS CENTRO,
        PP.numero AS POLITICA
    FROM tb_notas_fiscais AS NT
    INNER JOIN tb_filiais AS F ON F.id = NT.id_filial
    INNER JOIN tb_processos AS P ON P.id = NT.id_processo
    INNER JOIN tb_operacoes AS O ON O.id = NT.id_operacao
    INNER JOIN tb_centros_custos AS CC ON CC.id = P.id_centro_de_custo
    INNER JOIN tb_politicas_pagamento AS PP ON PP.id = NT.id_politica_pagamento
    WHERE NT.id_status_lancamento = %s 
    ORDER BY NT.tentativa_realizada ASC
    LIMIT %s
'''

PARAMETERS = '''
    SELECT
        id_status_nao_lancado AS NAO_LANCADO,
        id_status_em_lancamento AS EM_LANCAMENTO,
        id_status_lancado AS LANCADO,
        id_status_a_conferir AS A_CONFERIR
    FROM tb_controle_status_lancamento
'''

UPDATE_INVOICE = '''
    UPDATE tb_notas_fiscais
    SET id_status_lancamento = %s
    WHERE chave_acesso = %s 
'''

UPDATE_INVOICE_ERROR = '''
    UPDATE tb_notas_fiscais
    SET tentativa_realizada = tentativa_realizada + 1
    WHERE chave_acesso = %s 
'''

ITEMS_SOLUTION = '''
    SELECT  
        P.e18codpro AS "CODIGO PRODUTO",
        p.e18cst1 AS "ORIGEM"
    FROM cadite P 
    WHERE p.e18codpro = %s
    AND p.e01codigo = '1' 
'''

ITEMS_FOURMAQCONNECT = '''
    SELECT 
        INP.codigo AS "CODIGO",
        INP.origem AS "ORIGEM"
    FROM tb_itens_notas_fiscais AS INP
    INNER JOIN tb_notas_fiscais AS NF ON NF.id = INP.id_nota_fiscal
    WHERE NF.chave_acesso = %s
'''