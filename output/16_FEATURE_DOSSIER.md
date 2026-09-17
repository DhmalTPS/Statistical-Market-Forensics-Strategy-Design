# EBX FEATURE FORENSICS DOSSIER
## Task 4 — Reverse Engineering of PB / VB Features

Files used: 70 (Days 1–64 and 80–85)
Feature count: 288 (PB=216, VB=72)
GPU acceleration: True

## Methodology
- T structure is investigated using within-base correlations, scale, smoothness, responsiveness, price correlation and first-valid behaviour.
- Candidate features are generated only from raw Price.
- Candidate windows tested at: 5, 10, 30, 60, 90, 120, 300, 600, 900, 1500, 1800, 3600.
- Pearson, affine beta/alpha, MAE and RMSE are calculated for the full candidate library.
- Spearman correlation is calculated only after preliminary matching shortlisting.
- Lagged correlations are calculated only for strong candidate matches.
- No feature identity is declared solely from high correlation.

## T Structure Findings

# PB

## PB1
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB1_T1`
- Scale = 0.159167
- Difference scale = 0.102291
- Smoothness = 0.645339
- Responsiveness = 0.708293
- Price correlation = 0.024246
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.205782

### T2
- Feature = `PB1_T2`
- Scale = 0.11091
- Difference scale = 0.0507143
- Smoothness = 0.458923
- Responsiveness = 0.706794
- Price correlation = 0.033634
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.220072

### T3
- Feature = `PB1_T3`
- Scale = 0.0630364
- Difference scale = 0.0168378
- Smoothness = 0.267907
- Responsiveness = 0.705980
- Price correlation = 0.056235
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.313599

### T4
- Feature = `PB1_T4`
- Scale = 0.0450724
- Difference scale = 0.00844618
- Smoothness = 0.191973
- Responsiveness = 0.706165
- Price correlation = 0.081683
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.375568

### T5
- Feature = `PB1_T5`
- Scale = 0.0363241
- Difference scale = 0.00560273
- Smoothness = 0.158114
- Responsiveness = 0.706365
- Price correlation = 0.102572
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.383486

### T6
- Feature = `PB1_T6`
- Scale = 0.0308443
- Difference scale = 0.00420263
- Smoothness = 0.137885
- Responsiveness = 0.705045
- Price correlation = 0.117059
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.350487

### T7
- Feature = `PB1_T7`
- Scale = 0.0192393
- Difference scale = 0.00167156
- Smoothness = 0.0873233
- Responsiveness = 0.704521
- Price correlation = 0.184776
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.469384

### T8
- Feature = `PB1_T8`
- Scale = 0.0130322
- Difference scale = 0.000832315
- Smoothness = 0.0631653
- Responsiveness = 0.703744
- Price correlation = 0.248391
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.584345

### T9
- Feature = `PB1_T9`
- Scale = 0.010468
- Difference scale = 0.00055651
- Smoothness = 0.0523465
- Responsiveness = 0.701990
- Price correlation = 0.311278
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.624961

### T10
- Feature = `PB1_T10`
- Scale = 0.00766163
- Difference scale = 0.000330817
- Smoothness = 0.041717
- Responsiveness = 0.696645
- Price correlation = 0.398589
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.742602

### T11
- Feature = `PB1_T11`
- Scale = 0.00712406
- Difference scale = 0.00027335
- Smoothness = 0.0394541
- Responsiveness = 0.693947
- Price correlation = 0.435864
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.637551

### T12
- Feature = `PB1_T12`
- Scale = 0.00470972
- Difference scale = 0.000135794
- Smoothness = 0.0300672
- Responsiveness = 0.674115
- Price correlation = 0.535910
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB10
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `PB10_T1`
- Scale = 0.163472
- Difference scale = 0.00251201
- Smoothness = 0.0153447
- Responsiveness = -0.011038
- Price correlation = 0.999380
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.946805

### T2
- Feature = `PB10_T2`
- Scale = 0.162901
- Difference scale = 0.00214173
- Smoothness = 0.0130645
- Responsiveness = -0.008840
- Price correlation = 0.998898
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.942382

### T3
- Feature = `PB10_T3`
- Scale = 0.161381
- Difference scale = 0.00168572
- Smoothness = 0.0102569
- Responsiveness = -0.005746
- Price correlation = 0.997205
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.938848

### T4
- Feature = `PB10_T4`
- Scale = 0.159804
- Difference scale = 0.00140676
- Smoothness = 0.00856784
- Responsiveness = -0.005192
- Price correlation = 0.994870
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.934828

### T5
- Feature = `PB10_T5`
- Scale = 0.158573
- Difference scale = 0.00126965
- Smoothness = 0.00776519
- Responsiveness = -0.005159
- Price correlation = 0.992803
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.928769

### T6
- Feature = `PB10_T6`
- Scale = 0.157494
- Difference scale = 0.00117831
- Smoothness = 0.0073141
- Responsiveness = -0.002947
- Price correlation = 0.990967
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.920128

### T7
- Feature = `PB10_T7`
- Scale = 0.154399
- Difference scale = 0.000916276
- Smoothness = 0.00585197
- Responsiveness = -0.001281
- Price correlation = 0.978126
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.922791

### T8
- Feature = `PB10_T8`
- Scale = 0.153876
- Difference scale = 0.000768828
- Smoothness = 0.00488508
- Responsiveness = -0.004837
- Price correlation = 0.956528
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.932455

### T9
- Feature = `PB10_T9`
- Scale = 0.154883
- Difference scale = 0.000700683
- Smoothness = 0.0045083
- Responsiveness = -0.003250
- Price correlation = 0.940897
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.933403

### T10
- Feature = `PB10_T10`
- Scale = 0.156524
- Difference scale = 0.000637117
- Smoothness = 0.004209
- Responsiveness = -0.003857
- Price correlation = 0.897981
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.944115

### T11
- Feature = `PB10_T11`
- Scale = 0.15652
- Difference scale = 0.000603225
- Smoothness = 0.00413715
- Responsiveness = -0.003836
- Price correlation = 0.880401
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.916548

### T12
- Feature = `PB10_T12`
- Scale = 0.143796
- Difference scale = 0.000526977
- Smoothness = 0.00364572
- Responsiveness = -0.000870
- Price correlation = 0.773851
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB11
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `PB11_T1`
- Scale = 0.164839
- Difference scale = 0.00256834
- Smoothness = 0.0152633
- Responsiveness = -0.006059
- Price correlation = 0.999431
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.950044

### T2
- Feature = `PB11_T2`
- Scale = 0.165273
- Difference scale = 0.00220259
- Smoothness = 0.01318
- Responsiveness = -0.005759
- Price correlation = 0.999030
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.945521

### T3
- Feature = `PB11_T3`
- Scale = 0.166361
- Difference scale = 0.00171841
- Smoothness = 0.0100375
- Responsiveness = -0.003097
- Price correlation = 0.997467
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.941310

### T4
- Feature = `PB11_T4`
- Scale = 0.167428
- Difference scale = 0.00146875
- Smoothness = 0.00854732
- Responsiveness = -0.003152
- Price correlation = 0.995332
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.936659

### T5
- Feature = `PB11_T5`
- Scale = 0.168291
- Difference scale = 0.00136576
- Smoothness = 0.00787439
- Responsiveness = -0.003963
- Price correlation = 0.993187
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.930563

### T6
- Feature = `PB11_T6`
- Scale = 0.168992
- Difference scale = 0.00127482
- Smoothness = 0.00742603
- Responsiveness = -0.004085
- Price correlation = 0.991001
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.922167

### T7
- Feature = `PB11_T7`
- Scale = 0.171311
- Difference scale = 0.00104789
- Smoothness = 0.00620039
- Responsiveness = -0.001856
- Price correlation = 0.977403
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.924115

### T8
- Feature = `PB11_T8`
- Scale = 0.170236
- Difference scale = 0.00087899
- Smoothness = 0.00500992
- Responsiveness = -0.002034
- Price correlation = 0.958016
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.931800

### T9
- Feature = `PB11_T9`
- Scale = 0.170617
- Difference scale = 0.000783478
- Smoothness = 0.00470084
- Responsiveness = -0.002267
- Price correlation = 0.941877
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.934479

### T10
- Feature = `PB11_T10`
- Scale = 0.17544
- Difference scale = 0.00073032
- Smoothness = 0.00433081
- Responsiveness = -0.000988
- Price correlation = 0.906442
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.951482

### T11
- Feature = `PB11_T11`
- Scale = 0.177611
- Difference scale = 0.000692763
- Smoothness = 0.00416816
- Responsiveness = -0.001022
- Price correlation = 0.885662
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.925223

### T12
- Feature = `PB11_T12`
- Scale = 0.175882
- Difference scale = 0.00062035
- Smoothness = 0.00381064
- Responsiveness = -0.000509
- Price correlation = 0.798433
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB12
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB12_T1`
- Scale = 7.95832e-05
- Difference scale = 5.11457e-05
- Smoothness = 0.645341
- Responsiveness = 0.708287
- Price correlation = 0.024222
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.205764

### T2
- Feature = `PB12_T2`
- Scale = 0.000110914
- Difference scale = 5.07138e-05
- Smoothness = 0.458933
- Responsiveness = 0.706802
- Price correlation = 0.033601
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.220060

### T3
- Feature = `PB12_T3`
- Scale = 0.000189126
- Difference scale = 5.05127e-05
- Smoothness = 0.267918
- Responsiveness = 0.705961
- Price correlation = 0.056127
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.313552

### T4
- Feature = `PB12_T4`
- Scale = 0.000270385
- Difference scale = 5.06775e-05
- Smoothness = 0.191973
- Responsiveness = 0.706123
- Price correlation = 0.081690
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.375501

### T5
- Feature = `PB12_T5`
- Scale = 0.000326975
- Difference scale = 5.04257e-05
- Smoothness = 0.15811
- Responsiveness = 0.706329
- Price correlation = 0.102537
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.383497

### T6
- Feature = `PB12_T6`
- Scale = 0.000370066
- Difference scale = 5.04333e-05
- Smoothness = 0.137887
- Responsiveness = 0.704983
- Price correlation = 0.117014
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.350434

### T7
- Feature = `PB12_T7`
- Scale = 0.000577306
- Difference scale = 5.01521e-05
- Smoothness = 0.0873454
- Responsiveness = 0.704477
- Price correlation = 0.184635
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.469295

### T8
- Feature = `PB12_T8`
- Scale = 0.00078195
- Difference scale = 4.99484e-05
- Smoothness = 0.0631521
- Responsiveness = 0.703579
- Price correlation = 0.247974
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.584326

### T9
- Feature = `PB12_T9`
- Scale = 0.000942091
- Difference scale = 5.01048e-05
- Smoothness = 0.0523233
- Responsiveness = 0.701807
- Price correlation = 0.311115
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.624861

### T10
- Feature = `PB12_T10`
- Scale = 0.00115023
- Difference scale = 4.9655e-05
- Smoothness = 0.0417227
- Responsiveness = 0.696590
- Price correlation = 0.398523
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.742585

### T11
- Feature = `PB12_T11`
- Scale = 0.00128224
- Difference scale = 4.92413e-05
- Smoothness = 0.0394644
- Responsiveness = 0.693871
- Price correlation = 0.435688
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.638055

### T12
- Feature = `PB12_T12`
- Scale = 0.00169766
- Difference scale = 4.89401e-05
- Smoothness = 0.0300656
- Responsiveness = 0.673764
- Price correlation = 0.536472
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB13
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB13_T1`
- Scale = 7.95816e-05
- Difference scale = 5.11495e-05
- Smoothness = 0.645366
- Responsiveness = 0.708372
- Price correlation = 0.024190
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.207269

### T2
- Feature = `PB13_T2`
- Scale = 0.000110962
- Difference scale = 5.07158e-05
- Smoothness = 0.458775
- Responsiveness = 0.707143
- Price correlation = 0.034052
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.222379

### T3
- Feature = `PB13_T3`
- Scale = 0.000189344
- Difference scale = 5.05363e-05
- Smoothness = 0.267935
- Responsiveness = 0.706594
- Price correlation = 0.057147
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.317327

### T4
- Feature = `PB13_T4`
- Scale = 0.000270936
- Difference scale = 5.07211e-05
- Smoothness = 0.192072
- Responsiveness = 0.707457
- Price correlation = 0.082695
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.380085

### T5
- Feature = `PB13_T5`
- Scale = 0.000328526
- Difference scale = 5.05259e-05
- Smoothness = 0.157883
- Responsiveness = 0.708520
- Price correlation = 0.102031
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.390018

### T6
- Feature = `PB13_T6`
- Scale = 0.000371479
- Difference scale = 5.05272e-05
- Smoothness = 0.137751
- Responsiveness = 0.708109
- Price correlation = 0.119412
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.357573

### T7
- Feature = `PB13_T7`
- Scale = 0.000576222
- Difference scale = 5.03889e-05
- Smoothness = 0.0871232
- Responsiveness = 0.710566
- Price correlation = 0.186222
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.479897

### T8
- Feature = `PB13_T8`
- Scale = 0.00079101
- Difference scale = 5.02274e-05
- Smoothness = 0.0635274
- Responsiveness = 0.712643
- Price correlation = 0.241565
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.597025

### T9
- Feature = `PB13_T9`
- Scale = 0.000934774
- Difference scale = 5.02477e-05
- Smoothness = 0.0525721
- Responsiveness = 0.715544
- Price correlation = 0.299798
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.647203

### T10
- Feature = `PB13_T10`
- Scale = 0.00115519
- Difference scale = 5.00152e-05
- Smoothness = 0.0419772
- Responsiveness = 0.719494
- Price correlation = 0.365019
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.764773

### T11
- Feature = `PB13_T11`
- Scale = 0.00126655
- Difference scale = 4.96482e-05
- Smoothness = 0.038909
- Responsiveness = 0.721418
- Price correlation = 0.393853
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 0.682949

### T12
- Feature = `PB13_T12`
- Scale = 0.00165554
- Difference scale = 4.8525e-05
- Smoothness = 0.0306968
- Responsiveness = 0.733308
- Price correlation = 0.562828
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB14
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB14_T1`
- Scale = 0.609231
- Difference scale = 0.446242
- Smoothness = 0.725063
- Responsiveness = 0.510294
- Price correlation = 0.022902
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.179110

### T2
- Feature = `PB14_T2`
- Scale = 0.434418
- Difference scale = 0.221976
- Smoothness = 0.508992
- Responsiveness = 0.561079
- Price correlation = 0.032050
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.201437

### T3
- Feature = `PB14_T3`
- Scale = 0.251973
- Difference scale = 0.0717503
- Smoothness = 0.287425
- Responsiveness = 0.624785
- Price correlation = 0.053876
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.305687

### T4
- Feature = `PB14_T4`
- Scale = 0.177596
- Difference scale = 0.0356668
- Smoothness = 0.203808
- Responsiveness = 0.645338
- Price correlation = 0.076948
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.370219

### T5
- Feature = `PB14_T5`
- Scale = 0.145364
- Difference scale = 0.023928
- Smoothness = 0.167394
- Responsiveness = 0.654399
- Price correlation = 0.092264
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.381005

### T6
- Feature = `PB14_T6`
- Scale = 0.125133
- Difference scale = 0.0179581
- Smoothness = 0.14535
- Responsiveness = 0.657528
- Price correlation = 0.109914
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.350635

### T7
- Feature = `PB14_T7`
- Scale = 0.0790811
- Difference scale = 0.00719754
- Smoothness = 0.092171
- Responsiveness = 0.668772
- Price correlation = 0.168910
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.468342

### T8
- Feature = `PB14_T8`
- Scale = 0.0556871
- Difference scale = 0.0036171
- Smoothness = 0.0655075
- Responsiveness = 0.672428
- Price correlation = 0.237606
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.581773

### T9
- Feature = `PB14_T9`
- Scale = 0.0454741
- Difference scale = 0.00243672
- Smoothness = 0.0541486
- Responsiveness = 0.676044
- Price correlation = 0.292764
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.628400

### T10
- Feature = `PB14_T10`
- Scale = 0.034891
- Difference scale = 0.00146487
- Smoothness = 0.0430933
- Responsiveness = 0.676948
- Price correlation = 0.393300
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.742679

### T11
- Feature = `PB14_T11`
- Scale = 0.0318457
- Difference scale = 0.00121685
- Smoothness = 0.0396204
- Responsiveness = 0.675423
- Price correlation = 0.429510
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.651090

### T12
- Feature = `PB14_T12`
- Scale = 0.0212839
- Difference scale = 0.000626882
- Smoothness = 0.030458
- Responsiveness = 0.672432
- Price correlation = 0.599977
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB15
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB15_T1`
- Scale = 43.611
- Difference scale = 41.3429
- Smoothness = 0.953044
- Responsiveness = 0.594904
- Price correlation = 0.017476
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.258760

### T2
- Feature = `PB15_T2`
- Scale = 39.1295
- Difference scale = 27.3166
- Smoothness = 0.702251
- Responsiveness = 0.664130
- Price correlation = 0.025560
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.300482

### T3
- Feature = `PB15_T3`
- Scale = 34.935
- Difference scale = 14.6414
- Smoothness = 0.421209
- Responsiveness = 0.762258
- Price correlation = 0.051129
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.432980

### T4
- Feature = `PB15_T4`
- Scale = 33.3055
- Difference scale = 10.0848
- Smoothness = 0.304361
- Responsiveness = 0.803520
- Price correlation = 0.065904
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.508517

### T5
- Feature = `PB15_T5`
- Scale = 32.5308
- Difference scale = 8.15587
- Smoothness = 0.252276
- Responsiveness = 0.823524
- Price correlation = 0.082695
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.527233

### T6
- Feature = `PB15_T6`
- Scale = 32.0398
- Difference scale = 7.02975
- Smoothness = 0.220851
- Responsiveness = 0.835937
- Price correlation = 0.093771
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.513078

### T7
- Feature = `PB15_T7`
- Scale = 31.3797
- Difference scale = 4.35606
- Smoothness = 0.139098
- Responsiveness = 0.872201
- Price correlation = 0.141179
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.654389

### T8
- Feature = `PB15_T8`
- Scale = 30.8837
- Difference scale = 3.07175
- Smoothness = 0.0993962
- Responsiveness = 0.890439
- Price correlation = 0.201184
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.767694

### T9
- Feature = `PB15_T9`
- Scale = 30.6095
- Difference scale = 2.50405
- Smoothness = 0.0811467
- Responsiveness = 0.895183
- Price correlation = 0.241412
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.809259

### T10
- Feature = `PB15_T10`
- Scale = 30.0765
- Difference scale = 1.92631
- Smoothness = 0.0635268
- Responsiveness = 0.906053
- Price correlation = 0.318612
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.886674

### T11
- Feature = `PB15_T11`
- Scale = 29.9651
- Difference scale = 1.74613
- Smoothness = 0.0580836
- Responsiveness = 0.911232
- Price correlation = 0.361750
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.845065

### T12
- Feature = `PB15_T12`
- Scale = 28.7722
- Difference scale = 1.22241
- Smoothness = 0.0419115
- Responsiveness = 0.932954
- Price correlation = 0.554890
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB16
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB16_T1`
- Scale = 35.1267
- Difference scale = 19.9362
- Smoothness = 0.567579
- Responsiveness = 0.408937
- Price correlation = 0.020813
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.258611

