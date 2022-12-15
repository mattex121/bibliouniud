from datetime import date,datetime


def str_date_list(date: list[str]) -> list[str]:
    output = list()
    for d in date:
        output.append(date_to_str_it(d))
    del date
    return output

"dd-mm-yyyy"
def date_to_str_it(date: str)->str:
    param = (datetime.strptime(date, "%d-%m-%Y")).strftime("%A/%-d/%B/%Y").split("/")
    match param[0]:
        case "Monday":
            param[0] = "Lunedì"
        case "Tuesday":
            param[0] = "Martedì"
        case "Wednesday":
            param[0] = "Mercoledì"
        case "Thursday":
            param[0] = "Giovedì"
        case "Friday":
            param[0] = "Venerdì"
        case "Saturday":
            param[0] = "Sabato"
        case "Sunday":
            param[0] = "Domenica"

    match param[2]:
        case "January":
            param[2] = "Gennaio"
        case "February":
            param[2]= "Febbraio"
        case "March":
            param[2] = "Marzo"
        case "April":
            param[2] = "Aprile"
        case "May":
            param[2] = "Maggio"
        case "June":
            param[2] = "Giugno"
        case"July":
            param[2] = "Luglio"
        case "August":
            param[2] = "Agosto"
        case "September":
            param[2] = "Settembre"
        case "October":
            param[2] = "Ottobre"
        case "November":
            param[2] = "Novembre"
        case "December":
            param[2] = "Dicembre"
    return f"{param[0]} {param[1]} {param[2]} {param[3]}"

def date_str_it_to_str_en(date: str)->str:
    param = date.split(" ")
    match param[2]:
        case "Gennaio":
            param[2] = "1"
        case "Febbraio":
            param[2] = "2"
        case "Marzo":
            param[2] = "3"
        case "Aprile":
            param[2] = "4"
        case "Maggio":
            param[2] = "5"
        case "Giugno":
            param[2] = "6"
        case "Luglio":
            param[2] = "7"
        case "Agosto":
            param[2] = "8"
        case "Settembre":
            param[2] = "8"
        case "Ottobre":
            param[2] = "10"
        case "Novembre":
            param[2] = "11"
        case "Dicembre":
            param[2] = "12"
    return f"{param[1]}-{param[2]}-{param[3]}"