import csv
import json
from uuid import uuid4
import openpyxl


def split_event_name(event_name):
    if " vs " in event_name:
        return event_name.split(" vs ", 1)
    elif " - " in event_name:
        return event_name.split(" - ", 1)
    else:
        return None, None

# # функция поиска юникода
# def has_unicode(input_str):
#     encoded_str = input_str.encode('unicode-escape')
#     return b'\\u' in encoded_str

def decode_unicode(text):
    return text.encode('utf-8').decode('unicode_escape')

def process_data(filename):
    # with open(filename, encoding='utf-8') as file:
    #     reader_object = csv.reader(file, delimiter=",")
    result_dict = {}

    wb = openpyxl.load_workbook(filename)
    sheet = wb.active
    i = 1
    count_unicode_skip = 0
    for row in sheet.iter_rows(values_only=True):
        if not any(row):
            continue
        # print(i)
        i += 1
        date = str(row[0])
        sport = row[2]
        bk1_league = row[3]
        bk2_league = row[4]
        bk1_game = row[5]
        bk2_game = row[6]

        unicode = False
        decoded_game = decode_unicode(bk1_game)
        decoded_league = decode_unicode(bk1_league)

        if (bk1_game != decoded_game) or (bk1_league != decoded_league):
            unicode = True

        decoded_game = decode_unicode(bk2_game)
        decoded_league = decode_unicode(bk2_league)

        if (bk2_game != decoded_game) or (bk2_league != decoded_league):
            unicode = True

        if unicode:
            count_unicode_skip += 1
            print(count_unicode_skip)
            continue

        event_name_1 = bk1_game
        event_name_2 = bk2_game

        # замена pinnacle
        if bk1_league == "pinnacle":
            bk1_league = bk2_league
        if bk2_league == "pinnacle":
            bk2_league = bk1_league

        team1_1, team2_1 = split_event_name(event_name_1)
        team1_2, team2_2 = split_event_name(event_name_2)

        if team1_1 is None or team1_2 is None:
            continue

        is_cyber = 1 if 'esports' in sport else 0

        event1 = {
            "event_id": str(uuid4()),
            "event_name": event_name_1,
            "league": bk1_league,
            "team1": team1_1,
            "team2": team2_1
        }

        event2 = {
            "event_id": str(uuid4()),
            "event_name": event_name_2,
            "league": bk2_league,
            "team1": team1_2,
            "team2": team2_2
        }

        game_data = {
            "sport": sport,
            "event1": event1,
            "event2": event2,
            "is_cyber": is_cyber
        }

        if date not in result_dict:
            result_dict[date] = {"date": date, "data": []}
        result_dict[date]["data"].append(game_data)
    print(count_unicode_skip)
    print(i)
    result = list(result_dict.values())

    return result


def main():
    result = process_data("input_data.xlsx")
    with open('input_data.json', 'w') as fp:
        json.dump(result, fp)


if __name__ == "__main__":
    main()