### T2
- Feature = `PB16_T2`
- Scale = 34.8401
- Difference scale = 13.8549
- Smoothness = 0.397333
- Responsiveness = 0.431669
- Price correlation = 0.028538
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.300531

### T3
- Feature = `PB16_T3`
- Scale = 33.5259
- Difference scale = 7.89839
- Smoothness = 0.235349
- Responsiveness = 0.461244
- Price correlation = 0.053017
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.432676

### T4
- Feature = `PB16_T4`
- Scale = 32.5945
- Difference scale = 5.54834
- Smoothness = 0.171003
- Responsiveness = 0.475816
- Price correlation = 0.067063
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.507969

### T5
- Feature = `PB16_T5`
- Scale = 32.0179
- Difference scale = 4.51705
- Smoothness = 0.142112
- Responsiveness = 0.482388
- Price correlation = 0.083630
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.526794

### T6
- Feature = `PB16_T6`
- Scale = 31.6803
- Difference scale = 3.90483
- Smoothness = 0.123865
- Responsiveness = 0.486003
- Price correlation = 0.094782
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.512527

### T7
- Feature = `PB16_T7`
- Scale = 31.2358
- Difference scale = 2.4338
- Smoothness = 0.0787523
- Responsiveness = 0.501569
- Price correlation = 0.141734
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.654124

### T8
- Feature = `PB16_T8`
- Scale = 30.8093
- Difference scale = 1.72939
- Smoothness = 0.0562564
- Responsiveness = 0.509685
- Price correlation = 0.201617
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.767465

### T9
- Feature = `PB16_T9`
- Scale = 30.5577
- Difference scale = 1.40793
- Smoothness = 0.0456511
- Responsiveness = 0.514262
- Price correlation = 0.241739
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.809128

### T10
- Feature = `PB16_T10`
- Scale = 30.0535
- Difference scale = 1.09082
- Smoothness = 0.0363235
- Responsiveness = 0.522259
- Price correlation = 0.318691
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.886653

### T11
- Feature = `PB16_T11`
- Scale = 29.9411
- Difference scale = 0.987043
- Smoothness = 0.0329347
- Responsiveness = 0.523145
- Price correlation = 0.361885
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.844984

### T12
- Feature = `PB16_T12`
- Scale = 28.7633
- Difference scale = 0.690439
- Smoothness = 0.0237654
- Responsiveness = 0.533665
- Price correlation = 0.555086
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB17
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB17_T1`
- Scale = 43.611
- Difference scale = 41.3429
- Smoothness = 0.953044
- Responsiveness = 0.594904
- Price correlation = 0.017476
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.258760

### T2
- Feature = `PB17_T2`
- Scale = 39.1295
- Difference scale = 27.3166
- Smoothness = 0.702251
- Responsiveness = 0.664130
- Price correlation = 0.025560
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.300482

### T3
- Feature = `PB17_T3`
- Scale = 34.935
- Difference scale = 14.6414
- Smoothness = 0.421209
- Responsiveness = 0.762258
- Price correlation = 0.051129
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.432980

### T4
- Feature = `PB17_T4`
- Scale = 33.3055
- Difference scale = 10.0848
- Smoothness = 0.304361
- Responsiveness = 0.803520
- Price correlation = 0.065904
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.508517

### T5
- Feature = `PB17_T5`
- Scale = 32.5308
- Difference scale = 8.15587
- Smoothness = 0.252276
- Responsiveness = 0.823524
- Price correlation = 0.082695
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.527233

### T6
- Feature = `PB17_T6`
- Scale = 32.0398
- Difference scale = 7.02975
- Smoothness = 0.220851
- Responsiveness = 0.835937
- Price correlation = 0.093771
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.513078

### T7
- Feature = `PB17_T7`
- Scale = 31.3797
- Difference scale = 4.35606
- Smoothness = 0.139098
- Responsiveness = 0.872201
- Price correlation = 0.141179
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.654389

### T8
- Feature = `PB17_T8`
- Scale = 30.8837
- Difference scale = 3.07175
- Smoothness = 0.0993962
- Responsiveness = 0.890439
- Price correlation = 0.201184
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.767694

### T9
- Feature = `PB17_T9`
- Scale = 30.6095
- Difference scale = 2.50405
- Smoothness = 0.0811467
- Responsiveness = 0.895183
- Price correlation = 0.241412
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.809259

### T10
- Feature = `PB17_T10`
- Scale = 30.0765
- Difference scale = 1.92631
- Smoothness = 0.0635268
- Responsiveness = 0.906053
- Price correlation = 0.318612
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.886674

### T11
- Feature = `PB17_T11`
- Scale = 29.9651
- Difference scale = 1.74613
- Smoothness = 0.0580836
- Responsiveness = 0.911232
- Price correlation = 0.361750
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.845065

### T12
- Feature = `PB17_T12`
- Scale = 28.7722
- Difference scale = 1.22241
- Smoothness = 0.0419115
- Responsiveness = 0.932954
- Price correlation = 0.554890
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB18
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB18_T1`
- Scale = 92.016
- Difference scale = 92.6891
- Smoothness = 1.00905
- Responsiveness = 0.674160
- Price correlation = 0.018469
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.269549

### T2
- Feature = `PB18_T2`
- Scale = 104.397
- Difference scale = 79.7
- Smoothness = 0.766009
- Responsiveness = 0.748263
- Price correlation = 0.024768
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.306950

### T3
- Feature = `PB18_T3`
- Scale = 112.869
- Difference scale = 51.9791
- Smoothness = 0.458512
- Responsiveness = 0.830483
- Price correlation = 0.043242
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.433302

### T4
- Feature = `PB18_T4`
- Scale = 114.869
- Difference scale = 37.6285
- Smoothness = 0.328657
- Responsiveness = 0.852233
- Price correlation = 0.060996
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.506450

### T5
- Feature = `PB18_T5`
- Scale = 115.307
- Difference scale = 30.8306
- Smoothness = 0.26747
- Responsiveness = 0.862695
- Price correlation = 0.072692
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.521891

### T6
- Feature = `PB18_T6`
- Scale = 115.711
- Difference scale = 26.8737
- Smoothness = 0.231445
- Responsiveness = 0.869014
- Price correlation = 0.082937
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.506475

### T7
- Feature = `PB18_T7`
- Scale = 116.459
- Difference scale = 16.7927
- Smoothness = 0.145981
- Responsiveness = 0.884345
- Price correlation = 0.132578
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.653074

### T8
- Feature = `PB18_T8`
- Scale = 115.38
- Difference scale = 11.8974
- Smoothness = 0.103489
- Responsiveness = 0.892056
- Price correlation = 0.182231
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.775319

### T9
- Feature = `PB18_T9`
- Scale = 115.002
- Difference scale = 9.69829
- Smoothness = 0.084134
- Responsiveness = 0.893280
- Price correlation = 0.229270
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.823405

### T10
- Feature = `PB18_T10`
- Scale = 113.249
- Difference scale = 7.4293
- Smoothness = 0.0656351
- Responsiveness = 0.899176
- Price correlation = 0.289547
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.901111

### T11
- Feature = `PB18_T11`
- Scale = 112.492
- Difference scale = 6.78642
- Smoothness = 0.0606635
- Responsiveness = 0.903325
- Price correlation = 0.318300
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.866665

### T12
- Feature = `PB18_T12`
- Scale = 109.233
- Difference scale = 4.65091
- Smoothness = 0.0440184
- Responsiveness = 0.919333
- Price correlation = 0.486506
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB2
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB2_T1`
- Scale = 0.896237
- Difference scale = 0.702738
- Smoothness = 0.787644
- Responsiveness = 0.410720
- Price correlation = 0.000454
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.001082

### T2
- Feature = `PB2_T2`
- Scale = 0.317329
- Difference scale = 0.174936
- Smoothness = 0.557997
- Responsiveness = 0.408525
- Price correlation = 0.000886
- First valid index = 20
- Last valid index = 23339
- Mean pairwise Pearson = 0.001725

### T3
- Feature = `PB2_T3`
- Scale = 0.0606329
- Difference scale = 0.0194758
- Smoothness = 0.326806
- Responsiveness = 0.407263
- Price correlation = 0.000604
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.001455

### T4
- Feature = `PB2_T4`
- Scale = 0.0210615
- Difference scale = 0.00479648
- Smoothness = 0.23183
- Responsiveness = 0.407665
- Price correlation = 0.001866
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.050824

### T5
- Feature = `PB2_T5`
- Scale = 0.0114723
- Difference scale = 0.00215359
- Smoothness = 0.191491
- Responsiveness = 0.408883
- Price correlation = 0.000626
- First valid index = 180
- Last valid index = 23339
- Mean pairwise Pearson = 0.080982

### T6
- Feature = `PB2_T6`
- Scale = 0.00720497
- Difference scale = 0.00120511
- Smoothness = 0.16769
- Responsiveness = 0.407447
- Price correlation = 0.002260
- First valid index = 240
- Last valid index = 23339
- Mean pairwise Pearson = -0.000176

### T7
- Feature = `PB2_T7`
- Scale = 0.00182921
- Difference scale = 0.000190796
- Smoothness = 0.10518
- Responsiveness = 0.407635
- Price correlation = 0.017515
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.005664

### T8
- Feature = `PB2_T8`
- Scale = 0.000623231
- Difference scale = 4.7385e-05
- Smoothness = 0.076607
- Responsiveness = 0.405978
- Price correlation = 0.030576
- First valid index = 1200
- Last valid index = 23339
- Mean pairwise Pearson = 0.103926

### T9
- Feature = `PB2_T9`
- Scale = 0.000323449
- Difference scale = 2.10197e-05
- Smoothness = 0.062872
- Responsiveness = 0.403067
- Price correlation = 0.044724
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.075436

### T10
- Feature = `PB2_T10`
- Scale = 0.000152489
- Difference scale = 7.52782e-06
- Smoothness = 0.0492025
- Responsiveness = 0.395618
- Price correlation = 0.053142
- First valid index = 3000
- Last valid index = 23339
- Mean pairwise Pearson = 0.356469

### T11
- Feature = `PB2_T11`
- Scale = 0.000116889
- Difference scale = 5.20596e-06
- Smoothness = 0.0453134
- Responsiveness = 0.395050
- Price correlation = 0.033715
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = -0.028750

### T12
- Feature = `PB2_T12`
- Scale = 3.99108e-05
- Difference scale = 1.27851e-06
- Smoothness = 0.0321949
- Responsiveness = 0.387071
- Price correlation = 0.232740
- First valid index = 7200
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB3
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB3_T1`
- Scale = 21.2817
- Difference scale = 13.4588
- Smoothness = 0.626918
- Responsiveness = 0.791490
- Price correlation = 0.032912
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.300270

### T2
- Feature = `PB3_T2`
- Scale = 15.197
- Difference scale = 7.02342
- Smoothness = 0.46002
- Responsiveness = 0.853842
- Price correlation = 0.044538
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.325456

### T3
- Feature = `PB3_T3`
- Scale = 8.89366
- Difference scale = 2.43636
- Smoothness = 0.276866
- Responsiveness = 0.910018
- Price correlation = 0.077463
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.409798

### T4
- Feature = `PB3_T4`
- Scale = 6.33254
- Difference scale = 1.23504
- Smoothness = 0.198123
- Responsiveness = 0.929686
- Price correlation = 0.104585
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.426548

### T5
- Feature = `PB3_T5`
- Scale = 5.25705
- Difference scale = 0.829052
- Smoothness = 0.161831
- Responsiveness = 0.937848
- Price correlation = 0.127148
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.392039

### T6
- Feature = `PB3_T6`
- Scale = 4.68511
- Difference scale = 0.625444
- Smoothness = 0.138609
- Responsiveness = 0.942755
- Price correlation = 0.157732
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.324125

### T7
- Feature = `PB3_T7`
- Scale = 3.33514
- Difference scale = 0.253158
- Smoothness = 0.0772048
- Responsiveness = 0.950995
- Price correlation = 0.227909
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.351788

### T8
- Feature = `PB3_T8`
- Scale = 3.06003
- Difference scale = 0.126514
- Smoothness = 0.0421491
- Responsiveness = 0.956324
- Price correlation = 0.276824
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.507145

### T9
- Feature = `PB3_T9`
- Scale = 3.24621
- Difference scale = 0.0843316
- Smoothness = 0.0259594
- Responsiveness = 0.958477
- Price correlation = 0.311975
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.632943

### T10
- Feature = `PB3_T10`
- Scale = 3.7284
- Difference scale = 0.0497635
- Smoothness = 0.0136615
- Responsiveness = 0.958154
- Price correlation = 0.377411
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.871862

### T11
- Feature = `PB3_T11`
- Scale = 4.00579
- Difference scale = 0.041357
- Smoothness = 0.0107734
- Responsiveness = 0.959649
- Price correlation = 0.357809
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.864895

### T12
- Feature = `PB3_T12`
- Scale = 5.2585
- Difference scale = 0.0198046
- Smoothness = 0.00361617
- Responsiveness = 0.965872
- Price correlation = 0.167566
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB4
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB4_T1`
- Scale = 0.795834
- Difference scale = 0.511457
- Smoothness = 0.645339
- Responsiveness = 0.708293
- Price correlation = 0.024246
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.205782

### T2
- Feature = `PB4_T2`
- Scale = 1.1091
- Difference scale = 0.507143
- Smoothness = 0.458923
- Responsiveness = 0.706794
- Price correlation = 0.033634
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.220072

### T3
- Feature = `PB4_T3`
- Scale = 1.89109
- Difference scale = 0.505133
- Smoothness = 0.267907
- Responsiveness = 0.705980
- Price correlation = 0.056235
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.313599

### T4
- Feature = `PB4_T4`
- Scale = 2.70434
- Difference scale = 0.506771
- Smoothness = 0.191973
- Responsiveness = 0.706165
- Price correlation = 0.081683
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.375568

### T5
- Feature = `PB4_T5`
- Scale = 3.26917
- Difference scale = 0.504245
- Smoothness = 0.158114
- Responsiveness = 0.706365
- Price correlation = 0.102572
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.383486

### T6
- Feature = `PB4_T6`
- Scale = 3.70132
- Difference scale = 0.504315
- Smoothness = 0.137885
- Responsiveness = 0.705045
- Price correlation = 0.117059
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.350487

### T7
- Feature = `PB4_T7`
- Scale = 5.77179
- Difference scale = 0.501469
- Smoothness = 0.0873233
- Responsiveness = 0.704521
- Price correlation = 0.184776
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.469384

### T8
- Feature = `PB4_T8`
- Scale = 7.81934
- Difference scale = 0.499389
- Smoothness = 0.0631653
- Responsiveness = 0.703744
- Price correlation = 0.248391
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.584345

### T9
- Feature = `PB4_T9`
- Scale = 9.42119
- Difference scale = 0.500859
- Smoothness = 0.0523465
- Responsiveness = 0.701990
- Price correlation = 0.311278
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.624961

### T10
- Feature = `PB4_T10`
- Scale = 11.4924
- Difference scale = 0.496225
- Smoothness = 0.041717
- Responsiveness = 0.696645
- Price correlation = 0.398589
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.742602

### T11
- Feature = `PB4_T11`
- Scale = 12.8233
- Difference scale = 0.49203
- Smoothness = 0.0394541
- Responsiveness = 0.693947
- Price correlation = 0.435864
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.637551

### T12
- Feature = `PB4_T12`
- Scale = 16.955
- Difference scale = 0.488859
- Smoothness = 0.0300672
- Responsiveness = 0.674115
- Price correlation = 0.535910
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB5
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB5_T1`
- Scale = 0.00795832
- Difference scale = 0.00511457
- Smoothness = 0.645341
- Responsiveness = 0.708287
- Price correlation = 0.024222
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.205764

### T2
- Feature = `PB5_T2`
- Scale = 0.0110914
- Difference scale = 0.00507138
- Smoothness = 0.458933
- Responsiveness = 0.706802
- Price correlation = 0.033601
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.220060

### T3
- Feature = `PB5_T3`
- Scale = 0.0189126
- Difference scale = 0.00505127
- Smoothness = 0.267918
- Responsiveness = 0.705961
- Price correlation = 0.056127
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.313552

### T4
- Feature = `PB5_T4`
- Scale = 0.0270385
- Difference scale = 0.00506775
- Smoothness = 0.191973
- Responsiveness = 0.706123
- Price correlation = 0.081690
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.375501

### T5
- Feature = `PB5_T5`
- Scale = 0.0326975
- Difference scale = 0.00504257
- Smoothness = 0.15811
- Responsiveness = 0.706329
- Price correlation = 0.102537
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.383497

### T6
- Feature = `PB5_T6`
- Scale = 0.0370066
- Difference scale = 0.00504333
- Smoothness = 0.137887
- Responsiveness = 0.704983
- Price correlation = 0.117014
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.350434

### T7
- Feature = `PB5_T7`
- Scale = 0.0577306
- Difference scale = 0.00501521
- Smoothness = 0.0873454
- Responsiveness = 0.704477
- Price correlation = 0.184635
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.469295

### T8
- Feature = `PB5_T8`
- Scale = 0.078195
- Difference scale = 0.00499484
- Smoothness = 0.0631521
- Responsiveness = 0.703579
- Price correlation = 0.247974
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.584326

