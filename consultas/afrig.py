GTA = pd.read_csv(f"{my_address_df}/TRADE_2026.csv",sep=';',encoding='utf-8')   ## TRADE_2026.csv - arquivo concatenado mensalmente de GTA emitidas no SIDAGRO legado!
GTA['MUNICIPIO_ORIGEM'] = GTA['MUNICIPIO_ORIGEM'].str.strip()
GTA['MUNICIPIO_DESTINO'] = GTA['MUNICIPIO_DESTINO'].str.strip()
GTA = GTA.reset_index(drop=True)
       
# Filtra as colunas de interesse: 
GTA_bov = GTA[(GTA.DATA_EMISSAO>='2026-08-01')&(GTA.ESPECIE.isin(["BOVINO", "BUBALINO"]))][['DATA_EMISSAO','ESPECIE', 'FINALIDADE_DE_TRANSITO','TOTAL_DE_MACHOS', 'TOTAL_DE_FEMEAS', 'TOTAL_DE_ANIMAIS', 'CODIGO_DO_MUNICIPIO_ORIGEM', 'MUNICIPIO_ORIGEM','UF_DESTINO', 'CODIGO_MUNICIPIO_DESTINO','MUNICIPIO_DESTINO']]

# Agrupa os valores por data | espécie | finalidade de trânsito| municipio origem | municipio destino:
GTA_bov_agg = GTA_bov.groupby(['DATA_EMISSAO','ESPECIE','FINALIDADE_DE_TRANSITO','CODIGO_DO_MUNICIPIO_ORIGEM', 'MUNICIPIO_ORIGEM','UF_DESTINO', 'CODIGO_MUNICIPIO_DESTINO','MUNICIPIO_DESTINO'])[['TOTAL_DE_MACHOS','TOTAL_DE_FEMEAS', 'TOTAL_DE_ANIMAIS']].sum().reset_index()

# Gera o arquivo csv: 
GTA_bov_agg.to_csv(f"{my_address}/TRANSITO_BOVIDEOS_AGOSTO2026.csv", index=False, encoding="utf-8-sig")


    