import argparse
import json
import os
import re

'''
template.json中保存了样例的prompt，对于MedM-VL模型，每张传入的图像需要一个<image>标签对应
label_map将标签对应为实际的选项
'''

with open("templates.json", "r", encoding="utf-8") as f:
        templates = json.load(f)
    
label_map={
    "qd":{
        0:"A.normal curvature",
        1:"B.straight curvature",
        2:"C.reverse curvature"
    },
    "sl":{
        0:"B.abnormal",
        1:"A.normal"
    },
    "zjppt":{
        0:"A.normal",
        1:"B.bulging",
        2:"C.protrusion",
        3:"D.extrusion"
    },
    "zyzg":{
        0:"A.normal",
        1:"B.mild stenosis",
        2:"C.moderate stenosis",
        3:"D.severe stenosis"
    }
}
#bbox_pattern用于匹配提供的bounding box格式
bbox_pattern = re.compile(r'\((\d+),(\d+)\)\((\d+),(\d+)\)')

#MedM-VL训练数据集格式
'''
数据格式样例:
[{
    "id":"病人id",
    "task":"数据类型",
    "object": "具体部位",
    "answer": "答案，仅用于方便测试结果",
    "conversation":[
                {
                    "from": "human",
                    "value": "<image>\nprompt"
                },
                {
                    "from": "gpt",
                    "value": "答案"
                }
                ],
    "image":["image_path"]},
]
'''

def str2list(v):
    return json.loads(v)
#build_data用于生成单条的数据
def build_data(id,task,path,type,answer,label,sag_image):
    num_map={1:"",2:"two",3:"three"}
    data_person={
        "id":id,
        "task":task,
        "image":path,
        "object":label
    }
    answer_format=""
    if task !="positioning":
        answer_format=label_map[task][answer]
    else:
        match = bbox_pattern.match(answer)
        if match:
            x1, y1, x2, y2 = map(int, match.groups())

        answer_format=f"<ref>{label}<ref><box>({x1},{y1}),({x2},{y2})<box>" 
    data_person["answer"]=answer_format
    conversations=[{"from": "human","value":""}]
    conversation=templates[task]
    if task !="positioning":
        image_num=len(sag_image)
    else:
        image_num=1
    conversation=conversation.replace("[image]","<image>\n"*image_num)   #传入多张image需要多个特殊字符
    conversation=conversation.replace("[image_num]",num_map[image_num])
    '''
    修改了prompt后可以在下面的代码中修改对promt的特殊处理
    '''
    if task=="qd":
        pass
    elif task=="sl":
        pass
    elif task=="zjppt":
        conversation=conversation.replace("[label]",label)
    elif task=="zyzg":
        conversation=conversation.replace("[label]",label)
        if "-" in label:
            conversation=conversation.replace("[object]","intervertebral disc")
        else:
            conversation=conversation.replace("[object]","cervical vertebrae")
    elif task=="positioning":
        conversation=conversation.replace("[label]",label)
        conversation=conversation.replace("[answer]",answer_format)

    conversations[0]["value"]=conversation
    if type=="train":
        conversations.append({
                    "from": "gpt",
                    "value": answer_format
                })
    data_person["conversations"]=conversations
    return data_person  
#build_dataset 用于构建整个数据集
def build_dataset(task,path,label_data,output_folder,type,sag_image,sag_type,suffix):
    all_people_data = []
    for patient_dict in label_data:
        id=patient_dict["id"]
        image_path=[]
        for sag in sag_image:
            image_path.append(os.path.join(path,id+"/sag/"+str(sag)+".png"))
        if task !="positioning":
            answer=patient_dict[task]
        if task in ["qd","sl"]:
            data=build_data(id,task,image_path,type,answer,"",sag_image)
            all_people_data.append(data)
        elif task=="zjppt":
            for index,label_ in enumerate(["2-3","3-4","4-5","5-6","6-7"]):
                label=f"C{label_[0]}-C{label_[-1]}"
                image_path_=image_path+[os.path.join(path,id+"/tra/"+label_+".png")]
                answer_=answer[index]
                data=build_data(id,task,image_path_,type,answer_,label,sag_image)
                all_people_data.append(data)
        elif task=="zyzg":
            for index,label_ in enumerate(["2","2-3","3","3-4","4","4-5","5","5-6","6","6-7","7"]):
                if "-" in label_:
                    label=f"C{label_[0]}-C{label_[-1]}"
                else:
                    label=f"C{label_}"
                image_path_=image_path+[os.path.join(path,id+"/tra/"+label_+".png")]
                answer_=answer[index]
                data=build_data(id,task,image_path_,type,answer_,label,sag_image)
                all_people_data.append(data)
        elif task=="positioning":
            for index,label_ in enumerate(["2","3","4","5","6","7"]):
                for sag in sag_image:
                    label=f"C{label_}"
                    image_path_=[os.path.join(path,id+"/sag/"+str(sag)+".png")]
                    answer=patient_dict[label][sag-5]
                    data=build_data(id,task,image_path_,type,answer,label,sag_image)
                    all_people_data.append(data)
    output_path = os.path.join(output_folder, f"{task}_{type}{'_' + suffix if suffix else ''}.json")
    if sag_type != "seperate":
        with open(output_path,'w') as json_file:
            json.dump(all_people_data, json_file, ensure_ascii=False, indent=4)    
    else:
        return all_people_data
             
         
            