### T9
- Feature = `PB5_T9`
- Scale = 0.0942091
- Difference scale = 0.00501048
- Smoothness = 0.0523233
- Responsiveness = 0.701807
- Price correlation = 0.311115
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.624861

### T10
- Feature = `PB5_T10`
- Scale = 0.115023
- Difference scale = 0.0049655
- Smoothness = 0.0417227
- Responsiveness = 0.696590
- Price correlation = 0.398523
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.742585

### T11
- Feature = `PB5_T11`
- Scale = 0.128224
- Difference scale = 0.00492413
- Smoothness = 0.0394644
- Responsiveness = 0.693871
- Price correlation = 0.435688
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.638055

### T12
- Feature = `PB5_T12`
- Scale = 0.169766
- Difference scale = 0.00489401
- Smoothness = 0.0300656
- Responsiveness = 0.673764
- Price correlation = 0.536472
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB6
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB6_T1`
- Scale = 0.000196807
- Difference scale = 4.74078e-05
- Smoothness = 0.244957
- Responsiveness = 0.550985
- Price correlation = 0.037880
- First valid index = 13
- Last valid index = 23339
- Mean pairwise Pearson = 0.075640

### T2
- Feature = `PB6_T2`
- Scale = 0.000135878
- Difference scale = 1.61317e-05
- Smoothness = 0.118882
- Responsiveness = 0.260226
- Price correlation = 0.052661
- First valid index = 28
- Last valid index = 23339
- Mean pairwise Pearson = 0.059305

### T3
- Feature = `PB6_T3`
- Scale = 7.54009e-05
- Difference scale = 3.05514e-06
- Smoothness = 0.0393093
- Responsiveness = 0.057434
- Price correlation = 0.095822
- First valid index = 88
- Last valid index = 23339
- Mean pairwise Pearson = 0.153131

### T4
- Feature = `PB6_T4`
- Scale = 5.29348e-05
- Difference scale = 1.04545e-06
- Smoothness = 0.0196252
- Responsiveness = 0.019028
- Price correlation = 0.134403
- First valid index = 178
- Last valid index = 23339
- Mean pairwise Pearson = 0.206540

### T5
- Feature = `PB6_T5`
- Scale = 4.30463e-05
- Difference scale = 5.53769e-07
- Smoothness = 0.0130837
- Responsiveness = 0.007992
- Price correlation = 0.165260
- First valid index = 268
- Last valid index = 23339
- Mean pairwise Pearson = 0.175130

### T6
- Feature = `PB6_T6`
- Scale = 3.7202e-05
- Difference scale = 3.55939e-07
- Smoothness = 0.00981924
- Responsiveness = 0.004679
- Price correlation = 0.190375
- First valid index = 358
- Last valid index = 23339
- Mean pairwise Pearson = 0.095997

### T7
- Feature = `PB6_T7`
- Scale = 2.27027e-05
- Difference scale = 9.0617e-08
- Smoothness = 0.00402728
- Responsiveness = 0.001108
- Price correlation = 0.302253
- First valid index = 898
- Last valid index = 23339
- Mean pairwise Pearson = 0.231159

### T8
- Feature = `PB6_T8`
- Scale = 1.52809e-05
- Difference scale = 3.0632e-08
- Smoothness = 0.00206606
- Responsiveness = -0.002027
- Price correlation = 0.400650
- First valid index = 1798
- Last valid index = 23339
- Mean pairwise Pearson = 0.426739

### T9
- Feature = `PB6_T9`
- Scale = 1.28106e-05
- Difference scale = 1.67059e-08
- Smoothness = 0.00142014
- Responsiveness = -0.001940
- Price correlation = 0.459750
- First valid index = 2698
- Last valid index = 23339
- Mean pairwise Pearson = 0.521410

### T10
- Feature = `PB6_T10`
- Scale = 8.71233e-06
- Difference scale = 7.5578e-09
- Smoothness = 0.000882983
- Responsiveness = -0.001154
- Price correlation = 0.548889
- First valid index = 4498
- Last valid index = 23339
- Mean pairwise Pearson = 0.711300

### T11
- Feature = `PB6_T11`
- Scale = 7.55479e-06
- Difference scale = 5.68834e-09
- Smoothness = 0.000772269
- Responsiveness = -0.001762
- Price correlation = 0.584170
- First valid index = 5398
- Last valid index = 23339
- Mean pairwise Pearson = 0.614369

### T12
- Feature = `PB6_T12`
- Scale = 3.3128e-06
- Difference scale = 1.69862e-09
- Smoothness = 0.000522224
- Responsiveness = -0.002540
- Price correlation = 0.578087
- First valid index = 10798
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB7
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB7_T1`
- Scale = 1.15652
- Difference scale = 1.13017
- Smoothness = 0.97786
- Responsiveness = 0.682832
- Price correlation = 0.018513
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.274293

### T2
- Feature = `PB7_T2`
- Scale = 1.25767
- Difference scale = 0.917142
- Smoothness = 0.729712
- Responsiveness = 0.762979
- Price correlation = 0.026426
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.314613

### T3
- Feature = `PB7_T3`
- Scale = 1.35626
- Difference scale = 0.604144
- Smoothness = 0.446624
- Responsiveness = 0.838307
- Price correlation = 0.043759
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.442354

### T4
- Feature = `PB7_T4`
- Scale = 1.38256
- Difference scale = 0.446278
- Smoothness = 0.323447
- Responsiveness = 0.861435
- Price correlation = 0.061534
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.514706

### T5
- Feature = `PB7_T5`
- Scale = 1.3896
- Difference scale = 0.368812
- Smoothness = 0.264582
- Responsiveness = 0.870683
- Price correlation = 0.072744
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.530490

### T6
- Feature = `PB7_T6`
- Scale = 1.39673
- Difference scale = 0.321471
- Smoothness = 0.230186
- Responsiveness = 0.875461
- Price correlation = 0.084210
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.517009

### T7
- Feature = `PB7_T7`
- Scale = 1.41021
- Difference scale = 0.203899
- Smoothness = 0.146029
- Responsiveness = 0.890910
- Price correlation = 0.136272
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.661879

### T8
- Feature = `PB7_T8`
- Scale = 1.40182
- Difference scale = 0.145292
- Smoothness = 0.103408
- Responsiveness = 0.897870
- Price correlation = 0.185917
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.781248

### T9
- Feature = `PB7_T9`
- Scale = 1.4006
- Difference scale = 0.118072
- Smoothness = 0.0841851
- Responsiveness = 0.900047
- Price correlation = 0.231933
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.831237

### T10
- Feature = `PB7_T10`
- Scale = 1.3813
- Difference scale = 0.0914195
- Smoothness = 0.065626
- Responsiveness = 0.904939
- Price correlation = 0.293429
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.904412

### T11
- Feature = `PB7_T11`
- Scale = 1.377
- Difference scale = 0.08261
- Smoothness = 0.0604191
- Responsiveness = 0.907838
- Price correlation = 0.315203
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.875522

### T12
- Feature = `PB7_T12`
- Scale = 1.3331
- Difference scale = 0.0570804
- Smoothness = 0.043728
- Responsiveness = 0.928682
- Price correlation = 0.496848
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB8
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_INCREASES_WITH_T**

### T1
- Feature = `PB8_T1`
- Scale = 31.0006
- Difference scale = 30.5504
- Smoothness = 0.984964
- Responsiveness = 0.610670
- Price correlation = 0.036294
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.277140

### T2
- Feature = `PB8_T2`
- Scale = 32.8636
- Difference scale = 24.5898
- Smoothness = 0.747704
- Responsiveness = 0.657413
- Price correlation = 0.039612
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.318035

### T3
- Feature = `PB8_T3`
- Scale = 34.0608
- Difference scale = 16.061
- Smoothness = 0.47226
- Responsiveness = 0.691654
- Price correlation = 0.054822
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.447945

### T4
- Feature = `PB8_T4`
- Scale = 34.3826
- Difference scale = 12.0069
- Smoothness = 0.350131
- Responsiveness = 0.702720
- Price correlation = 0.068450
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.521240

### T5
- Feature = `PB8_T5`
- Scale = 34.4494
- Difference scale = 10.0529
- Smoothness = 0.291393
- Responsiveness = 0.708117
- Price correlation = 0.081127
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.536937

### T6
- Feature = `PB8_T6`
- Scale = 34.4816
- Difference scale = 8.82334
- Smoothness = 0.254771
- Responsiveness = 0.708398
- Price correlation = 0.088024
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.522569

### T7
- Feature = `PB8_T7`
- Scale = 34.7728
- Difference scale = 5.75102
- Smoothness = 0.165986
- Responsiveness = 0.719171
- Price correlation = 0.138992
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.671647

### T8
- Feature = `PB8_T8`
- Scale = 34.8219
- Difference scale = 4.1593
- Smoothness = 0.118928
- Responsiveness = 0.726397
- Price correlation = 0.190085
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.792657

### T9
- Feature = `PB8_T9`
- Scale = 34.8538
- Difference scale = 3.41265
- Smoothness = 0.0970406
- Responsiveness = 0.730694
- Price correlation = 0.224745
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.841418

### T10
- Feature = `PB8_T10`
- Scale = 34.6876
- Difference scale = 2.65479
- Smoothness = 0.0768172
- Responsiveness = 0.744261
- Price correlation = 0.309847
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.917439

### T11
- Feature = `PB8_T11`
- Scale = 34.5829
- Difference scale = 2.39814
- Smoothness = 0.0697026
- Responsiveness = 0.746340
- Price correlation = 0.324773
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.890951

### T12
- Feature = `PB8_T12`
- Scale = 33.8498
- Difference scale = 1.67879
- Smoothness = 0.0493597
- Responsiveness = 0.762560
- Price correlation = 0.511030
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## PB9
- T pattern: **RESPONSIVENESS_NON_MONOTONIC**

### T1
- Feature = `PB9_T1`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T2
- Feature = `PB9_T2`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T3
- Feature = `PB9_T3`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T4
- Feature = `PB9_T4`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T5
- Feature = `PB9_T5`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T6
- Feature = `PB9_T6`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T7
- Feature = `PB9_T7`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T8
- Feature = `PB9_T8`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T9
- Feature = `PB9_T9`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T10
- Feature = `PB9_T10`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T11
- Feature = `PB9_T11`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = 1.000000

### T12
- Feature = `PB9_T12`
- Scale = 0.164162
- Difference scale = 0.00359131
- Smoothness = 0.0217144
- Responsiveness = -0.014072
- Price correlation = 0.999764
- First valid index = 1
- Last valid index = 23339
- Mean pairwise Pearson = nan

# VB

## VB1
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_NON_MONOTONIC**

### T1
- Feature = `VB1_T1`
- Scale = 26.6036
- Difference scale = 33.2044
- Smoothness = 1.2511
- Responsiveness = 0.001763
- Price correlation = -0.016810
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.032541

### T2
- Feature = `VB1_T2`
- Scale = 14.9486
- Difference scale = 11.214
- Smoothness = 0.74762
- Responsiveness = 0.004684
- Price correlation = -0.022589
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.056180

### T3
- Feature = `VB1_T3`
- Scale = 9.34928
- Difference scale = 2.85483
- Smoothness = 0.307554
- Responsiveness = 0.010011
- Price correlation = -0.016874
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.142073

### T4
- Feature = `VB1_T4`
- Scale = 7.56688
- Difference scale = 1.36088
- Smoothness = 0.179894
- Responsiveness = 0.013080
- Price correlation = -0.023058
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.211497

### T5
- Feature = `VB1_T5`
- Scale = 6.795
- Difference scale = 0.900823
- Smoothness = 0.134166
- Responsiveness = 0.011199
- Price correlation = -0.020633
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.213191

### T6
- Feature = `VB1_T6`
- Scale = 6.28001
- Difference scale = 0.684993
- Smoothness = 0.109145
- Responsiveness = 0.011409
- Price correlation = -0.014182
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.160116

### T7
- Feature = `VB1_T7`
- Scale = 5.07791
- Difference scale = 0.286171
- Smoothness = 0.056
- Responsiveness = 0.015428
- Price correlation = -0.010559
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.279041

### T8
- Feature = `VB1_T8`
- Scale = 4.48761
- Difference scale = 0.152083
- Smoothness = 0.0344998
- Responsiveness = 0.011784
- Price correlation = -0.021370
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.413553

### T9
- Feature = `VB1_T9`
- Scale = 4.1934
- Difference scale = 0.108196
- Smoothness = 0.026061
- Responsiveness = 0.012322
- Price correlation = -0.004283
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.476656

### T10
- Feature = `VB1_T10`
- Scale = 3.85146
- Difference scale = 0.0692615
- Smoothness = 0.0182209
- Responsiveness = 0.013132
- Price correlation = 0.006021
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.636046

### T11
- Feature = `VB1_T11`
- Scale = 3.66659
- Difference scale = 0.0602874
- Smoothness = 0.0160733
- Responsiveness = 0.005108
- Price correlation = -0.000967
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.463590

### T12
- Feature = `VB1_T12`
- Scale = 3.11519
- Difference scale = 0.0332844
- Smoothness = 0.0105957
- Responsiveness = 0.016585
- Price correlation = -0.076684
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## VB2
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `VB2_T1`
- Scale = 0.00153646
- Difference scale = 0.000739287
- Smoothness = 0.49089
- Responsiveness = -0.022933
- Price correlation = -0.227427
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.493510

### T2
- Feature = `VB2_T2`
- Scale = 0.00128588
- Difference scale = 0.000370914
- Smoothness = 0.299875
- Responsiveness = -0.024193
- Price correlation = -0.284148
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.566904

### T3
- Feature = `VB2_T3`
- Scale = 0.00101727
- Difference scale = 0.000124385
- Smoothness = 0.12653
- Responsiveness = -0.026239
- Price correlation = -0.355347
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.692806

### T4
- Feature = `VB2_T4`
- Scale = 0.000932553
- Difference scale = 6.22335e-05
- Smoothness = 0.0686597
- Responsiveness = -0.020977
- Price correlation = -0.388645
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.750280

### T5
- Feature = `VB2_T5`
- Scale = 0.000901151
- Difference scale = 4.12895e-05
- Smoothness = 0.0481745
- Responsiveness = -0.025410
- Price correlation = -0.405009
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.764968

### T6
- Feature = `VB2_T6`
- Scale = 0.000875441
- Difference scale = 3.11269e-05
- Smoothness = 0.0370537
- Responsiveness = -0.026140
- Price correlation = -0.418318
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.758932

### T7
- Feature = `VB2_T7`
- Scale = 0.000796051
- Difference scale = 1.25146e-05
- Smoothness = 0.0162575
- Responsiveness = -0.018522
- Price correlation = -0.467234
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.827803

### T8
- Feature = `VB2_T8`
- Scale = 0.000727837
- Difference scale = 6.20756e-06
- Smoothness = 0.00869972
- Responsiveness = -0.021107
- Price correlation = -0.474752
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.878253

### T9
- Feature = `VB2_T9`
- Scale = 0.0006935
- Difference scale = 4.12922e-06
- Smoothness = 0.0061683
- Responsiveness = -0.020913
- Price correlation = -0.483193
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.898601

### T10
- Feature = `VB2_T10`
- Scale = 0.00063053
- Difference scale = 2.45642e-06
- Smoothness = 0.00403971
- Responsiveness = -0.016833
- Price correlation = -0.459790
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.936067

### T11
- Feature = `VB2_T11`
- Scale = 0.000612857
- Difference scale = 2.04982e-06
- Smoothness = 0.00337557
- Responsiveness = -0.016890
- Price correlation = -0.446010
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.913558

### T12
- Feature = `VB2_T12`
- Scale = 0.000513725
- Difference scale = 1.01402e-06
- Smoothness = 0.0019896
- Responsiveness = -0.014877
- Price correlation = -0.358554
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## VB3
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_NON_MONOTONIC | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `VB3_T1`
- Scale = 1.76148e-05
- Difference scale = 9.63887e-06
- Smoothness = 0.552485
- Responsiveness = -0.029256
- Price correlation = -0.208632
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.458983

### T2
- Feature = `VB3_T2`
- Scale = 1.60781e-05
- Difference scale = 5.37396e-06
- Smoothness = 0.340686
- Responsiveness = -0.037284
- Price correlation = -0.265152
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.528723

### T3
- Feature = `VB3_T3`
- Scale = 1.36371e-05
- Difference scale = 2.08374e-06
- Smoothness = 0.154423
- Responsiveness = -0.044181
- Price correlation = -0.334630
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.650761

### T4
- Feature = `VB3_T4`
- Scale = 1.24822e-05
- Difference scale = 1.16132e-06
- Smoothness = 0.0894168
- Responsiveness = -0.046454
- Price correlation = -0.376190
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.708725

### T5
- Feature = `VB3_T5`
- Scale = 1.19649e-05
- Difference scale = 8.06015e-07
- Smoothness = 0.0661165
- Responsiveness = -0.050864
- Price correlation = -0.394277
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.720725

### T6
- Feature = `VB3_T6`
- Scale = 1.15861e-05
- Difference scale = 6.29119e-07
- Smoothness = 0.0525473
- Responsiveness = -0.052212
- Price correlation = -0.406694
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.711801

### T7
- Feature = `VB3_T7`
- Scale = 1.04261e-05
- Difference scale = 2.77434e-07
- Smoothness = 0.0263968
- Responsiveness = -0.050609
- Price correlation = -0.427048
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.790495

### T8
- Feature = `VB3_T8`
- Scale = 9.69756e-06
- Difference scale = 1.45819e-07
- Smoothness = 0.0155263
- Responsiveness = -0.049382
- Price correlation = -0.462014
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.849323

### T9
- Feature = `VB3_T9`
- Scale = 9.19969e-06
- Difference scale = 9.92496e-08
- Smoothness = 0.0112917
- Responsiveness = -0.049600
- Price correlation = -0.485315
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.876199

### T10
- Feature = `VB3_T10`
- Scale = 8.45527e-06
- Difference scale = 5.91784e-08
- Smoothness = 0.00756267
- Responsiveness = -0.033703
- Price correlation = -0.496702
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.922626

### T11
- Feature = `VB3_T11`
- Scale = 8.22985e-06
- Difference scale = 4.93976e-08
- Smoothness = 0.00610283
- Responsiveness = -0.029216
- Price correlation = -0.470746
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.895713

