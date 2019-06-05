### Abstract

In this paper we exploit knowledge of class hierarchies to aid the training of semantic segmentation convolutional neural networks. We do not modify the architecture of the network itself, but rather propose to compute a loss that is a summation of classification losses at different levels of class abstraction. This allows the network to differentiate serious errors (the wrong superclass) from minor errors (correct superclass but incorrect finescale class) and to learn visual features that are shared between classes that belong to the same superclass. The method is straightforward to implement (we provide a PyTorch implementation that can be used with any existing semantic segmentation network) and we show that it yields performance improvements (faster convergence, better mean IOU) relative to training with a flat class hierarchy and exactly the same CNN architecture. We provide results for the Helen face segmentation dataset and Mapillary Vistas road scene segmentation dataset.

![HSS_overview](imgs/HSSOverview.pdf)