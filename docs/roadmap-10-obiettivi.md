# Piano operativo: prossimi 10 obiettivi

Questo piano distingue le funzioni già presenti dalle integrazioni che richiedono ulteriore sviluppo o accessi esterni. Non indica che esistano già cinque agenti autonomi.

## Obiettivi e stato

1. **Archivio video locale** — presente: registra URL pubblici, nicchia, hook parafrasato, formato, visualizzazioni dichiarate dall'utente, data e note.
2. **Controlli di qualità in ingresso** — presente: verifica URL HTTP/HTTPS, richiede un hook e segnala i link duplicati.
3. **Ricerca nell'archivio** — presente: filtro testuale per nicchia e ordinamento per data di salvataggio o visualizzazioni registrate.
4. **Esportazione portabile** — presente: esportazione JSON e CSV; importazione JSON con esclusione di duplicati e record non validi.
5. **Analisi descrittiva dei pattern** — presente: riepiloga formati, parole ricorrenti e metriche inserite; non attribuisce causalità.
6. **Fonti di trend ufficiali** — presente: collegamenti al Creative Center per trend/hashtag e Top Ads. I Top Ads sono pubblicità, non prova diretta delle performance organiche.
7. **Feed notizie affidabile** — presente: raccolta RSS tramite GitHub Actions ogni sei ore, con avvio manuale e test.
8. **Bozze SEO orientate all'obiettivo** — presente in versione iniziale: genera hook, scaletta, keyword, caption e CTA; la bozza richiede revisione umana.
9. **Ricerca semi-automatica di video organici reali** — da sviluppare: definire fonti accessibili e consentite, provenienza, data di osservazione e criteri di confronto; non inventare metriche né aggirare accessi.
10. **Coordinamento degli agenti e ciclo di revisione** — da sviluppare: orchestrazione reale, input/output definiti, log, gestione errori e approvazione umana prima della pubblicazione. I ruoli documentati non eseguono autonomamente attività in background.

## Criteri minimi di accettazione

- Ogni metrica raccolta deve avere una fonte e una data di osservazione, quando disponibili.
- Separare dati osservati, interpretazioni e raccomandazioni.
- Non pubblicare automaticamente contenuti o accedere ad account senza autorizzazione esplicita.
- Conservare un passaggio di approvazione umana per gli script finali.
- Verificare il deployment GitHub Pages e testare le funzioni su smartphone dopo ogni modifica.

## Fonti ufficiali di partenza

- [TikTok Creative Center](https://ads.tiktok.com/help/article/creative-center?lang=it): risorse creative, trend, annunci e strumenti.
- [Come usare Trends](https://ads.tiktok.com/resources/help/article/how-to-use-trends): filtri per settore/periodo e analisi degli hashtag.
- [Top Ads Dashboard](https://ads.tiktok.com/resources/help/article/how-to-use-the-top-ads-dashboard): analisi di creatività pubblicitarie ad alte prestazioni.
