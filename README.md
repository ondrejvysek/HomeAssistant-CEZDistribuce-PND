# Home Assistant ČEZ Distribuce Portál Naměřených Dat
Script a nastavení Home Assistant slouží pro vyčítání dat o spotřebě a výrobě elektřiny z distribučního portálu https://www.cezdistribuce.cz/ v denních úhrnech

Po správném nastavení a spuštění scripu vznikou v Home Assistant tyto senzory:

* sensor.pnd_data (obsahujíc data výroby a spotřeby za vámi zvolený interval - např období vyúčtování)
* sensor.pnd_consumption a sensor.pnd_production v KWh je to den zpětně souhrn za den (data se vyčítají po půlnoci za den zpětně)
* sensor.pnd_total_interval_consumption resp sensor.pnd_total_interval_production v KWh součet za období
* sensor.pnd_running kontrolní senzor který se zapne při spuštění a vypne při úspěšném dokončení (úspěšnost je +/-95%) lze použít v automatizaci pro opětovné spuštění skriptu

Výsledkem pak může být například takovýto dashboard (návod na jeho výrobu je popsán níže)

![](/obrazky/00-prehled.png)

## Co je potřeba
1. Přihlášení do Distribučního Portálu
2. [HomeAssistant](#homeassistant)
   - AddOn AppDaemon (https://github.com/hassio-addons/addon-appdaemon)
   - Script pro stažení dat
   - Naplánování aktualizace
   - HACS (https://hacs.xyz/)
   - ApexCharts Card (https://github.com/RomRider/apexcharts-card)
3. Tvorba Dashboardu


## Distribuční portál
Zažádejte si o přihlášení do Distribučního Portálu na webu https://dip.cezdistribuce.cz/irj/portal/ obvykle vyřízeno do druhého dne.

Po přihlášení ověřte, že máte k dispozici váš elektroměr v sekci "Množina zařízení". V tuto chvíli script stahuje všechna data, tedy pokud máte více elektroměrů, nemusí script fungovat správně.

![](/obrazky/01-pnd.png)

## HomeAssistant
Pokud toto čtete, více k čemu je HomeAssistant dobrý, pokud přeci ne, více na [stránkách projektu](https://www.home-assistant.io/).Kromě funkčního HomeAssistanta je nutné mít také k dispozici přihlašovací token, který snadno vytvoříte:
1. Klikněte na vaše jméno vlevo dole
2. Klikněte na záložku "Zabezpečení" nahoře
3. V dolní části stránky klikněte na "Vytvořit token"
4. Token pojmenujte např. "AppDaemon" (bez uvozovek) a klikněte na OK
5. zobrazený token si zkopírujte, budete jej za chvíli potřebovat. **POZOR: Token se zobrazí pouze zde a pouze jednou, pokud si jej nezkopírujete, nebude již přístupný a bude nutné vytvořit nový**

![](/obrazky/02-hatoken.png)

## AppDaemon
AppDaemon je volně spojené, vícevláknové, sandboxované prostředí pro spouštění Pythonu, určené pro psaní automačních aplikací pro software domácí automatizace Home Assistant. Více o AppDaemon naleznete na [GitHubu autora](https://github.com/hassio-addons/addon-appdaemon)
