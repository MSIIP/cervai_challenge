# 数据构建代码说明

该代码用于构建适配 MedM-VL 多模态模型训练格式的数据集。

### 1. 推荐项目结构

```
.
├── script/                  
    ├── build_dataset.py     # 数据集构建代码
    ├── build.sh             # 数据集构建脚本
    ├── split.py             # 切分开发集的样例代码
    ├── templates.json       # 各任务的prompt模板
    ├── test_predict.json    # 样例的提交格式，同时作为测试集标签（标签都是0）
    └── evaluate.py          # 结果评估代码            
└── data/ 
    ├── bounding_box_train.json  # 全部数据的bounding box信息
    ├── train.json           # 全部数据的标签
    ├── train_label.json     # 训练集标签（非定位任务）
    ├── dev_label.json       # 开发集标签（非定位任务）
    ├── train_box.json       # 训练集定位框（定位任务）
    ├── dev_box.json         # 开发集定位框（定位任务）
    ├── dataset/             # 输出数据目录
    └── mri_images/          # 图片数据总目录
        ├── train/            
    	└── test/          
```

推荐的项目代码库结构如上，其中train_label.json、dev_label.json为切分train.json得到的训练集和开发集，train_box.json、dev_box.json为切分bounding_box_train.json的定位信息训练集和开发集。

### 2. build.sh参数信息

| 参数                  | 类型      | 默认值                                     | 描述                                                         |
| --------------------- | --------- | ------------------------------------------ | ------------------------------------------------------------ |
| `--task_type`         | list[str] | `["qd","sl","zjppt","zyzg","positioning"]` | 要构建的任务类型，包括：`qd`、`sl`、`zjppt`、`zyzg`、`positioning` |
| `--train_images_path` | str       | `/data/mri_images/train`                   | 训练图像的根目录                                             |
| `--test_images_path`  | str       | `/data/mri_images/train`                   | 测试图像的根目录                                             |
| `--train_label_path`  | str       | `/data/train_label.json`                   | 非定位任务的训练标签文件路径                                 |
| `--test_label_path`   | str       | `/data/dev_label.json`                     | 非定位任务的测试标签文件路径                                 |
| `--train_box`         | str       | `/data/train_box.json`                     | 定位任务的训练框标注文件路径                                 |
| `--test_box`          | str       | `/data/dev_box.json`                       | 定位任务的测试框标注文件路径                                 |
| `--output_folder`     | str       | `/data/dataset`                            | 输出生成的 JSON 数据集的目录                                 |
| `--sag_image`         | list[int] | `[6]`                                      | 所使用的矢状面图像编号，[5，6]会同时给予模型两张矢状位图像   |
| `--sag_type`          | str       | `""`                                       | 设置为 `seperate` 时，会为每个矢状切片单独构建数据，如sag_image为[5,6,7]时相当于单独执行[5]、[6]、[7]（不会影响定位任务） |
| `--suffix`            | str       | `""`                                       | 输出文件名的后缀                                             |
| `--type_dataset`      | str       | `"both"`                                   | 可选 `train`、`dev`、`test` 或 `both`，指定构建数据集的形式，both代表`train`和`dev` |

### 3. split.py切分开发集代码

该代码简单的划分了训练集和开发集，可以参考修改

### 4. 需要提交的内容

不要提交构建的开发集的答案！

实际的测试集数据是mri_images/test中的图像数据，标签信息在data/test_predict.json中，该文件同时为提交文件的样例，其中所有标签都被设置为了0。

### 5. evaluate.py评估脚本

调用示例如下，需要替换标签位置和预测生成的答案位置

文件格式应和data/test_predict.json一致

python evaluate.py --label_path "../data/test_label.json" --answer_path "./output/answer.json"

### 6. 参考训练数据构建脚本

（1）切分数据，得到训练集和开发集数据

运行python split.py

（2）构建训练集和开发集

曲度和顺列任务数据较少，推荐使用矢状位5、6、7三张图片分别构建训练数据，定位数据同样推荐使用更多数据

```
python build_dataset.py \
    --task_type '["qd","sl","positioning"]' \
    --train_images_path "../data/mri_images/train" \
    --test_images_path "../data/mri_images/train" \
    --train_label_path "../data/train_label.json" \
    --test_label_path "../data/dev_label.json" \
    --train_box "../data/train_box.json" \
    --test_box "../data/dev_box.json" \
    --output_folder "../data/dataset" \
    --sag_image "[5,6,7]" \
    --sag_type "seperate" \
    --suffix "" \
    --type_dataset "train"
```

椎间盘膨突和中央椎管任务数据较多，可以只用正中一张图片构建数据

```
python build_dataset.py \
    --task_type '["zjppt","zyzg"]' \
    --train_images_path "../data/mri_images/train" \
    --test_images_path "../data/mri_images/train" \
    --train_label_path "../data/train_label.json" \
    --test_label_path "../data/dev_label.json" \
    --train_box "../data/train_box.json" \
    --test_box "../data/dev_box.json" \
    --output_folder "../data/dataset" \
    --sag_image "[6]" \
    --sag_type "" \
    --suffix "" \
    --type_dataset "train"
```

（3）构建开发集

```
python build_dataset.py \
    --task_type '["qd","sl","zjppt","zyzg"]' \
    --train_images_path "../data/mri_images/train" \
    --test_images_path "../data/mri_images/train" \
    --train_label_path "../data/train_label.json" \
    --test_label_path "../data/dev_label.json" \
    --train_box "../data/train_box.json" \
    --test_box "../data/dev_box.json" \
    --output_folder "../data/dataset" \
    --sag_image "[6]" \
    --sag_type "" \
    --suffix "" \
    --type_dataset "dev"
```

（4）构建测试集

这里简单使用矢状位正中一张图片

```
python build_dataset.py \
    --task_type '["qd","sl","zjppt","zyzg"]' \
    --train_images_path "../data/mri_images/train" \
    --test_images_path "../data/mri_images/test" \
    --train_label_path "../data/train_label.json" \
    --test_label_path "../data/test_predict.json" \
    --train_box "../data/train_box.json" \
    --test_box "" \
    --output_folder "../data/dataset" \
    --sag_image "[6]" \
    --sag_type "" \
    --suffix "" \
    --type_dataset "test"
```

