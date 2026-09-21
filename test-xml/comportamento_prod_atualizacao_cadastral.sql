SELECT
    a.cd_propriedade,
    a.cd_produtor,
    a.nm_produtor,
    a.cd_exploracao,
    MAX(a.dt_finalizacao) AS dt_finalizacao, -- Pega a data máxima
    SUM(COALESCE(n.nascidos_machos, 0)) AS nascidos_machos,
    SUM(COALESCE(n.nascidos_femeas, 0)) AS nascidos_femeas,
    SUM(COALESCE(g_in.qtd_gta_entrada, 0)) AS qtd_gta_entrada,
    SUM(COALESCE(g_in.total_animais_entrada, 0)) AS qt_animais_entrada,
    SUM(COALESCE(g_in_cancel.gta_canceled_C, 0)) AS gta_entrada_canceled_C,
    SUM(COALESCE(g_in_cancel.gta_canceled_K, 0)) AS gta_entrada_canceled_K,
    SUM(COALESCE(g_out.qtd_gta_saida, 0)) AS qtd_gta_saida,
    SUM(COALESCE(g_out.total_animais_saida, 0)) AS qt_animais_saida,
    SUM(COALESCE(g_out_cancel.gta_saida_canceled_C, 0)) AS gta_saida_canceled_C,
    SUM(COALESCE(g_out_cancel.gta_saida_canceled_K, 0)) AS gta_saida_canceled_K
FROM 
(
    SELECT
        ctpo.cd_propriedade,
        cteo.cd_exploracao,
        ctpd.cd_produtor,
        ctpd.nm_produtor,
        MAX(ctacp.dt_finalizacao) AS dt_finalizacao
    FROM db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor ctacp
    JOIN db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor_nucleo ctacpn 
        ON ctacp.id_atualizacao_cadastral_produtor = ctacpn.id_atualizacao_cadastral_produtor
    JOIN db_dlsidagro_staging.client_tb_exploracao cteo
        ON ctacpn.id_exploracao = cteo.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_propriedade ctpo
        ON cteo.id_propriedade = ctpo.id_propriedade
    JOIN db_dlsidagro_staging.client_tb_exploracao_produtor ctep
        ON cteo.id_exploracao = ctep.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_produtor ctpd
        ON ctep.id_produtor = ctpd.id_produtor
    WHERE ctacp.in_concluida = 'S'
    AND cteo.id_especie = 1
    AND ctep.in_titular = 'S'
    AND ctacp.dt_finalizacao >= '2026-06-02'
    GROUP BY ctpo.cd_propriedade, cteo.cd_exploracao, ctpd.cd_produtor, ctpd.nm_produtor
) a

LEFT JOIN (
    SELECT 
        cte.cd_exploracao,
        SUM(CASE WHEN ctes.tp_sexo = 'M' THEN ctl.qt_animal_lancamento ELSE 0 END) AS nascidos_machos,
        SUM(CASE WHEN ctes.tp_sexo = 'F' THEN ctl.qt_animal_lancamento ELSE 0 END) AS nascidos_femeas
    FROM db_dlsidagro_staging.client_tb_lancamento ctl
    JOIN db_dlsidagro_staging.client_tb_estratificacao_nucleo cten
        ON ctl.id_estratificacao_nucleo = cten.id_estratificacao_nucleo
    JOIN db_dlsidagro_staging.client_tb_nucleo ctn 
        ON cten.id_nucleo = ctn.id_nucleo
    JOIN db_dlsidagro_staging.client_tb_exploracao cte 
        ON ctn.id_exploracao = cte.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_estratificacao ctes
        ON cten.id_estratificacao = ctes.id_estratificacao
    WHERE ctl.id_tipo_lancamento = 25
    AND ctl.dt_atualizacao >= '2026-05-01'
    AND ctl.in_debito_credito = 'C'
    AND cte.id_especie = 1
    GROUP BY cte.cd_exploracao -- Removido dt_atualizacao do GROUP BY
) n
    ON a.cd_exploracao = n.cd_exploracao

