import argparse
import json
from sklearn.metrics import f1_score

def compute_metrics(test_label, random_answer):
    id_to_label = {item['id']: item for item in test_label}
    id_to_pred = {item['id']: item for item in random_answer}
    
    qd_true, qd_pred = [], []
    sl_true, sl_pred = [], []
    zjppt_true, zjppt_pred = [], []
    zyzg_true, zyzg_pred = [], []

    for key in id_to_label.keys():
        if key in id_to_pred:
            qd_true.append(id_to_label[key]['qd'])
            qd_pred.append(id_to_pred[key]['qd'])

            sl_true.append(id_to_label[key]['sl'])
            sl_pred.append(id_to_pred[key]['sl'])

            zjppt_true.extend(id_to_label[key]['zjppt'])
            zjppt_pred.extend(id_to_pred[key]['zjppt'])

            zyzg_true.extend(id_to_label[key]['zyzg'])
            zyzg_pred.extend(id_to_pred[key]['zyzg'])

    qd_f1 = f1_score(qd_true, qd_pred, average="macro")  
    sl_f1 = f1_score(sl_true, sl_pred, labels=[0], average="macro") 
    zjppt_f1 = f1_score(zjppt_true, zjppt_pred, average="macro") 
    zyzg_f1 = f1_score(zyzg_true, zyzg_pred, average="macro")  

    final_score = (qd_f1 * 0.2) + (sl_f1 * 0.2) + (zjppt_f1 * 0.3) + (zyzg_f1 * 0.3)
    return final_score

def main():
    parser = argparse.ArgumentParser(description="Evaluate prediction file against labels")
    parser.add_argument('--label_path', type=str, required=True, help="Path to the label JSON file")
    parser.add_argument('--answer_path', type=str, required=True, help="Path to the prediction JSON file")
    args = parser.parse_args()

    with open(args.label_path, 'r') as f:
        test_label = json.load(f)

    with open(args.answer_path, 'r') as f:
        random_answer = json.load(f)

    score = compute_metrics(test_label, random_answer)
    print("Final Score:", score)

if __name__ == "__main__":
    main()