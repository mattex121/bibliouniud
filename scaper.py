import requests
from bs4 import BeautifulSoup
from datetime import date,datetime,timedelta
import date_converter


def get_token(session: requests.Session) -> str:
    page = session.get("https://planner.uniud.it/PortalePlanning/uniud-biblio/index.php?include=form")
    pagebs = BeautifulSoup(page.text, 'html.parser')
    token = pagebs.find(id="main_form").input["value"]
    return token


def get_days(session: requests.Session,sede: int,servizio: int) -> list:
    url = f"https://planner.uniud.it/PortalePlanning/uniud-biblio/ajax.php?tipo=data_inizio_form&area={sede}&servizio={servizio}&_lang=it"
    days = session.get(url).json()
    start = datetime.fromisoformat(datetime.strptime(days["min"], "%d-%m-%Y").strftime("%Y-%m-%d"))
    date_list = [(start + timedelta(days=x)).strftime("%d-%m-%Y") for x in range(20)]
    for d in days["days"]:
        if d in date_list:
            date_list.remove(d)
    date_list = date_converter.str_date_list(date_list)
    return date_list



def get_timetable(session:requests.Session,sede:int,servizio:int,data:str,cf:str,durata:int)->dict:
    url = f"https://planner.uniud.it/PortalePlanning/uniud-biblio/ajax.php?_lang=it&area={sede}&data_inizio={data}&servizio={servizio}&tentativi=0&tipo=timetable_available&associazione_risorse_servizi=1&chiave_primaria={cf}&durata_servizio={durata}"
    timetable = session.get(url)
    return timetable.json()

def get_review_page(session:requests.Session,servizio:int,durata:int,timestamp:int,end_time:int,res:int,data_inizio:str,area:int,cf:str,email:str,nome_cognome:str,telefono:str,token:str):
    post = f"servizio={servizio}&durata_servizio={durata}&timestamp={timestamp}&end_time={end_time}&risorsa={res}&data_inizio={data_inizio}&area={area}&codice_fiscale={cf}&email={email}&1595428644={nome_cognome}&gdpr=1&phone={telefono}&_token={token}"
    url = "https://planner.uniud.it/PortalePlanning/uniud-biblio/index.php?include=review"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    review = session.post(url, headers=headers, data=post)
    result = BeautifulSoup(review.text, 'html.parser').find(id="conferma").parent
    url = "https://planner.uniud.it/PortalePlanning/uniud-biblio/index.php?include=confirmed"
    post = f"public_primary={result.contents[1]['value']}&entry={result.contents[3]['value']}&_token={result.contents[5]['value']}&conferma="
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    review = session.post(url, headers=headers, data=post)
    return review