LEFT JOIN (
    SELECT
        cted.cd_exploracao,
        COUNT(DISTINCT ctg.nr_gta) AS qtd_gta_entrada,
        SUM(cteg.qt_animais) AS total_animais_entrada
    FROM db_dlsidagro_staging.client_tb_gta ctg
    JOIN db_dlsidagro_staging.client_tb_nucleo ctnd
        ON ctg.id_nucleo_destino = ctnd.id_nucleo
    JOIN db_dlsidagro_staging.client_tb_exploracao cted
        ON ctnd.id_exploracao = cted.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_estratificacao_gta cteg
        ON ctg.id_gta = cteg.id_gta
    JOIN db_dlsidagro_staging.client_tb_estratificacao ctege
        ON cteg.id_estratificacao = ctege.id_estratificacao
    JOIN db_dlsidagro_staging.client_tb_faixa_etaria ctfe 
        ON ctege.id_faixa_etaria = ctfe.id_faixa_etaria
    WHERE ctg.id_especie = 1
    AND ctg.dt_emissao_gta >= '2026-04-25'
    AND ctege.tp_sexo = 'F'
    AND cteg.qt_animais >= 50
    AND ctfe.ds_faixa_etaria IN ('Acima de 36 meses', 'De 25 até 36 meses')
    GROUP BY cted.cd_exploracao
) g_in
    ON a.cd_exploracao = g_in.cd_exploracao

LEFT JOIN (
    SELECT 
        cted.cd_exploracao,
        COUNT(DISTINCT CASE WHEN ctg.st_gta = 'C' THEN ctg.nr_gta END) AS gta_canceled_C,
        COUNT(DISTINCT CASE WHEN ctg.st_gta = 'K' THEN ctg.nr_gta END) AS gta_canceled_K
    FROM db_dlsidagro_staging.client_tb_gta ctg
    JOIN db_dlsidagro_staging.client_tb_nucleo ctnd
        ON ctg.id_nucleo_destino = ctnd.id_nucleo
    JOIN db_dlsidagro_staging.client_tb_exploracao cted
        ON ctnd.id_exploracao = cted.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_estratificacao_gta cteg
        ON ctg.id_gta = cteg.id_gta
    JOIN db_dlsidagro_staging.client_tb_estratificacao ctege
        ON cteg.id_estratificacao = ctege.id_estratificacao
    JOIN db_dlsidagro_staging.client_tb_faixa_etaria ctfe
        ON ctege.id_faixa_etaria = ctfe.id_faixa_etaria
    WHERE ctg.id_especie = 1
    AND ctg.dt_emissao_gta >= '2026-04-25'
    AND ctege.tp_sexo = 'F'
    AND cteg.qt_animais >= 50
    AND ctfe.ds_faixa_etaria IN ('Acima de 36 meses', 'De 25 até 36 meses')
    AND ctg.st_gta IN ('C', 'K')
    GROUP BY cted.cd_exploracao
) g_in_cancel
    ON  a.cd_exploracao = g_in_cancel.cd_exploracao

