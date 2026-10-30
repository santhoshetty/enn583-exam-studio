T = dict(
id='w11', week=11, tab='Segmentation & grasping', title='Segmentation and grasp prediction',
lead='Dense, per-pixel prediction (semantic and instance segmentation) with encoder–decoder networks, then how robots predict where and how to grasp: planar vs 6-DoF, generative vs discriminative, geometric vs task-aware.',
docs=[dict(path='notes/Week11.pdf', title='Week 11 lecture: Segmentation and grasp prediction', pages=44),
      dict(path='notes/papers/Contact-GraspNet.pdf', title='Contact-GraspNet paper (Sundermeyer et al., ICRA 2021)', pages=7)],
prac=None,
eli5=[
 ('Semantic vs instance', 'Semantic segmentation colours every pixel by type (“cup”, “table”). Instance segmentation also tells the two cups apart.', None),
 ('Encoder–decoder', 'Squeeze the picture down to understand <i>what</i> is there, then blow it back up to say <i>where</i>, with skip connections passing the fine edges across so boundaries stay sharp.', None),
 ('Grasp = where + how', 'For a top-down grab you need a spot, an angle, how wide to open, and how good it is: (x, y, θ, w, q). In full 3D the hand can also tilt, so 6-DoF.', None),
 ('Contact-GraspNet', 'Instead of searching every possible hand pose in space, ask each visible surface point: “could a finger touch here?” If yes, predict the rest. Far fewer things to guess.', None),
],
svg='''<svg class="dg" viewBox="0 0 520 170" role="img" aria-label="U-Net: encoder downsamples, decoder upsamples, skip connections copy high-resolution features across">
<g>
<rect class="sk" x="20" y="20" width="26" height="120"/><rect class="sk" x="70" y="40" width="26" height="80"/><rect class="sk" x="120" y="60" width="26" height="40"/>
<rect class="fe" x="190" y="70" width="40" height="20"/>
<rect class="sk" x="274" y="60" width="26" height="40"/><rect class="sk" x="324" y="40" width="26" height="80"/><rect class="sk" x="374" y="20" width="26" height="120"/>
<path class="ac" d="M46 80 H70 M96 80 H120 M146 80 H190 M230 80 H274 M300 80 H324 M350 80 H374 M400 80 H430"/>
<path class="ev dash" d="M33 20 C33 5 387 5 387 20"/><path class="ev dash" d="M83 40 C83 28 337 28 337 40"/>
<rect class="bx" x="432" y="20" width="76" height="120"/><text x="440" y="75" class="sm">C logits</text><text x="440" y="92" class="sm">per pixel</text>
<text x="20" y="160" class="sm">encoder: downsample (what)</text><text x="280" y="160" class="sm">decoder: upsample (where)</text><text x="150" y="16" class="sm">skip connections keep boundaries</text>
</g></svg>''',
svgcap='Dense prediction needs output size = input size. The encoder shrinks the image to about H/8 × W/8 features; the decoder upsamples; U-Net skips copy high-resolution detail across. The output is C class logits per pixel.',
videos=['NhdzGfB1q74', 'qRLKYSLXElM'],
body=r'''
<div class="sub"><h3>1. Semantic and instance segmentation</h3>
<p><b>Semantic</b> [[p4]] [[p5]]: one class per pixel; trained with a pixel mask and pixel-wise cross-entropy; measured by <b>mean IoU</b>. The output is a vector of C logits per pixel: use <b>softmax</b> if the classes are mutually exclusive and an element-wise <b>sigmoid</b> if not. The prediction is \(\arg\max_c p_c(i,j)\).</p>
<p><b>Instance</b> [[p6]] [[p7]]: a separate mask and label for each object instance; classification + mask losses; mask AP. Mask R-CNN = Faster R-CNN + a mask head [[p15]].</p>
<p>Mask IoU uses the same formula as boxes, on pixel sets: \(|P\cap G|/|P\cup G|\) (practice Q34).</p>
<div class="ex"><b>Worked example.</b> Predicted mask 120 px, GT 100 px, overlap 80 px: IoU = 80/(120+100−80) = 80/140 = <b>0.571</b>.</div>
<p><b>Class imbalance</b> (practice Q33): if obstacles cover 5% of pixels, predicting “background” everywhere gives 95% pixel accuracy but obstacle IoU = 0 and mean IoU = (0.95 + 0)/2 = 0.475. An unweighted loss is dominated by the common class. Fixes: class weighting, focal or Dice losses, sampling.</p>
<div class="widget" data-w="imbalance"></div></div>

<div class="sub"><h3>2. Dense-prediction architecture</h3>
<p>Output size = input size, but encoder features are spatially smaller [[p9]], hence the <b>encoder–decoder</b> [[p10]]. Downsampling uses pooling or strided convolutions; upsampling uses unpooling or <b>transposed convolutions</b> [[p12]]. <b>Skip connections</b> (U-Net) copy high-resolution but semantically low-level encoder features to the decoder, preserving boundaries and fine detail [[p13]]. The same design serves depth prediction and other dense tasks [[p8]].</p>
<p>Modern models [[p16]]–[[p18]]: DeepLabv3/v3+ (CNN), Mask2Former and SegFormer (transformer), and promptable foundation models <b>SAM2 / SAM3</b> (segment from point or box prompts; SAM3 adds open-vocabulary text prompts).</p></div>

<div class="sub"><h3>3. Grasp prediction</h3>
<p>Given an image of an object, how should the robot pick it up [[p22]]? Two categories: <b>top-down (planar)</b> and <b>6-DoF</b> grasps.</p>
<ul><li>Planar grasp \((x, y, \theta, w, q)\): centre in the image, in-plane gripper angle, opening width, quality [[p23]].</li>
<li>6-DoF grasp \((x, y, z, \phi, \theta, \psi, w, q)\): 3D position + 3D orientation + width + quality [[p24]].</li></ul>
<p>Inputs usually add depth or point clouds for geometry [[p25]]. Training data [[p26]]: human labels (Cornell), simulation (Jacquard), real RGB-D + analytic grasps (GraspNet-1Billion).</p>
<div class="tw"><table><tr><th>Generative</th><th>Discriminative</th></tr><tr><td>image → grasp(s) directly</td><td>image + proposed grasp → quality (“90% chance of success”)</td></tr>
<tr><td>multi-grasp as detection (Faster R-CNN-like); <b>GG-CNN</b> predicts angle, width and quality per pixel like segmentation, so it runs in real time</td><td><b>Dex-Net 2.0</b>: slow, because cost grows with the number of candidate grasps evaluated</td></tr></table></div>
<p class="note">From [[p27]]–[[p32]]. “Generative” here means generating candidates directly, not necessarily a probabilistic generative model.</p>
<p>Top-down grasping assumes a fixed approach direction and can’t exploit arbitrary 3-D surfaces [[p33]], hence 6-DoF methods: <b>Contact-GraspNet</b> (per-point contact prediction) [[p34]]; <b>AnyGrasp</b> (practical pretrained 6-DoF detection and tracking in clutter) [[p35]]; <b>diffusion models</b> (an object has many valid grasps, so learn a <i>distribution</i>: refine noisy poses iteratively, generate diverse candidates, then filter by quality and collision, e.g. GraspGen) [[p36]] [[p37]].</p>
<p><b>Beyond geometry</b> [[p38]]: geometry-only asks <i>where can I grasp?</i> (RGB-D → feasible poses); semantic / language-conditioned asks <i>what should I grasp, and how, for the task?</i> (RGB-D + instruction → task-conditioned poses, e.g. GraspMolmo, GraspVLA, “grasp the mug by the handle”). Where to start [[p41]]: AnyGrasp (practical), GraspMolmo/GraspVLA (language), Contact-GraspNet (understanding), GraspNet-1Billion (data).</p>
<div class="exam"><b>Exam angle.</b> Q26 and Q33–34 test segmentation outputs, losses and IoU. For grasping expect definitions (planar vs 6-DoF parameters; generative vs discriminative trade-off) and a scenario: “cluttered bin, unknown objects, segmentation is unreliable: which approach?” (Contact-GraspNet or AnyGrasp on the full scene cloud).</div></div>
''',
paper=dict(title='Contact-GraspNet (Sundermeyer, Mousavian, Triebel, Fox, ICRA 2021)', sixty=r'''
<p><b>Problem.</b> 6-DoF grasping of unknown objects in clutter. Previous pipelines first <i>segment</i> the object, generate grasps on the isolated object cloud, then filter collisions with another network. That causes (1) sensitivity to segmentation errors, (2) no scene context (table, neighbours) for collisions and (3) prediction in a huge, unconstrained 6-DoF space [[P:p2]].</p>
<p><b>Key idea</b>: treat each observed 3D point as a potential <b>contact point</b> c. A grasp is \(t_g = c + \tfrac{w}{2}b + d\,a\), \(R_g = [\,b,\ a\times b,\ a\,]\) (a = approach vector, b = baseline vector, d = fixed gripper offset). Per point the network only predicts contact confidence, a, b and the width w: <b>4-DoF instead of 6-DoF + width</b>, which makes learning much easier and ties grasps to the observed geometry. It runs on the <b>full scene point cloud</b> (PointNet++), so collisions are considered during generation; segmentation is optional, only to choose the target.</p>
<p><b>Headline numbers.</b> Trained on <b>17.7M simulated grasps</b> (ACRONYM, 8,872 ShapeNet meshes), class-agnostic. Real Franka robot, 9 cluttered scenes, 51 unseen objects (Table I [[P:p6]]): success <b>90.20%</b> vs 80.39% for the segmentation + CollisionNet pipeline (62.7% for 6-DOF GraspNet), 84.31% on the first attempt, 59 vs 67 attempts. That is “over 90%”, halving the failure rate. Runtime 0.28 s per scene.</p>
<p><b>How to read it.</b> Sim results report <i>success</i> (no collision, object held after shaking) against <i>coverage</i> (% of ground-truth grasps within 2 cm of a prediction). Ablations: cropping local regions raises coverage; training on a small 5-category dataset fails to generalise; the weighted width-bin loss prevents collapse to narrow widths.</p>''',
),
tut=r'''
<p><b>1. Motivation.</b> Multi-stage pipelines (segment → per-object grasps → collision check) have many failure points: segmentation errors (over/under-segmentation) wreck the grasps; grasps generated on an isolated object can’t see the table or neighbours, so many collide; the 6-DoF search space is large and slow, unsuitable for closed-loop grasping.</p>
<p><b>2. Representation.</b> Each grasp is anchored at an observed contact point c, so its position is mostly known. The network predicts the approach and baseline directions (3 DoF of rotation) and the width w. The full pose follows from \(t_g = c + \tfrac w2 b + d a\) and \(R_g = [b, a\times b, a]\). Sampling contacts across the visible surface covers the modes of the grasp distribution.</p>
<p><b>3. Whole-scene input.</b> The full cloud includes the table and neighbouring objects, so the network learns which grasps would collide and avoids them during generation. Grasps are found even if segmentation is wrong (the under-segmented drill, Fig. 7); masks are needed only to pick which object’s grasps to execute.</p>
<p><b>4. Training and sim-to-real.</b> 17.7M physics-simulated parallel-jaw grasps on 8,872 ShapeNet meshes (ACRONYM), placed in random stable cluttered scenes and rendered as depth, class-agnostic. Noise injection helps real sensors. Transfer is shown on a real Franka Panda with a RealSense L515 and 51 unseen objects: 90.2% success.</p>
<p><b>5. Evidence.</b> Ablations: the weighted width loss is crucial (without it, widths collapse narrow); local regions increase coverage; a large, diverse dataset is essential (the small 5-category dataset fails). Comparison: 90.2% vs 80.4% (segmentation + CollisionNet) and 62.7% (6-DOF GraspNet), with more first-try successes. Remaining limits: thick objects needing near-maximum width get low confidence; small objects have low-confidence contacts; parallel-jaw only; no task semantics.</p>''',
quiz=[
 ('A per-pixel classifier for 6 mutually exclusive terrain types should use…', ['one sigmoid per image', 'softmax over 6 logits per pixel with cross-entropy', 'a box regression loss', 'triplet loss'], 1, 'Mutually exclusive classes → softmax over C logits per pixel [[p5]].'),
 ('What is the purpose of U-Net skip connections?', ['Reduce parameters', 'Copy high-resolution encoder features to the decoder to keep boundaries and details', 'Add language conditioning', 'Remove the need for upsampling'], 1, 'From [[p13]].'),
 ('Why is discriminative grasp prediction (e.g. Dex-Net 2.0) slow?', ['It uses a transformer', 'It must evaluate every candidate grasp separately, so cost grows with the number of candidates', 'It needs 6-DoF poses', 'It runs on CPUs only'], 1, 'From [[p30]].'),
],
)
