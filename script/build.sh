#!/bin/bash

python build_dataset.py \
    --task_type '["qd","sl"]' \
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
    --type_dataset "both"