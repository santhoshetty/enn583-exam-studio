T = dict(
id='w02', week=2, tab='Features & matching', title='Detectors, descriptors and matching',
lead='The first stage of visual odometry: find distinctive points, give each a fingerprint, and decide which points in two images are the same physical point.',
docs=[dict(path='notes/Week02.pdf', title='Week 2 lecture: Visual correspondences', pages=105),
      dict(path='notes/papers/SuperGlue.pdf', title='SuperGlue paper (Sarlin et al., CVPR 2020)', pages=18),
      dict(path='notes/papers/LightGlue.pdf', title='LightGlue paper (Lindenberger et al., ICCV 2023)', pages=18)],
prac=('kitti_introduction.ipynb + week-2-lightglue-demo.ipynb', 'loads KITTI stereo frames, then matches SuperPoint keypoints with LightGlue between frames (this notebook has saved outputs).'),
eli5=[
 ('Detector = “where to look”', 'Pick spots you could find again, such as the corner of a window, not the middle of a blank wall. Good spots are distinctive, repeatable and well localised.', 'SuperPoint picks the keypoints that LightGlue then matches on KITTI.'),
 ('Descriptor = fingerprint', 'Describe the neighbourhood of each spot as a list of numbers (SIFT: 128 floats) or bits (BRIEF/ORB: 256 bits), so the same spot in another photo gets a similar fingerprint.', None),
 ('Matching = speed dating', 'Each point in image A looks for its most similar partner in B. If the best and second-best partners are almost equally good, walk away (ratio test). Only keep pairs who choose each other (cross-check).', None),
 ('Learned matching', 'SuperGlue lets all the points “talk” within and across both images before deciding, like solving a jigsaw by looking at neighbouring pieces. Points with no partner go in the dustbin.', 'LightGlue (SuperGlue’s faster successor) stops early on easy frame pairs.'),
],
svg='''<svg class="dg" viewBox="0 0 520 190" role="img" aria-label="FAST test: 16 pixel circle around candidate p; 12 contiguous pixels darker than p minus t make a corner">
<g transform="translate(95,95)">
''' + ''.join(f'<rect class="{"sk" if i in range(12) else "bx"}" x="{round(64*__import__("math").sin(i*3.14159*2/16))-10}" y="{round(-64*__import__("math").cos(i*3.14159*2/16))-10}" width="20" height="20"/><text class="sm" x="{round(64*__import__("math").sin(i*3.14159*2/16))-6}" y="{round(-64*__import__("math").cos(i*3.14159*2/16))+4}">{i+1}</text>' for i in range(16)) + '''
<rect class="fi" x="-10" y="-10" width="20" height="20"/><text x="-4" y="5" style="fill:var(--bg)">p</text>
</g>
<text x="200" y="40">FAST corner test (N ≥ 12, threshold t)</text>
<rect class="sk" x="200" y="56" width="16" height="16"/><text x="224" y="69">12 contiguous pixels all darker than I(p) − t</text>
<rect class="bx" x="200" y="82" width="16" height="16"/><text x="224" y="95">remaining 4 pixels: anything</text>
<text x="200" y="125">Quick reject: test pixels 1, 5, 9, 13 first;</text>
<text x="200" y="144">at least 3 of the 4 must pass, else not a corner.</text>
<text x="200" y="170" class="sm">Only intensity comparisons: no gradients, no floating point.</text>
</svg>''',
svgcap='FAST compares 16 pixels on a radius-3 circle with the centre. A long contiguous arc that is all brighter or all darker than the centre by more than t marks a corner (practice exam Q3).',
videos=['4AvTMVD9ig0', '0sPlnrEMyYk'],
body=r'''
<div class="sub"><h3>1. Why correspondences, and why they are hard</h3>
<p>The VO pipeline [[p12]] has two stages: (1) <b>visual correspondences</b> (find distinctive regions and the same region in the next image), then (2) <b>motion estimation</b> from them (Weeks 4–5). “Odometry” comes from the Greek <i>odos</i> (route) and <i>metron</i> (measure) [[p6]].</p>
<p>The challenges [[p18]] [[p19]] [[p20]]: <b>geometric</b> (scale change, rotation, perspective distortion), <b>appearance</b> (light and shadow, season and weather, exposure and white balance, blur and noise) and <b>ambiguity</b> (repeated patterns, visual aliasing, low texture). Repeated floor tiles give several plausible matches for one feature (practice Q2).</p>
<p>The general pipeline is <b>detection → description → matching</b> [[p21]]. Some methods cover two stages (SIFT = detector + descriptor) and some are combinations (ORB = FAST + BRIEF) [[p22]].</p>
<div class="tw"><table><tr><th>Stage</th><th>Classical</th><th>Learned</th></tr>
<tr><td>Detection</td><td>Harris, FAST, DoG (SIFT), SURF, AKAZE</td><td>SuperPoint, DISK, R2D2</td></tr>
<tr><td>Description</td><td>SIFT, SURF, BRIEF, ORB, BRISK, AKAZE</td><td>SuperPoint, DISK, D2-Net, R2D2</td></tr>
<tr><td>Matching</td><td>NN, brute force, ratio test, cross-check, ANN</td><td>SuperGlue, LightGlue, LoFTR</td></tr></table></div>
<p class="note">Table from [[p23]].</p></div>

<div class="sub"><h3>2. What makes a good feature</h3>
<p>A good feature is <b>distinctive</b> (different enough from other regions to match unambiguously), <b>repeatable</b> (detected again under small changes of viewpoint, scale, illumination and noise) and <b>well localised</b> (a sharp position, so small image changes don’t shift it much) [[p36]]. A corner beats an edge, because along an edge you can slide without change (the aperture problem), and an edge beats a flat patch.</p></div>

<div class="sub"><h3>3. Moravec and Harris corners</h3>
<p><b>Moravec (1980)</b> shifts a small window in a few directions and measures the change with SSD:</p>\[s(u,v,\delta) = \sum_{i,j}\big(I(u+\delta_u+i,\ v+\delta_v+j) - I(u+i,\ v+j)\big)^2\]<p>The score is the <b>minimum</b> over shifts, so a corner must change in every direction [[p46]]. Weaknesses: it gives high scores on edges that are not at 0°, 45° or 90° (only 8 directions are tested), and it is inefficient.</p>
<p><b>Harris (1988)</b> uses image derivatives instead. The structure tensor is \(A = w * \begin{bmatrix} J_u^2 & J_uJ_v \\ J_uJ_v & J_v^2\end{bmatrix}\), with \(w\) a window or Gaussian weighting [[p48]]. Its eigenvectors give the directions of fastest and slowest change; its eigenvalues give how much change [[p49]]:</p>
<ul><li>both eigenvalues large → <b>corner</b></li><li>one large, one small → <b>edge</b></li><li>both small → <b>flat</b> [[p50]]</li></ul>
<div class="ex"><b>Worked example.</b> \(A = \mathrm{diag}(50, 48)\) → corner. \(A = \mathrm{diag}(50, 1)\) → edge (strong change in one direction only). \(A = \mathrm{diag}(1, 0.5)\) → flat.</div></div>

<div class="sub"><h3>4. Descriptors: SIFT and BRIEF</h3>
<p>Comparing raw patches with SSD \(\sum(a-b)^2\) or SAD \(\sum|a-b|\) is naive: it breaks under rotation, scale and illumination change [[p57]].</p>
<p><b>SIFT</b> (1999/2004) aims to be invariant to scale, rotation, moderate perspective, illumination and noise [[p60]]:</p>
<ol><li><b>Scale space:</b> blur with increasing σ (like seeing the scene from further away) and take the Difference of Gaussians \(D(u,v,\sigma) = L(u,v,k\sigma) - L(u,v,\sigma)\) [[p62]].</li>
<li><b>Extrema:</b> a candidate must be a max or min compared with its neighbours in the same scale <i>and</i> the scales above and below (26 neighbours) [[p63]].</li>
<li><b>Orientation:</b> histogram of gradient orientations weighted by magnitude; the strongest bin is the keypoint orientation, giving rotation invariance [[p64]].</li>
<li><b>Clean-up:</b> remove edge-like, low-contrast and badly localised candidates [[p65]].</li>
<li><b>Descriptor:</b> 4×4 sub-regions, an 8-bin orientation histogram each, concatenated: 4·4·8 = <b>128 numbers</b> [[p66]].</li></ol>
<p><b>BRIEF</b> (2010) compares random pairs of pixels in a smoothed patch; each comparison gives one bit (e.g. 256 bits = 32 bytes) [[p70]]. Matching uses the <b>Hamming distance</b> (XOR then count bits), which is very fast and needs no floating point [[p71]]. It is <b>not rotation or scale invariant</b> and needs a separate detector [[p72]].</p>
<div class="ex"><b>Worked example.</b> Hamming distance between 10110010 and 10011010: XOR = 00101000 → <b>2</b> bits differ.</div></div>

<div class="sub"><h3>5. FAST and ORB</h3>
<p><b>FAST</b> (2006) looks at a circle of 16 pixels around candidate p. If <b>N contiguous pixels</b> (typically N ≥ 12) are all brighter than \(I_p + t\) or all darker than \(I_p - t\), p is a corner. A high-speed test checks pixels 1, 9, 5 and 13 first; for a corner at least 3 of them must pass [[p76]]. A decision tree learned from data picks the test order to minimise comparisons [[p77]]. There are no gradients, no convolution and no eigenvalues [[p78]].</p>
<p><b>ORB</b> (2011) = <b>oFAST + rBRIEF</b> [[p83]] [[p84]]. oFAST adds a scale pyramid (an idea from SIFT), a Harris score to reject points on lines, and an orientation from the vector between the keypoint and the <b>intensity centroid</b> of its patch. rBRIEF rotates BRIEF’s sampling pattern by that orientation.</p>
<div class="tw"><table><tr><th>Name</th><th>Type</th><th>Invariant to</th><th>Speed</th></tr>
<tr><td>Harris</td><td>detector</td><td>rotation (partly)</td><td>medium</td></tr><tr><td>FAST</td><td>detector</td><td>none (original)</td><td>very fast</td></tr>
<tr><td>SIFT</td><td>det + desc</td><td>scale, rotation</td><td>slow</td></tr><tr><td>SURF</td><td>det + desc</td><td>scale, rotation</td><td>faster than SIFT (integral images)</td></tr>
<tr><td>ORB</td><td>det + desc</td><td>rotation, scale (limited)</td><td>real-time</td></tr><tr><td>BRIEF</td><td>descriptor</td><td>not rotation</td><td>very fast</td></tr></table></div>
<p class="note">Summary table from [[p97]].</p></div>

<div class="sub"><h3>6. Matching: brute force, ratio test, cross-check</h3>
<p>Brute force: for each descriptor in A, find the most similar in B, using <b>Euclidean</b> distance for float descriptors and <b>Hamming</b> for binary ones [[p87]].</p>
<p><b>Lowe’s ratio test</b> [[p88]]: accept if \(\dfrac{\|A - B_1\|}{\|A - B_2\|} &lt; \theta\) (best over second best). A ratio near 1 means the match is ambiguous.</p>
<p><b>Cross-check (mutual NN)</b> [[p89]]: discard \((A_1, B_1)\) if some \(A_2\) is closer to \(B_1\) than \(A_1\) is.</p>
<div class="ex"><b>Worked example (practice Q4).</b> Distances 35 and 40, θ = 0.80, strict “&lt;”. Ratio = 35/40 = <b>0.875</b>, which is not below 0.80 → <b>reject</b>. With distances 24 and 40 the ratio is 0.6 → accept.</div>
<div class="widget" data-w="ratio"></div>
<p>Practical baseline [[p103]]: <b>ORB + Hamming brute force + ratio test or cross-check</b>, then RANSAC geometric verification when false matches remain (Week 4). Try SIFT for large scale or viewpoint change and weak texture, or when you need fewer but more reliable matches (at higher cost) [[p102]]. Use approximate NN for large descriptor sets.</p></div>

<div class="sub"><h3>7. Learned matching and recent trends</h3>
<p>Traditional matching treats each feature in isolation, but real matching is a <b>joint assignment problem</b> [[p91]].</p>
<div class="tw"><table><tr><th>Traditional</th><th>Learned (SuperGlue, LightGlue)</th></tr>
<tr><td>compares features mostly independently</td><td>reasons about all features jointly</td></tr>
<tr><td>rules: ratio test, cross-check</td><td>learns which matches are mutually consistent</td></tr>
<tr><td>fixed thresholds reject ambiguity</td><td>predicts correspondences <i>and</i> unmatched points</td></tr>
<tr><td>same compute for every pair</td><td>can adapt compute to difficulty (LightGlue)</td></tr></table></div>
<p class="note">Comparison from [[p92]].</p>
<p>Trend [[p99]] [[p100]]: there are <b>sparse learned pipelines</b> (learned detector, descriptor and matcher) and <b>detector-free / dense</b> ones (e.g. LoFTR) that avoid committing to a few keypoints, which helps in low texture and under hard viewpoint changes.</p>
<div class="exam"><b>Exam angle.</b> Six of the 40 practice questions are on this week. Know which stage produces what (the descriptor outputs an appearance representation, Q1), the FAST rule (Q3), the ratio-test arithmetic with strict inequality (Q4), SuperGlue as the matcher between features and the geometric back end (Q5), and why LightGlue’s early exit lowers <i>average</i> latency (Q6).</div></div>
''',
paper=dict(title='SuperGlue (CVPR 2020) and LightGlue (ICCV 2023)', sixty=r'''
<p><b>Problem.</b> Nearest-neighbour matching plus heuristics (ratio test, mutual check) fails with repeated structure, large viewpoint change and occlusion. SuperGlue is a learned <b>“middle-end”</b> between the front end (feature extraction) and the back end (pose / MAP estimation).</p>
<p><b>Key idea.</b> The inputs are two sets of local features (keypoint position + confidence, and a descriptor). A keypoint encoder adds position to each descriptor. An attentional graph neural network alternates <b>self-attention</b> (within an image: context) and <b>cross-attention</b> (between images: candidate matches) for 9 layers. It then builds a score matrix with an extra <b>dustbin</b> row and column for unmatched points and solves a differentiable optimal-transport problem (<b>Sinkhorn</b>, 100 iterations). The result is a partial assignment in which each point gets at most one match [[P:p5]].</p>
<p><b>Headline numbers.</b> Indoor ScanNet with SuperPoint features (Table 2 [[P:p6]]): pose AUC@20° rises from 36.40 (NN + mutual) to <b>51.84</b>, and match precision from 50.4% to <b>84.4%</b>. 12M parameters, 69 ms per pair (15 FPS) on a GTX 1080.</p>
<p><b>LightGlue</b> keeps SuperGlue’s accuracy but adapts its compute. It <b>stops early</b> once its predictions are confident (adaptive depth) and <b>prunes points</b> it judges unmatchable (adaptive width). On MegaDepth (Table 2): SuperGlue AUC@5/10/20 = 49.7/67.1/80.6 at 70.0 ms; LightGlue 49.9/67.0/80.1 at 44.2 ms; adaptive LightGlue 49.4/67.2/80.1 at <b>31.4 ms</b>.</p>
<p><b>Limitation.</b> Both are <b>sparse</b> and depend on the external detector: no keypoints means nothing to match. Attention cost grows with the number of keypoints.</p>
<p><b>How to read their results.</b> “AUC@10°” is the area under the cumulative pose-error curve up to 10°: higher means more image pairs have accurate relative pose. <i>Precision</i> is the fraction of predicted matches that are correct; <i>matching score</i> is correct matches over all detected keypoints. In an ablation table, compare each “No X” row with the full model: the biggest drop marks the most important component.</p>''',
),
tut=r'''
<h4>SuperGlue</h4>
<p><b>1. What problem?</b> Independent descriptor matching ignores context: a point on a repeated window has several equally good partners, and fixed heuristics either keep wrong matches or throw away good ones. Matching is a <b>joint assignment</b>: one physical point can match at most one point, and the choices must be geometrically consistent with each other. Some points (occluded, out of view, unrepeatable) have <b>no</b> partner, so the method must also decide what stays unmatched (dustbin).</p>
<p><b>2. Inputs.</b> For each image: keypoint positions with detection confidence, plus local descriptors (SuperPoint or SIFT). SuperGlue adds positional encoding and context through attention. Detection and description happen <i>before</i> it, and pose estimation (RANSAC + E/PnP) after.</p>
<p><b>3. Ingredients.</b> Self-attention (same image): each feature learns about salient points around it. Cross-attention (other image): it looks for candidate matches, like a human glancing back and forth. Optimal transport / Sinkhorn: jointly selects one-to-one correspondences. Dustbin: absorbs features with no reliable match. A broader view helps an ambiguous point: if its neighbours match consistently, the correct candidate is the one that fits that pattern.</p>
<p><b>4. Capabilities and limits.</b> It improves most with wide baselines, repeated structure and large appearance change. The authors evaluate by downstream <b>pose accuracy (AUC)</b>, precision and matching score, not just match counts. Limits: GPU cost, quadratic attention in the number of keypoints, and reliance on the detector (poor or few keypoints means poor matches).</p>
<h4>LightGlue</h4>
<p><b>1. What remains?</b> It keeps SuperGlue’s attention-based joint reasoning and dustbin idea, but SuperGlue is costly in time and memory and hard to train. Robots need low latency and fit on embedded compute: VO runs at camera rate and other modules share the processor.</p>
<p><b>2. Central idea.</b> Easy pairs (large overlap, little appearance change) become confident after a few layers, so the network checks its confidence after each layer and exits early (depth). Points that are clearly unmatchable are dropped from later layers (width). Table 5: easy pairs stop at layer 4.7 on average (hard ones 6.9) with a 1.86× speed-up.</p>
<p><b>3. Comparison.</b> It is not only faster: accuracy matches or slightly exceeds SuperGlue (Table 2), and it trains in a few GPU-days. Adaptive compute lowers <i>average</i> latency while still spending more on hard pairs, which suits real-time and embedded robots.</p>
<p><b>4. Limits.</b> It still needs an external detector and descriptor. With too few keypoints, matching fails. It is a <b>sparse</b> matcher. Detector-free dense matchers (LoFTR) are preferable in low texture, under extreme viewpoint change, or when dense correspondence is needed, at a higher compute cost (LoFTR 181 ms vs 44 ms).</p>
<p>Ablation from SuperGlue Table 4 [[P:p7]] (AUC@20 / precision): NN + mutual 36.40/50.4 · no GNN 38.56/66.0 · no cross-attention 42.57/74.0 · no positional encoding 47.12/75.8 · 3 layers 46.93/79.9 · full (9 layers) 51.84/84.4.</p>''',
quiz=[
 ('ORB descriptors are compared with which distance?', ['Euclidean distance on 128 floats', 'Hamming distance on bit strings', 'Cosine distance on image patches', 'Mahalanobis distance on keypoint positions'], 1, 'ORB is binary (rBRIEF), so the distance is the number of differing bits, computed with XOR + popcount.'),
 ('The two largest eigenvalues of a Harris structure tensor are 80 and 2. The pixel is most likely…', ['a corner', 'an edge', 'a flat region', 'a blob at a coarser scale'], 1, 'One large and one small eigenvalue means change in one direction only: an edge [[p50]].'),
 ('Best and second-best descriptor distances are 30 and 50; the ratio threshold is 0.7. Result?', ['Reject, ratio 0.6 ≥ 0.7', 'Accept, ratio 0.6 &lt; 0.7', 'Reject, ratio 1.67 &gt; 1', 'Accept, because 30 &lt; 50'], 1, '30/50 = 0.6 &lt; 0.7, so the best match is clearly better than the runner-up.'),
],
)
