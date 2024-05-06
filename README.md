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
   - [AddOn AppDaemon](#appdaemon)
   - AddOn File Editor (nebo jakoukoliv možnost úpravy konfiguračních souborů v HA)
   - Script pro stažení dat
   - [Naplánování automatické aktualizace](#nastavení-automatické-aktualizace-dat)
   - [HACS](#instalace-hacs)
   - [ApexCharts Card](#instalace-apexcharts-card)
3. [Tvorba Dashboardu](#tvorba-dashboardu)
4. [Nápady a plány](#pl%C3%A1ny-a-n%C3%A1pady)
5. [Změny (Changelog)](#změny)


## Distribuční portál
Zažádejte si o přihlášení do Distribučního Portálu na webu https://dip.cezdistribuce.cz/irj/portal/ obvykle vyřízeno do druhého dne.

Po přihlášení ověřte, že máte k dispozici váš elektroměr v sekci "Množina zařízení". V tuto chvíli script stahuje všechna data, tedy pokud máte více elektroměrů, nemusí script fungovat správně.

**Pozn.: Skript prozatím neumí správně pracovat s uživatelskými sestavami a více elektroměry.** Zvolte v portále "Rychlá sestava" a "Všechny EANy" nebo odpovídající elektroměr a odhlaste se z portálu.

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
      ha_url: http://192.168.1.100:8123
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

### Nastavení automatické aktualizace dat
Skript, který získává data vyčkává na událost _run_pnd_ v rámci Home Assistant. Nejsnazší cestou je vytvoření automatizace, která v pravidelném čase stažení dat spustí.
1. V Home Assistant zvolit "Nastavení" > "Automatizace a scény"
2. Vytvořit novou automatizaci
   * parametr "Když" > "Přidat spouštěč" zvolit "Čas" a zvolte čas, ve kterém se má spouštět. Data na portále jsou dostupná několik minut po půlnoci, můžete nastavit např. 00:30:00 AM tedy 30 minut po půlnoci se spustí.
   * parametr "Pak provést" zvolit "Ruční událost" do "Typ události" zadat _run_pnd_
3. Uložit automatizaci - zvolte jméno automatizace, které si přejete

Ověřte funkčnost nastavení (AppDaemon, skript a automatizace) > vpravo nahoře tři tečky > "Spustit"

Chod skriptu trvá cca 50vteřin, poté byste měli vidět odpovídající entity v HA.

YAML kód automatizace
```
alias: Run PDN
description: ""
trigger:
  - platform: time
    at: "00:30:00"
condition: []
action:
  - event: run_pnd
    event_data: {}
mode: single
```

### Řešení problémů se skriptem
pokud se vyskytne problém (např data se nestahují), přepněte nastavení "Log Level" v AppDaemon na Info a restartujte AppDaemon. Pak je dostupný log v cestě /homeassistant/appdaemon/pnd.log

### Instalace HACS
Postup instalalce je uvedený na [stránkách projektu](https://hacs.xyz/)

### Instalace ApexCharts Card
Postup instalace je uvedený na [stránkách projektu](https://github.com/RomRider/apexcharts-card)

## Tvorba Dashboardu
Cílem návodu není do detailu popisovat jak v Home Assistant vytvářet dashboardy, níže uvádím ukázky grafů, které lze s výše získaných dat vytvořit. Pokud vytvoříte nějaký super graf, přidejte kód zde na Gitu.

Pokud jste postupovali dle návodu a máte data v Home Assistantu, pak stačí vytvořit novou "Manuální kartu" a do ní zkopírovat kód jednotlivých karet níže.

### PND Včerejší stav spotřeby/výroby
Využívá senzory _sensor.pnd_consumption_ a _sensor.pnd_production_ které obsahují denní spotřebu resp výrobu za **předchozí den**. Senzory jsou třídy (device_class) energy a jsou tedy automaticky ukládány do dlouhodobých dat v HomeAssistant
```
type: custom:apexcharts-card
stacked: true
graph_span: 7d
span:
  end: day
header:
  show: true
  title: PND Včerejší stav
series:
  - entity: sensor.pnd_consumption
    name: Spotřeba
    color: var(--error-color)
    opacity: 0.8
    invert: true
    type: column
    group_by:
      func: last
      duration: 1d
  - entity: sensor.pnd_production
    name: Výroba
    color: var(--success-color)
    opacity: 0.8
    type: column
    group_by:
      func: last
      duration: 1d
```
![](/obrazky/pnd-vcerejsi-stav.png)

### Přehled celkové výroby / spotřeby
Používá kartu rychlý náhled. Jsou využita data ze senzorů _sensor.pnd_total_interval_consumption_ resp _sensor.pnd_total_interval_production_

```
show_name: true
show_icon: true
show_state: true
type: glance
entities:
  - entity: sensor.pnd_total_interval_consumption
    name: Spotřeba za Období
  - entity: sensor.pnd_total_interval_production
    name: Výroba za Období
state_color: false
title: Celkový přehled
```
![](/obrazky/pnd-celkem-nahled.png)

### Přehled celkové výroby / spotřeby v koláčovém grafu
Jsou využita data ze senzorů _sensor.pnd_total_interval_consumption_ resp _sensor.pnd_total_interval_production_
```
type: custom:apexcharts-card
chart_type: donut
header:
  show: true
  title: PND Shrnutí Období
apex_config:
  plotOptions:
    pie:
      donut:
        total:
          show: true
          showAlways: true
series:
  - entity: sensor.pnd_total_interval_production
    name: Výroba
    color: var(--success-color)
  - entity: sensor.pnd_total_interval_consumption
    name: Spotřeba
    color: var(--error-color)
```
![](/obrazky/pnd-celkem-kolac.png)

### Přehled výroby / spotřeby za posledních 10 dní
Využívá data _sensor.pnd_data_

```
type: custom:apexcharts-card
stacked: true
graph_span: 10d
span:
  end: day
header:
  show: true
  title: PND Posledních 10 dní
series:
  - entity: sensor.pnd_data
    name: Výroba
    attribute: production
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.production[index]];
      });
    color: var(--success-color)
    opacity: 0.8
    invert: false
    type: column
  - entity: sensor.pnd_data
    name: Spotřeba
    attribute: consumption
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.consumption[index]];
      });
    color: var(--error-color)
    opacity: 0.8
    invert: true
    type: column
```
![](/obrazky/pnd-poslednich10dni.png)

### Všechna data výroby / spotřeby z intervalu, agregace po týdnech

```
type: custom:apexcharts-card
stacked: true
graph_span: 1y
span:
  end: day
header:
  show: true
  title: PND Historická Data (Týdenní agregace)
series:
  - entity: sensor.pnd_data
    name: Výroba
    attribute: production
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.production[index]];
      });
    color: var(--success-color)
    opacity: 0.8
    invert: false
    type: column
    group_by:
      func: sum
      duration: 7d
  - entity: sensor.pnd_data
    name: Spotřeba
    attribute: consumption
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.consumption[index]];
      });
    color: var(--error-color)
    opacity: 0.8
    invert: true
    type: column
    group_by:
      func: sum
      duration: 7d
```
![](/obrazky/pnd-vsechnadata-tydenni.png)

### Všechna data výroby / spotřeby z intervalu, agregace po měsících

```
type: custom:apexcharts-card
stacked: true
graph_span: 1y
span:
  end: day
header:
  show: true
  title: PND Historická Data (Měsíční agregace)
series:
  - entity: sensor.pnd_data
    name: Výroba
    attribute: production
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.production[index]];
      });
    color: var(--success-color)
    opacity: 0.8
    invert: false
    type: column
    group_by:
      func: sum
      duration: 1month
  - entity: sensor.pnd_data
    name: Spotřeba
    attribute: consumption
    data_generator: |
      return entity.attributes.pnddate.map((pnd, index) => {
        return [new Date(pnd).getTime(), entity.attributes.consumption[index]];
      });
    color: var(--error-color)
    opacity: 0.8
    invert: true
    type: column
    group_by:
      func: sum
      duration: 1month
```
![](/obrazky/pnd-vsechnadata-mesicni.png)

# Plány a nápady
- [ ] Zpracování více EANů (Elektroměrů)
- [ ] Skript nepracuje správně, pokud uživatel zvolil uživatelskou sestavu. Pro správné fungování prozatím zvolte ručně "Rychlá sestava" a portál zavřete, script bude fungovat správně. na řešení pracuji
# Změny
0.9.2: 5.4.2024
- [x] Změna vyhledání intervalu z ID na nadřazený název
- [x] Vynucení "Výchozí sestava" a "Všechny EANy"
