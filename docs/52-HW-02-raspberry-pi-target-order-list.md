# Raspberry Pi target hardware — bestellijst

Deze lijst houdt de fysieke onderdelen voor de Event Timing Raspberry Pi Zero testopstelling bij.

De lijst staat in de Event Timing meta-repository omdat bestellen en samenstellen van targethardware
geen verantwoordelijkheid is van de Raspberry Pi image-repository.

## Kiwi Electronics — eerstvolgende bestelling

| Onderdeel | Doel | Status | Product |
| --- | --- | --- | --- |
| Waveshare 2.13inch e-Paper HAT+ (250×122, SPI) | lokaal statusdisplay + DS3231 RTC | bestellen | https://www.kiwi-electronics.com/nl/waveshare-2-13inch-e-paper-hat-plus-voor-raspberry-pi-250x122-spi-e-ink-display-20801 |
| Pimoroni GPIO Hammer Header male | GPIO-header zonder solderen aan Pi Zero | bestellen | https://www.kiwi-electronics.com/nl/gpio-hammer-header-male-20120 |
| 40-pin GPIO Header 2x20 Female | optionele female socket / mechanische testoptie bovenop de Hammer Header | meebestellen | https://www.kiwi-electronics.com/en/40-pin-gpio-header-2x20-female-2173?search=header%20female |
| Raspberry Pi Debug Probe | programmer/debugger + 3,3 V USB-UART voor bootconsole | bestellen | https://www.kiwi-electronics.com/en/raspberry-pi-debug-probe-11345 |

De female 2x20 header is geen vaste stack-keuze. We bestellen hem mee als goedkope test- en adapteroptie, bijvoorbeeld om bovenop de Hammer Header te passen en verschillende HAT/header-opbouwen te kunnen proberen voordat de definitieve mechanische stack wordt vastgelegd.

### RTC-batterij — vrijwel geschikt, connector nog bevestigen

| Onderdeel | Status | Wat is al geverifieerd? | Open punt |
| --- | --- | --- | --- |
| Raspberry Pi 5 RTC Battery / ML2020 | kandidaat voor dezelfde Kiwi-bestelling | ML2020 is oplaadbare Li-Mn 3.0 V; Waveshare vraagt oplaadbare 3/3.3 V lithium; elektrische laadspanning is plausibel compatibel | Waveshare noemt alleen "2PIN JST"; bevestig dat dit fysiek JST-SH 1.0 mm is en dat stekker/polariteit overeenkomen |

Product:
https://www.kiwi-electronics.com/nl/rtc-batterij-voor-raspberry-pi-5-11586

**Besluit:** elektrisch niet meer blokkeren. Alleen de fysieke connector/polariteit blijft een
kwalificatiepunt. Als de Waveshare-connector als JST-SH met passende polariteit wordt bevestigd,
kan deze batterij gewoon mee in de Kiwi-bestelling.

## Van Alles en Meer — kandidaat

| Onderdeel | Doel | Status | Product |
| --- | --- | --- | --- |
| Pololu 4813 JST-SH breakout, 3-pin side-entry | vaste UART/debug-aansluiting aan zijkant | kandidaat | https://www.vanallesenmeer.nl/Pololu-4813-JST-SH-breakoutboard-3-pin-side-entry-set-2 |

Deze breakout is pas nodig als we de vaste UART-aansluiting gaan bouwen. Voor de eerste boot kan
de Debug Probe met tijdelijke bedrading worden gebruikt.

## In bezit

| Onderdeel | Doel | Status | Opmerking |
| --- | --- | --- | --- |
| Raspberry Pi Zero W versie 1 | test-target | in bezit | BCM2835 / ARM11, 512 MB; target-architectuur armv6l |
| SanDisk microSD 32 GB | boot/testmedia | in bezit | geleverd met NOOBS; opnieuw schrijven met de door GitHub gebouwde test-image (Raspberry Pi Imager alleen als writer) |
| Raspberry Pi voeding 2,5 A | voeding test-target | in bezit | uit starterset |
| Raspberry Pi Zero behuizing | tijdelijke behuizing | in bezit | drie deksels, waaronder GPIO-uitsparing |
| mini-HDMI → HDMI adapter | lokale video indien nodig | in bezit | uit Zero Essentials Kit |
| micro-USB → USB adapter | USB-OTG indien nodig | in bezit | uit Zero Essentials Kit |
| standaard 40-pin male header | reserve / alternatief | in bezit | vereist solderen; voorlopig niet gebruiken als Hammer Header wordt toegepast |

Bron starterset:
https://www.raspberrystore.nl/PrestaShop/nl/raspberry-pi-zero-v1-en-v2/485-raspberry-pi-zero-1w-starterset.html

## Onderweg

| Onderdeel | Doel | Status |
| --- | --- | --- |
| Button SHIM | vijf knoppen + RGB-status via I2C | onderweg |

Product:
https://www.pilover.com/en/shop/button-shim-2/

## Later

| Onderdeel | Doel | Status | Opmerking |
| --- | --- | --- | --- |
| UUGear Zero4U | vier USB-poorten onder Pi Zero | later | eerst Pi + Button SHIM + e-paper mechanisch kwalificeren |
| koperfolie / kopertape | eventueel soldeerloos Button SHIM-contact | alleen indien nodig | pas beoordelen na fysieke passing |
| 3D-geprinte houder | mechanische fixatie UART-breakout / eventueel veercontact | later | pas ontwerpen na fysieke passing |

Zero4U:
https://www.uugear.com/product/zero4u/

## Volgorde na levering

1. Pi Zero + Hammer Header droog passen.
2. Button SHIM vlak tegen de onderzijde passen en pinlengte meten.
3. Debug Probe aansluiten en seriële console kwalificeren.
4. Waveshare HAT+ bovenop passen.
5. UART/JST-positie bepalen met oog op toekomstige Zero4U.
6. RTC-batterij pas aansluiten na connector-, polariteits- en laadcontrole.
7. Zero4U pas toevoegen nadat de boven- en onderzijde mechanisch zijn gekwalificeerd.
