import datetime
import json
from io import BytesIO
import requests
import logging
from typing import Dict
from pyzbar.pyzbar import decode
from PIL import Image
import scaper
import date_converter

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)

#insert telegram token into secret.txt
token = str(open("secret.txt","r").read())
data = json.load(open("biblio.json"))
# !/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

SCELTA_INIZIALE, PRENOTAZIONE, NOME, COGNOME, CF, EMAIL, TELEFONO, RIEPILOGO_REGISTRAZIONE, \
DELETE_ACCOUNT, MODIFICA, DIGITO, SCELTA_TEMPO, GIORNO = range(13)


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    reply_text = "Benvenuto nel bot per la prenotazione delle biblioteche ed aule studio uniud!\n\n"
    if context.user_data:
        if context.user_data["registrazione_terminata"]:
            reply_text += (
                f"Ciao {context.user_data['nome']} {context.user_data['cognome']} dimmi cosa vuoi fare!"
            )
            reply_keyboard = [
                ['Prenota!'],
                ['Mostra dati personali'],
                ['Modifica dati personali', 'Cancella account'],
            ]
        else:
            reply_text += (
                "La registazione precedente è stata interrotta, registrati di nuovo così potrai prenotare più agevolmente"
            )
            reply_keyboard = [
                ['Registrati'],
                ['Annulla'],
            ]
    else:
        context.user_data.clear()
        reply_text += (
            "Non so ancora molto di te, registrati così potrai prenotare più agevolmente"
        )
        reply_keyboard = [
            ['Registrati'],
            ['Annulla'],
        ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)

    return SCELTA_INIZIALE


def modifica(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    reply_keyboard = [
        ['Nome', 'Cognome', 'Codice Fiscale'],
        ['Numero telefono', 'Email'],
        ['Fine']
    ]
    reply_text = "Tramite questo menù potrai modificare i tuoi dati personali, dimmi tu cosa desideri modificare"
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)
    return MODIFICA


