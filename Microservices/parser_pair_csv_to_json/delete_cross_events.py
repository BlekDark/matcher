import json


def decode_unicode(text):
    return text.encode('utf-8').decode('unicode_escape')


def main():
    with open('input_data.json', 'r', encoding='utf-8') as input_file:
        data = json.load(input_file)

    with open('EventIdListForDel.txt', 'r') as id_file:
        events_id = id_file.read()
        events_id = events_id[1:-1]
        events_id = events_id.split(', ')
        print(len(events_id))

    total_events = 0
    deleted_events = 0
    deleted_unicode_events = 0
    deleted_cross_events = 0

    for item in data:
        events = item['data']
        total_events += len(events)

        updated_events = []
        for event in events:
            unicode = False
            original_event_name = event['event1']['event_name']
            original_league = event['event1']['league']

            decoded_event_name = decode_unicode(event['event1']['event_name'])
            decoded_league = decode_unicode(event['event1']['league'])
            if (original_event_name != decoded_event_name) or (original_league != decoded_league):
                unicode = True

            original_event_name = event['event2']['event_name']
            original_league = event['event2']['league']

            decoded_event_name = decode_unicode(event['event2']['event_name'])
            decoded_league = decode_unicode(event['event2']['league'])
            if (original_event_name != decoded_event_name) or (original_league != decoded_league):
                unicode = True

            # if unicode:
            #     print(original_event_name)
            #     print(decoded_event_name)
            #     print('Unicode!')

            if (event['event1']['event_id'] not in events_id) and not unicode:
                updated_events.append(event)
            else:
                deleted_events += 1
                if event['event1']['event_id'] in events_id:
                    deleted_cross_events += 1
                else:
                    deleted_unicode_events += 1

        item['data'] = updated_events

    with open('input_data_new.json', 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=True)

    remaining_events = total_events - deleted_events

    print(f"Total events: {total_events}")
    print(f"Deleted events (including unicode): {deleted_events}")
    print(f"Deleted crossed events: {deleted_cross_events}")
    print(f"Deleted events with unicode: {deleted_unicode_events}")
    print(f"Remaining events: {remaining_events}")


if __name__ == '__main__':
    main()