### T12
- Feature = `VB3_T12`
- Scale = 6.72827e-06
- Difference scale = 2.66435e-08
- Smoothness = 0.00407876
- Responsiveness = -0.030165
- Price correlation = -0.393233
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## VB4
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_NON_MONOTONIC | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `VB4_T1`
- Scale = 1.76147e-05
- Difference scale = 9.63917e-06
- Smoothness = 0.552487
- Responsiveness = -0.029316
- Price correlation = -0.208632
- First valid index = 5
- Last valid index = 23339
- Mean pairwise Pearson = 0.458977

### T2
- Feature = `VB4_T2`
- Scale = 1.60784e-05
- Difference scale = 5.37428e-06
- Smoothness = 0.340696
- Responsiveness = -0.037324
- Price correlation = -0.265151
- First valid index = 10
- Last valid index = 23339
- Mean pairwise Pearson = 0.528714

### T3
- Feature = `VB4_T3`
- Scale = 1.36376e-05
- Difference scale = 2.08388e-06
- Smoothness = 0.154448
- Responsiveness = -0.044222
- Price correlation = -0.334627
- First valid index = 30
- Last valid index = 23339
- Mean pairwise Pearson = 0.650769

### T4
- Feature = `VB4_T4`
- Scale = 1.24827e-05
- Difference scale = 1.16168e-06
- Smoothness = 0.0894193
- Responsiveness = -0.046623
- Price correlation = -0.376181
- First valid index = 60
- Last valid index = 23339
- Mean pairwise Pearson = 0.708734

### T5
- Feature = `VB4_T5`
- Scale = 1.19655e-05
- Difference scale = 8.06029e-07
- Smoothness = 0.0661179
- Responsiveness = -0.050910
- Price correlation = -0.394267
- First valid index = 90
- Last valid index = 23339
- Mean pairwise Pearson = 0.720733

### T6
- Feature = `VB4_T6`
- Scale = 1.15857e-05
- Difference scale = 6.29201e-07
- Smoothness = 0.0525523
- Responsiveness = -0.052273
- Price correlation = -0.406684
- First valid index = 120
- Last valid index = 23339
- Mean pairwise Pearson = 0.711816

### T7
- Feature = `VB4_T7`
- Scale = 1.04254e-05
- Difference scale = 2.77477e-07
- Smoothness = 0.0264001
- Responsiveness = -0.050794
- Price correlation = -0.427034
- First valid index = 300
- Last valid index = 23339
- Mean pairwise Pearson = 0.790508

### T8
- Feature = `VB4_T8`
- Scale = 9.69778e-06
- Difference scale = 1.45837e-07
- Smoothness = 0.0155291
- Responsiveness = -0.049457
- Price correlation = -0.462008
- First valid index = 600
- Last valid index = 23339
- Mean pairwise Pearson = 0.849317

### T9
- Feature = `VB4_T9`
- Scale = 9.19999e-06
- Difference scale = 9.92521e-08
- Smoothness = 0.0112918
- Responsiveness = -0.049696
- Price correlation = -0.485325
- First valid index = 900
- Last valid index = 23339
- Mean pairwise Pearson = 0.876196

### T10
- Feature = `VB4_T10`
- Scale = 8.45482e-06
- Difference scale = 5.91897e-08
- Smoothness = 0.0075635
- Responsiveness = -0.033836
- Price correlation = -0.496705
- First valid index = 1500
- Last valid index = 23339
- Mean pairwise Pearson = 0.922626

### T11
- Feature = `VB4_T11`
- Scale = 8.23069e-06
- Difference scale = 4.94094e-08
- Smoothness = 0.00610286
- Responsiveness = -0.029297
- Price correlation = -0.470752
- First valid index = 1800
- Last valid index = 23339
- Mean pairwise Pearson = 0.895714

### T12
- Feature = `VB4_T12`
- Scale = 6.72797e-06
- Difference scale = 2.66466e-08
- Smoothness = 0.00407875
- Responsiveness = -0.030195
- Price correlation = -0.393204
- First valid index = 3600
- Last valid index = 23339
- Mean pairwise Pearson = nan

## VB5
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_INCREASES_WITH_T | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `VB5_T1`
- Scale = 5.1162e-05
- Difference scale = 3.22213e-05
- Smoothness = 0.635718
- Responsiveness = -0.032225
- Price correlation = -0.194536
- First valid index = 4
- Last valid index = 23339
- Mean pairwise Pearson = 0.351046

### T2
- Feature = `VB5_T2`
- Scale = 7.50156e-05
- Difference scale = 2.8834e-05
- Smoothness = 0.385285
- Responsiveness = -0.035098
- Price correlation = -0.222751
- First valid index = 9
- Last valid index = 23339
- Mean pairwise Pearson = 0.380937

### T3
- Feature = `VB5_T3`
- Scale = 0.000132673
- Difference scale = 2.32663e-05
- Smoothness = 0.177701
- Responsiveness = -0.039282
- Price correlation = -0.257816
- First valid index = 29
- Last valid index = 23339
- Mean pairwise Pearson = 0.461229

### T4
- Feature = `VB5_T4`
- Scale = 0.000189168
- Difference scale = 1.96777e-05
- Smoothness = 0.109031
- Responsiveness = -0.040564
- Price correlation = -0.270576
- First valid index = 59
- Last valid index = 23339
- Mean pairwise Pearson = 0.502180

### T5
- Feature = `VB5_T5`
- Scale = 0.000232525
- Difference scale = 1.81788e-05
- Smoothness = 0.0826821
- Responsiveness = -0.045746
- Price correlation = -0.272160
- First valid index = 89
- Last valid index = 23339
- Mean pairwise Pearson = 0.497079

### T6
- Feature = `VB5_T6`
- Scale = 0.000263023
- Difference scale = 1.69479e-05
- Smoothness = 0.0687035
- Responsiveness = -0.044402
- Price correlation = -0.277223
- First valid index = 119
- Last valid index = 23339
- Mean pairwise Pearson = 0.459079

### T7
- Feature = `VB5_T7`
- Scale = 0.000393282
- Difference scale = 1.36275e-05
- Smoothness = 0.0366694
- Responsiveness = -0.029183
- Price correlation = -0.306318
- First valid index = 299
- Last valid index = 23339
- Mean pairwise Pearson = 0.531929

### T8
- Feature = `VB5_T8`
- Scale = 0.000532425
- Difference scale = 1.13187e-05
- Smoothness = 0.0232113
- Responsiveness = -0.024758
- Price correlation = -0.331158
- First valid index = 599
- Last valid index = 23339
- Mean pairwise Pearson = 0.622865

### T9
- Feature = `VB5_T9`
- Scale = 0.000634688
- Difference scale = 1.02802e-05
- Smoothness = 0.0178651
- Responsiveness = -0.023126
- Price correlation = -0.316469
- First valid index = 899
- Last valid index = 23339
- Mean pairwise Pearson = 0.658143

### T10
- Feature = `VB5_T10`
- Scale = 0.000795649
- Difference scale = 9.31788e-06
- Smoothness = 0.012914
- Responsiveness = -0.023996
- Price correlation = -0.314946
- First valid index = 1499
- Last valid index = 23339
- Mean pairwise Pearson = 0.768844

### T11
- Feature = `VB5_T11`
- Scale = 0.000849239
- Difference scale = 8.85232e-06
- Smoothness = 0.0113711
- Responsiveness = -0.029280
- Price correlation = -0.315085
- First valid index = 1799
- Last valid index = 23339
- Mean pairwise Pearson = 0.671738

### T12
- Feature = `VB5_T12`
- Scale = 0.0010026
- Difference scale = 7.77477e-06
- Smoothness = 0.00783751
- Responsiveness = -0.033215
- Price correlation = -0.234547
- First valid index = 3599
- Last valid index = 23339
- Mean pairwise Pearson = nan

## VB6
- T pattern: **SMOOTHNESS_DECREASES_WITH_T | RESPONSIVENESS_DECREASES_WITH_T | PRICE_CORR_DECREASES_WITH_T**

### T1
- Feature = `VB6_T1`
- Scale = 16.1037
- Difference scale = 22.7767
- Smoothness = 1.4149
- Responsiveness = -0.001827
- Price correlation = 0.007995
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.130019

### T2
- Feature = `VB6_T2`
- Scale = 2.28904
- Difference scale = 3.21354
- Smoothness = 1.40998
- Responsiveness = -0.008271
- Price correlation = 0.005000
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.655409

### T3
- Feature = `VB6_T3`
- Scale = 1.28237
- Difference scale = 1.77018
- Smoothness = 1.38651
- Responsiveness = -0.019032
- Price correlation = 0.003697
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.927233

### T4
- Feature = `VB6_T4`
- Scale = 1.20482
- Difference scale = 1.65077
- Smoothness = 1.38108
- Responsiveness = -0.021222
- Price correlation = 0.001926
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.955287

### T5
- Feature = `VB6_T5`
- Scale = 1.19362
- Difference scale = 1.62592
- Smoothness = 1.3766
- Responsiveness = -0.023463
- Price correlation = 0.001760
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.962706

### T6
- Feature = `VB6_T6`
- Scale = 1.19149
- Difference scale = 1.61307
- Smoothness = 1.37221
- Responsiveness = -0.024002
- Price correlation = 0.001438
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.964865

### T7
- Feature = `VB6_T7`
- Scale = 1.184
- Difference scale = 1.59234
- Smoothness = 1.3636
- Responsiveness = -0.024344
- Price correlation = 0.001702
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.979634

### T8
- Feature = `VB6_T8`
- Scale = 1.17684
- Difference scale = 1.58491
- Smoothness = 1.35883
- Responsiveness = -0.023555
- Price correlation = 0.000248
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.987377

### T9
- Feature = `VB6_T9`
- Scale = 1.1711
- Difference scale = 1.57397
- Smoothness = 1.35526
- Responsiveness = -0.025061
- Price correlation = -0.001042
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.990484

### T10
- Feature = `VB6_T10`
- Scale = 1.15641
- Difference scale = 1.56135
- Smoothness = 1.34846
- Responsiveness = -0.024088
- Price correlation = 0.002478
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.994960

### T11
- Feature = `VB6_T11`
- Scale = 1.15677
- Difference scale = 1.55261
- Smoothness = 1.34721
- Responsiveness = -0.024457
- Price correlation = 0.003168
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = 0.993424

### T12
- Feature = `VB6_T12`
- Scale = 1.15361
- Difference scale = 1.53128
- Smoothness = 1.33995
- Responsiveness = -0.022209
- Price correlation = -0.004223
- First valid index = 2
- Last valid index = 23339
- Mean pairwise Pearson = nan

## Feature Hypotheses

# PB

## PB1

### PB1_T1
- T = 1
- Best hypothesis = `log_return_5`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 2000.01
- alpha = -6.21127e-06
- MAE = 7.38766e-06
- RMSE = 1.69489e-05
- Score = 0.799985
- Score gap = 0.000015
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.791756

### PB1_T2
- T = 2
- Best hypothesis = `log_return_10`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1000.01
- alpha = -6.13503e-06
- MAE = 7.26509e-06
- RMSE = 1.55561e-05
- Score = 0.799979
- Score gap = 0.000021
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.894641

### PB1_T3
- T = 3
- Best hypothesis = `log_return_30`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 333.337
- alpha = -5.92886e-06
- MAE = 6.6945e-06
- RMSE = 1.29235e-05
- Score = 0.799969
- Score gap = 0.000031
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.964112

### PB1_T4
- T = 4
- Best hypothesis = `log_return_60`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 166.669
- alpha = -5.77825e-06
- MAE = 6.89553e-06
- RMSE = 1.28487e-05
- Score = 0.799956
- Score gap = 0.000044
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.981573

### PB1_T5
- T = 5
- Best hypothesis = `log_return_90`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 111.112
- alpha = -5.53779e-06
- MAE = 6.73827e-06
- RMSE = 1.24046e-05
- Score = 0.799947
- Score gap = 0.000053
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.987499

### PB1_T6
- T = 6
- Best hypothesis = `log_return_120`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 83.3342
- alpha = -5.40064e-06
- MAE = 6.55553e-06
- RMSE = 1.23848e-05
- Score = 0.799939
- Score gap = 0.000061
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.990493

### PB1_T7
- T = 7
- Best hypothesis = `log_return_300`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 33.3341
- alpha = -5.08153e-06
- MAE = 5.84997e-06
- RMSE = 9.11712e-06
- Score = 0.799922
- Score gap = 0.000078
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.996186

### PB1_T8
- T = 8
- Best hypothesis = `log_return_600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 16.6667
- alpha = -4.69334e-06
- MAE = 5.297e-06
- RMSE = 7.89425e-06
- Score = 0.799899
- Score gap = 0.000101
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998005

### PB1_T9
- T = 9
- Best hypothesis = `log_return_900`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 11.1115
- alpha = -4.40521e-06
- MAE = 5.05617e-06
- RMSE = 7.35821e-06
- Score = 0.799881
- Score gap = 0.000119
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998630

### PB1_T10
- T = 10
- Best hypothesis = `log_return_1500`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 6.66696
- alpha = -3.875e-06
- MAE = 4.60102e-06
- RMSE = 6.62551e-06
- Score = 0.799853
- Score gap = 0.000137
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999129

### PB1_T11
- T = 11
- Best hypothesis = `log_return_1800`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 5.55578
- alpha = -3.50393e-06
- MAE = 4.66061e-06
- RMSE = 6.32181e-06
- Score = 0.799846
- Score gap = 0.000123
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999220

### PB1_T12
- T = 12
- Best hypothesis = `log_return_3600`
- Pearson = 0.999999
- Spearman = 1.000000
- beta = 2.77752
- alpha = -2.8658e-06
- MAE = 3.6183e-06
- RMSE = 4.42339e-06
- Score = 0.799829
- Score gap = 0.000077
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999548

## PB10

### PB10_T1
- T = 1
- Best hypothesis = `rolling_max_5`
- Pearson = 0.999882
- Spearman = 0.999802
- beta = 0.9999
- alpha = 0.010025
- MAE = 0.00116815
- RMSE = 0.00251107
- Score = 0.797627
- Score gap = 0.001025
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T2
- T = 2
- Best hypothesis = `rolling_max_10`
- Pearson = 0.999915
- Spearman = 0.999856
- beta = 0.999918
- alpha = 0.00823975
- MAE = 0.000831638
- RMSE = 0.00214131
- Score = 0.798085
- Score gap = 0.001234
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T3
- T = 3
- Best hypothesis = `rolling_max_30`
- Pearson = 0.999947
- Spearman = 0.999910
- beta = 0.999956
- alpha = 0.00444412
- MAE = 0.000482471
- RMSE = 0.00168516
- Score = 0.798599
- Score gap = 0.006491
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T4
- T = 4
- Best hypothesis = `rolling_max_60`
- Pearson = 0.999963
- Spearman = 0.999935
- beta = 0.999961
- alpha = 0.00391006
- MAE = 0.000347882
- RMSE = 0.00140777
- Score = 0.798858
- Score gap = 0.007895
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T5
- T = 5
- Best hypothesis = `rolling_max_90`
- Pearson = 0.999970
- Spearman = 0.999942
- beta = 0.999968
- alpha = 0.00323486
- MAE = 0.000286159
- RMSE = 0.00127081
- Score = 0.798978
- Score gap = 0.008385
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T6
- T = 6
- Best hypothesis = `rolling_max_120`
- Pearson = 0.999973
- Spearman = 0.999948
- beta = 0.999972
- alpha = 0.0028038
- MAE = 0.000252504
- RMSE = 0.00117562
- Score = 0.799056
- Score gap = 0.009114
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T7
- T = 7
- Best hypothesis = `rolling_max_300`
- Pearson = 0.999982
- Spearman = 0.999960
- beta = 0.999985
- alpha = 0.00146103
- MAE = 0.000159623
- RMSE = 0.000908219
- Score = 0.799264
- Score gap = 0.015292
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T8
- T = 8
- Best hypothesis = `rolling_max_600`
- Pearson = 0.999988
- Spearman = 0.999965
- beta = 0.99999
- alpha = 0.000965118
- MAE = 0.000115626
- RMSE = 0.00074879
- Score = 0.799391
- Score gap = 0.025936
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T9
- T = 9
- Best hypothesis = `rolling_max_900`
- Pearson = 0.999989
- Spearman = 0.999965
- beta = 0.999993
- alpha = 0.000724792
- MAE = 0.000100245
- RMSE = 0.000682314
- Score = 0.799438
- Score gap = 0.031615
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T10
- T = 10
- Best hypothesis = `rolling_max_1500`
- Pearson = 0.999990
- Spearman = 0.999964
- beta = 0.999987
- alpha = 0.00127411
- MAE = 8.10284e-05
- RMSE = 0.000608216
- Score = 0.799487
- Score gap = 0.031400
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T11
- T = 11
- Best hypothesis = `rolling_max_1800`
- Pearson = 0.999991
- Spearman = 0.999962
- beta = 0.999992
- alpha = 0.000827789
- MAE = 7.6433e-05
- RMSE = 0.000583735
- Score = 0.799499
- Score gap = 0.031332
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB10_T12
- T = 12
- Best hypothesis = `rolling_max_3600`
- Pearson = 0.999992
- Spearman = 0.999950
- beta = 0.999999
- alpha = 6.10352e-05
- MAE = 5.76257e-05
- RMSE = 0.000486907
- Score = 0.799533
- Score gap = 0.032302
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

## PB11

### PB11_T1
- T = 1
- Best hypothesis = `rolling_min_5`
- Pearson = 0.999884
- Spearman = 0.999800
- beta = 0.999893
- alpha = 0.0106659
- MAE = 0.00118251
- RMSE = 0.00256867
- Score = 0.797601
- Score gap = 0.000899
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T2
- T = 2
- Best hypothesis = `rolling_min_10`
- Pearson = 0.999913
- Spearman = 0.999853
- beta = 0.99992
- alpha = 0.00803375
- MAE = 0.000870735
- RMSE = 0.0022028
- Score = 0.798049
- Score gap = 0.002422
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T3
- T = 3
- Best hypothesis = `rolling_min_30`
- Pearson = 0.999950
- Spearman = 0.999909
- beta = 0.999947
- alpha = 0.00526047
- MAE = 0.000501295
- RMSE = 0.00171889
- Score = 0.798608
- Score gap = 0.006507
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T4
- T = 4
- Best hypothesis = `rolling_min_60`
- Pearson = 0.999963
- Spearman = 0.999929
- beta = 0.99996
- alpha = 0.00397491
- MAE = 0.000351552
- RMSE = 0.00146748
- Score = 0.798868
- Score gap = 0.008986
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T5
- T = 5
- Best hypothesis = `rolling_min_90`
- Pearson = 0.999969
- Spearman = 0.999939
- beta = 0.999965
- alpha = 0.00352097
- MAE = 0.000292935
- RMSE = 0.0013619
- Score = 0.798974
- Score gap = 0.008183
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T6
- T = 6
- Best hypothesis = `rolling_min_120`
- Pearson = 0.999972
- Spearman = 0.999945
- beta = 0.999968
- alpha = 0.00323868
- MAE = 0.00026446
- RMSE = 0.00127243
- Score = 0.799047
- Score gap = 0.008847
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T7
- T = 7
- Best hypothesis = `rolling_min_300`
- Pearson = 0.999981
- Spearman = 0.999959
- beta = 0.999979
- alpha = 0.00207138
- MAE = 0.000175814
- RMSE = 0.00103703
- Score = 0.799245
- Score gap = 0.012292
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T8
- T = 8
- Best hypothesis = `rolling_min_600`
- Pearson = 0.999986
- Spearman = 0.999962
- beta = 0.999993
- alpha = 0.00075531
- MAE = 0.000125435
- RMSE = 0.000874631
- Score = 0.799379
- Score gap = 0.013220
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T9
- T = 9
- Best hypothesis = `rolling_min_900`
- Pearson = 0.999988
- Spearman = 0.999965
- beta = 1
- alpha = -0.00031662
- MAE = 0.000107313
- RMSE = 0.000781985
- Score = 0.799441
- Score gap = 0.018018
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T10
- T = 10
- Best hypothesis = `rolling_min_1500`
- Pearson = 0.999991
- Spearman = 0.999964
- beta = 0.999993
- alpha = 0.000656128
- MAE = 8.65914e-05
- RMSE = 0.000717988
- Score = 0.799460
- Score gap = 0.027967
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T11
- T = 11
- Best hypothesis = `rolling_min_1800`
- Pearson = 0.999991
- Spearman = 0.999963
- beta = 0.999997
- alpha = 0.000259399
- MAE = 8.75368e-05
- RMSE = 0.000683398
- Score = 0.799488
- Score gap = 0.028935
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

### PB11_T12
- T = 12
- Best hypothesis = `rolling_min_3600`
- Pearson = 0.999992
- Spearman = 0.999951
- beta = 1
- alpha = -0.000312805
- MAE = 7.29705e-05
- RMSE = 0.000594009
- Score = 0.799514
- Score gap = 0.059405
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 1.000000

## PB12

### PB12_T1
- T = 1
- Best hypothesis = `rolling_return_5`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 4.56745e-18
- RMSE = 3.03214e-16
- Score = 0.800000
- Score gap = 0.000015
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.791756

### PB12_T2
- T = 2
- Best hypothesis = `rolling_return_10`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 1.21825e-18
- RMSE = 1.61147e-16
- Score = 0.800000
- Score gap = 0.000021
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.894639

### PB12_T3
- T = 3
- Best hypothesis = `rolling_return_30`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 6.09646e-19
- RMSE = 9.30784e-17
- Score = 0.800000
- Score gap = 0.000031
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.964110

### PB12_T4
- T = 4
- Best hypothesis = `rolling_return_60`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 6.10432e-19
- RMSE = 9.31384e-17
- Score = 0.800000
- Score gap = 0.000044
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.981573

### PB12_T5
- T = 5
- Best hypothesis = `rolling_return_90`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 6.1122e-19
- RMSE = 9.31985e-17
- Score = 0.800000
- Score gap = 0.000053
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.987499

### PB12_T6
- T = 6
- Best hypothesis = `rolling_return_120`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000061
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.990493

### PB12_T7
- T = 7
- Best hypothesis = `rolling_return_300`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000078
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.996186

### PB12_T8
- T = 8
- Best hypothesis = `rolling_return_600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000101
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998006

