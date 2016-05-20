# Mastertools

Collection of useful python scripts.

## Evaluate detections

Creates two output files `good_list` and `bad_list`,
where `good_list` contains images where more than one box was predicted correctly.
`bad_list` contains images where no boxes were correctly predicted.

```
python evaluate_detections.py recall <recall-output> <ground-truth-list>
```

or

```
python evaluate_detections.py valid <predicted-boxes> <ground-truth-list>
```

## Image View

Open one image to inspect its labels:
```
python imageview.py data/images/image.jpg
```

Open a folder to browse all its images:
```
python imageview.py data/images/
```

Open a list of images from a txt-file:
```
python imageview.py good_list.txt
```

### Browse good/bad detections:
This is easier than using `evaluate_detections` directly.

```
python imageview.py good <weights-name> <ground-truths>
python imageview.py bad <weights-name> <ground-truths>
```

Example:
```
python imageview.py good exp_wide_graybg_manymodel kitti
```
