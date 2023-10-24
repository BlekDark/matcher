import json


#  результат матча
file_name1 = "processed_data.json"
#  исходники для матчера
file_name2 = "input_data.json"
with open(file_name1, 'r+', encoding='utf-8') as file1:
    with open(file_name2, 'r+', encoding='utf-8') as file2:
        file1 = json.load(file1)
        file2 = json.load(file2)
        for i in ["mismatched_pairs"]:

            for mismatch_pair in file1[i]:
                # print(i["overall_similarity"])
                if int(mismatch_pair["overall_similarity"]) > 90:
                    event_id1 = mismatch_pair["event1"]["event_id"]
                    event_id2 = mismatch_pair["event2"]["event_id"]
                    sport = mismatch_pair["sport"]
                    date_event = mismatch_pair["date"]
                    for key_file2, date_events in enumerate(file2):
                        # if flag_event1 and flag_event2:
                        #     break
                        if date_event != date_events["date"]:
                            continue
                        data_array = date_events["data"]
                        for key, event_serch in enumerate(data_array):
                            if event_id2 == event_serch["event2"]["event_id"]:
                                print(event_id2)
                                del file2[key_file2]["data"][key]
                                mismatch_pair["event2"]["true_pair"] = event_serch["event1"]

        with open('new_result.json', 'w') as fp:
            json.dump(file2, fp)
# unmatched_results, mismatched_pairs