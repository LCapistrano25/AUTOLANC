PARAMETERS = '''
    SELECT
        id_status_nao_lancado AS NAO_LANCADO,
        id_status_em_lancamento AS EM_LANCAMENTO,
        id_status_lancado AS LANCADO,
        id_status_a_conferir AS A_CONFERIR
    FROM public.tb_controle_status_lancamento
'''