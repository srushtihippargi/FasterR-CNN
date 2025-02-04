This repository implements **Faster R-CNN**, a two-stage anchor-based object detector with **Region Proposal Networks (RPN)** and **Fast R-CNN** for precise object detection.

## Dataset
We use the **props dataset** from the **University of Michigan's PROGRESS Lab**, led by **Professor Chad Jenkins**. Below is an example of processed dataset images.

## Model Architecture
- **Stage 1: Region Proposal Network (RPN)** generates object proposals.
- **Stage 2: Fast R-CNN** refines proposals and predicts class labels.

## Training Pipeline
1. **Anchor Generation:** Generates anchors at FPN feature map locations.
2. **Anchor-GT Matching:** Assigns GT boxes to anchors using IoU thresholds.
3. **Box Regression Deltas:** Transforms anchors into predicted bounding boxes.

## Results
Intermediate visualizations (anchors, GT boxes, bounding box predictions) are available in the **Jupyter notebooks**. Below is the final result from the trained two-stage detector.

![Screenshot from 2025-02-02 18-07-58](https://github.com/user-attachments/assets/b43df29b-1339-4e36-ac50-fec320752658)![Screenshot from 2025-02-02 18-08-19](https://github.com/user-attachments/assets/211294fa-cc6d-431e-bbc9-6eb756c225a7)