### PB12_T9
- T = 9
- Best hypothesis = `rolling_return_900`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000119
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998631

### PB12_T10
- T = 10
- Best hypothesis = `rolling_return_1500`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000147
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999130

### PB12_T11
- T = 11
- Best hypothesis = `rolling_return_1800`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000154
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999221

### PB12_T12
- T = 12
- Best hypothesis = `rolling_return_3600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1
- alpha = 0
- MAE = 0
- RMSE = 0
- Score = 0.800000
- Score gap = 0.000171
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999548

## PB13

### PB13_T1
- T = 1
- Best hypothesis = `rolling_return_5`
- Pearson = 1.000000
- Spearman = 0.999802
- beta = 1
- alpha = 1.05366e-10
- MAE = 2.49657e-09
- RMSE = 5.7512e-09
- Score = 0.799920
- Score gap = 0.000001
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.791755

### PB13_T2
- T = 2
- Best hypothesis = `log_return_10`
- Pearson = 1.000000
- Spearman = 0.999935
- beta = 0.999996
- alpha = 6.41317e-09
- MAE = 4.95675e-09
- RMSE = 9.74122e-09
- Score = 0.799964
- Score gap = 0.000003
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.894639

### PB13_T3
- T = 3
- Best hypothesis = `log_return_30`
- Pearson = 1.000000
- Spearman = 0.999983
- beta = 0.999993
- alpha = 1.88208e-08
- MAE = 1.24309e-08
- RMSE = 2.05615e-08
- Score = 0.799977
- Score gap = 0.000010
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.964110

### PB13_T4
- T = 4
- Best hypothesis = `log_return_60`
- Pearson = 1.000000
- Spearman = 0.999991
- beta = 0.999991
- alpha = 3.70533e-08
- MAE = 2.31503e-08
- RMSE = 3.60312e-08
- Score = 0.799975
- Score gap = 0.000017
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.981572

### PB13_T5
- T = 5
- Best hypothesis = `log_return_90`
- Pearson = 1.000000
- Spearman = 0.999993
- beta = 0.999991
- alpha = 5.54919e-08
- MAE = 3.31549e-08
- RMSE = 4.93811e-08
- Score = 0.799972
- Score gap = 0.000021
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.987499

### PB13_T6
- T = 6
- Best hypothesis = `log_return_120`
- Pearson = 1.000000
- Spearman = 0.999994
- beta = 0.999989
- alpha = 7.39105e-08
- MAE = 4.26514e-08
- RMSE = 6.23496e-08
- Score = 0.799969
- Score gap = 0.000027
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.990493

### PB13_T7
- T = 7
- Best hypothesis = `log_return_300`
- Pearson = 1.000000
- Spearman = 0.999996
- beta = 0.999979
- alpha = 1.84135e-07
- MAE = 9.7627e-08
- RMSE = 1.33231e-07
- Score = 0.799959
- Score gap = 0.000031
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.996185

### PB13_T8
- T = 8
- Best hypothesis = `log_return_600`
- Pearson = 1.000000
- Spearman = 0.999997
- beta = 0.999963
- alpha = 3.68658e-07
- MAE = 1.7891e-07
- RMSE = 2.32973e-07
- Score = 0.799946
- Score gap = 0.000039
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998005

### PB13_T9
- T = 9
- Best hypothesis = `log_return_900`
- Pearson = 1.000000
- Spearman = 0.999998
- beta = 0.999953
- alpha = 5.37802e-07
- MAE = 2.41362e-07
- RMSE = 3.13133e-07
- Score = 0.799940
- Score gap = 0.000048
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998630

### PB13_T10
- T = 10
- Best hypothesis = `log_return_1500`
- Pearson = 1.000000
- Spearman = 0.999998
- beta = 0.999944
- alpha = 8.6416e-07
- MAE = 3.60152e-07
- RMSE = 4.58867e-07
- Score = 0.799928
- Score gap = 0.000073
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999130

### PB13_T11
- T = 11
- Best hypothesis = `log_return_1800`
- Pearson = 1.000000
- Spearman = 0.999998
- beta = 0.999941
- alpha = 1.02846e-06
- MAE = 4.15167e-07
- RMSE = 5.20045e-07
- Score = 0.799926
- Score gap = 0.000077
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999220

### PB13_T12
- T = 12
- Best hypothesis = `log_return_3600`
- Pearson = 1.000000
- Spearman = 0.999999
- beta = 0.999962
- alpha = 2.02008e-06
- MAE = 6.6343e-07
- RMSE = 8.02937e-07
- Score = 0.799913
- Score gap = 0.000090
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999548

## PB14

### PB14_T1
- T = 1
- Best hypothesis = `momentum_5`
- Pearson = 0.802313
- Spearman = 0.931307
- beta = 63.6616
- alpha = 0.0104617
- MAE = 0.245156
- RMSE = 0.359344
- Score = 0.587775
- Score gap = 0.001140
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.700727

### PB14_T2
- T = 2
- Best hypothesis = `momentum_10`
- Pearson = 0.856424
- Spearman = 0.955262
- beta = 34.2204
- alpha = 0.0071221
- MAE = 0.149445
- RMSE = 0.226315
- Score = 0.633235
- Score gap = 0.000658
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.755810

### PB14_T3
- T = 3
- Best hypothesis = `momentum_30`
- Pearson = 0.910385
- Spearman = 0.972643
- beta = 12.1078
- alpha = 0.00484542
- MAE = 0.0681941
- RMSE = 0.101854
- Score = 0.682612
- Score gap = 0.000113
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.875004

### PB14_T4
- T = 4
- Best hypothesis = `momentum_60`
- Pearson = 0.927338
- Spearman = 0.977497
- beta = 6.17858
- alpha = 0.00437923
- MAE = 0.0448839
- RMSE = 0.0658077
- Score = 0.697098
- Score gap = 0.000377
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.907899

### PB14_T5
- T = 5
- Best hypothesis = `momentum_90`
- Pearson = 0.935703
- Spearman = 0.979300
- beta = 4.20532
- alpha = 0.00343342
- MAE = 0.0350392
- RMSE = 0.0514916
- Score = 0.704294
- Score gap = 0.000492
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.922711

### PB14_T6
- T = 6
- Best hypothesis = `momentum_120`
- Pearson = 0.941119
- Spearman = 0.980560
- beta = 3.1823
- alpha = 0.00308779
- MAE = 0.0294741
- RMSE = 0.0437834
- Score = 0.708156
- Score gap = 0.000304
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.931648

### PB14_T7
- T = 7
- Best hypothesis = `momentum_300`
- Pearson = 0.954045
- Spearman = 0.982617
- beta = 1.2891
- alpha = 0.00253986
- MAE = 0.0174396
- RMSE = 0.0248852
- Score = 0.719715
- Score gap = 0.000471
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.949135

### PB14_T8
- T = 8
- Best hypothesis = `momentum_600`
- Pearson = 0.957927
- Spearman = 0.985358
- beta = 0.666682
- alpha = 0.00199406
- MAE = 0.0114727
- RMSE = 0.0157036
- Score = 0.727141
- Score gap = 0.000194
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.955732

### PB14_T9
- T = 9
- Best hypothesis = `momentum_900`
- Pearson = 0.960052
- Spearman = 0.984670
- beta = 0.450829
- alpha = 0.00179586
- MAE = 0.00884894
- RMSE = 0.0120994
- Score = 0.730592
- Score gap = 0.000172
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.959296

### PB14_T10
- T = 10
- Best hypothesis = `momentum_1500`
- Pearson = 0.967081
- Spearman = 0.986693
- beta = 0.277497
- alpha = 0.00115008
- MAE = 0.00626802
- RMSE = 0.00840085
- Score = 0.738487
- Score gap = 0.000192
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.966784

### PB14_T11
- T = 11
- Best hypothesis = `momentum_1800`
- Pearson = 0.969165
- Spearman = 0.986092
- beta = 0.233235
- alpha = 0.000916273
- MAE = 0.00553703
- RMSE = 0.00768489
- Score = 0.739738
- Score gap = 0.000280
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.968318

### PB14_T12
- T = 12
- Best hypothesis = `momentum_3600`
- Pearson = 0.978195
- Spearman = 0.987059
- beta = 0.120909
- alpha = 0.000672724
- MAE = 0.00339358
- RMSE = 0.00438193
- Score = 0.748876
- Score gap = 0.000166
- Days represented = 69
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.977827

## PB15

### PB15_T1
- T = 1
- Best hypothesis = `zscore_5`
- Pearson = 0.945350
- Spearman = 0.940788
- beta = 39.7902
- alpha = 50.1257
- MAE = 11.6771
- RMSE = 14.177
- Score = 0.695400
- Score gap = 0.161990
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.551158

### PB15_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 0.944380
- Spearman = 0.957659
- beta = 30.9514
- alpha = 50.2729
- MAE = 10.3413
- RMSE = 12.8257
- Score = 0.700946
- Score gap = 0.135864
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.726860

### PB15_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 0.947512
- Spearman = 0.963823
- beta = 24.8587
- alpha = 50.6408
- MAE = 8.91674
- RMSE = 11.1599
- Score = 0.706250
- Score gap = 0.099574
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.863964

### PB15_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 0.949345
- Spearman = 0.964645
- beta = 23.0829
- alpha = 50.884
- MAE = 8.34399
- RMSE = 10.4864
- Score = 0.708293
- Score gap = 0.044711
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.904077

### PB15_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 0.949940
- Spearman = 0.965283
- beta = 22.4033
- alpha = 51.1384
- MAE = 7.98209
- RMSE = 10.1382
- Score = 0.709620
- Score gap = 0.023209
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.918610

### PB15_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 0.949820
- Spearman = 0.965750
- beta = 21.9903
- alpha = 51.3
- MAE = 7.85829
- RMSE = 9.94185
- Score = 0.709875
- Score gap = 0.055574
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.925453

### PB15_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 0.949617
- Spearman = 0.963777
- beta = 21.1639
- alpha = 51.9185
- MAE = 7.66685
- RMSE = 9.72147
- Score = 0.709237
- Score gap = 0.071073
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.940002

### PB15_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 0.950968
- Spearman = 0.961903
- beta = 20.9866
- alpha = 51.9786
- MAE = 7.60996
- RMSE = 9.56122
- Score = 0.709002
- Score gap = 0.035323
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.944785

### PB15_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 0.950358
- Spearman = 0.960410
- beta = 20.9125
- alpha = 52.1049
- MAE = 7.61306
- RMSE = 9.49115
- Score = 0.707926
- Score gap = 0.055048
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.946860

### PB15_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 0.951460
- Spearman = 0.959466
- beta = 20.818
- alpha = 52.3965
- MAE = 7.38261
- RMSE = 9.29907
- Score = 0.708506
- Score gap = 0.004337
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.949160

### PB15_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 0.951929
- Spearman = 0.956978
- beta = 20.8547
- alpha = 52.521
- MAE = 7.25366
- RMSE = 9.06833
- Score = 0.708840
- Score gap = 0.032110
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.950147

### PB15_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 0.950228
- Spearman = 0.955708
- beta = 20.759
- alpha = 53.9643
- MAE = 6.92679
- RMSE = 8.69266
- Score = 0.707814
- Score gap = 0.037769
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.949514

## PB16

### PB16_T1
- T = 1
- Best hypothesis = `zscore_10`
- Pearson = 0.782505
- Spearman = 0.795077
- beta = 22.8877
- alpha = 50.226
- MAE = 17.8711
- RMSE = 21.879
- Score = 0.517237
- Score gap = 0.025350
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.793856

### PB16_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 0.802378
- Spearman = 0.817389
- beta = 23.3791
- alpha = 50.4144
- MAE = 17.3261
- RMSE = 20.7295
- Score = 0.537923
- Score gap = 0.034143
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.884364

### PB16_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 0.897056
- Spearman = 0.914881
- beta = 22.5984
- alpha = 50.708
- MAE = 11.8888
- RMSE = 14.8118
- Score = 0.644242
- Score gap = 0.056290
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.926159

### PB16_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 0.923649
- Spearman = 0.940043
- beta = 21.9739
- alpha = 50.9414
- MAE = 9.96704
- RMSE = 12.5125
- Score = 0.675690
- Score gap = 0.022298
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.938355

### PB16_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 0.933176
- Spearman = 0.949130
- beta = 21.6794
- alpha = 51.1782
- MAE = 9.14682
- RMSE = 11.47
- Score = 0.687733
- Score gap = 0.011223
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.942643

### PB16_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 0.937261
- Spearman = 0.953519
- beta = 21.4367
- alpha = 51.3297
- MAE = 8.76275
- RMSE = 10.9894
- Score = 0.693150
- Score gap = 0.061881
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.944011

### PB16_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 0.944981
- Spearman = 0.958685
- beta = 20.9722
- alpha = 51.9018
- MAE = 8.01501
- RMSE = 10.1425
- Score = 0.702651
- Score gap = 0.066408
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.947386

### PB16_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 0.948128
- Spearman = 0.959331
- beta = 20.8906
- alpha = 51.9998
- MAE = 7.76901
- RMSE = 9.7408
- Score = 0.705591
- Score gap = 0.032947
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.949518

### PB16_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 0.948664
- Spearman = 0.958589
- beta = 20.8424
- alpha = 52.1054
- MAE = 7.73832
- RMSE = 9.64026
- Score = 0.705533
- Score gap = 0.053258
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.949551

### PB16_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 0.950270
- Spearman = 0.958251
- beta = 20.7764
- alpha = 52.4004
- MAE = 7.47031
- RMSE = 9.36626
- Score = 0.706987
- Score gap = 0.003840
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.950831

### PB16_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 0.951360
- Spearman = 0.956141
- beta = 20.8061
- alpha = 52.5254
- MAE = 7.3443
- RMSE = 9.13835
- Score = 0.707711
- Score gap = 0.032515
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.951558

### PB16_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 0.949924
- Spearman = 0.955228
- beta = 20.7425
- alpha = 53.9684
- MAE = 6.95409
- RMSE = 8.72274
- Score = 0.707293
- Score gap = 0.037584
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.950207

## PB17

### PB17_T1
- T = 1
- Best hypothesis = `zscore_5`
- Pearson = 0.945350
- Spearman = 0.940788
- beta = 39.7902
- alpha = -49.8743
- MAE = 11.6771
- RMSE = 14.177
- Score = 0.695400
- Score gap = 0.161990
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.551158

### PB17_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 0.944380
- Spearman = 0.957659
- beta = 30.9514
- alpha = -49.7271
- MAE = 10.3413
- RMSE = 12.8257
- Score = 0.700945
- Score gap = 0.135864
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.726860

### PB17_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 0.947512
- Spearman = 0.963823
- beta = 24.8587
- alpha = -49.3592
- MAE = 8.91674
- RMSE = 11.1599
- Score = 0.706250
- Score gap = 0.099574
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.863964

### PB17_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 0.949345
- Spearman = 0.964645
- beta = 23.0829
- alpha = -49.116
- MAE = 8.34399
- RMSE = 10.4864
- Score = 0.708293
- Score gap = 0.044711
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.904077

### PB17_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 0.949940
- Spearman = 0.965283
- beta = 22.4033
- alpha = -48.8616
- MAE = 7.98209
- RMSE = 10.1382
- Score = 0.709620
- Score gap = 0.023209
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.918610

### PB17_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 0.949820
- Spearman = 0.965750
- beta = 21.9903
- alpha = -48.7
- MAE = 7.85829
- RMSE = 9.94185
- Score = 0.709875
- Score gap = 0.055574
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.925453

### PB17_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 0.949617
- Spearman = 0.963777
- beta = 21.1639
- alpha = -48.0815
- MAE = 7.66685
- RMSE = 9.72147
- Score = 0.709237
- Score gap = 0.071073
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.940002

### PB17_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 0.950967
- Spearman = 0.961903
- beta = 20.9866
- alpha = -48.0214
- MAE = 7.60996
- RMSE = 9.56122
- Score = 0.709002
- Score gap = 0.035322
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.944785

### PB17_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 0.950358
- Spearman = 0.960410
- beta = 20.9125
- alpha = -47.8951
- MAE = 7.61306
- RMSE = 9.49115
- Score = 0.707926
- Score gap = 0.055048
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.946860

### PB17_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 0.951460
- Spearman = 0.959466
- beta = 20.818
- alpha = -47.6035
- MAE = 7.38261
- RMSE = 9.29907
- Score = 0.708506
- Score gap = 0.004337
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.949160

### PB17_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 0.951929
- Spearman = 0.956978
- beta = 20.8547
- alpha = -47.479
- MAE = 7.25366
- RMSE = 9.06833
- Score = 0.708840
- Score gap = 0.032110
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.950147

### PB17_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 0.950228
- Spearman = 0.955708
- beta = 20.759
- alpha = -46.0357
- MAE = 6.92679
- RMSE = 8.69266
- Score = 0.707814
- Score gap = 0.037769
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.949514

## PB18

### PB18_T1
- T = 1
- Best hypothesis = `zscore_5`
- Pearson = 0.995173
- Spearman = 0.997089
- beta = 88.5732
- alpha = -0.0237503
- MAE = 6.63366
- RMSE = 9.0552
- Score = 0.779761
- Score gap = 0.200827
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.496211

### PB18_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 0.993716
- Spearman = 0.998244
- beta = 86.9492
- alpha = -0.0946604
- MAE = 7.19272
- RMSE = 11.6887
- Score = 0.778474
- Score gap = 0.175393
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.710872

### PB18_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 0.995751
- Spearman = 0.998819
- beta = 84.3647
- alpha = -0.174938
- MAE = 6.23985
- RMSE = 10.4201
- Score = 0.782916
- Score gap = 0.159472
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.894299

### PB18_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 0.996576
- Spearman = 0.998990
- beta = 83.4222
- alpha = -0.128918
- MAE = 5.74916
- RMSE = 9.45761
- Score = 0.784867
- Score gap = 0.097878
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.944499

### PB18_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 0.996767
- Spearman = 0.999037
- beta = 83.0729
- alpha = -0.164759
- MAE = 5.53093
- RMSE = 9.22315
- Score = 0.785413
- Score gap = 0.064114
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.962132

### PB18_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 0.996981
- Spearman = 0.999066
- beta = 82.9068
- alpha = -0.232764
- MAE = 5.47452
- RMSE = 9.06171
- Score = 0.785752
- Score gap = 0.059012
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.970638

### PB18_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 0.997327
- Spearman = 0.999053
- beta = 82.5392
- alpha = -0.23018
- MAE = 5.29051
- RMSE = 8.48259
- Score = 0.786639
- Score gap = 0.142422
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.987104

### PB18_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 0.997634
- Spearman = 0.999013
- beta = 82.1234
- alpha = -0.0196848
- MAE = 5.08312
- RMSE = 7.90241
- Score = 0.787335
- Score gap = 0.093404
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.992340

### PB18_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 0.997640
- Spearman = 0.999012
- beta = 82.0057
- alpha = -0.231068
- MAE = 5.04363
- RMSE = 7.89405
- Score = 0.787342
- Score gap = 0.090429
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.994024

### PB18_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 0.997846
- Spearman = 0.998894
- beta = 81.9373
- alpha = -0.172963
- MAE = 4.98875
- RMSE = 7.42388
- Score = 0.787683
- Score gap = 0.037380
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.995571

### PB18_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 0.997844
- Spearman = 0.998862
- beta = 81.8169
- alpha = -0.310145
- MAE = 4.9338
- RMSE = 7.23598
- Score = 0.787813
- Score gap = 0.032270
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.996094

### PB18_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 0.998282
- Spearman = 0.998931
- beta = 81.6253
- alpha = -0.463942
- MAE = 4.48593
- RMSE = 6.32472
- Score = 0.788956
- Score gap = 0.113636
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.997318

## PB2

### PB2_T1
- T = 1
- Best hypothesis = `momentum_5`
- Pearson = 0.711974
- Spearman = 0.687530
- beta = 72.7454
- alpha = -0.00288436
- MAE = 0.453976
- RMSE = 0.63201
- Score = 0.439852
- Score gap = 0.000098
- Days represented = 70
- Confidence = **LOW**
- Best lag = 5 with lag correlation = -0.711653

### PB2_T2
- T = 2
- Best hypothesis = `momentum_10`
- Pearson = 0.712897
- Spearman = 0.689859
- beta = 18.332
- alpha = -0.00151831
- MAE = 0.161047
- RMSE = 0.223077
- Score = 0.441206
- Score gap = 0.000048
- Days represented = 70
- Confidence = **LOW**
- Best lag = 10 with lag correlation = -0.712351

### PB2_T3
- T = 3
- Best hypothesis = `rolling_return_30`
- Pearson = 0.714575
- Spearman = 0.692792
- beta = 201.893
- alpha = -0.000517854
- MAE = 0.0313682
- RMSE = 0.0421046
- Score = 0.442859
- Score gap = 0.000005
- Days represented = 70
- Confidence = **LOW**
- Best lag = 30 with lag correlation = -0.713628

### PB2_T4
- T = 4
- Best hypothesis = `momentum_60`
- Pearson = 0.713847
- Spearman = 0.691707
- beta = 0.510938
- alpha = -0.000224682
- MAE = 0.0109365
- RMSE = 0.0145053
- Score = 0.442531
- Score gap = 0.000008
- Days represented = 70
- Confidence = **LOW**
- Best lag = 60 with lag correlation = -0.715353

### PB2_T5
- T = 5
- Best hypothesis = `rolling_return_90`
- Pearson = 0.712174
- Spearman = 0.692158
- beta = 22.4915
- alpha = -0.000155602
- MAE = 0.00581396
- RMSE = 0.00793817
- Score = 0.442861
- Score gap = 0.000003
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.695185

### PB2_T6
- T = 6
- Best hypothesis = `rolling_return_120`
- Pearson = 0.712779
- Spearman = 0.689772
- beta = 12.6864
- alpha = -0.000120852
- MAE = 0.00377456
- RMSE = 0.00513178
- Score = 0.438557
- Score gap = 0.000025
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.699596

### PB2_T7
- T = 7
- Best hypothesis = `momentum_300`
- Pearson = 0.725160
- Spearman = 0.697912
- beta = 0.0210347
- alpha = -4.9565e-05
- MAE = 0.000990699
- RMSE = 0.00128114
- Score = 0.446393
- Score gap = 0.000058
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.720223

### PB2_T8
- T = 8
- Best hypothesis = `rolling_return_600`
- Pearson = 0.724116
- Spearman = 0.697574
- beta = 0.531755
- alpha = -2.21991e-05
- MAE = 0.000345482
- RMSE = 0.00044044
- Score = 0.443899
- Score gap = 0.000018
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.721797

### PB2_T9
- T = 9
- Best hypothesis = `rolling_return_900`
- Pearson = 0.725935
- Spearman = 0.710834
- beta = 0.249041
- alpha = -1.2425e-05
- MAE = 0.000182465
- RMSE = 0.000233716
- Score = 0.446793
- Score gap = 0.000008
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.724202

### PB2_T10
- T = 10
- Best hypothesis = `rolling_return_1500`
- Pearson = 0.738066
- Spearman = 0.710471
- beta = 0.0892106
- alpha = -9.36431e-06
- MAE = 8.63442e-05
- RMSE = 0.000108071
- Score = 0.453300
- Score gap = 0.000007
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.746131

### PB2_T11
- T = 11
- Best hypothesis = `rolling_return_1800`
- Pearson = 0.742830
- Spearman = 0.711759
- beta = 0.0636617
- alpha = -7.10634e-06
- MAE = 6.41632e-05
- RMSE = 8.08166e-05
- Score = 0.458982
- Score gap = 0.000133
- Days represented = 68
- Confidence = **LOW**
- Best lag = 60 with lag correlation = -0.757868

### PB2_T12
- T = 12
- Best hypothesis = `rolling_max_120`
- Pearson = 0.775064
- Spearman = 0.801057
- beta = 0.00034017
- alpha = -0.0338864
- MAE = 3.76795e-05
- RMSE = 4.57191e-05
- Score = 0.513883
- Score gap = 0.007635
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.811405

## PB3

### PB3_T1
- T = 1
- Best hypothesis = `zscore_10`
- Pearson = 0.930602
- Spearman = 0.949834
- beta = 16.6341
- alpha = 50.2029
- MAE = 5.91962
- RMSE = 7.7685
- Score = 0.686893
- Score gap = 0.067026
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.752166

### PB3_T2
- T = 2
- Best hypothesis = `zscore_30`
- Pearson = 0.939237
- Spearman = 0.956151
- beta = 10.7095
- alpha = 50.1503
- MAE = 4.08385
- RMSE = 5.18325
- Score = 0.696308
- Score gap = 0.065861
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.841519

### PB3_T3
- T = 3
- Best hypothesis = `zscore_90`
- Pearson = 0.940157
- Spearman = 0.959114
- beta = 6.037
- alpha = 50.089
- MAE = 2.33894
- RMSE = 3.02836
- Score = 0.698302
- Score gap = 0.010374
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.904387

### PB3_T4
- T = 4
- Best hypothesis = `zscore_120`
- Pearson = 0.927209
- Spearman = 0.957403
- beta = 4.20866
- alpha = 50.1369
- MAE = 1.72541
- RMSE = 2.34725
- Score = 0.687587
- Score gap = 0.003557
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.925467

### PB3_T5
- T = 5
- Best hypothesis = `zscore_300`
- Pearson = 0.938428
- Spearman = 0.953022
- beta = 3.44545
- alpha = 50.0471
- MAE = 1.38836
- RMSE = 1.75761
- Score = 0.694143
- Score gap = 0.045530
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.926180

### PB3_T6
- T = 6
- Best hypothesis = `zscore_300`
- Pearson = 0.940568
- Spearman = 0.964092
- beta = 2.98514
- alpha = 50.0806
- MAE = 1.13631
- RMSE = 1.54386
- Score = 0.700211
- Score gap = 0.017456
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.931001

### PB3_T7
- T = 7
- Best hypothesis = `zscore_900`
- Pearson = 0.938851
- Spearman = 0.955991
- beta = 1.9009
- alpha = 50.0715
- MAE = 0.749301
- RMSE = 0.977935
- Score = 0.696723
- Score gap = 0.024796
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.938150

### PB3_T8
- T = 8
- Best hypothesis = `zscore_1800`
- Pearson = 0.929855
- Spearman = 0.948371
- beta = 1.35045
- alpha = 50.0909
- MAE = 0.564978
- RMSE = 0.756309
- Score = 0.685763
- Score gap = 0.015818
- Days represented = 68
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.950232

### PB3_T9
- T = 9
- Best hypothesis = `zscore_3600`
- Pearson = 0.912705
- Spearman = 0.919813
- beta = 1.09073
- alpha = 50.0531
- MAE = 0.511526
- RMSE = 0.631454
- Score = 0.661387
- Score gap = 0.038765
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.962410

### PB3_T10
- T = 10
- Best hypothesis = `price_ma_ratio_3600`
- Pearson = 0.861402
- Spearman = 0.892999
- beta = 1148.03
- alpha = 50.1846
- MAE = 0.484547
- RMSE = 0.659304
- Score = 0.622753
- Score gap = 0.005681
- Days represented = 41
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.915055

### PB3_T11
- T = 11
- Best hypothesis = `price_ma_ratio_3600`
- Pearson = 0.833287
- Spearman = 0.898308
- beta = 1128.64
- alpha = 50.1888
- MAE = 0.539948
- RMSE = 0.724614
- Score = 0.598947
- Score gap = 0.003332
- Days represented = 26
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.914401

### PB3_T12
- T = 12
- Best hypothesis = `sma_600`
- Pearson = 0.958439
- Spearman = 0.981191
- beta = 50.3774
- alpha = -5011.47
- MAE = 2.11404
- RMSE = 2.97947
- Score = 0.725941
- Score gap = 0.000289
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.958646

## PB4

### PB4_T1
- T = 1
- Best hypothesis = `log_return_5`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000
- alpha = -3.10554e-05
- MAE = 3.69365e-05
- RMSE = 8.47494e-05
- Score = 0.799985
- Score gap = 0.000015
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.791756

### PB4_T2
- T = 2
- Best hypothesis = `log_return_10`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.1
- alpha = -6.13495e-05
- MAE = 7.26484e-05
- RMSE = 0.000155563
- Score = 0.799979
- Score gap = 0.000021
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.894641

### PB4_T3
- T = 3
- Best hypothesis = `log_return_30`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.1
- alpha = -0.000177865
- MAE = 0.000200826
- RMSE = 0.000387711
- Score = 0.799969
- Score gap = 0.000031
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.964112

### PB4_T4
- T = 4
- Best hypothesis = `log_return_60`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.1
- alpha = -0.00034673
- MAE = 0.000413667
- RMSE = 0.00077093
- Score = 0.799956
- Score gap = 0.000044
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.981573

### PB4_T5
- T = 5
- Best hypothesis = `log_return_90`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.1
- alpha = -0.000498401
- MAE = 0.000606449
- RMSE = 0.00111638
- Score = 0.799947
- Score gap = 0.000053
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.987499

### PB4_T6
- T = 6
- Best hypothesis = `log_return_120`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.1
- alpha = -0.000648085
- MAE = 0.00078673
- RMSE = 0.00148618
- Score = 0.799939
- Score gap = 0.000061
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.990493

### PB4_T7
- T = 7
- Best hypothesis = `log_return_300`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.2
- alpha = -0.00152433
- MAE = 0.00175503
- RMSE = 0.00273525
- Score = 0.799922
- Score gap = 0.000078
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.996186

### PB4_T8
- T = 8
- Best hypothesis = `log_return_600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000
- alpha = -0.00281611
- MAE = 0.0031784
- RMSE = 0.00473662
- Score = 0.799899
- Score gap = 0.000101
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998005

