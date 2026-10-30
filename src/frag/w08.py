T = dict(
id='w08', week=8, tab='Deep learning', title='Deep learning for robotic vision',
lead='Start with the task (input, output, supervision, loss, metric), reuse pretrained backbones wisely, understand CNNs and Vision Transformers, and remember that deploying a model costs more than a test-set score.',
docs=[dict(path='notes/Week08.pdf', title='Week 8 lecture: Deep learning recap for robotic vision', pages=99),
      dict(path='notes/papers/ViT.pdf', title='ViT paper (Dosovitskiy et al., ICLR 2021)', pages=22)],
prac=('week-8-deep-learning.ipynb', '“Is the route blocked?”: builds a binary image classifier for a mobile robot on top of a pretrained backbone instead of training from scratch.'),
eli5=[
 ('Backbone + head', 'The backbone is a trained eye that turns pixels into a rich description; the head is a small specialist that answers one question from that description. Swap heads for new tasks.', 'the route-blocked classifier keeps a pretrained backbone and trains only a small head.'),
 ('Transfer learning ladder', 'Borrow a chef’s knife skills (pretrained features). With a few recipes, only learn the plating (linear probe); with many, retrain more of the chef.', None),
 ('Attention', 'Every image patch asks a question (query), advertises what it holds (key) and carries a message (value). A wheel patch listens most to the patches that help it, such as “forklift body”.', None),
 ('Confidence ≠ probability', 'A model can say “90% sure” about something it has never seen, like a student confidently guessing on a topic outside the syllabus.', 'pick the decision threshold for the cost of a missed obstacle, not the best accuracy.'),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="ViT: image cut into patches, linearly projected to tokens with a class token, transformer layers with attention, head on class token">
<g>
<rect class="bx" x="10" y="35" width="96" height="96"/>
<path class="ln" d="M42 35v96M74 35v96M10 67h96M10 99h96" style="stroke:var(--line)"/><text x="10" y="26" class="sm">image → P×P patches</text>
<path class="ac" d="M110 83 H140"/>
<g>''' + ''.join(f'<rect class="{"fe" if i==0 else "sk"}" x="{146+i*20}" y="72" width="16" height="22"/>' for i in range(10)) + '''</g>
<text x="146" y="64" class="sm">[class] + patch tokens + positions</text>
<path class="ac" d="M350 83 H375"/>
<rect class="sk" x="380" y="45" width="100" height="76"/><text x="388" y="70">Transformer</text><text x="388" y="90" class="sm">× L layers</text><text x="388" y="108" class="sm">attention + MLP</text>
<path class="ev" d="M430 121 V150 H160 V96"/><text x="200" y="164" class="sm">class-token output → linear head → label</text>
</g></svg>''',
svgcap='A Vision Transformer turns a 224×224 image with 16×16 patches into 196 tokens (+1 class token). Attention lets every token use information from every other token.',
videos=['NetSJM590Lo', '5T-iXNNiwIs'],
body=r'''
<div class="sub"><h3>1. When to learn</h3>
<p>The problem ladder [[p9]] [[p11]] [[p13]]: some problems have a <b>hand-crafted</b> solution (W2 detectors); some have a <b>score function</b> you can optimise (PnP, BA, factor graphs); for others you cannot even write a score, so you <b>learn from data</b> (image classification). Hierarchy: AI ⊃ machine learning ⊃ deep learning [[p17]]. The lecturer’s recap list [[p20]] (fine-tuning, SGD, transfer learning, augmentation, activations, pooling, data splits, softmax, cross-entropy) is assumed knowledge.</p></div>

<div class="sub"><h3>2. Start with the task</h3>
<div class="tw"><table><tr><th>Task</th><th>Output</th><th>Supervision</th><th>Loss (example)</th><th>Metric</th></tr>
<tr><td>Classification</td><td>one label per image</td><td>image label</td><td>cross-entropy</td><td>(per-class) accuracy</td></tr>
<tr><td>Semantic segmentation</td><td>class per pixel</td><td>pixel mask</td><td>pixel-wise CE</td><td>mean IoU</td></tr>
<tr><td>Detection</td><td>set of boxes + labels + scores</td><td>box + label per object</td><td>classification + box regression</td><td>AP at an IoU threshold</td></tr>
<tr><td>Instance segmentation</td><td>mask + label per instance</td><td>mask per object</td><td>cls + box + mask</td><td>mask AP</td></tr>
<tr><td>Depth prediction</td><td>depth per pixel</td><td>GT depth (sensor or stereo)</td><td>L2</td><td>RMSE</td></tr>
<tr><td>Place recognition</td><td>ranked list of database images</td><td>place IDs, GPS, pos/neg pairs</td><td>contrastive</td><td>Recall@K, PR</td></tr>
<tr><td>Obstacle warning</td><td>P(path blocked)</td><td>blocked / clear labels</td><td>binary CE</td><td>precision, recall, false-stop and missed-obstacle rates at the chosen threshold</td></tr></table></div>
<p class="note">Rows from [[p23]]–[[p30]]. Practice Q26: a per-pixel terrain class needs per-pixel logits, cross-entropy and mean mask IoU.</p>
<p><b>Architecture</b> [[p31]] [[p32]] [[p33]]: an encoder (<b>backbone</b>) produces a learned representation or embedding (a vector, feature map, pyramid or token sequence), and a task-specific <b>head</b> produces the output. Reusing a pretrained backbone is transfer learning. Vocabulary [[p37]]: data (an assumed operating distribution), backbone, head, <b>loss</b> (the training signal) and <b>metric</b> (an external measure of deployed behaviour, which is not the loss).</p></div>

<div class="sub"><h3>3. To train or not to train</h3>
<div class="tw"><table><tr><th>Strategy</th><th>Use when</th><th>Limitation</th></tr>
<tr><td>1. Direct feature reuse</td><td>few or no labels; retrieval, similarity, clustering, place recognition</td><td>cannot reshape the representation</td></tr>
<tr><td>2. Linear probe / train a head (frozen backbone)</td><td>labels available, keep the backbone</td><td>backbone cannot adapt</td></tr>
<tr><td>3. Partial fine-tuning</td><td>domain differs; probe insufficient; moderate data</td><td>choose which layers to unfreeze</td></tr>
<tr><td>4. Full fine-tuning</td><td>enough representative data; large domain gap</td><td>compute and overfitting risk</td></tr>
<tr><td>5. From scratch</td><td>no suitable pretrained model, unusual modality, huge dataset</td><td>most data and compute</td></tr></table></div>
<p class="note">Ladder from [[p34]] [[p35]]. More fine-tuning isn’t automatically better: with a small dataset it can destroy pretrained features or overfit. A linear probe is diagnostic: if it works, the representation already contains the information.</p>
<p><b>Splits</b> [[p36]]: <b>train</b> to learn, <b>validation</b> to monitor and tune (thresholds, hyperparameters; never learn from it), <b>test</b> for the final real-world estimate, used once. Practice Q40: choosing a threshold on the test set makes it no longer independent.</p>
<p><b>Where the signal comes from</b> [[p39]]: supervised labels (expensive) vs <b>self-supervised</b> targets built from unlabelled images. Contrastive / triplet learning pulls two crops of the same image together and pushes other images apart [[p40]]. A masked autoencoder hides patches and reconstructs them [[p41]]. DINOv3 is student–teacher distillation over views [[p42]]. CLIP is contrastive language–image pretraining [[p44]].</p></div>

<div class="sub"><h3>4. Architectures: FC, CNN, ResNet, ViT</h3>
<p>A fully connected layer computes \(y = a(W^\top x + b)\) [[p51]]; outputs are read as class confidences [[p55]]. A <b>convolution</b> applies the same local filter everywhere (weight sharing means fewer parameters and a translation-related inductive bias), and stacking grows the receptive field. CNNs are translation <b>equivariant</b> (shift the input → the feature map shifts), which is <b>not</b> the same as invariant [[p56]]. ResNets add skip connections [[p60]].</p>
<p><b>Vision Transformer</b> [[p65]]–[[p77]]: cut the image into patches, project each linearly to an embedding, then let tokens update each other with attention. For each token \(q_i = W_qx_i\), \(k_j = W_kx_j\) (“what I contain”, used for matching) and \(v_j = W_vx_j\) (“what I can send”). The score is \(q_i\cdot k_j\); the softmax weights sum to 1; the message is \(z_i = \sum_j a_{ij}v_j\); a residual connection keeps what the token knew: \(x_i' = x_i + z_i\). In matrix form, \(\mathrm{softmax}(QK^\top/\sqrt d)V\). Multi-head attention runs several of these in parallel, and layers stack.</p>
<div class="ex"><b>Worked example.</b> Scores 2.4, 2.1, 0.8, −0.5 → softmax weights 0.501, 0.371, 0.101, 0.028. A 224×224 image with P = 16 gives 196 tokens; P = 8 gives 784 tokens and (784/196)² = <b>16×</b> the attention pairs.</div>
<div class="widget" data-w="softmax"></div><div class="widget" data-w="vit"></div></div>

<div class="sub"><h3>5. From computer vision to robotic vision</h3>
<p>Computer vision <i>tests</i> on data (“87% accuracy”); robotic vision <i>deploys</i> into the world, where errors have costs [[p79]] [[p80]] [[p81]]. A threshold turns scores into actions [[p82]]: a <b>lower threshold</b> gives more positives, higher recall and more false positives; a <b>higher</b> one gives higher precision and more false negatives. Choose by physical consequence [[p83]]: a false positive (unnecessary stop) costs delay; a <b>false negative</b> (missed obstacle) risks a collision.</p>
<p><b>Confidence is not probability</b> [[p84]]: softmax expresses relative preference. Calibration asks whether stated confidence matches observed accuracy; a reliability diagram bins predictions by confidence and plots accuracy per bin [[p87]]. Confidence can stay high under distribution shift.</p>
<p><b>Distribution shift</b> [[p89]]–[[p97]]: deep learning assumes deployment data match training data. Feature shift (appearance changes) and class shift (new objects) both break this. CNNs have no mechanism for unseen classes and often misclassify them <b>with high confidence</b>, because the score grows with distance from the decision boundary.</p>
<div class="exam"><b>Exam angle.</b> Q26 (task/loss/metric alignment), Q27 (lowering the threshold reduces misses), Q28 (aggregate accuracy hides rare-class and latency failures), Q40 (test-set hygiene). Learn the task table: it maps directly onto MCQ distractors.</div></div>
''',
paper=dict(title='An Image is Worth 16×16 Words: ViT (Dosovitskiy et al., ICLR 2021)', sixty=r'''
<p><b>Problem.</b> Can a standard Transformer work directly on images with minimal changes? Yes: treat image patches as tokens.</p>
<p><b>Key idea</b> (Sec. 3.1, Fig. 1 [[P:p3]]): reshape \(x\in\mathbb R^{H\times W\times C}\) into \(N = HW/P^2\) flattened patches; project each linearly to D dims (patch embeddings); prepend a learnable <b>[class] token</b> whose final state, after LayerNorm, is the image representation; add learnable <b>1-D position embeddings</b> (2-D-aware ones gave no significant gain). The head is an MLP during pre-training and a single linear layer for fine-tuning.</p>
<p><b>Inductive bias.</b> CNNs build in locality, 2-D neighbourhood structure and translation equivariance in every layer. In ViT only the MLPs are local; self-attention is global, and 2-D structure is used only when cutting patches and when interpolating position embeddings for a new resolution. So ViT must learn spatial relations from data.</p>
<p><b>Headline numbers.</b> Trained on ImageNet alone (mid-sized) it is a few % <b>below</b> comparable ResNets. Pre-trained on ImageNet-21k or JFT-300M, “large scale training trumps inductive bias”: ViT-H/14 reaches <b>88.55%</b> ImageNet top-1. Variants: Base (12 layers, D = 768, 86M params), Large (24, 1024, 307M), Huge (32, 1280, 632M). Fig. 3: pre-trained on ImageNet, ViT-L does worse than ViT-B; only JFT-300M shows the full benefit of large models.</p>''',
),
tut=r'''
<p><b>1. Image → sequence.</b> Split the image into P×P patches (N = HW/P²), flatten each (P²·C numbers), project linearly to a D-dim token, prepend the class token and add position embeddings so the model knows where each patch came from, since attention itself is order-agnostic.</p>
<p><b>2. Through the Transformer.</b> Each layer: LayerNorm → multi-head self-attention → residual → LayerNorm → MLP → residual. Attention computes, for each token, a weighted mix of all tokens’ values, with weights from query·key similarity. So a wheel patch can absorb information from a distant forklift-body patch in one layer.</p>
<p><b>3. Class token.</b> A learnable extra token with no image content. Through attention it gathers a summary of all patches; its final output feeds the classification head.</p>
<p><b>4. Missing biases.</b> Locality, 2-D neighbourhoods and translation equivariance are hard-wired in CNNs but must be learned by ViT, which therefore needs more data (or strong regularisation or pre-training) to generalise.</p>
<p><b>5. Patch size.</b> Small patches keep fine detail but give long sequences, and attention cost grows with N² (halve P → 4× tokens → 16× attention). Large patches are cheap but blur small structures (thin poles, distant obstacles).</p>
<p><b>6. Why pre-training helps.</b> Large datasets let the model learn the regularities that CNN biases would supply for free, and then transfer them. It underfits small data less well than a CNN would.</p>
<p><b>7. Global attention in robotics.</b> It is useful for context and long-range relations (is this wheel part of a forklift? does the corridor continue?). Local structure still matters for precise boundaries, small objects and geometry (feature localisation, depth edges).</p>
<p><b>8. Reuse.</b> The patch-token backbone transfers to detection (DETR-style decoders with queries), segmentation (a per-token decoder upsampled to pixels), depth (dense prediction heads such as DPT) and place recognition (aggregating patch features as in AnyLoc). Each needs a task head, sometimes a decoder for dense outputs, and the matching loss and metric.</p>
<p><b>Attention video (optional, long).</b> 3Blue1Brown, “Attention in transformers, step-by-step” (26:09): <a href="https://www.youtube.com/watch?v=eMlx5fFNoYc" target="_blank" rel="noopener">open on YouTube ↗</a>. Watching it, think of tokens as image patches: the query is what the patch is looking for, the key is what it advertises, the value is what it sends.</p>''',
quiz=[
 ('A model must output a depth value for every pixel. Which combination fits?', ['Per-image logit, CE, accuracy', 'Per-pixel regression, L2 loss, RMSE', 'Boxes, GIoU, AP', 'Embedding, triplet loss, Recall@5'], 1, 'Depth prediction row of the task table [[p27]].'),
 ('You have 300 labelled images and a large domain gap. Which is the most sensible first step?', ['Train a ViT-H from scratch', 'Fine-tune everything for 1000 epochs', 'Linear probe on a frozen pretrained backbone, then consider partial fine-tuning', 'Use the test set to choose the layers to unfreeze'], 2, 'Few labels favour frozen features; partial fine-tuning if the probe is insufficient [[p35]].'),
 ('A CNN is translation-equivariant. This means…', ['a shifted input gives the same output', 'a shifted input gives a correspondingly shifted feature map', 'it is rotation invariant', 'it needs no pooling'], 1, 'Equivariance ≠ invariance [[p56]].'),
],
)