def main():
    parser = argparse.ArgumentParser(description="Build MedM-VL train dataset")
    parser.add_argument('--task_type', type=str2list,default='["qd","sl","zjppt","zyzg","positioning"]', help="List of datatype in JSON list format")
    parser.add_argument('--train_images_path', type=str, default='/data/mri_images/train', help="Path to the images")
    parser.add_argument('--test_images_path', type=str, default='/data/mri_images/test', help="Path to the images")
    parser.add_argument('--train_label_path', type=str, default = '/data/train.json', help="Path to the train JSON file")
    parser.add_argument('--test_label_path', type=str, default = '/data/test.json', help="Path to the test JSON file")
    parser.add_argument('--train_box', type=str, default = '/data/train_box.json', help="Path to the train bounding box JSON file")
    parser.add_argument('--test_box', type=str, default = '/data/test_box.json', help="Path to the test bounding box JSON file")
    parser.add_argument('--output_folder', type=str, default = '/data', help="Path to output dataset")
    parser.add_argument('--sag_image', type=str2list,default='[6]', help="List of sag image")
    parser.add_argument('--sag_type', type=str, default = '', help="whether to seperate the sag image")
    parser.add_argument('--suffix', type=str, default = '', help="suffix of data")
    parser.add_argument('--type_dataset', type=str, default = 'both', help="Make train or test dataset or both")
    args = parser.parse_args()
    task_type=args.task_type
    with open(args.train_label_path, 'r') as f:
        train_label_data = json.load(f)
    with open(args.test_label_path, 'r') as f:
        test_label_data = json.load(f)
    if "positioning" in task_type:
        with open(args.train_box, 'r') as f:
            train_box = json.load(f)
        with open(args.test_box, 'r') as f:
            test_box = json.load(f)
    train_path=args.train_images_path
    train_images_path = os.path.abspath(train_path)
    test_path=args.test_images_path
    test_images_path = os.path.abspath(test_path)
    sag_image=args.sag_image
    type_dataset = args.type_dataset
    output_folder = args.output_folder
    sag_type = args.sag_type
    suffix=args.suffix
    for task in task_type:
        if task !="positioning":
            if sag_type== "seperate":
                if type_dataset =="train" or type_dataset =="both":
                    train_data=[]
                    output_path = os.path.join(output_folder, f"{task}_train{'_' + suffix if suffix else ''}.json")
                    for sag in sag_image:
                        train_data.extend(build_dataset(task,train_images_path,train_label_data,output_folder,"train",[sag],sag_type,suffix))
                    with open(output_path,'w') as json_file:
                        json.dump(train_data, json_file, ensure_ascii=False, indent=4)  
                if type_dataset =="dev" or type_dataset =="both":
                    test_data=[]
                    output_path = os.path.join(output_folder, f"{task}_dev{'_' + suffix if suffix else ''}.json")
                    for sag in sag_image:
                        test_data.extend(build_dataset(task,test_images_path,test_label_data,output_folder,"dev",[sag],sag_type,suffix))
                    with open(output_path,'w') as json_file:
                        json.dump(test_data, json_file, ensure_ascii=False, indent=4)    
                if type_dataset =="test":
                    test_data=[]
                    output_path = os.path.join(output_folder, f"{task}_test{'_' + suffix if suffix else ''}.json")
                    for sag in sag_image:
                        test_data.extend(build_dataset(task,test_images_path,test_label_data,output_folder,"test",[sag],sag_type,suffix))
                    with open(output_path,'w') as json_file:
                        json.dump(test_data, json_file, ensure_ascii=False, indent=4)    
            else:
                if type_dataset =="train" or type_dataset =="both":
                    build_dataset(task,train_images_path,train_label_data,output_folder,"train",sag_image,sag_type,suffix)
                if type_dataset =="dev" or type_dataset =="both":
                    build_dataset(task,test_images_path,test_label_data,output_folder,"dev",sag_image,sag_type,suffix)
                if type_dataset =="test":
                    build_dataset(task,test_images_path,test_label_data,output_folder,"test",sag_image,sag_type,suffix)
            
        else:
            if type_dataset !="dev":
                build_dataset(task,train_images_path,train_box,output_folder,"train",sag_image,"",suffix)
            if type_dataset !="train":
                build_dataset(task,test_images_path,test_box,output_folder,"dev",sag_image,"",suffix)

if __name__ == "__main__":
    main()