### PB4_T9
- T = 9
- Best hypothesis = `log_return_900`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.3
- alpha = -0.0039646
- MAE = 0.00455046
- RMSE = 0.00662243
- Score = 0.799881
- Score gap = 0.000119
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998630

### PB4_T10
- T = 10
- Best hypothesis = `log_return_1500`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.4
- alpha = -0.00581247
- MAE = 0.00690145
- RMSE = 0.00993835
- Score = 0.799853
- Score gap = 0.000137
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999129

### PB4_T11
- T = 11
- Best hypothesis = `log_return_1800`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 10000.4
- alpha = -0.00630689
- MAE = 0.00838913
- RMSE = 0.0113791
- Score = 0.799846
- Score gap = 0.000123
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999220

### PB4_T12
- T = 12
- Best hypothesis = `log_return_3600`
- Pearson = 0.999999
- Spearman = 1.000000
- beta = 9999.06
- alpha = -0.0103164
- MAE = 0.013026
- RMSE = 0.0159241
- Score = 0.799829
- Score gap = 0.000077
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999548

## PB5

### PB5_T1
- T = 1
- Best hypothesis = `rolling_return_5`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 2.50163e-10
- RMSE = 5.06058e-10
- Score = 0.800000
- Score gap = 0.000015
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.791756

### PB5_T2
- T = 2
- Best hypothesis = `rolling_return_10`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 3.15842e-10
- RMSE = 6.55203e-10
- Score = 0.800000
- Score gap = 0.000021
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.894639

### PB5_T3
- T = 3
- Best hypothesis = `rolling_return_30`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = -1.45519e-11
- MAE = 6.34826e-10
- RMSE = 1.17548e-09
- Score = 0.800000
- Score gap = 0.000031
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.964110

### PB5_T4
- T = 4
- Best hypothesis = `rolling_return_60`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 9.01146e-10
- RMSE = 1.7585e-09
- Score = 0.800000
- Score gap = 0.000044
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.981573

### PB5_T5
- T = 5
- Best hypothesis = `rolling_return_90`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 1.13517e-09
- RMSE = 2.1243e-09
- Score = 0.800000
- Score gap = 0.000053
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.987499

### PB5_T6
- T = 6
- Best hypothesis = `rolling_return_120`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 1.43536e-09
- RMSE = 2.57444e-09
- Score = 0.800000
- Score gap = 0.000061
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.990493

### PB5_T7
- T = 7
- Best hypothesis = `rolling_return_300`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 2.58016e-09
- RMSE = 4.04816e-09
- Score = 0.800000
- Score gap = 0.000078
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.996186

