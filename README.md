# Home Assistant ČEZ Distribuce Portál Naměřených Dat
Script a nastavení Home Assistant slouží pro vyčítání dat o spotřebě a výrobě elektřiny z distribučního portálu https://www.cezdistribuce.cz/ v denních úhrnech

Po správném nastavení a spuštění scripu vznikou v Home Assistant tyto senzory:

* sensor.pnd_data (obsahujíc data výroby a spotřeby za vámi zvolený interval - např období vyúčtování)
* sensor.pnd_consumption a sensor.pnd_production v KWh je to den zpětně souhrn za den (data se vyčítají po půlnoci za den zpětně)
* sensor.pnd_total_interval_consumption resp sensor.pnd_total_interval_production v KWh součet za období
* sensor.pnd_running kontrolní senzor který se zapne při spuštění a vypne při úspěšném dokončení (úspěšnost je +/-95%) lze použít v automatizaci pro opětovné spuštění skriptu

Výsledkem pak může být například takovýto dashboard (návod na jeho výrobu je popsán níže)

![](/obrazky/00-prehled.png)

**POZOR: Pokud již používáte AppDaemon nebo máte ve svém HA výše uvedené entity, návod je potřeba odpovídajícím způsobem upravit, abyste zachovali to co již používáte. Takové úpravy nejsou v návodu uvedeny.**

## Co je potřeba
1. Přihlášení do Distribučního Portálu
2. [HomeAssistant](#homeassistant)
   - AddOn AppDaemon
   - AddOn File Editor (nebo jakoukoliv možnost úpravy konfiguračních souborů v HA)
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

### Instalace a nastavení AppDaemon
1. V nastavení HA zvolte "Doplňky" a dále pak "Obchod s doplňky"
2. Vyhledejte AppDaemon, zvolte jej a klikněte na "Nainstalovat". Instalace dle rychlosti vašeho HW a internetu je hotova do několika minut.
3. Po instalaci přejděte do nastavení AppDaemon
   - v části "System Packages" přidejte _chromium-chromedriver_ a _chromium_. Pozn.: pokaždé vložte jeden název a stiskněte enter, je nutné přidávat postupně
   - v části "Python packages" přidejte _selenium_ a _pandas_. Pozn.: pokaždé vložte jeden název a stiskněte enter, je nutné přidávat postupně
   - Klikněte na "Uložit". Konfigurace by měla odpovídat obrázku níže
4. Spusťte doplněk AppDaemon
  
![](/obrazky/04-appdaemon-config.png)

### Konfigurace prostředí AppDaemon
1. V nastavení File editoru vypněte možnost "Enforce Basepath" a zvolte "Uložit" (doplněk se restartuje)
2. Spusťte File File Editor a otevřete soubor _addon_configs/a0d7b954_appdaemon/appdaemon.yaml_. (pozor je nutné ve File Editoru přejít do kořenové složky, proto se nastavovala volba výše.
3. v části plugins>HASS doplňte
```
ha_url: http://ip-adresa-nebo-url-vaseho-ha:8123
token: vas-token-ktery-jste-si-vytvorili-vyse
```
4. v části appdaemon doplňte `app_dir: /homeassistant/appdaemon/apps`
5. přidejte část:
```
logs:
  pnd:
    name: pnd
    filename: /homeassistant/appdaemon/pnd.log
```
6. soubor uložte a restartujte doplněk AppDaemon

Celý appdaemon.yaml vypadá nějak takto:
```
---
appdaemon:
  latitude: 52.379189
  longitude: 4.899431
  elevation: 2
  time_zone: Europe/Amsterdam
  thread_duration_warning_threshold: 60
  plugins:
    HASS:
      type: hass
      ha_url: http://http://homeassistant.local/:8123
      token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
  app_dir: /homeassistant/appdaemon/apps
http:
  url: http://127.0.0.1:5050
admin:
api:
hadashboard:
logs:
  pnd:
    name: pnd
    filename: /homeassistant/appdaemon/pnd.log
```
### Vytvoření aplikace PND v AppDaemon
1. ve File Editor přejdět do složky homeassistant/
2. vytvořte složku _appdaemon_ a přejděte do ní
3. vytvořte složku _apps_ a přejděte do ní
4. vytvořte složku _pnd_
5. ve složce _apps_ vytvořte soubor _apps.yaml_ s obsahem:
   * parametr **PNDUserName** je váš email s přihlášením do portálu
   * parametr **PNDUserPassword** je heslo pro přihláše
   * parametr **DataInterval** je interval dat, které budete chtít stahovat - například období fixace smlouvy. Nedoporučuji víc jak rok, mohlo by zahltit databázi.
```
---
pnd:
  module: pnd
  class: pnd
  log: pnd
  PNDUserName: "vas email s prihlasenim do portalu distribuce"
  PNDUserPassword: "vase heslo do portalu distribuce"
  DataInterval: "27.10.2023 00:00 - 27.10.2024 00:00"
  DownloadFolder: "/homeassistant/appdaemon/apps/pnd"
```
6. soubor uložte
7. do složky _apps_ nahrajte soubor [pnd.py](/pnd.py)
8. restartujte doplněk AppDaemon. Pozn.: při aktualizaci souboru pnd.py za novější, není nutné doplněk restartovat

Tím je kom

