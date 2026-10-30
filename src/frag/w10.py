T = dict(
id='w10', week=10, tab='Object detection', title='Object detection and open-vocabulary perception',
lead='Predict a variable-size set of boxes with labels and scores: two-stage, one-stage and transformer detectors, how they are trained, how IoU, precision, recall and AP measure them, and how language lets a detector find classes it was never trained on.',
docs=[dict(path='notes/Week10.pdf', title='Week 10 lecture: Object detection and open-vocabulary perception', pages=94),
      dict(path='notes/papers/DETR.pdf', title='DETR paper (Carion et al., ECCV 2020)', pages=26)],
prac=None,
eli5=[
 ('How many objects?', 'A classifier answers one question per photo; a detector must say how many things there are and where. That variable count is what makes detection hard.', None),
 ('IoU', 'Lay two cut-out rectangles on top of each other: IoU is the overlapping area divided by the total area covered. 1 = perfect match, 0 = no overlap.', None),
 ('NMS vs DETR', 'Old detectors shout many guesses and then delete near-duplicates (NMS). DETR gives each of its 100 “seats” one object, so duplicates are trained away.', None),
 ('Open vocabulary', 'Instead of a fixed menu of 80 dishes, you describe what you want in words (“the red mug”) and the detector looks for it.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 190" role="img" aria-label="Precision-recall curve with area under it as AP, and IoU of two boxes">
<rect class="sk" x="20" y="40" width="80" height="80"/><rect class="bx" x="60" y="80" width="80" height="80" style="fill:none;stroke:var(--eli);stroke-width:2"/>
<rect class="fa" x="60" y="80" width="40" height="40" style="opacity:.55"/>
<text x="20" y="30" class="sm">IoU = overlap / union</text><text x="20" y="182" class="sm">4×4 boxes offset by 2: 4/28 = 0.14</text>
<g transform="translate(220,20)">
<path class="ln" d="M0 0 V150 H270"/><text x="-14" y="8" class="sm">1</text><text x="-14" y="150" class="sm">0</text><text x="265" y="165" class="sm">1</text>
<text x="100" y="168" class="sm">recall</text><text x="-12" y="80" class="sm" transform="rotate(-90 -12 80)">precision</text>
<path class="sk" d="M0 0 H108 V37 H162 V64 H216 V150 H0 Z" style="opacity:.8"/>
<path class="ac" d="M0 0 H108 L108 50 L108 37 L162 37 L162 60 L162 64 L216 64 L216 150"/>
<text x="20" y="110">AP = shaded area</text><text x="20" y="128" class="sm">(precision made monotone)</text>
</g></svg>''',
svgcap='Left: IoU decides whether a box counts as a hit. Right: sweeping the confidence threshold traces a precision–recall curve; AP is the area under its monotone envelope (the worked example below gives AP = 0.664).',
videos=['RgQbweTwrkU', '-DTztxwUYjA'],
body=r'''
<div class="sub"><h3>1. The detection task</h3>
<p>Input an image; output a <b>set</b> of boxes \((x_{min}, y_{min}, x_{max}, y_{max})\), each with a class-score distribution [[p9]] [[p10]]. The key challenge [[p13]]: the <b>number of outputs depends on the image</b>, unlike classification or segmentation. Candidate objects come from [[p14]]:</p>
<ol><li><b>two-stage</b> detectors: anchors + a region proposal network;</li><li><b>anchor-based one-stage</b>: predefined reference boxes;</li><li><b>anchor-free / point-based</b>: every image location predicts;</li><li><b>transformers</b>: learned object queries.</li></ol></div>

<div class="sub"><h3>2. Two-stage detectors (Faster R-CNN)</h3>
<p>A reliable, modular baseline that is easy to fine-tune (Detectron2, MMDetection, TorchVision). Descendants: Mask R-CNN, Cascade R-CNN, Sparse R-CNN [[p17]].</p>
<p><b>Stage 1</b>: a dense grid of <b>anchors</b> at each location (3 scales × 3 aspect ratios). The RPN predicts an <b>objectness</b> score and a box refinement for each; keep the top-N (e.g. 1,000) proposals [[p18]]–[[p21]]. <b>Stage 2</b>: <b>RoI pooling</b> turns regions of different sizes into fixed-size features [[p24]]; the head predicts class probabilities (including background) and refines the box [[p26]].</p>
<p><b>Post-processing</b> [[p32]]: drop low-confidence predictions, then remove duplicates with <b>non-maximum suppression</b> (keep the highest-scoring box and suppress same-class boxes with IoU above a threshold). DETR-style detectors generally need no NMS.</p></div>

<div class="sub"><h3>3. One-stage and point-based detectors</h3>
<p>These go straight from image to detections [[p35]]. <b>Anchor-based</b>: SSD, RetinaNet, EfficientDet (less dominant now). <b>Point-based</b>: every pixel predicts class scores and box geometry: FCOS, CornerNet, CenterNet; currently YOLOv8, YOLO11, RTMDet.</p>
<p><b>FCOS</b> [[p37]]–[[p42]] is anchor-free and proposal-free, so it has no anchor hyperparameters (which are sensitive) and no anchor-overlap computation. Per pixel it predicts class scores and a <b>centerness</b> score; their product gives centerness-aware scores. It regresses the box from each pixel, then thresholds away low-confidence pixels.</p></div>

<div class="sub"><h3>4. Transformer detectors (DETR)</h3>
<p>Predict a <b>fixed-size set</b> of object hypotheses directly instead of many candidates cleaned up afterwards [[p44]].</p>
<div class="tw"><table><tr><th>One-stage</th><th>DETR-style</th></tr><tr><td>anchors / points</td><td>learned object queries</td></tr><tr><td>thousands of candidates</td><td>small fixed set of queries</td></tr><tr><td>many duplicates</td><td>one-to-one predictions</td></tr><tr><td>requires NMS</td><td>typically no NMS</td></tr><tr><td>local dense prediction</td><td>global attention / set prediction</td></tr></table></div>
<p class="note">Comparison from [[p46]].</p>
<p>The original DETR had slow training convergence, trouble with small objects and costly global attention [[p47]]. Fixes: <b>Deformable DETR</b> (sparse attention, multi-scale, faster convergence), <b>DINO</b> (better query initialisation, denoising training) and <b>RT-DETR</b> (real-time, still NMS-free).</p></div>

<div class="sub"><h3>5. Training detectors</h3>
<p>Detection = <b>classification + localisation + assignment</b> (which prediction is responsible for which ground-truth object) [[p49]]. Losses:</p>
<ul><li><b>Classification</b> [[p50]]: CE (softmax), BCE (sigmoid), or <b>focal loss</b> for heavy imbalance.</li>
<li><b>Box regression</b> [[p51]]: L1 on coordinates, or IoU-based losses (1 − IoU, GIoU, DIoU, CIoU). Coordinate losses ask whether the numbers are close; IoU losses ask whether the boxes overlap well.</li>
<li><b>Objectness</b> [[p52]]: is there any object here (RPN, YOLO)?</li></ul>
<p><b>Class imbalance</b> [[p53]]: thousands of candidates, mostly background, and easy negatives dominate the loss. Remedies: sampling, focal loss (down-weights easy, correct examples), DETR’s one-to-one matching. Datasets [[p54]]: COCO (80 classes), Objects365 (365 classes, 2M images, 30M boxes), OpenImages V7 (600 classes, 15.9M boxes), LVIS (1200+ classes, long tail), nuImages (driving).</p></div>

<div class="sub"><h3>6. Evaluating detectors: IoU, precision, recall, AP</h3>
<p>\(\mathrm{IoU} = \frac{|A\cap B|}{|A\cup B|} = \frac{I}{|A|+|B|-I}\). A detection is a <b>true positive</b> if IoU ≥ threshold, the class is correct <b>and</b> that ground-truth object was not already matched by a higher-scoring detection; every other detection is a <b>false positive</b>; every unmatched ground-truth object is a <b>false negative</b> [[p59]]–[[p62]].</p>
<div class="ex"><b>Worked example (practice Q31).</b> Box areas 60 and 50, intersection 30: IoU = 30/(60+50−30) = 30/80 = <b>0.375</b>. Boxes (0,0,4,4) and (2,2,6,6): I = 4, U = 16+16−4 = 28 → <b>0.143</b>.</div>
<div class="widget" data-w="iou"></div>
<p>\(\text{Precision} = \frac{TP}{TP+FP}\) (what fraction of detections are right) and \(\text{Recall} = \frac{TP}{TP+FN}\) (what fraction of objects were found). Both depend on the confidence threshold <i>and</i> the IoU threshold [[p66]]. Sweeping the confidence threshold traces a PR curve. <b>AP</b> = area under the PR curve for one class at one IoU threshold (COCO samples it at 101 recall values). <b>mAP</b> = mean AP over classes, \(\frac1k\sum AP_i\) [[p67]]. COCO “mAP” also averages over IoU thresholds 0.5:0.95 [[p68]].</p>
<div class="ex"><b>Worked example (AP).</b> 5 ground-truth objects; detections sorted by confidence are TP, TP, FP, TP, FP, FP, TP. Precision: 1, 1, 0.667, 0.75, 0.6, 0.5, 0.571. Recall: 0.2, 0.4, 0.4, 0.6, 0.6, 0.6, 0.8. Making precision monotone (max to the right) and summing over recall steps: 0.2·1 + 0.2·1 + 0.2·0.75 + 0.2·0.571 = <b>AP = 0.664</b>. One object was never found, so recall stops at 0.8.</div>
<div class="widget" data-w="pr"></div>
<p><b>Caveats for robotics</b> [[p69]] [[p70]]: AP summarises <i>many</i> thresholds, while a robot runs at one (practice Q32). mAP punishes low recall strongly. The IoU threshold may be stricter than the task needs. mAP weights every class equally, whatever its real importance. Also check recall at a fixed false-positive rate, latency, distance-dependent recall and safety-critical classes. Choose the threshold for the application [[p91]]: high recall for safety, high precision if false alarms trigger costly actions.</p></div>

<div class="sub"><h3>7. Open set and open vocabulary</h3>
<p>Closed-set training uses a fixed class list (COCO: 80) [[p73]]. In deployment, novel objects appear and are often <b>labelled as a known class</b> [[p75]].</p>
<ul><li><b>Closed set</b>: choose among known classes.</li><li><b>Open set</b>: detect known classes and flag novel objects as <i>unknown</i>.</li><li><b>Open vocabulary</b>: detect objects described by text, beyond the trained list [[p77]].</li></ul>
<p>How: <b>CLIP</b> aligns image and text embeddings, so similarity answers “does this image match this concept?”. Detection also needs “where?”, so propose regions or queries and score each against text embeddings; the head becomes language-conditioned [[p80]]–[[p83]]. <b>Grounding DINO</b> builds on DETR/DINO, aligns queries to phrases, and lets you change the vocabulary at inference [[p84]]. Prompts matter [[p85]]: wording changes which objects are found, their labels and confidences, and more specific prompts aren’t always better. Limits [[p86]]: visual difficulty (small, occluded, domain shift), language difficulty (synonyms, fine-grained classes), attributes and state (“the empty cup”), relations and affordances (“something I can grasp”). <b>Open vocabulary ≠ open-ended reasoning.</b> Others: OWL-ViT/OWLv2, GLIP, YOLO-World, YOLOE [[p87]].</p>
<p>Practical advice [[p89]]: start simple with a strong pretrained baseline (Faster R-CNN) and fine-tune; evaluate the errors that matter.</p>
<div class="exam"><b>Exam angle.</b> Q31 (IoU calculation), Q32 (AP across thresholds vs one operating point), Q27 (threshold vs misses). Expect TP/FP/FN counting with an IoU threshold and duplicates, a precision/recall calculation, and why DETR needs no NMS.</div></div>
''',
paper=dict(title='End-to-End Object Detection with Transformers: DETR (Carion et al., ECCV 2020)', sixty=r'''
<p><b>Problem.</b> Detectors depend on hand-designed parts: anchors, proposal heuristics and NMS. DETR treats detection as <b>direct set prediction</b>.</p>
<p><b>Key idea</b> (Fig. 2, Sec. 3 [[P:p6]]): a CNN backbone (ResNet-50), a transformer encoder and a decoder with <b>N = 100 learned object queries</b>. A shared FFN turns each query into a class (including ∅ “no object”) and a box (centre, height, width). Training uses <b>Hungarian matching</b>: find the permutation that minimises \(\sum_i \mathcal L_{match}\), where \(\mathcal L_{match} = -\mathbb 1_{c_i\neq\varnothing}\hat p(c_i) + \mathbb 1_{c_i\neq\varnothing}\mathcal L_{box}\) and \(\mathcal L_{box} = \lambda_{iou}\,\text{GIoU} + \lambda_{L1}\|b-\hat b\|_1\). The Hungarian loss is then applied to the matched pairs; unmatched queries learn to predict ∅ (down-weighted ×10 for imbalance). One-to-one assignment penalises duplicates, so <b>no NMS</b> is needed.</p>
<p><b>Headline numbers</b> (Table 1, COCO val): DETR (41M parameters, 86 GFLOPs, 28 FPS) gets <b>AP 42.0</b>, matching a tuned Faster R-CNN-FPN+ (42.0). APL is 61.1 vs 53.4 (<b>+7.8</b>, global attention helps large objects), but APS is 20.5 vs 26.6 (<b>−5.5</b>, small objects suffer). Loss ablation (Table 4): class + L1 only gives 35.8 AP; class + GIoU 39.9; both 40.6.</p>
<p><b>Limitations</b>: long training (300–500 epochs), weak on small objects, and a maximum of N detections.</p>''',
),
tut=r'''
<p><b>1. What DETR removes.</b> Anchor generation, proposal heuristics and NMS post-processing. Treating detection as predicting a <b>set</b> (order-free, fixed size N, padded with ∅) and training it with a one-to-one bipartite matching makes a single forward pass give final detections.</p>
<p><b>2. Object queries.</b> N = 100 learned embeddings fed to the decoder. Each attends to the image features (and to the other queries) and outputs one prediction: a class distribution including ∅, and a box. Queries not matched to any ground truth are trained to predict “no object”.</p>
<p><b>3. Matching during training.</b> The Hungarian algorithm finds the lowest-cost one-to-one assignment between predictions and ground truth (padded with ∅). The cost uses the predicted <b>class probability</b> and <b>box similarity</b> (L1 + GIoU). One-to-one assignment means each object supervises exactly one query.</p>
<p><b>4. Why no NMS.</b> If two queries predicted the same object, only one would be matched; the other would be pushed towards ∅. Through self-attention between queries the decoder learns to avoid duplicates, so there is nothing for NMS to remove.</p>
<p><b>5. Limitations and evidence.</b> Very long training (300 epochs baseline, 500 for the main comparison, vs a 9× schedule for Faster R-CNN). Small objects: APS 20.5 vs 26.6 for Faster R-CNN-FPN+ (Table 1), linked to single-scale, low-resolution features and global attention cost. Fixed N caps the detections per image (they visualise the 100 slots). The later Deformable DETR and DINO address these.</p>
<p><b>6. Versus conventional detectors.</b> Conventional detectors represent candidates as anchors or proposals at many positions, regress offsets, and handle duplicates with NMS. DETR’s queries are global, learned slots with no fixed spatial prior; boxes are predicted directly in normalised coordinates; duplicates are handled by the set loss rather than by post-processing.</p>''',
quiz=[
 ('Box A area 80, box B area 40, intersection 20. IoU?', ['0.25', '0.20', '0.50', '0.17'], 1, '20/(80+40−20) = 20/100 = 0.20.'),
 ('12 detections, 9 true positives, 15 ground-truth objects. Precision and recall?', ['P = 0.6, R = 0.75', 'P = 0.75, R = 0.6', 'P = 0.75, R = 0.75', 'P = 0.6, R = 0.6'], 1, 'P = 9/12 = 0.75; R = 9/15 = 0.6.'),
 ('Why does DETR generally not need NMS?', ['It uses anchors', 'One-to-one bipartite matching trains each object to be predicted by exactly one query', 'It uses focal loss', 'It only detects large objects'], 1, 'Duplicates are penalised during training, so they are rarely produced.'),
],
)