LEFT JOIN ( -- GTA SAÍDA VÁLIDAS - CORRIGIDO: Removido dt_finalizacao do GROUP BY
    SELECT 
        cteo.cd_exploracao, 
        COUNT(DISTINCT ctg.nr_gta) AS qtd_gta_saida,
        SUM(cteg.qt_animais) AS total_animais_saida
    FROM db_dlsidagro_staging.client_tb_gta ctg
    JOIN db_dlsidagro_staging.client_tb_nucleo ctno
        ON ctg.id_nucleo_origem = ctno.id_nucleo
    JOIN db_dlsidagro_staging.client_tb_exploracao cteo
        ON ctno.id_exploracao = cteo.id_exploracao
    JOIN db_dlsidagro_staging.client_tb_estratificacao_gta cteg
        ON ctg.id_gta = cteg.id_gta
    JOIN db_dlsidagro_staging.client_tb_estratificacao ctege
        ON cteg.id_estratificacao = ctege.id_estratificacao
    JOIN db_dlsidagro_staging.client_tb_faixa_etaria ctfe
        ON ctege.id_faixa_etaria = ctfe.id_faixa_etaria
    JOIN (
        SELECT
            cteo2.cd_exploracao,
            MAX(ctacp.dt_finalizacao) AS dt_finalizacao
        FROM db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor ctacp
        JOIN db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor_nucleo ctacpn
            ON tacp.id_atualizacao_cadastral_produtor = ctacpn.id_atualizacao_cadastral_produtor
        JOIN db_dlsidagro_staging.client_tb_exploracao cteo2
            ON ctacpn.id_exploracao = cteo2.id_exploracao
        WHERE ctacp.in_concluida = 'S'
        AND ctacp.dt_finalizacao >= '2026-05-17' -- CORRIGIDO: mesma data da query principal
        GROUP BY cteo2.cd_exploracao
        ) a_inner
        ON cteo.cd_exploracao = a_inner.cd_exploracao 
    WHERE ctg.id_especie = 1
    AND ctege.tp_sexo = 'F'
    AND cteg.qt_animais >= 50
    AND ctfe.ds_faixa_etaria IN ('Acima de 36 meses', 'De 25 até 36 meses')
    AND ctg.dt_emissao_gta >= a_inner.dt_finalizacao
    GROUP BY cteo.cd_exploracao -- CORRIGIDO: Removido a_inner.dt_finalizacao
) g_out
    ON  a.cd_exploracao = g_out.cd_exploracao

LEFT JOIN ( -- GTA SAÍDA CANCELADAS - CORRIGIDO
    SELECT
    cteo.cd_exploracao,
    COUNT(DISTINCT CASE WHEN ctg.st_gta = 'C' THEN ctg.nr_gta END) AS gta_saida_canceled_C, 
    COUNT(DISTINCT CASE WHEN ctg.st_gta = 'K' THEN ctg.nr_gta END) AS gta_saida_canceled_K
    FROM db_dlsidagro_staging.client_tb_gta ctg
    JOIN db_dlsidagro_staging.client_tb_nucleo ctno 
        ON ctg.id_nucleo_origem = ctno.id_nucleo 
    JOIN db_dlsidagro_staging.client_tb_exploracao cteo
        ON ctno.id_exploracao = cteo.id_exploracao 
    JOIN db_dlsidagro_staging.client_tb_estratificacao_gta cteg
        ON ctg.id_gta = cteg.id_gta
    JOIN db_dlsidagro_staging.client_tb_estratificacao ctege
        ON cteg.id_estratificacao = ctege.id_estratificacao
    JOIN db_dlsidagro_staging.client_tb_faixa_etaria ctfe
        ON ctege.id_faixa_etaria = ctfe.id_faixa_etaria
    JOIN (SELECT
            cteo2.cd_exploracao,
            MAX(ctacp.dt_finalizacao) AS dt_finalizacao
          FROM db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor ctacp
          JOIN db_dlsidagro_staging.client_tb_atualizacao_cadastral_produtor_nucleo ctacpn
            ON ctacp.id_atualizacao_cadastral_produtor = ctacpn.id_atualizacao_cadastral_produtor
          JOIN db_dlsidagro_staging.client_tb_exploracao cteo2
            ON ctacpn.id_exploracao = cteo2.id_exploracao 
          WHERE ctacp.in_concluida = 'S'
          AND ctacp.dt_finalizacao >= '2026-05-17' -- CORRIGIDO: mesma data da query principal
          GROUP BY cteo2.cd_exploracao
          ) a_inner
        ON  cteo.cd_exploracao = a_inner.cd_exploracao
    WHERE ctg.id_especie = 1
    AND ctege.tp_sexo = 'F'
    AND cteg.qt_animais >= 50
    AND ctfe.ds_faixa_etaria IN ('Acima de 36 meses', 'De 25 até 36 meses')
    AND ctg.st_gta IN ('C', 'K')
    AND ctg.dt_emissao_gta >= a_inner.dt_finalizacao 
    GROUP BY cteo.cd_exploracao
) g_out_cancel
     ON a.cd_exploracao =  g_out_cancel.cd_exploracao
GROUP BY a.cd_propriedade, a.cd_produtor, a.nm_produtor, a.cd_exploracao -- Agrupa por cd_exploracao para somar tudo