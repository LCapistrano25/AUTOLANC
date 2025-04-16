ITEMS_SOLUTION = '''
    SELECT  
        P.e18codpro AS "CODIGO PRODUTO",
        p.e18cst1 AS "ORIGEM"
    FROM cadite P 
    WHERE p.e18codpro = %s
    AND p.e01codigo = '1' 
'''