### PB5_T8
- T = 8
- Best hypothesis = `rolling_return_600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 2.46608e-09
- RMSE = 4.81996e-09
- Score = 0.800000
- Score gap = 0.000101
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998006

### PB5_T9
- T = 9
- Best hypothesis = `rolling_return_900`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 3.20629e-09
- RMSE = 6.86215e-09
- Score = 0.800000
- Score gap = 0.000119
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.998631

### PB5_T10
- T = 10
- Best hypothesis = `rolling_return_1500`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 6.06632e-09
- RMSE = 9.40707e-09
- Score = 0.800000
- Score gap = 0.000147
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999130

### PB5_T11
- T = 11
- Best hypothesis = `rolling_return_1800`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 4.91804e-09
- RMSE = 9.56204e-09
- Score = 0.800000
- Score gap = 0.000154
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999221

### PB5_T12
- T = 12
- Best hypothesis = `rolling_return_3600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 100
- alpha = 0
- MAE = 8.04122e-09
- RMSE = 1.25663e-08
- Score = 0.800000
- Score gap = 0.000171
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999548

## PB6

### PB6_T1
- T = 1
- Best hypothesis = `momentum_10`
- Pearson = 0.929118
- Spearman = 0.913545
- beta = 0.0144871
- alpha = 2.60472e-07
- MAE = 5.30105e-05
- RMSE = 7.13601e-05
- Score = 0.674650
- Score gap = 0.000003
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.936170

### PB6_T2
- T = 2
- Best hypothesis = `momentum_30`
- Pearson = 0.884832
- Spearman = 0.863513
- beta = 0.00560253
- alpha = 8.36469e-08
- MAE = 4.65174e-05
- RMSE = 6.29562e-05
- Score = 0.619835
- Score gap = 0.000084
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 3 with lag correlation = 0.964869

### PB6_T3
- T = 3
- Best hypothesis = `price_ma_ratio_120`
- Pearson = 0.891807
- Spearman = 0.878651
- beta = 0.282713
- alpha = 7.11267e-08
- MAE = 2.56511e-05
- RMSE = 3.49043e-05
- Score = 0.628538
- Score gap = 0.000006
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 10 with lag correlation = 0.957437

### PB6_T4
- T = 4
- Best hypothesis = `price_minus_ma_300`
- Pearson = 0.884009
- Spearman = 0.869651
- beta = 0.00126737
- alpha = -5.39809e-08
- MAE = 1.84702e-05
- RMSE = 2.51247e-05
- Score = 0.619776
- Score gap = 0.000001
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 17 with lag correlation = 0.936689

### PB6_T5
- T = 5
- Best hypothesis = `price_ma_ratio_300`
- Pearson = 0.860505
- Spearman = 0.848960
- beta = 0.100401
- alpha = 1.70462e-07
- MAE = 1.60704e-05
- RMSE = 2.18672e-05
- Score = 0.596169
- Score gap = 0.000020
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 34 with lag correlation = 0.965586

### PB6_T6
- T = 6
- Best hypothesis = `log_return_300`
- Pearson = 0.899363
- Spearman = 0.887549
- beta = 0.0517913
- alpha = 1.50004e-07
- MAE = 1.19456e-05
- RMSE = 1.61513e-05
- Score = 0.639830
- Score gap = 0.000007
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 36 with lag correlation = 0.926111

### PB6_T7
- T = 7
- Best hypothesis = `price_minus_ma_1500`
- Pearson = 0.872034
- Spearman = 0.862010
- beta = 0.000248551
- alpha = -5.88565e-08
- MAE = 8.10513e-06
- RMSE = 1.07995e-05
- Score = 0.610783
- Score gap = 0.000003
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 60 with lag correlation = 0.931715

### PB6_T8
- T = 8
- Best hypothesis = `momentum_1500`
- Pearson = 0.885321
- Spearman = 0.868368
- beta = 0.000101021
- alpha = 1.94873e-07
- MAE = 5.4361e-06
- RMSE = 6.9449e-06
- Score = 0.621301
- Score gap = 0.000056
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 60 with lag correlation = 0.907966

### PB6_T9
- T = 9
- Best hypothesis = `rolling_mean_300`
- Pearson = 0.936722
- Spearman = 0.837181
- beta = 7.66961e-05
- alpha = -0.00767325
- MAE = 2.33584e-06
- RMSE = 2.9174e-06
- Score = 0.651502
- Score gap = 0.000000
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.958956

### PB6_T10
- T = 10
- Best hypothesis = `ema_1500`
- Pearson = 0.971738
- Spearman = 0.822669
- beta = 6.93877e-05
- alpha = -0.00694202
- MAE = 1.19541e-06
- RMSE = 1.37622e-06
- Score = 0.681105
- Score gap = 0.008310
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 37 with lag correlation = 0.932634

### PB6_T11
- T = 11
- Best hypothesis = `sma_1800`
- Pearson = 0.925206
- Spearman = 0.860672
- beta = 6.14001e-05
- alpha = -0.00612982
- MAE = 2.36733e-06
- RMSE = 2.72315e-06
- Score = 0.644619
- Score gap = 0.008216
- Days represented = 2
- Confidence = **MEDIUM**
- Best lag = 19 with lag correlation = 0.985987

### PB6_T12
- T = 12
- Best hypothesis = `sma_3600`
- Pearson = 0.940849
- Spearman = 0.892708
- beta = 3.49796e-05
- alpha = -0.00348836
- MAE = 1.14284e-06
- RMSE = 1.31063e-06
- Score = 0.669420
- Score gap = 0.003719
- Days represented = 39
- Confidence = **MEDIUM**
- Best lag = 60 with lag correlation = 0.967578

## PB7

### PB7_T1
- T = 1
- Best hypothesis = `zscore_5`
- Pearson = 1.000000
- Spearman = 0.999958
- beta = 1.11803
- alpha = 1.39698e-07
- MAE = 5.63164e-06
- RMSE = 0.000103611
- Score = 0.799976
- Score gap = 0.216027
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.523293

### PB7_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.05409
- alpha = 0
- MAE = 1.33998e-07
- RMSE = 3.58359e-06
- Score = 0.800000
- Score gap = 0.186442
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.733823

### PB7_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.0171
- alpha = 0
- MAE = 6.54962e-08
- RMSE = 1.01725e-07
- Score = 0.800000
- Score gap = 0.165203
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.900266

### PB7_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00844
- alpha = 0
- MAE = 3.48738e-08
- RMSE = 7.09513e-08
- Score = 0.800000
- Score gap = 0.105299
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.947688

### PB7_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.0056
- alpha = 0
- MAE = 5.40485e-08
- RMSE = 8.87616e-08
- Score = 0.800000
- Score gap = 0.071164
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.964997

### PB7_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00419
- alpha = 0
- MAE = 6.97572e-08
- RMSE = 1.0361e-07
- Score = 0.800000
- Score gap = 0.072980
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.973506

### PB7_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00167
- alpha = 0
- MAE = 2.84009e-08
- RMSE = 6.42587e-08
- Score = 0.800000
- Score gap = 0.146453
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.989338

### PB7_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00083
- alpha = 0
- MAE = 4.18348e-08
- RMSE = 7.69819e-08
- Score = 0.800000
- Score gap = 0.100607
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.994653

### PB7_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00056
- alpha = 0
- MAE = 3.9319e-08
- RMSE = 7.54766e-08
- Score = 0.800000
- Score gap = 0.103165
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.996456

### PB7_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00033
- alpha = 0
- MAE = 6.69971e-08
- RMSE = 1.00017e-07
- Score = 0.800000
- Score gap = 0.043423
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.997847

### PB7_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00028
- alpha = 0
- MAE = 3.69648e-08
- RMSE = 7.01026e-08
- Score = 0.800000
- Score gap = 0.044254
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.998175

### PB7_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 1.000000
- Spearman = 1.000000
- beta = 1.00014
- alpha = 0
- MAE = 8.09278e-08
- RMSE = 1.07528e-07
- Score = 0.800000
- Score gap = 0.115216
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999044

## PB8

### PB8_T1
- T = 1
- Best hypothesis = `zscore_5`
- Pearson = 0.930274
- Spearman = 0.933106
- beta = 28.0491
- alpha = 65.9359
- MAE = 8.97786
- RMSE = 11.399
- Score = 0.679470
- Score gap = 0.147072
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.508536

### PB8_T2
- T = 2
- Best hypothesis = `zscore_10`
- Pearson = 0.947516
- Spearman = 0.959430
- beta = 26.1096
- alpha = 59.5834
- MAE = 8.34849
- RMSE = 10.5073
- Score = 0.704807
- Score gap = 0.136152
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.714574

### PB8_T3
- T = 3
- Best hypothesis = `zscore_30`
- Pearson = 0.956669
- Spearman = 0.977412
- beta = 24.4505
- alpha = 54.6016
- MAE = 7.75356
- RMSE = 9.91585
- Score = 0.720719
- Score gap = 0.120636
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.867720

### PB8_T4
- T = 4
- Best hypothesis = `zscore_60`
- Pearson = 0.959194
- Spearman = 0.981694
- beta = 24.0633
- alpha = 53.0689
- MAE = 7.58184
- RMSE = 9.74803
- Score = 0.724827
- Score gap = 0.072472
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.910588

### PB8_T5
- T = 5
- Best hypothesis = `zscore_90`
- Pearson = 0.960722
- Spearman = 0.983331
- beta = 23.9366
- alpha = 52.4674
- MAE = 7.47141
- RMSE = 9.58293
- Score = 0.726985
- Score gap = 0.045141
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.926799

### PB8_T6
- T = 6
- Best hypothesis = `zscore_120`
- Pearson = 0.960197
- Spearman = 0.984277
- beta = 23.8279
- alpha = 52.1435
- MAE = 7.4918
- RMSE = 9.6414
- Score = 0.726898
- Score gap = 0.025970
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.934425

### PB8_T7
- T = 7
- Best hypothesis = `zscore_300`
- Pearson = 0.961180
- Spearman = 0.985279
- beta = 23.7748
- alpha = 51.3861
- MAE = 7.44267
- RMSE = 9.51333
- Score = 0.728616
- Score gap = 0.102068
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.950795

### PB8_T8
- T = 8
- Best hypothesis = `zscore_600`
- Pearson = 0.963622
- Spearman = 0.985388
- beta = 24.0502
- alpha = 51.057
- MAE = 7.19969
- RMSE = 9.26827
- Score = 0.731224
- Score gap = 0.067862
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.958222

### PB8_T9
- T = 9
- Best hypothesis = `zscore_900`
- Pearson = 0.962465
- Spearman = 0.984500
- beta = 24.0296
- alpha = 51.0664
- MAE = 7.28306
- RMSE = 9.37873
- Score = 0.729879
- Score gap = 0.049100
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.958694

### PB8_T10
- T = 10
- Best hypothesis = `zscore_1500`
- Pearson = 0.963444
- Spearman = 0.984588
- beta = 24.1444
- alpha = 50.8446
- MAE = 7.12743
- RMSE = 9.20573
- Score = 0.731069
- Score gap = 0.021113
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.961280

### PB8_T11
- T = 11
- Best hypothesis = `zscore_1800`
- Pearson = 0.963867
- Spearman = 0.983913
- beta = 24.268
- alpha = 50.8342
- MAE = 7.14453
- RMSE = 9.17535
- Score = 0.730919
- Score gap = 0.010252
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.962032

### PB8_T12
- T = 12
- Best hypothesis = `zscore_3600`
- Pearson = 0.963053
- Spearman = 0.982633
- beta = 24.4936
- alpha = 50.81
- MAE = 7.00923
- RMSE = 8.79519
- Score = 0.730606
- Score gap = 0.070982
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.962124

## PB9

### PB9_T1
- T = 1
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T2
- T = 2
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T3
- T = 3
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T4
- T = 4
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T5
- T = 5
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T6
- T = 6
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T7
- T = 7
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T8
- T = 8
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T9
- T = 9
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T10
- T = 10
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T11
- T = 11
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

### PB9_T12
- T = 12
- Best hypothesis = `ema_5`
- Pearson = 0.999891
- Spearman = 0.999816
- beta = 1.00014
- alpha = -0.0140762
- MAE = 0.00176883
- RMSE = 0.00244547
- Score = 0.797319
- Score gap = 0.000354
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.999816

# VB

## VB1

### VB1_T1
- T = 1
- Best hypothesis = `rolling_std_5`
- Pearson = -0.334681
- Spearman = -0.374246
- beta = -4224.92
- alpha = 48.0027
- MAE = 18.2113
- RMSE = 24.7205
- Score = 0.120216
- Score gap = 0.008266
- Days represented = 70
- Confidence = **LOW**
- Best lag = 4 with lag correlation = 0.208060

### VB1_T2
- T = 2
- Best hypothesis = `rolling_std_10`
- Pearson = -0.410224
- Spearman = -0.463202
- beta = -2286.06
- alpha = 40.2375
- MAE = 10.6235
- RMSE = 13.414
- Score = 0.185921
- Score gap = 0.015060
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.325379

### VB1_T3
- T = 3
- Best hypothesis = `rolling_std_30`
- Pearson = -0.522522
- Spearman = -0.569357
- beta = -1194.41
- alpha = 40.6673
- MAE = 6.21295
- RMSE = 7.77041
- Score = 0.284844
- Score gap = 0.022481
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.507843

### VB1_T4
- T = 4
- Best hypothesis = `rolling_std_60`
- Pearson = -0.572633
- Spearman = -0.612713
- beta = -764.262
- alpha = 41.4229
- MAE = 4.85253
- RMSE = 6.02384
- Score = 0.328398
- Score gap = 0.032990
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.566885

### VB1_T5
- T = 5
- Best hypothesis = `rolling_std_90`
- Pearson = -0.591134
- Spearman = -0.633008
- beta = -595.167
- alpha = 42.0369
- MAE = 4.29658
- RMSE = 5.35312
- Score = 0.345551
- Score gap = 0.032052
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.587369

### VB1_T6
- T = 6
- Best hypothesis = `rolling_std_120`
- Pearson = -0.598092
- Spearman = -0.643587
- beta = -489.627
- alpha = 42.289
- MAE = 3.96559
- RMSE = 4.94112
- Score = 0.352570
- Score gap = 0.024898
- Days represented = 70
- Confidence = **LOW**
- Best lag = 4 with lag correlation = -0.687883

### VB1_T7
- T = 7
- Best hypothesis = `rolling_std_300`
- Pearson = -0.640170
- Spearman = -0.678783
- beta = -270.31
- alpha = 43.355
- MAE = 3.13625
- RMSE = 3.88929
- Score = 0.387296
- Score gap = 0.019008
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.639005

### VB1_T8
- T = 8
- Best hypothesis = `rolling_std_600`
- Pearson = -0.678115
- Spearman = -0.711131
- beta = -177.383
- alpha = 44.1103
- MAE = 2.67498
- RMSE = 3.30369
- Score = 0.420925
- Score gap = 0.032387
- Days represented = 69
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.677735

### VB1_T9
- T = 9
- Best hypothesis = `rolling_std_900`
- Pearson = -0.693353
- Spearman = -0.698584
- beta = -143.986
- alpha = 44.5536
- MAE = 2.44321
- RMSE = 3.02236
- Score = 0.426396
- Score gap = 0.026581
- Days represented = 69
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.693061

### VB1_T10
- T = 10
- Best hypothesis = `rolling_std_1500`
- Pearson = -0.702342
- Spearman = -0.734593
- beta = -111.542
- alpha = 45.1347
- MAE = 2.17252
- RMSE = 2.68137
- Score = 0.448028
- Score gap = 0.019625
- Days represented = 68
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.773494

### VB1_T11
- T = 11
- Best hypothesis = `rolling_std_1800`
- Pearson = -0.717209
- Spearman = -0.741459
- beta = -101.659
- alpha = 45.4183
- MAE = 2.13124
- RMSE = 2.57674
- Score = 0.454855
- Score gap = 0.024635
- Days represented = 67
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.805059

### VB1_T12
- T = 12
- Best hypothesis = `rolling_max_30`
- Pearson = -0.830074
- Spearman = -0.702536
- beta = -13.3371
- alpha = 1377.34
- MAE = 2.01226
- RMSE = 2.35111
- Score = 0.515927
- Score gap = 0.003563
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.830674

## VB2

### VB2_T1
- T = 1
- Best hypothesis = `range_5`
- Pearson = 0.843525
- Spearman = 0.837145
- beta = 0.251865
- alpha = 0.000653762
- MAE = 0.000606861
- RMSE = 0.000831897
- Score = 0.578946
- Score gap = 0.021678
- Days represented = 70
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.851218

### VB2_T2
- T = 2
- Best hypothesis = `range_3600`
- Pearson = 0.866452
- Spearman = 0.759510
- beta = 0.00514631
- alpha = 0.000350842
- MAE = 0.000811129
- RMSE = 0.00121542
- Score = 0.572487
- Score gap = 0.005119
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.827995

### VB2_T3
- T = 3
- Best hypothesis = `momentum_3600`
- Pearson = -0.917613
- Spearman = -0.770899
- beta = -0.00477639
- alpha = 0.00119777
- MAE = 0.000660049
- RMSE = 0.000899139
- Score = 0.613814
- Score gap = 0.003255
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.932371

### VB2_T4
- T = 4
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.933865
- Spearman = 0.783006
- beta = 0.0176112
- alpha = 0.000598082
- MAE = 0.000564185
- RMSE = 0.000790698
- Score = 0.633011
- Score gap = 0.046376
- Days represented = 1
- Confidence = **LOW**
- Best lag = 42 with lag correlation = -0.954043

### VB2_T5
- T = 5
- Best hypothesis = `rolling_return_3600`
- Pearson = -0.856890
- Spearman = -0.757673
- beta = -0.338771
- alpha = 0.00175586
- MAE = 0.000527006
- RMSE = 0.000670851
- Score = 0.575328
- Score gap = 0.012672
- Days represented = 2
- Confidence = **LOW**
- Best lag = 45 with lag correlation = -0.961032

### VB2_T6
- T = 6
- Best hypothesis = `sma_90`
- Pearson = -0.886262
- Spearman = -0.862702
- beta = -0.00540953
- alpha = 0.543378
- MAE = 0.000255322
- RMSE = 0.000349307
- Score = 0.620589
- Score gap = 0.043695
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.892866

### VB2_T7
- T = 7
- Best hypothesis = `ema_300`
- Pearson = -0.876799
- Spearman = -0.860276
- beta = -0.004116
- alpha = 0.415757
- MAE = 0.000220629
- RMSE = 0.0002887
- Score = 0.623198
- Score gap = 0.012265
- Days represented = 3
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.957093

