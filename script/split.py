import json

with open("../data/train.json", 'r') as f:
    label_data = json.load(f)
with open("../data/bounding_box_train.json", 'r') as f:
    box_data = json.load(f)

box_dict = {item["id"]: item for item in box_data}

train_label = label_data[:320]
dev_label = label_data[320:]

train_box = [box_dict[item["id"]] for item in train_label if item["id"] in box_dict]
dev_box = [box_dict[item["id"]] for item in dev_label if item["id"] in box_dict]

with open("../data/train_label.json", 'w') as json_file:
    json.dump(train_label, json_file, ensure_ascii=False, indent=4)
with open("../data/dev_label.json", 'w') as json_file:
    json.dump(dev_label, json_file, ensure_ascii=False, indent=4)
with open("../data/train_box.json", 'w') as json_file:
    json.dump(train_box, json_file, ensure_ascii=False, indent=4)
with open("../data/dev_box.json", 'w') as json_file:
    json.dump(dev_box, json_file, ensure_ascii=False, indent=4)
