import json
#  результат матча
file_name1 = "processed_data (1).json"
#  исходники для матчера
file_name2 = "input_data.json"
with open(file_name1, 'r+', encoding='utf-8') as file1:
    with open(file_name2, 'r', encoding='utf-8') as file2:
        print(type(file1))
        file1 = json.load(file1)
        file2 = json.load(file2)
        for i in ["mismatched_pairs"]:

            for mismatch_pair in file1[i]:
                event_id1 = mismatch_pair["event1"]["event_id"]
                event_id2 = mismatch_pair["event2"]["event_id"]
                sport = mismatch_pair["sport"]
                date_event = mismatch_pair["date"]
                flag_event1 = 0
                flag_event2 = 0
                for date_events in file2:
                    if flag_event1 and flag_event2:
                        break
                    if date_event != date_events["date"]:
                        continue
                    for event_serch in date_events["data"]:
                        if event_serch["sport"] != sport:
                            continue
                        if event_id1 == event_serch["event1"]["event_id"]:
                            flag_event1 = 1
                            mismatch_pair["event1"]["true_pair"] = event_serch["event2"]
                        if event_id2 == event_serch["event2"]["event_id"]:
                            flag_event2 = 1
                            mismatch_pair["event2"]["true_pair"] = event_serch["event1"]

        with open('new_result.json', 'w') as fp:
            json.dump(file1, fp)
# unmatched_results, mismatched_pairs