### VB2_T8
- T = 8
- Best hypothesis = `ema_120`
- Pearson = -0.897409
- Spearman = -0.915072
- beta = -0.00409884
- alpha = 0.413047
- MAE = 0.000447851
- RMSE = 0.000661041
- Score = 0.650098
- Score gap = 0.040684
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 60 with lag correlation = -0.925576

### VB2_T9
- T = 9
- Best hypothesis = `sma_1500`
- Pearson = -0.921953
- Spearman = -0.717532
- beta = -0.00368562
- alpha = 0.372172
- MAE = 0.000168827
- RMSE = 0.000205854
- Score = 0.595518
- Score gap = 0.019941
- Days represented = 2
- Confidence = **LOW**
- Best lag = 60 with lag correlation = -0.947851

### VB2_T10
- T = 10
- Best hypothesis = `ema_120`
- Pearson = -0.883862
- Spearman = -0.843265
- beta = -0.005581
- alpha = 0.560846
- MAE = 0.000370295
- RMSE = 0.000490748
- Score = 0.610812
- Score gap = 0.009284
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.959276

### VB2_T11
- T = 11
- Best hypothesis = `ema_300`
- Pearson = -0.894635
- Spearman = -0.804691
- beta = -0.003886
- alpha = 0.395854
- MAE = 0.000306481
- RMSE = 0.000402967
- Score = 0.615382
- Score gap = 0.010519
- Days represented = 3
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.966828

### VB2_T12
- T = 12
- Best hypothesis = `ema_1500`
- Pearson = -0.888335
- Spearman = -0.813726
- beta = -0.00361113
- alpha = 0.362196
- MAE = 0.000236903
- RMSE = 0.000304228
- Score = 0.605741
- Score gap = 0.010182
- Days represented = 21
- Confidence = **MEDIUM**
- Best lag = 60 with lag correlation = 0.985943

## VB3

### VB3_T1
- T = 1
- Best hypothesis = `range_5`
- Pearson = 0.764655
- Spearman = 0.760711
- beta = 0.00262181
- alpha = 1.00852e-05
- MAE = 7.96573e-06
- RMSE = 1.13245e-05
- Score = 0.500832
- Score gap = 0.004796
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.771213

### VB3_T2
- T = 2
- Best hypothesis = `range_3600`
- Pearson = 0.847256
- Spearman = 0.750906
- beta = 6.16224e-05
- alpha = 7.06662e-06
- MAE = 1.03754e-05
- RMSE = 1.5835e-05
- Score = 0.556159
- Score gap = 0.018042
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.781035

### VB3_T3
- T = 3
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.898586
- Spearman = 0.762171
- beta = 0.000223935
- alpha = 1.11159e-05
- MAE = 8.64063e-06
- RMSE = 1.28204e-05
- Score = 0.597670
- Score gap = 0.000330
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.918500

### VB3_T4
- T = 4
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.923994
- Spearman = 0.775849
- beta = 0.000227734
- alpha = 1.14079e-05
- MAE = 7.72513e-06
- RMSE = 1.105e-05
- Score = 0.622369
- Score gap = 0.044227
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.944098

### VB3_T5
- T = 5
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.933451
- Spearman = 0.783686
- beta = 0.000229002
- alpha = 1.15066e-05
- MAE = 7.28239e-06
- RMSE = 1.03172e-05
- Score = 0.633153
- Score gap = 0.030893
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.953641

### VB3_T6
- T = 6
- Best hypothesis = `rolling_mean_90`
- Pearson = -0.882255
- Spearman = -0.863395
- beta = -6.73176e-05
- alpha = 0.00676552
- MAE = 3.21067e-06
- RMSE = 4.43814e-06
- Score = 0.618069
- Score gap = 0.000000
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.859844

### VB3_T7
- T = 7
- Best hypothesis = `ema_30`
- Pearson = -0.897621
- Spearman = -0.913086
- beta = -5.31809e-05
- alpha = 0.0053649
- MAE = 6.27385e-06
- RMSE = 8.64783e-06
- Score = 0.647456
- Score gap = 0.061483
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.952688

### VB3_T8
- T = 8
- Best hypothesis = `ema_600`
- Pearson = -0.876081
- Spearman = -0.798345
- beta = -5.10882e-05
- alpha = 0.00516477
- MAE = 3.15553e-06
- RMSE = 4.12596e-06
- Score = 0.590081
- Score gap = 0.001415
- Days represented = 6
- Confidence = **LOW**
- Best lag = 60 with lag correlation = 0.962436

### VB3_T9
- T = 9
- Best hypothesis = `rolling_mean_600`
- Pearson = -0.897361
- Spearman = -0.845177
- beta = -5.06324e-05
- alpha = 0.0051157
- MAE = 3.46447e-06
- RMSE = 4.35013e-06
- Score = 0.607757
- Score gap = 0.000000
- Days represented = 4
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.906026

### VB3_T10
- T = 10
- Best hypothesis = `ema_600`
- Pearson = -0.960140
- Spearman = -0.955582
- beta = -6.93627e-05
- alpha = 0.00697083
- MAE = 1.67832e-06
- RMSE = 2.3026e-06
- Score = 0.718191
- Score gap = 0.079041
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.961296

### VB3_T11
- T = 11
- Best hypothesis = `ema_600`
- Pearson = -0.949158
- Spearman = -0.947890
- beta = -5.22886e-05
- alpha = 0.00527588
- MAE = 3.87585e-06
- RMSE = 4.9621e-06
- Score = 0.649730
- Score gap = 0.049604
- Days represented = 3
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.932516

### VB3_T12
- T = 12
- Best hypothesis = `rolling_max_60`
- Pearson = 0.946815
- Spearman = 0.931755
- beta = 3.80944e-05
- alpha = -0.00379206
- MAE = 4.24105e-06
- RMSE = 6.00062e-06
- Score = 0.697261
- Score gap = 0.000099
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.984012

## VB4

### VB4_T1
- T = 1
- Best hypothesis = `range_5`
- Pearson = 0.764653
- Spearman = 0.760710
- beta = 0.00262175
- alpha = 1.00847e-05
- MAE = 7.96575e-06
- RMSE = 1.13254e-05
- Score = 0.500825
- Score gap = 0.004794
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.771215

### VB4_T2
- T = 2
- Best hypothesis = `range_3600`
- Pearson = 0.847255
- Spearman = 0.750906
- beta = 6.16224e-05
- alpha = 7.06669e-06
- MAE = 1.03754e-05
- RMSE = 1.58351e-05
- Score = 0.556159
- Score gap = 0.018040
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.781033

### VB4_T3
- T = 3
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.898585
- Spearman = 0.762170
- beta = 0.000223935
- alpha = 1.1116e-05
- MAE = 8.64069e-06
- RMSE = 1.28205e-05
- Score = 0.597669
- Score gap = 0.000326
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.918498

### VB4_T4
- T = 4
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.923992
- Spearman = 0.775848
- beta = 0.000227734
- alpha = 1.1408e-05
- MAE = 7.72519e-06
- RMSE = 1.10501e-05
- Score = 0.622367
- Score gap = 0.044226
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.944095

### VB4_T5
- T = 5
- Best hypothesis = `rolling_std_3600`
- Pearson = 0.933449
- Spearman = 0.783684
- beta = 0.000229001
- alpha = 1.15067e-05
- MAE = 7.28243e-06
- RMSE = 1.03174e-05
- Score = 0.633151
- Score gap = 0.030892
- Days represented = 1
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.953639

### VB4_T6
- T = 6
- Best hypothesis = `rolling_mean_90`
- Pearson = -0.882255
- Spearman = -0.863395
- beta = -6.7318e-05
- alpha = 0.00676556
- MAE = 3.21072e-06
- RMSE = 4.43817e-06
- Score = 0.618069
- Score gap = 0.000000
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.859839

### VB4_T7
- T = 7
- Best hypothesis = `ema_30`
- Pearson = -0.897617
- Spearman = -0.913083
- beta = -5.31813e-05
- alpha = 0.00536494
- MAE = 6.27413e-06
- RMSE = 8.64809e-06
- Score = 0.647451
- Score gap = 0.061481
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = 0.952688

### VB4_T8
- T = 8
- Best hypothesis = `ema_600`
- Pearson = -0.876087
- Spearman = -0.798342
- beta = -5.10882e-05
- alpha = 0.00516477
- MAE = 3.15558e-06
- RMSE = 4.12634e-06
- Score = 0.590080
- Score gap = 0.001412
- Days represented = 6
- Confidence = **LOW**
- Best lag = 60 with lag correlation = 0.962436

### VB4_T9
- T = 9
- Best hypothesis = `rolling_mean_600`
- Pearson = -0.897367
- Spearman = -0.845179
- beta = -5.06337e-05
- alpha = 0.00511582
- MAE = 3.46474e-06
- RMSE = 4.35029e-06
- Score = 0.607757
- Score gap = 0.000000
- Days represented = 4
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.906021

### VB4_T10
- T = 10
- Best hypothesis = `ema_600`
- Pearson = -0.960140
- Spearman = -0.955583
- beta = -6.93631e-05
- alpha = 0.00697087
- MAE = 1.67831e-06
- RMSE = 2.30261e-06
- Score = 0.718192
- Score gap = 0.079046
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.961296

### VB4_T11
- T = 11
- Best hypothesis = `ema_600`
- Pearson = -0.949160
- Spearman = -0.947890
- beta = -5.22891e-05
- alpha = 0.00527593
- MAE = 3.8758e-06
- RMSE = 4.9622e-06
- Score = 0.649733
- Score gap = 0.049611
- Days represented = 3
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.932519

### VB4_T12
- T = 12
- Best hypothesis = `rolling_max_60`
- Pearson = 0.946851
- Spearman = 0.931790
- beta = 3.80929e-05
- alpha = -0.00379191
- MAE = 4.23939e-06
- RMSE = 5.9982e-06
- Score = 0.697307
- Score gap = 0.000099
- Days represented = 1
- Confidence = **MEDIUM**
- Best lag = 1 with lag correlation = -0.984011

## VB5

### VB5_T1
- T = 1
- Best hypothesis = `range_5`
- Pearson = 0.999996
- Spearman = 0.995272
- beta = 0.00999841
- alpha = -2.74449e-08
- MAE = 9.46914e-08
- RMSE = 1.42148e-07
- Score = 0.797881
- Score gap = 0.035569
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.808642

### VB5_T2
- T = 2
- Best hypothesis = `range_10`
- Pearson = 0.999996
- Spearman = 0.997684
- beta = 0.00999911
- alpha = -6.19511e-08
- MAE = 1.59176e-07
- RMSE = 2.29203e-07
- Score = 0.798670
- Score gap = 0.058452
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.925626

### VB5_T3
- T = 3
- Best hypothesis = `range_30`
- Pearson = 0.999995
- Spearman = 0.999146
- beta = 0.0100012
- alpha = -1.54956e-07
- MAE = 3.17933e-07
- RMSE = 4.41594e-07
- Score = 0.799126
- Score gap = 0.076135
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.984184

### VB5_T4
- T = 4
- Best hypothesis = `range_60`
- Pearson = 0.999994
- Spearman = 0.999554
- beta = 0.0100023
- alpha = -2.50075e-07
- MAE = 4.69313e-07
- RMSE = 6.43239e-07
- Score = 0.799253
- Score gap = 0.079399
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.994034

### VB5_T5
- T = 5
- Best hypothesis = `range_90`
- Pearson = 0.999994
- Spearman = 0.999677
- beta = 0.0100037
- alpha = -3.25104e-07
- MAE = 5.86042e-07
- RMSE = 7.93227e-07
- Score = 0.799291
- Score gap = 0.079695
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.996522

### VB5_T6
- T = 6
- Best hypothesis = `range_120`
- Pearson = 0.999994
- Spearman = 0.999733
- beta = 0.0100042
- alpha = -3.99072e-07
- MAE = 6.8042e-07
- RMSE = 9.20868e-07
- Score = 0.799295
- Score gap = 0.081117
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.997618

### VB5_T7
- T = 7
- Best hypothesis = `range_300`
- Pearson = 0.999992
- Spearman = 0.999826
- beta = 0.0100045
- alpha = -7.34493e-07
- MAE = 1.05272e-06
- RMSE = 1.46746e-06
- Score = 0.799295
- Score gap = 0.086858
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999318

### VB5_T8
- T = 8
- Best hypothesis = `range_600`
- Pearson = 0.999992
- Spearman = 0.999806
- beta = 0.010003
- alpha = -1.03307e-06
- MAE = 1.47845e-06
- RMSE = 2.04983e-06
- Score = 0.799266
- Score gap = 0.088609
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999722

### VB5_T9
- T = 9
- Best hypothesis = `range_900`
- Pearson = 0.999991
- Spearman = 0.999775
- beta = 0.0100022
- alpha = -1.47172e-06
- MAE = 1.73003e-06
- RMSE = 2.41447e-06
- Score = 0.799264
- Score gap = 0.090882
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999826

### VB5_T10
- T = 10
- Best hypothesis = `range_1500`
- Pearson = 0.999991
- Spearman = 0.999602
- beta = 0.0100025
- alpha = -2.05939e-06
- MAE = 2.22645e-06
- RMSE = 2.968e-06
- Score = 0.799204
- Score gap = 0.094135
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999904

### VB5_T11
- T = 11
- Best hypothesis = `range_1800`
- Pearson = 0.999992
- Spearman = 0.999516
- beta = 0.0100024
- alpha = -2.26311e-06
- MAE = 2.43366e-06
- RMSE = 3.21519e-06
- Score = 0.799162
- Score gap = 0.099204
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999919

### VB5_T12
- T = 12
- Best hypothesis = `range_3600`
- Pearson = 0.999990
- Spearman = 0.998554
- beta = 0.0100016
- alpha = -2.07382e-06
- MAE = 3.14794e-06
- RMSE = 4.04581e-06
- Score = 0.798772
- Score gap = 0.116232
- Days represented = 70
- Confidence = **HIGH**
- Best lag = 1 with lag correlation = 0.999955

## VB6

### VB6_T1
- T = 1
- Best hypothesis = `range_5`
- Pearson = 0.034380
- Spearman = 0.168152
- beta = 28.2907
- alpha = 1.10865
- MAE = 1.22471
- RMSE = 5.32495
- Score = -0.048575
- Score gap = 0.018886
- Days represented = 13
- Confidence = **LOW**
- Best lag = 2 with lag correlation = -0.100367

### VB6_T2
- T = 2
- Best hypothesis = `range_5`
- Pearson = 0.170999
- Spearman = 0.281048
- beta = 62.9524
- alpha = 0.745343
- MAE = 1.0313
- RMSE = 1.92874
- Score = 0.024991
- Score gap = 0.021566
- Days represented = 64
- Confidence = **LOW**
- Best lag = 6 with lag correlation = -0.114088

### VB6_T3
- T = 3
- Best hypothesis = `range_5`
- Pearson = 0.333659
- Spearman = 0.349567
- beta = 81.9602
- alpha = 0.473553
- MAE = 0.835054
- RMSE = 1.19961
- Score = 0.113829
- Score gap = 0.032740
- Days represented = 70
- Confidence = **LOW**
- Best lag = 22 with lag correlation = -0.071821

### VB6_T4
- T = 4
- Best hypothesis = `range_5`
- Pearson = 0.369737
- Spearman = 0.370460
- beta = 87.1494
- alpha = 0.416393
- MAE = 0.795984
- RMSE = 1.11359
- Score = 0.137552
- Score gap = 0.034497
- Days represented = 70
- Confidence = **LOW**
- Best lag = 35 with lag correlation = -0.044655

### VB6_T5
- T = 5
- Best hypothesis = `range_5`
- Pearson = 0.385964
- Spearman = 0.378418
- beta = 88.9434
- alpha = 0.390988
- MAE = 0.783526
- RMSE = 1.0958
- Score = 0.148683
- Score gap = 0.035398
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.065428

### VB6_T6
- T = 6
- Best hypothesis = `range_5`
- Pearson = 0.394463
- Spearman = 0.383410
- beta = 91.1197
- alpha = 0.376318
- MAE = 0.777092
- RMSE = 1.08658
- Score = 0.155287
- Score gap = 0.035477
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = -0.089587

### VB6_T7
- T = 7
- Best hypothesis = `range_5`
- Pearson = 0.416398
- Spearman = 0.393520
- beta = 94.0541
- alpha = 0.342875
- MAE = 0.764381
- RMSE = 1.07121
- Score = 0.170078
- Score gap = 0.035254
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.074932

### VB6_T8
- T = 8
- Best hypothesis = `range_5`
- Pearson = 0.427152
- Spearman = 0.396990
- beta = 96.558
- alpha = 0.327314
- MAE = 0.758625
- RMSE = 1.06572
- Score = 0.176144
- Score gap = 0.036051
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.088008

### VB6_T9
- T = 9
- Best hypothesis = `range_5`
- Pearson = 0.434503
- Spearman = 0.398515
- beta = 99.3753
- alpha = 0.318804
- MAE = 0.755678
- RMSE = 1.05817
- Score = 0.180126
- Score gap = 0.036173
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.093879

### VB6_T10
- T = 10
- Best hypothesis = `range_5`
- Pearson = 0.440922
- Spearman = 0.400347
- beta = 100.825
- alpha = 0.311553
- MAE = 0.745568
- RMSE = 1.04709
- Score = 0.183519
- Score gap = 0.034199
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.100292

### VB6_T11
- T = 11
- Best hypothesis = `range_5`
- Pearson = 0.443396
- Spearman = 0.400946
- beta = 101.113
- alpha = 0.303949
- MAE = 0.741948
- RMSE = 1.04389
- Score = 0.185480
- Score gap = 0.034701
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.102399

### VB6_T12
- T = 12
- Best hypothesis = `range_5`
- Pearson = 0.452322
- Spearman = 0.407608
- beta = 100.758
- alpha = 0.274107
- MAE = 0.726044
- RMSE = 1.02973
- Score = 0.194012
- Score gap = 0.034413
- Days represented = 70
- Confidence = **LOW**
- Best lag = 1 with lag correlation = 0.111753

## Interpretation Rule
A candidate is treated as a hypothesis rather than a confirmed identity. High correlation, stable affine parameters, low reconstruction error, cross-day persistence and sensible lag behaviour increase confidence; isolated correlation does not.
