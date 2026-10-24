# Social Mentor — TikTok Intelligence

**Social Mentor** è il brand pubblico del progetto: una dashboard in italiano per monitorare notizie TikTok e trasformarle in bozze video per creator, professionisti e piccole attività.

## Funzioni
- Interfaccia responsive per smartphone.
- Ricerca e filtri per categoria e tipo di fonte.
- Bozza video con hook iniziale, testo a schermo, parlato, keyword SEO, caption e CTA.
- Salvataggio delle notizie nel browser usato.
- Archivio locale di esempi video pubblici con filtro per nicchia, ordinamento, analisi descrittiva dei pattern e rimozione dei duplicati.
- Importazione/esportazione dell'archivio di ricerca in JSON e CSV.
- Laboratorio SEO iniziale per generare bozze da rivedere manualmente.
- Piano operativo: [prossimi 10 obiettivi](docs/roadmap-10-obiettivi.md).
- Raccolta RSS tramite GitHub Actions, programmata ogni sei ore e avviabile manualmente.

## Pubblicazione gratuita con GitHub Pages
1. Apri **Settings → Pages** in questo repository.
2. In **Build and deployment**, scegli **Deploy from a branch**.
3. Scegli il branch **main** e la cartella **/(root)**, poi premi **Save**.
4. Dopo il deploy, copia l’indirizzo pubblicato mostrato da GitHub Pages nelle impostazioni del repository. Il titolo e il branding del sito sono **Social Mentor**. Nota: l’indirizzo gratuito GitHub Pages continua a includere il nome dell’account proprietario; per cambiare anche quella parte serve pubblicare il sito da un account o un’organizzazione GitHub con nome brand, se disponibile.

## Raccolta delle notizie
- Per una nuova raccolta manuale: dalla gestione del progetto, apri **Actions → Refresh TikTok news → Run workflow**.
- Il workflow prova a raccogliere i feed ogni sei ore.
- **Ricarica notizie** nella dashboard rilegge il feed già pubblicato. La raccolta automatica è programmata ogni sei ore; l’avvio manuale resta disponibile nella sezione Actions del progetto. Il browser non contiene token segreti.
- Le notizie provengono da ricerche RSS pubbliche di Google News. Disponibilità e qualità dipendono dai feed esterni.

## Verifica delle fonti
Le voci non riconosciute come provenienti direttamente da un dominio TikTok ufficiale sono etichettate **Trend / da verificare**. I collegamenti Google News possono nascondere il dominio finale dell'editore: controlla sempre la pagina originale prima di presentare una notizia come confermata.

Le idee video sono bozze da personalizzare, non garanzie di visualizzazioni. Progetto indipendente, non affiliato a TikTok.

## Controlli pratici prima di usare una bozza
1. Inserisci un argomento specifico nel laboratorio SEO e verifica che appaiano obiettivo, hook, alternative, scaletta, keyword, caption, CTA e checklist.
2. Prova **Copia bozza** e, se disponibile, **Copia solo il parlato**; se il browser blocca gli appunti, seleziona e copia il testo manualmente.
3. Aggiungi all'archivio un esempio pubblico della nicchia scelta e genera una bozza sullo stesso tema: gli spunti salvati devono comparire solo quando ci sono parole pertinenti.
4. Ricarica la pagina e controlla che l'archivio sia ancora presente nello stesso browser. I dati sono locali e non vengono sincronizzati automaticamente tra dispositivi.
5. Verifica manualmente le fonti, le date, i diritti di audio/immagini e la pertinenza delle keyword prima di pubblicare. La compilazione GitHub Pages non equivale a un test interattivo completo nel browser.
