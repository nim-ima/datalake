WITH mov AS (
  SELECT
    ftm.cd_municipio_ibge,
    ftm.ds_municipio,
    cte.nm_especie,
    ctes.tp_sexo,
    ctfe.ds_faixa_etaria,
    ctl.qt_animal_lancamento * CASE
        WHEN ctl.id_tipo_lancamento = 32 THEN 1
        WHEN ctl.id_tipo_lancamento = 26 THEN -1
        WHEN ctl.in_debito_credito = 'C' THEN 1
        ELSE -1
    END AS mov
  FROM db_dlsidagro_staging.client_tb_exploracao ctexp
  JOIN db_dlsidagro_staging.client_tb_propriedade ctprop ON ctprop.id_propriedade = ctexp.id_propriedade
  JOIN db_dlsidagro_staging.client_tb_pessoa ctps ON ctps.id_pessoa = ctprop.id_pessoa_juridica
  JOIN db_dlsidagro_staging.fiscal_tb_municipio ftm ON ftm.id_municipio = ctps.id_municipio
  JOIN db_dlsidagro_staging.client_tb_especie cte ON cte.id_especie = ctexp.id_especie
  JOIN db_dlsidagro_staging.client_tb_nucleo ctn ON ctn.id_exploracao = ctexp.id_exploracao
  JOIN db_dlsidagro_staging.client_tb_estratificacao_nucleo cten ON cten.id_nucleo = ctn.id_nucleo
  JOIN db_dlsidagro_staging.client_tb_estratificacao ctes ON ctes.id_estratificacao = cten.id_estratificacao
  JOIN db_dlsidagro_staging.client_tb_faixa_etaria ctfe ON ctfe.id_faixa_etaria = ctes.id_faixa_etaria
  JOIN db_dlsidagro_staging.client_tb_lancamento ctl ON ctl.id_estratificacao_nucleo = cten.id_estratificacao_nucleo
  WHERE ctl.id_tipo_lancamento IN (25,26,27,28,29,31,32,34,37)
    AND ctexp.id_especie IN (1,2)
    AND CAST(ctl.dt_lancamento AS DATE) <= '2026-06-30'
)
SELECT
  nm_especie,
  ds_municipio AS municipio,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'F' AND ds_faixa_etaria = 'De 0 até 12 meses'  THEN mov ELSE 0 END) AS f_0_12,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'F' AND ds_faixa_etaria = 'De 13 até 24 meses' THEN mov ELSE 0 END) AS f_13_24,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'F' AND ds_faixa_etaria = 'De 25 até 36 meses' THEN mov ELSE 0 END) AS f_25_36,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'F' AND ds_faixa_etaria = 'Acima de 36 meses' THEN mov ELSE 0 END) AS f_acima_36,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'M' AND ds_faixa_etaria = 'De 0 até 12 meses'  THEN mov ELSE 0 END) AS m_0_12,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'M' AND ds_faixa_etaria = 'De 13 até 24 meses' THEN mov ELSE 0 END) AS m_13_24,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'M' AND ds_faixa_etaria = 'De 25 até 36 meses' THEN mov ELSE 0 END) AS m_25_36,
  SUM(CASE WHEN UPPER(SUBSTR(tp_sexo,1,1)) = 'M' AND ds_faixa_etaria = 'Acima de 36 meses' THEN mov ELSE 0 END) AS m_acima_36,
  SUM(mov) AS total
FROM mov
GROUP BY nm_especie, ds_municipio
ORDER BY nm_especie, ds_municipio;