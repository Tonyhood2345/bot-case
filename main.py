import pandas as pd
import os

URL_ACQUIRENTI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=1947365306&single=true&output=csv"
URL_IMMOBILI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=835643388&single=true&output=csv"

OUTPUT_DIR = "pagine_clienti"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("SCARICO DATI...")
try:
    # Scarichiamo forzando la codifica utf-8
    acquirenti = pd.read_csv(URL_ACQUIRENTI, encoding='utf-8')
    immobili = pd.read_csv(URL_IMMOBILI, encoding='utf-8')
    
    # Rimuoviamo eventuali spazi vuoti nascosti nei nomi delle colonne
    acquirenti.columns = acquirenti.columns.str.strip()
    immobili.columns = immobili.columns.str.strip()
    
    # Pulisco i numeri (tolgo €, punti, spazi e caratteri non numerici)
    acquirenti['Budget Max'] = pd.to_numeric(acquirenti['Budget Max'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    immobili['prezzo'] = pd.to_numeric(immobili['prezzo'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    print("✅ Dati scaricati e allineati!")
except Exception as e:
    print(f"❌ Errore lettura dati: {e}")
    exit()

# Template HTML aggiornato per evitare problemi di visualizzazione dei caratteri
html_template = """<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Proposte per {nome}</title></head>
<body>
    <h1>Ciao {nome}</h1>
    <p>Ecco le case trovate a {citta}:</p>
    {contenuto}
</body>
</html>"""

print("CERCO MATCH...")
count = 0

for index, cliente in acquirenti.iterrows():
    nome = str(cliente['Nome'])
    # Usiamo il recupero sicuro della colonna per evitare problemi con la 'à'
    citta = str(cliente.get('Città', cliente.get('Citta', '')))
    budget = cliente['Budget Max']
    
    # Controllo di sicurezza se il budget o la città sono vuoti
    if pd.isna(budget) or not citta:
        continue
        
    # Filtro: cerco la città nella zona dell'immobile e controllo il budget
    match = immobili[
        (immobili['zona'].str.contains(citta, case=False, na=False)) & 
        (immobili['prezzo'] <= budget)
    ]
    
    if not match.empty:
        schede = ""
        for idx, casa in match.iterrows():
            schede += f"<p>🏠 {casa['zona']} - € {casa['prezzo']:,}</p>".replace(",", ".") # Formatta il prezzo in stile 200.000
        
        # Generiamo un ID sicuro per il nome del file
        cliente_id = cliente.get('id', index)
        file_path = f"{OUTPUT_DIR}/proposte_{cliente_id}.html"
        
        # Salviamo specificando encoding='utf-8' per non far crashare Windows con gli accenti
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_template.format(nome=nome, citta=citta, contenuto=schede))
        print(f"✅ Pagina creata per {nome} -> {file_path}")
        count += 1

if count == 0:
    print("⚠️ Nessuna pagina creata. Verifica che i nomi delle città coincidano tra i due fogli e che i budget siano superiori ai prezzi delle case.")
