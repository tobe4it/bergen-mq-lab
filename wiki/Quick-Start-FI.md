# Pikaopas — IBM MQSC (Suomi)

> Suorita numeroitu MQSC-tiedosto olemassa olevassa IBM MQ -jononhallinnassa Ansiblen avulla. DISPLAY QMGR on vain luku -komento.

[Wiki Home](https://github.com/tobe4it/bergen-mq-lab/wiki/Home) · [Canonical MQSC reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)

## 1. Valmistelu

Asenna riippuvuudet ohjauskoneeseen ja suorita komennot projektin juurihakemistosta.

```bash
git clone https://github.com/tobe4it/bergen-mq-lab.git
cd bergen-mq-lab
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
cp ansible/examples/mqsc-inventory.yml ansible/inventory.mqsc.local.yml
```

## 2. Yhteysasetukset

Muokkaa paikallista inventorya: jokainen jononhallinta tarvitsee oman aliaksen, palvelimen, käyttäjän ja oikean nimen. Windows käyttää WinRM/PSRP:tä; konteille määritä runtime ja nimi. Säilytä salasanat Vaultissa.

```yaml
mqsc_targets:
  hosts:
    linux-mq:
      ansible_host: mq.example.invalid
      ansible_user: mqdeploy
      mqsc_platform: linux
      mqsc_qmgr: QM01
      mqsc_installation: /opt/mqm
      mqsc_become: true
      mqsc_become_user: mqm
```

## 3. MQSC-tiedosto

Valitse kaikkialla käyttämätön C########-muutostunnus. Komennot suoritetaan tiedostojärjestyksessä.

```bash
mkdir -p mqsc/linux-mq
printf 'DISPLAY QMGR\n' > mqsc/linux-mq/C00000010.mqsc
```

## 4. Auditointi ja tarkistus

Audit tarkistaa alustan ja todellisen MQ-version. Validate tarkistaa lisäksi syntaksin mutta ei objektien tilaa tai oikeuksia.

```bash
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml --target linux-mq --mode validate
```

## 5. Suoritus hyväksynnällä

Käytä vasta hyväksynnän jälkeen tarkastetun suunnitelman tarkkaa SHA-256-tiivistettä ja hyväksyntäviitettä. Älä keksi tiivistettä; apply voi muuttaa objekteja.

```bash
# Replace the placeholder with the SHA-256 from the REVIEWED plan.
export REVIEWED_PLAN_SHA256='<reviewed-plan-sha256>'
python3 tools/mqsc_change.py C00000010 -i ansible/inventory.mqsc.local.yml \
  --target linux-mq --mode apply \
  --approve-sha256 "$REVIEWED_PLAN_SHA256" --approval-ref CHG-123
```

## 6. Useita kohteita ja raportit

Useita jononhallintoja varten tee järjestetty manifest ja yhteinen MQSC-tiedosto. Raportit: ansible/reports/mqsc/. Virhe voi jättää osittaisia muutoksia.

```yaml
# mqsc/changes/C00000011.yml
targets: [linux-mq, aix-mq]
mq_series: ['9.4', '10.0']
```

```bash
printf 'DISPLAY QMGR\n' > mqsc/changes/C00000011.mqsc
python3 tools/mqsc_change.py C00000011 -i ansible/inventory.mqsc.local.yml --mode validate
```

[Technical reference](https://github.com/tobe4it/bergen-mq-lab/blob/main/docs/MQSC-DEPLOY.md)
