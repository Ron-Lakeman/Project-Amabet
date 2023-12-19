# Code Review AMABET
Ik heb mijn code laten reviewen door Wouter Bentvelzen en Jet van Ommeren. Zij hebben een aantal verbeterpunten aangekaart die ik in deze code review zal gaan analyseren.

## Wouter Bentvelzen verbeterpunten: 
### Dictionary-aanpassingen:
Het aanmaken van de dictionaries in het helpers.py-bestand kan op een meer gestructureerde manier worden gedaan. Kies betere variabel namen om consistentie te waarborgen, aangezien de huidige implementatie enigszins slordig oogt. Verwijder ongebruikte variabelen, aangezien sommige ervan zijn gedefinieerd zonder dat ze later in de code worden gebruikt. Hoewel het misschien niet altijd duidelijk was welke data nodig zou zijn op het moment van aanmaken, is het behouden van de dictionaries in een apart helpers-bestand een goede keuze geweest om de app.py overzichtelijk te houden.

### Verkorting van regels:
Overwegen om de lengte van sommige regels te verminderen, vooral bij het aanmaken van dictionaries en Bet-objects, zou de code compacter en leesbaarder hebben kunnen maken.

### Toename van commentaar:
Op een aantal plaatsen in de code zouden comments toegevoegd kunnen worden gevoegd om deze leesbaarder te maken. Dit is niet echt een afweging, maar meer iets wat gewoon moet worden gedaan.
Update: ondertussen meer comments toegevoegd aan de app.py na de review.

### Verwijderen van dode code:
Op een aantal plaatsen in de code moeten uitgefiltede print statements en onbruikbare stukjes code nog worden verwijderd.
Update: ondertussen is hier ook naar gekeken.

## Jet verbeterpunten: 
### Bet history op efficiëntere manier aanmaken
De Bet_history class wordt op op een vrij efficiente manier aangemaakt. Er wordt namelijk onderscheid gemaakt tussen een gewonnen en verloren bet. Het aanmaken van een object wordt op bijna dezelfde manier gedaan, op de status en de balance_change na. Ondanks dat alleen deze variablen verschillend zijn, wordt het volledige object om een andere manier aangemaakt, wat leidt tot veel herhaalde code. Wanneer de conditie zou worden gesteld midden in het aanmaken van het object, hoeft veel code niet te worden herhaald. 

### Vermijdt import *
Bij het importeren heb ik meerdere keren de "from x import *" benadering gebruikt, maar blijkbaar wordt dit afgeraden. De reden hiervoor is dat het voor de lezer niet duidelijk is welke functies precies worden geimporteerd wat de code onleesbaar is. Daarnaast is het onpraktisch omdat het mogelijk kan leiden tot naamconfliceten. 

### Vermijdt gebruik van getallen zonder uitleg
In de functie calculate_odds in helpers.py worden enkele getallen gegeven zonder uitleg. Dit zijn de getallen die worden uitgedeeld aan een team dat een wedstrijd wint. Namelijk 3 punten. Echter maakt dit de code minder leesbaar en zal het worden ervaren als een getal dat uit de lucht komt vallen. Beter is om een variable met een duidelijke naam te gebruiken om de waarde van het getal in op te slaan, en dit vervolgens te gebruiken in de functie. Dit zal de code leesbaarder maken.

### Geen error handeling van unsuccesvolle requests
Er worden geen errors getoond wanneer een request niet succesvol wordt aangevraagd. Dit kan het opsporen van bugs moeilijker maken, aangezien er geen directe feedback wordt gegeven over wat er mis is gegaan. Om dit te verbeteren, zou de implementatie moeten worden aanpast om foutmeldingen te genereren en weer te geven wanneer een request niet succesvol is.

### Vermijdt gebruik van globale variablen
De globale variablen zoals live_score_id en match_info zijn achteraf misschien niet de beste optie geweest om de waardes van de variablen door te geven aan de andere functies. Over het algemeen worden globale variablen afgeraden. Dit heeft een aantal redenen, zoals dat bugs over het algemeen moeilijker zijn op te sporen. Daarnaast verminderd het de leesbaarheid van de code in het algemeen. Een betere manier had geweest om parameters van functies te gebruiken.