def modifica_dato(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    if not ("chose" in context.user_data):
        reply = f"Dimmi pure il tuo {text} così lo andrò ad aggiornare!"
        context.user_data["chose"] = text
        update.message.reply_text(reply)
    else:
        match context.user_data["chose"]:
            case "Nome":
                context.user_data["nome"] = text.lower().capitalize()
            case "Cognome":
                context.user_data["cognome"] = text.lower().capitalize()
            case "Codice Fiscale":
                context.user_data["cf"] = text.upper()
            case "Numero telefono":
                context.user_data["telefono"] = text
            case "Email":
                context.user_data["email"] = text.lower()
        del context.user_data["chose"]
        reply = "Ho aggiornato l'informazione, desideri modificare altro?"
        reply_keyboard = [
            ['Nome', 'Cognome', 'Codice Fiscale'],
            ['Numero telefono', 'Email'],
            ['Fine']
        ]
        update.message.reply_text(reply, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return MODIFICA


def register(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    reply_text = (
        f'Inserire il proprio nome: '
    )
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
    return NOME


def save_name(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.lower().capitalize()
    context.user_data['nome'] = text
    context.user_data["registrazione_terminata"] = False
    reply_text = (
        f'Bene {context.user_data["nome"]}, inserisci ora il tuo cognome:'
    )
    update.message.reply_text(reply_text)

    return COGNOME


def save_surname(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.lower().capitalize()
    context.user_data['cognome'] = text
    reply_text = (
        f'Bene {context.user_data["nome"]}, inserisci ora il tuo codice fiscale '
        f'oppure mandami una foto del codice a barre che sul retro:'
    )
    update.message.reply_text(reply_text)
    return CF


def save_cf(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.upper()
    context.user_data['cf'] = text
    reply_text = (
        f'Bene {context.user_data["nome"]}, inserisci ora la tua email:'
    )
    update.message.reply_text(reply_text)
    return EMAIL


# TODO Finire l'implementazione e verificare che vada su host remoto
def save_cf_photo(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    img = Image.open(BytesIO(requests.get(update.message.photo[3].get_file().file_path).content))
    output = decode(img)
    reply_text = (
        f'Bene {context.user_data["nome"]}, inserisci ora la tua email:'
    )
    update.message.reply_text(reply_text)
    return EMAIL


def save_email(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.lower()
    context.user_data['email'] = text
    reply_text = (
        f'Bene {context.user_data["nome"]}, inserisci ora il tuo numero di telefono:'
    )
    update.message.reply_text(reply_text)
    return TELEFONO


def save_telephone(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text.lower().capitalize()
    context.user_data['telefono'] = text
    context.user_data["registrazione_terminata"] = True
    reply_text = (
        f'Perfetto, la registrazione è quasi completata, è tutto corretto quanto sò di te?\n'
        f'Nome: {context.user_data["nome"]}\n'
        f'Cognome: {context.user_data["cognome"]}\n'
        f'Email: {context.user_data["email"]}\n'
        f'Codice fiscale: {context.user_data["cf"]}\n'
        f'Telefono: {context.user_data["telefono"]}'
    )
    reply_keyboard = [
        ['Perfetto'],
        ['Modifica'],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)
    return RIEPILOGO_REGISTRAZIONE


def mostra_dati(update: Update, context: CallbackContext) -> int:
    reply_text = (
        f'Queste sono le informazioni che ho di te:\n'
        f'Nome: {context.user_data["nome"]}\n'
        f'Cognome: {context.user_data["cognome"]}\n'
        f'Email: {context.user_data["email"]}\n'
        f'Codice fiscale: {context.user_data["cf"]}\n'
        f'Telefono: {context.user_data["telefono"]}'
    )
    reply_keyboard = [
        ['Modifica dati personali', 'Cancella account'],
        ['Annulla']
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(reply_text, reply_markup=markup)
    return SCELTA_INIZIALE


def cancella_account(update: Update, context: CallbackContext) -> int:
    if context.user_data:
        reply_text = (
            f'{context.user_data["nome"]}, sei veramente sicuro di voler cancellare i tuoi dati? \nDopo non ti sarà più possibile prenotarti senza fare una nuova registrazione'
        )
        reply_keyboard = [
            ['Si'],
            ['Annulla'],
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(reply_text, reply_markup=markup)
    else:
        reply_text = f'Non ho alcuna informazione su di te!'
        update.message.reply_text(reply_text)
    return DELETE_ACCOUNT


def conferma_cancellazione(update: Update, context: CallbackContext) -> int:
    if context.user_data:
        context.user_data.clear()
    reply_text = f'Ho cancellato tutto le informazioni'
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
    return PRENOTAZIONE


def prenota(update: Update, context: CallbackContext) -> int:
    if context.user_data:
        reply_text = f'Ciao {context.user_data["nome"]} benvenuto nel servizio di prenotazione, desideri prenotare per serivizio o per sede?'
        reply_keyboard = [
            ['Servizio', 'Sede'],
            ['Annulla'],
        ]
    else:
        reply_text = "Sei pregato prima di registrarti"
        update.message.reply_text(reply_text)
        return ConversationHandler.END
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return PRENOTAZIONE


def mostra_scelte(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    match text:
        case "sede":
            reply_text = "Ecco le sedi disponibili:"
            context.user_data["chosing"] = "sedi"
        case "servizio":
            reply_text = "Ecco i servizi disponibili:"
            context.user_data["chosing"] = "servizi"
        case _:
            reply_text = "Non sembra essere stata fatta una scelta valida, scegliere nuovamente!"
            reply_keyboard = [
                ['Servizio', 'Sede'],
                ['Annulla'],
            ]
            update.message.reply_text(reply_text,
                                      reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return PRENOTAZIONE

    # Inizializzo tastiera con lista sedi/servizi disponibili
    keyboard = list()
    for k in data[context.user_data["chosing"]]:
        l = list()
        l.append(str(data[context.user_data["chosing"]][k]["nome"]))
        keyboard.append(l)
        del l
    keyboard.append(["Indietro"])

    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return DIGITO


def salvo_risposta(update: Update, context: CallbackContext) -> int:
    scelta = update.message.text
    if scelta == "Indietro":
        if "second_chose" in context.user_data.keys():
            del context.user_data["second_chose"]
        del context.user_data["chosing"]
        reply_text = "Scegli pure tra:"
        reply_keyboard = [
            ['Servizio', 'Sede'],
            ['Annulla'],
        ]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return PRENOTAZIONE
    else:
        if (context.user_data["chosing"] in ["sedi", "servizi"]):
            for (k, v) in data[context.user_data["chosing"]].items():
                if scelta == v["nome"]:
                    context.user_data[context.user_data["chosing"]] = k
                    if "second_chose" not in context.user_data.keys():
                        if context.user_data["chosing"] == "servizi":
                            lista = v["sedi"]
                            loc = "sedi"
                            reply_text = f"Bene ora non ti resta che selezionare la sede desiderata:"
                            context.user_data["chosing"] = "sedi"
                            context.user_data["second_chose"] = True
                        else:
                            lista = v["servizi"]
                            loc = "servizi"
                            reply_text = f"Bene ora non ti resta che selezionare il servizio desiderato:"
                            context.user_data["chosing"] = "servizi"
                            context.user_data["second_chose"] = True
                        keyboard = list()
                        for l in lista:
                            t = list()
                            t.append(str(data[loc][str(l)]["nome"]))
                            keyboard.append(t)
                            del t
                        keyboard.append(["Indietro"])
                        update.message.reply_text(reply_text,
                                                  reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
                    else:
                        del context.user_data["second_chose"]
                        del context.user_data["chosing"]
                        print(context.user_data['sedi'])
                        print(context.user_data['servizi'])

                        # TODO togliere in produzione
                        update.message.text = ""
                        if "durata" in context.user_data.keys():
                            del context.user_data["durata"]

                        reply_text = f"Bene hai scelto la sede \"{data['sedi'][context.user_data['sedi']]['nome']}\" ed il servizio \"{data['servizi'][context.user_data['servizi']]['nome']}\""
                        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
                        return durata(update, context)
                    return DIGITO


def durata(update: Update, context: CallbackContext) -> int:
    scelta = update.message.text
    if scelta == "Indietro":
        del context.user_data["durata"]
        del context.user_data["sedi"]
        del context.user_data["servizi"]
        reply_text = "Scegli nuovamente tra:"
        reply_keyboard = [
            ['Servizio', 'Sede'],
            ['Annulla'],
        ]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return PRENOTAZIONE
    elif "durata" not in context.user_data.keys():
        reply_text = "Scegli pure la durata della tua prenotazione: "
        keyboard = list()
        for durata in data["durate"].keys():
            t = list()
            t.append(durata)
            keyboard.append(t)
            del t
        keyboard.append(["Indietro"])
        context.user_data["durata"] = True
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return SCELTA_TEMPO
    else:
        context.user_data["durata"] = scelta
        reply_text = f"Bene, procederai ora con la scelta del giorno in cui desiderai prenotare,attendi solo un'attimo:"
        context.user_data["session"] = requests.Session()
        context.user_data["token"] = scaper.get_token(context.user_data["session"])
        days = scaper.get_days(context.user_data["session"], context.user_data["sedi"], context.user_data["servizi"])
        keyboard = list()
        for d in days:
            row = list()
            row.append(d)
            keyboard.append(row)
            del row
        keyboard.append(["Indietro"])
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
        return GIORNO


def giorno(update: Update, context: CallbackContext) -> int:
    scelta = update.message.text
    if scelta == "Indietro":
        del context.user_data["durata"]
        del context.user_data["sedi"]
        del context.user_data["servizi"]
        reply_text = "Scegli nuovamente tra:"
        reply_keyboard = [
            ['Servizio', 'Sede'],
            ['Annulla'],
        ]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return PRENOTAZIONE
    else:
        date = date_converter.date_str_it_to_str_en(scelta)
        reply_text = "Bene, ora non resta che scegliere la data della prenotazione"
        timetable = scaper.get_timetable(context.user_data["session"], context.user_data["sedi"],
                                         context.user_data["servizi"], date, context.user_data["cf"],
                                         context.user_data["durata"])
        days = list((list(timetable.values())[0]).values())[0]
        times = dict()
        for k in days:
            for (k1, v1) in days[k].items():
                times[k1] = v1
        context.user_data["avaliable_times"] = times
        keyboad = list()
        for k in times:
            l = list()
            ora = (datetime.datetime.fromtimestamp(float(k))).strftime("%d-%m-%Y")

        update.message.reply_text(reply_text)
        return PRENOTAZIONE


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='conversationbot')
    updater = Updater(token, persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states SCELTA_INIZIALE, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SCELTA_INIZIALE: [
                MessageHandler(Filters.regex('^(Registrati)$'), register),
                MessageHandler(Filters.regex('^(Modifica dati personali)$'), modifica),
                MessageHandler(Filters.regex('^(Prenota!)$'), prenota),
                MessageHandler(Filters.regex('^(Cancella account)$'), cancella_account),
                MessageHandler(Filters.regex('^(Mostra dati personali)$'), mostra_dati)
            ],
            NOME: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), save_name)
            ],
            COGNOME: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), save_surname)
            ],
            CF: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), save_cf),
                # MessageHandler(Filters.photo, save_cf_photo)
            ],
            EMAIL: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), save_email)
            ],
            TELEFONO: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), save_telephone)
            ],
            RIEPILOGO_REGISTRAZIONE: [
                MessageHandler(Filters.regex('^(Perfetto)$'), start),
                MessageHandler(Filters.regex('^(Modifica)$'), modifica)
            ],
            DELETE_ACCOUNT: [
                MessageHandler(Filters.regex('^(Si)$'), conferma_cancellazione),
            ],
            MODIFICA: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Fine)$')), modifica_dato),
            ],
            PRENOTAZIONE: [
                MessageHandler(Filters.regex('^(Servizio|Sede)$') & ~(Filters.regex('^(Annulla)$')), mostra_scelte),
            ],
            DIGITO: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), salvo_risposta),
            ],
            SCELTA_TEMPO: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), durata),
            ],
            GIORNO: [
                MessageHandler(Filters.text & ~(Filters.regex('^(Annulla)$')), giorno),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^(Annulla|Fine)'), start)],
        name="my_conversation",
        persistent=True,
        allow_reentry=True,
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
