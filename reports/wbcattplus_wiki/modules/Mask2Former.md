# Mask2Former

> A unified transformer-based model for panoptic, instance, and semantic segmentation.

Mask2Former is a transformer-based architecture that treats segmentation as a set prediction problem. It uses a backbone to extract features, a pixel decoder to generate multi-scale features, and a transformer decoder with learnable queries to predict binary masks and class labels. The model supports semantic, instance, and panoptic segmentation tasks simultaneously.

## Files

### `mask2former/config.py`

Defines configuration parameters for MaskFormer2, including model architecture, loss weights, and training settings.

- `add_maskformer2_config` (function) - Registers MaskFormer2 configuration options into the Detectron2 CfgNode system.

### `mask2former/modeling/meta_arch/mask_former_head.py`

Implements the main segmentation head that combines pixel decoder and transformer decoder.

- `MaskFormerHead` (class) - Main segmentation head that processes multi-scale features through a transformer decoder to produce mask predictions.

### `mask2former/modeling/pixel_decoder/msdeformattn.py`

Implements MSDeformAttnPixelDecoder, which uses deformable attention to aggregate multi-scale features.

- `MSDeformAttnPixelDecoder` (class) - Pixel decoder using multi-scale deformable attention to enhance feature representation.
- `MSDeformAttnTransformerEncoderOnly` (class) - Transformer encoder for processing multi-scale features with deformable attention.

### `mask2former/modeling/transformer_decoder/mask2former_transformer_decoder.py`

Implements MultiScaleMaskedTransformerDecoder, the core transformer decoder for mask prediction.

- `MultiScaleMaskedTransformerDecoder` (class) - Transformer decoder that predicts masks using learnable queries and multi-scale features.

### `mask2former/modeling/criterion.py`

Defines the loss function for training, including classification, mask, and dice losses.

- `SetCriterion` (class) - Computes loss between predictions and ground truth using Hungarian matching.
- `HungarianMatcher` (class) - Performs optimal assignment between predictions and ground truth objects.

### `mask2former/maskformer_model.py`

Defines the main MaskFormer model architecture that integrates backbone, head, and criterion.

- `MaskFormer` (class) - Main model class that coordinates backbone, segmentation head, and loss computation.

### `mask2former/data/dataset_mappers/mask_former_semantic_dataset_mapper.py`

Preprocesses images and annotations for semantic segmentation training.

- `MaskFormerSemanticDatasetMapper` (class) - Applies augmentations and transforms to prepare data for semantic segmentation.

### `mask2former/data/datasets/register_pbcseg_full.py`

Registers the custom medical WBC dataset for semantic segmentation.

- `register_all_ade20k_full` (function) - Registers the PBCseg dataset with Detectron2's DatasetCatalog.

### `datasets/prepare_medical_sem_seg.py`

Preprocesses the medical WBC dataset into Detectron2 format.

- `__main__` (script) - Copies images and masks from raw data into train/val/test splits.

### `mask2former/modeling/pixel_decoder/ops/modules/ms_deform_attn.py`

Implements the Multi-Scale Deformable Attention module with CUDA support.

- `MSDeformAttn` (class) - CUDA-accelerated deformable attention mechanism for efficient multi-scale feature aggregation.

### `train_net.py`

Main training script that sets up and runs the training loop.

- `Trainer` (class) - Custom training class extending Detectron2's DefaultTrainer for MaskFormer.

### `demo/demo.py`

Provides a command-line interface for running inference on images.

- `VisualizationDemo` (class) - Handles image inference and visualization of segmentation results.

## Key Concepts

- **Set Prediction**: Mask2Former treats segmentation as predicting a fixed set of binary masks, each associated with a class label. This avoids traditional pixel-wise classification and enables end-to-end learning.
- **Learnable Queries**: The model uses learnable query vectors that act as object probes. The transformer decoder attends to image features through these queries to predict masks.
- **Multi-Scale Deformable Attention**: MSDeformAttn efficiently aggregates features from multiple resolution levels by learning adaptive sampling locations, improving feature representation for segmentation.
- **Hungarian Matching**: During training, predictions are matched to ground truth using the Hungarian algorithm to establish optimal one-to-one correspondence for loss computation.
- **Unified Architecture**: The same model can perform semantic, instance, and panoptic segmentation by enabling different output heads, sharing the same backbone and transformer decoder.

## Internal Relationships

- `mask2former/maskformer_model.py` → `mask2former/modeling/meta_arch/mask_former_head.py`: MaskFormer model instantiates MaskFormerHead for segmentation predictions.
- `mask2former/modeling/meta_arch/mask_former_head.py` → `mask2former/modeling/pixel_decoder/msdeformattn.py`: MaskFormerHead uses MSDeformAttnPixelDecoder to process backbone features.
- `mask2former/modeling/meta_arch/mask_former_head.py` → `mask2former/modeling/transformer_decoder/mask2former_transformer_decoder.py`: MaskFormerHead uses MultiScaleMaskedTransformerDecoder for mask prediction.
- `mask2former/modeling/meta_arch/mask_former_head.py` → `mask2former/modeling/criterion.py`: MaskFormerHead computes losses using SetCriterion during training.
- `train_net.py` → `mask2former/data/dataset_mappers/mask_former_semantic_dataset_mapper.py`: Training script uses dataset mapper to preprocess data for semantic segmentation.
- `mask2former/data/datasets/register_pbcseg_full.py` → `datasets/prepare_medical_sem_seg.py`: Dataset registration expects data prepared by the medical segmentation script.
- `mask2former/modeling/pixel_decoder/msdeformattn.py` → `mask2former/modeling/pixel_decoder/ops/modules/ms_deform_attn.py`: MSDeformAttnPixelDecoder imports MSDeformAttn module for deformable attention.
