INVOICES = ''' 
    SELECT 
        chave_acesso AS CHAVE,
        F.numero AS NUMERO_FILIAL,
        F.nome AS NOME_FILIAL,
        O.numero AS OPERACAO,
        NT.conferente AS CONFERENTE,
        NT.codigo_vendedor AS VENDEDOR,
        CC.numero AS CENTRO,
        PP.numero AS POLITICA,
        TL.nome AS TIPO_LANCAMENTO,
        numero_nota AS NUMERO_NOTA
    FROM tb_notas_fiscais AS NT
    INNER JOIN tb_filiais AS F ON F.id = NT.id_filial
    INNER JOIN tb_processos AS P ON P.id = NT.id_processo
    INNER JOIN tb_operacoes AS O ON O.id = NT.id_operacao
    INNER JOIN tb_centros_custos AS CC ON CC.id = P.id_centro_de_custo
    INNER JOIN tb_politicas_pagamento AS PP ON PP.id = NT.id_politica_pagamento
    INNER JOIN tb_tipos_lancamentos AS TL ON TL.id = NT.id_tipo_lancamento
    WHERE NT.id_status_lancamento = %s and tentativa_realizada < 25
    LIMIT %s
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