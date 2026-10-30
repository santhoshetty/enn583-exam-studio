T = dict(
id='w12', week=12, tab='Place recognition', title='Visual representations, retrieval and place recognition',
lead='“Have I been here before?” as image retrieval: global vs local descriptors, bag of words and TF-IDF, aggregation (NetVLAD, AnyLoc), contrastive training, and how to evaluate with precision, recall and Recall@K.',
docs=[dict(path='notes/Week12.pdf', title='Week 12 lecture: Visual representations, retrieval and place recognition', pages=80),
      dict(path='notes/papers/AnyLoc.pdf', title='AnyLoc paper (Keetha et al., 2023)', pages=10)],
prac=None,
eli5=[
 ('VPR = photo search', 'You show the robot a photo and it searches its album for the most similar picture of the <i>same place</i>, even if it’s now night, winter or seen from another angle.', None),
 ('Global vs local descriptors', 'Global: one summary sentence per photo (fast to compare, misses details). Local: a list of distinctive details (robust to viewpoint, slower to compare).', None),
 ('Bag of visual words', 'Turn each local feature into a “word” from a dictionary and compare photos by word counts, down-weighting words that appear everywhere (like “the”).', None),
 ('Contrastive learning', 'Teach the network that two photos of the same corner belong together and a lookalike corner somewhere else does not, especially the tricky lookalikes (hard negatives).', None),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="VPR pipeline: image, pretrained backbone, patch descriptors, aggregation to global descriptor, nearest-neighbour retrieval, geometric verification">
''' + ''.join(f'<rect class="{c}" x="{x}" y="55" width="76" height="50"/><text x="{x+6}" y="76" class="sm">{a}</text><text x="{x+6}" y="93" class="sm">{b}</text>' for x,a,b,c in [(6,'query','image','bx'),(92,'pretrained','ViT (DINOv2)','sk'),(178,'patch','descriptors','bx'),(264,'aggregate','GeM / VLAD','sk'),(350,'nearest-','neighbour top-K','bx'),(436,'verify','geometry / seq.','sk')]) + '''
<path class="ac" d="M82 80 H92 M168 80 H178 M254 80 H264 M340 80 H350 M426 80 H436"/>
<text x="6" y="40" class="sm">compact global descriptor = fast candidate search over a big database</text>
<text x="300" y="130" class="sm">local evidence / RANSAC rejects false loops</text>
</svg>''',
svgcap='Modern VPR [[p67]]: foundation-model patch features are aggregated into one global descriptor for fast retrieval; geometric verification or sequence matching makes the final decision (practice Q37).',
videos=['A_-nHCK9oBs', 'YF8BbMJIgCo'],
body=r'''
<div class="sub"><h3>1. Why visual place recognition</h3>
<p>VPR asks whether the robot has seen this place before [[p5]]. Uses [[p6]]: <b>loop-closure detection</b> (SLAM), the <b>kidnapped robot</b> problem, and <b>initial candidates</b> for full 6-DoF localisation (PnP). Why not GNSS [[p7]]? It is denied indoors and underground; non-line-of-sight and multipath signals in urban canyons and under canopy degrade it; and it may not be accurate enough.</p>
<p>VPR is an <b>image retrieval</b> problem [[p9]] [[p10]]: given a query, find the most similar database images, where “similar” should mean the same physical place despite appearance or viewpoint change. <b>Why not classification?</b> [[p14]] [[p15]] It needs a fixed set of place classes and retraining for new places, and it gives a label rather than a ranking. Retrieval simply inserts new reference images, returns ranked candidates, scales to large changing sets, and handles graded similarity between nearby places.</p></div>

<div class="sub"><h3>2. The VPR setting</h3>
<p>Reference (map, database) traverse vs query traverse [[p19]] [[p20]]; both can be built online [[p21]]. Compare query and reference descriptors to get a <b>similarity matrix</b> (or distance matrix) and declare a match if the similarity &gt; θ [[p26]] [[p27]]. Raw pixel differences fail under viewpoint and lighting change [[p22]]. If the robot repeats a route, the matrix shows a diagonal band [[p29]].</p>
<ul><li><b>Single-session</b>: database = query, both growing (loop closures while exploring) [[p32]].</li>
<li><b>Multi-session</b>: database from yesterday (constant), query today (growing) [[p33]].</li>
<li>Taxonomy [[p37]]: online vs batch × single vs multi session → online SLAM, mapping, multi-session and multi-robot mapping (merge maps), visual localisation.</li></ul>
<p><b>Challenges</b> [[p39]]–[[p43]]: viewpoint, dynamic objects and occlusion, illumination and weather (SeqSLAM: sunny summer day vs stormy winter night), seasons (a 3000 km journey across four seasons), and <b>perceptual aliasing</b> (different places that look the same).</p></div>

<div class="sub"><h3>3. Evaluation</h3>
<p>With ground-truth matches, VPR is a binary decision [[p46]]: \(P = \frac{TP}{TP+FP}\) (100 matches, 65 correct → P = 0.65) [[p48]]; \(R = \frac{TP}{GTP}\), where GTP counts queries that have a true match (100 found of 200 → R = 0.5) [[p50]]. Sweeping θ gives a PR curve. Also report maximum recall at 100/99/95% precision, AUPRC, and maximum F1 = \(\frac{2PR}{P+R}\) [[p51]]. With P = 0.65 and R = 0.5, F1 = 0.565.</p>
<p><b>Recall@K</b> (Week 8 task table): the fraction of queries with at least one correct match among the top K retrieved.</p>
<div class="ex"><b>Worked example (practice Q36).</b> First correct match at ranks 2, 5, 1, 6, and none for the fifth query. Within the top 2: ranks 2 and 1 → 2 of 5 → <b>Recall@2 = 0.40</b>. Recall@5 = 3/5 = 0.6.</div>
<div class="widget" data-w="recallk"></div>
<p>For safety-critical loop closures, <b>precision</b> usually matters more: one false loop corrupts the map. Question [[p79]]: high precision or high recall?</p></div>

<div class="sub"><h3>4. Descriptors</h3>
<div class="tw"><table><tr><th>Global (holistic)</th><th>Local</th></tr>
<tr><td>one vector per image</td><td>a set of vectors</td></tr><tr><td>compact, fast nearest-neighbour retrieval</td><td>preserves local structure</td></tr>
<tr><td>may lose spatial detail → struggles with viewpoint change</td><td>more robust to partial overlap and viewpoint change</td></tr><tr><td>examples: Gist, BRIEF-Gist, CNN feature maps</td><td>more expensive to match</td></tr></table></div>
<p class="note">Comparison from [[p65]].</p>
<p>Global [[p56]] [[p57]]: Gist; BRIEF-Gist (one BRIEF over the whole image); CNN features used as the descriptor (Sünderhauf et al. 2015). Local [[p58]] [[p59]]: SIFT or ORB, but a variable-sized set must become retrievable, hence the <b>bag of visual words</b> (Video Google): cluster descriptors into a vocabulary, describe each image as a word histogram, compare histograms [[p61]].</p>
<p><b>TF-IDF</b> [[p63]]: \(t_i = \frac{n_{id}}{n_d}\log\frac{N}{n_i}\). Here \(n_{id}\) is the count of word i in image d, \(n_d\) the words in d, N the number of images, and \(n_i\) how common word i is across the database (standard TF-IDF counts the images containing it). Words that are common everywhere get low weight.</p>
<div class="ex"><b>Worked example (slide numbers).</b> N = 1000 images, 100 words per image. w1 appears 10× in this image and 100× overall: \(0.1\cdot\log_{10}(1000/100) = 0.1\). w2 appears 10× here but 10,000× overall: \(0.1\cdot\log_{10}(0.1) = -0.1\). So w2 is a common word and carries much less (here even negative) weight. With the standard definition \(n_i \le N\), the weight would be ≥ 0, but the conclusion is the same: <b>w1 is more informative</b>.</div>
<p><b>Aggregation</b> [[p66]]: extract rich local features and pool them into one compact global descriptor. <b>NetVLAD</b> learns the aggregation for VPR. The modern pipeline [[p67]]: pretrained ViT / foundation model → patch descriptors → aggregation → global descriptor → nearest-neighbour retrieval (AnyLoc).</p>
<p><b>Cosine similarity</b> \(\cos = \frac{q^\top a}{\|q\|\|a\|}\); for unit vectors it is just the dot product. Practice Q35: q = (0.8, 0.6) gives qᵀa = 1 for a = q and −1 for b = −q.</p>
<div class="widget" data-w="cosine"></div></div>

<div class="sub"><h3>5. Learning descriptors</h3>
<p>Same place should be close and different places far apart [[p69]]–[[p72]]. Options: use a pretrained representation (ImageNet CNNs, DINO) without VPR training; <b>metric / contrastive learning</b> (contrastive, <b>triplet</b>, InfoNCE); or place-classification training (CosPlace). Triplet loss [[p73]] [[p74]]: anchor, positive (same place), negative (different place); pull positives together and push negatives apart, e.g. \(\max(0, d(a,p) - d(a,n) + m)\).</p>
<p>Challenges [[p75]]: choose negatives that are neither too easy nor too hard; decide how far you must move before it counts as a new place; GPS distance usually defines positives and negatives, but viewpoint means geographically close images can look very different; <b>hard-negative mining</b> matters because lookalike places are the informative examples.</p>
<p><b>VPR is only the first step</b> [[p77]] [[p78]] [[p80]]: retrieval generates candidates. <b>Geometric verification</b> or <b>sequence matching</b> (SeqSLAM exploits temporal coherence, which plain retrieval can’t) makes the decision. Choosing a method [[p79]]: which invariances you need, precision vs recall, online vs batch, runtime and compute.</p>
<div class="exam"><b>Exam angle.</b> Q35 (cosine), Q36 (Recall@K), Q37 (compact global descriptors for candidates, then rerank with local spatial evidence and accept only geometrically consistent candidates: this avoids false loops in repeated corridors and scales to big databases).</div></div>
''',
paper=dict(title='AnyLoc: Towards Universal Visual Place Recognition (Keetha et al., 2023)', sixty=r'''
<p><b>Problem.</b> The best VPR methods are trained for one environment, mostly urban driving, and degrade badly in unstructured settings. AnyLoc aims to be <b>universal</b>: anywhere (urban, indoor, aerial, underwater, subterranean, degraded), anytime (day–night, seasons) and anyview (including &gt; 90° viewpoint shifts), <b>without any VPR-specific training or fine-tuning</b> [[P:p1]].</p>
<p><b>Key idea.</b> Use dense per-pixel features from an off-the-shelf <b>self-supervised foundation model</b> (DINOv2 ViT-G, layer 31, value facet, which gives the sharpest contrast) and aggregate them <b>without supervision</b>: \(F_G = (\sum f_i^{\,p})^{1/p}\) (p = 1 GAP, p = 3 <b>GeM</b>, p → ∞ GMP), or <b>VLAD</b> (k-means vocabulary over database features, summing residuals \(f_i - c_k\) per cluster, hard or soft assignment) [[P:p3]].</p>
<p><b>Domains.</b> A PCA of DINOv2-GeM descriptors separates datasets into domains (Urban, Indoor, Aerial, SubT, Degraded, Underwater). Building <b>domain-specific VLAD vocabularies</b> gives a further ~6%. Features from VPR-trained MixVPR collapse into a small region of feature space.</p>
<p><b>Headline numbers.</b> Evaluated on 12 diverse datasets with <b>Recall@1</b> (and R@5): up to <b>4× higher Recall@1</b> than supervised state-of-the-art baselines (NetVLAD, CosPlace, MixVPR), especially in unstructured environments. Takeaway: self-supervised features <i>and</i> unsupervised aggregation are both crucial, and aggregated per-pixel features beat per-image (CLS) features.</p>''',
),
tut=r'''
<p><b>1. Motivation and “universal”.</b> Today’s strong VPR models are environment- and task-specific (trained on urban street views) and brittle elsewhere. Universal means one method that works across very different places, times and viewpoints with no retraining or fine-tuning for each new domain.</p>
<p><b>2. Features.</b> Dense patch features from large self-supervised models (DINO, DINOv2; CLIP was also considered). They were trained on huge, diverse data without labels, so they encode general visual semantics and structure instead of one dataset’s biases, and they stay discriminative across domains. The chosen layer/facet (ViT-G layer 31, value) gives the sharpest similarity contrast.</p>
<p><b>3. Local → global.</b> Aggregate the per-pixel features into one vector: GAP, GMP, GeM (generalised mean) and VLAD (hard and soft assignment to a k-means vocabulary, residual sums, then normalisation). VLAD on DINOv2 features performs best.</p>
<p><b>4. Evaluating generalisation.</b> 12 datasets covering structured (urban, indoor) and unstructured (aerial, underwater, subterranean, degraded) environments, day/night and seasonal change, and opposing viewpoints, measured by Recall@1 and R@5 against supervised baselines (NetVLAD, CosPlace, MixVPR). Evidence: large gains (up to 4× R@1) on unstructured sets, competitive on urban ones.</p>
<p><b>5. Domains.</b> A PCA of global descriptors reveals clusters that match environment types; queries land near their database. AnyLoc builds a separate VLAD vocabulary per domain, which improves results by about 6%.</p>
<p><b>Optional discussion: is “universal” justified?</b> The evidence is broad (12 datasets), but untested conditions include thermal or event cameras, heavy rain, snow and fog, forests and agricultural fields with self-similar vegetation, crowded dynamic scenes, long-term structural change (construction), and very large city-scale databases where ViT-G cost and VLAD descriptor size matter. A cautious reading is “broadly general” rather than proven universal.</p>''',
quiz=[
 ('q = (0.6, 0.8), a = (0.8, 0.6), b = (0, 1). Which database item ranks first by cosine similarity?', ['a (0.96)', 'b (0.80)', 'tie', 'neither, they are orthogonal'], 0, 'q·a = 0.48 + 0.48 = 0.96; q·b = 0.8 (all unit length).'),
 ('Six queries; first correct match at ranks 1, 3, 7, 1, none, 2. Recall@1 and Recall@5?', ['2/6 and 4/6', '2/6 and 5/6', '3/6 and 4/6', '1/6 and 4/6'], 0, 'R@1: ranks ≤ 1 → 2 queries. R@5: ranks ≤ 5 → 1, 3, 1, 2 → 4 queries.'),
 ('Why is VPR usually framed as retrieval rather than classification?', ['Classification is too accurate', 'New places can be added by inserting reference images, and retrieval returns a ranked list with graded similarity', 'Retrieval needs no descriptors', 'Classification cannot use CNNs'], 1, 'From [[p14]].'),
],
)
