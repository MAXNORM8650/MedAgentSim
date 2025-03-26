***** Replication dofile for "The electoral success of angels and demons" (JSPP, Nai, 2019)
****************************************



** Instructions

* 1. Use the dataset NEGex_1.0_candidates.dta
* 2. Run the syntax in the "Create variables" section (section A) first
* 3. Run the separate syntaxes to replicate all analyses, either the main analyses (section B) or the robustness checks (section C)
* 4. More general information about the data (NEGexy version 1.0) can be found in the following OSF repository: https://osf.io/mhpfg/








***** A. CREATE VARIABLES
****************************************


**** DVs


* fix for Argentina 

replace c_votesprc=41.75 if lastname3=="Macri [ARG]"
replace c_votesprc=22.5 if lastname3=="Kirchner [ARG]"
replace c_votesprc=3 if lastname3=="Massa [ARG]"
replace c_votesprc=2 if lastname3=="Binner [ARG]"


* Absolute success: % of votes received (controlling by number of candidates)

gen SUCCESS_abs = c_votesprc
tab SUCCESS_abs
sum SUCCESS_abs

gen SUCCESS_abs01 = SUCCESS_abs/100

* Relative success, based on ENP

gen SUCCESS_relENP = (c_votesprc/(100/e_ENPvotes))*100
label variable SUCCESS_relENP "Relative success, compared to avg candidate, ENP (Berggren et al 2010)"
tab SUCCESS_relENP
sum SUCCESS_relENP

* Deviation from average result in election, based on ENP

gen AVG_resENP = 100/e_ENPvotes

gen SUCCESS_devENP = c_votesprc - AVG_resENP
label variable SUCCESS_devENP "Deviation from average success in election, ENP (Rosar et al. 2008)"
tab SUCCESS_devENP
sum SUCCESS_devENP

* Winner

generate SUCCESS_win = c_rank
recode SUCCESS_win (1=1)(else=0)
tab SUCCESS_win





***** IVs

* personality quadratic terms

gen bfi_extrav2 = bfi_extrav^2
gen bfi_agree2 = bfi_agree^2
gen bfi_consc2 = bfi_consc^2
gen bfi_emot2 = bfi_emot^2
gen bfi_open2 = bfi_open^2
gen triad_narciss2 = triad_narciss^2
gen triad_psycho2 = triad_psycho^2
gen triad_machiav2 = triad_machiav^2




* personality standard deviations

gen sd_extrav = (sdbfi_c1 + sdbfi_c6)/2
gen sd_agree = (sdbfi_c2 + sdbfi_c7)/2
gen sd_consc = (sdbfi_c3 + sdbfi_c8)/2
gen sd_emot = (sdbfi_c4 + sdbfi_c9)/2
gen sd_open = (sdbfi_c5 + sdbfi_c10)/2
gen sd_narciss = (sdtriad_c1 + sdtriad_c4)/2
gen sd_psycho = (sdtriad_c2 + sdtriad_c5)/2
gen sd_machiav = (sdtriad_c3 + sdtriad_c6)/2

gen sd_alltraits = (sdbfi_c1 + sdbfi_c2 + sdbfi_c3 + sdbfi_c4 + sdbfi_c5 + sdbfi_c6 + sdbfi_c7 + sdbfi_c8 + sdbfi_c9 + sdbfi_c10 + sdtriad_c1 + sdtriad_c2 + sdtriad_c3 + sdtriad_c4 + sdtriad_c5 + sdtriad_c6) / 16



* competitiveness

tab sal_racecomp
generate compet = (sal_racecomp- 4)*-1
tab compet 

label variable compet "Competitiveness"


* OECD

gen oecd=.
replace oecd=	0	if country_codeNEGex=="AFG"
replace oecd=	0	if country_codeNEGex=="ALB"
replace oecd=	0	if country_codeNEGex=="DZA"
replace oecd=	0	if country_codeNEGex=="ASM"
replace oecd=	0	if country_codeNEGex=="AND"
replace oecd=	0	if country_codeNEGex=="AGO"
replace oecd=	0	if country_codeNEGex=="AIA"
replace oecd=	0	if country_codeNEGex=="ATG"
replace oecd=	0	if country_codeNEGex=="ARG"
replace oecd=	0	if country_codeNEGex=="ARM"
replace oecd=	0	if country_codeNEGex=="ABW"
replace oecd=	1	if country_codeNEGex=="AUS"
replace oecd=	1	if country_codeNEGex=="AUT"
replace oecd=	0	if country_codeNEGex=="AZE"
replace oecd=	0	if country_codeNEGex=="BHS"
replace oecd=	0	if country_codeNEGex=="BHR"
replace oecd=	0	if country_codeNEGex=="BGD"
replace oecd=	0	if country_codeNEGex=="BRB"
replace oecd=	0	if country_codeNEGex=="BLR"
replace oecd=	1	if country_codeNEGex=="BEL"
replace oecd=	0	if country_codeNEGex=="BLZ"
replace oecd=	0	if country_codeNEGex=="BEN"
replace oecd=	0	if country_codeNEGex=="BMU"
replace oecd=	0	if country_codeNEGex=="BTN"
replace oecd=	0	if country_codeNEGex=="BOL"
replace oecd=	0	if country_codeNEGex=="BIH"
replace oecd=	0	if country_codeNEGex=="BWA"
replace oecd=	0	if country_codeNEGex=="BVT"
replace oecd=	0	if country_codeNEGex=="BRA"
replace oecd=	0	if country_codeNEGex=="VGB"
replace oecd=	0	if country_codeNEGex=="BRN"
replace oecd=	0	if country_codeNEGex=="BGR"
replace oecd=	0	if country_codeNEGex=="BFA"
replace oecd=	0	if country_codeNEGex=="BDI"
replace oecd=	0	if country_codeNEGex=="KHM"
replace oecd=	0	if country_codeNEGex=="CMR"
replace oecd=	1	if country_codeNEGex=="CAN"
replace oecd=	0	if country_codeNEGex=="CPV"
replace oecd=	0	if country_codeNEGex=="CYM"
replace oecd=	0	if country_codeNEGex=="CAF"
replace oecd=	0	if country_codeNEGex=="TCD"
replace oecd=	1	if country_codeNEGex=="CHL"
replace oecd=	0	if country_codeNEGex=="CHN"
replace oecd=	0	if country_codeNEGex=="CXR"
replace oecd=	0	if country_codeNEGex=="COL"
replace oecd=	0	if country_codeNEGex=="COM"
replace oecd=	0	if country_codeNEGex=="COG"
replace oecd=	0	if country_codeNEGex=="COD"
replace oecd=	0	if country_codeNEGex=="COK"
replace oecd=	0	if country_codeNEGex=="CRI"
replace oecd=	0	if country_codeNEGex=="CIV"
replace oecd=	0	if country_codeNEGex=="CRO"
replace oecd=	0	if country_codeNEGex=="CUB"
replace oecd=	0	if country_codeNEGex=="CYP"
replace oecd=	1	if country_codeNEGex=="CZE"
replace oecd=	1	if country_codeNEGex=="DNK"
replace oecd=	0	if country_codeNEGex=="DJI"
replace oecd=	0	if country_codeNEGex=="DMA"
replace oecd=	0	if country_codeNEGex=="DOM"
replace oecd=	0	if country_codeNEGex=="ECU"
replace oecd=	0	if country_codeNEGex=="EGY"
replace oecd=	0	if country_codeNEGex=="SLV"
replace oecd=	0	if country_codeNEGex=="GNQ"
replace oecd=	0	if country_codeNEGex=="ERI"
replace oecd=	1	if country_codeNEGex=="EST"
replace oecd=	0	if country_codeNEGex=="ETH"
replace oecd=	0	if country_codeNEGex=="FRO"
replace oecd=	0	if country_codeNEGex=="FJI"
replace oecd=	1	if country_codeNEGex=="FIN"
replace oecd=	1	if country_codeNEGex=="FRA"
replace oecd=	0	if country_codeNEGex=="GUF"
replace oecd=	0	if country_codeNEGex=="PYF"
replace oecd=	0	if country_codeNEGex=="GAB"
replace oecd=	0	if country_codeNEGex=="GMB"
replace oecd=	0	if country_codeNEGex=="GRG"
replace oecd=	1	if country_codeNEGex=="DEU"
replace oecd=	0	if country_codeNEGex=="GHA"
replace oecd=	0	if country_codeNEGex=="GIB"
replace oecd=	1	if country_codeNEGex=="GRC"
replace oecd=	0	if country_codeNEGex=="GRL"
replace oecd=	0	if country_codeNEGex=="GRD"
replace oecd=	0	if country_codeNEGex=="GLP"
replace oecd=	0	if country_codeNEGex=="GUM"
replace oecd=	0	if country_codeNEGex=="GTM"
replace oecd=	0	if country_codeNEGex=="GGY"
replace oecd=	0	if country_codeNEGex=="GIN"
replace oecd=	0	if country_codeNEGex=="GNB"
replace oecd=	0	if country_codeNEGex=="GUY"
replace oecd=	0	if country_codeNEGex=="HTI"
replace oecd=	0	if country_codeNEGex=="HND"
replace oecd=	0	if country_codeNEGex=="HKG"
replace oecd=	1	if country_codeNEGex=="HUN"
replace oecd=	1	if country_codeNEGex=="ICE"
replace oecd=	0	if country_codeNEGex=="IND"
replace oecd=	0	if country_codeNEGex=="IDN"
replace oecd=	0	if country_codeNEGex=="IRN"
replace oecd=	0	if country_codeNEGex=="IRQ"
replace oecd=	1	if country_codeNEGex=="IRL"
replace oecd=	1	if country_codeNEGex=="ISR"
replace oecd=	1	if country_codeNEGex=="ITA"
replace oecd=	0	if country_codeNEGex=="JAM"
replace oecd=	1	if country_codeNEGex=="JAP"
replace oecd=	0	if country_codeNEGex=="JEY"
replace oecd=	0	if country_codeNEGex=="JOR"
replace oecd=	0	if country_codeNEGex=="KAZ"
replace oecd=	0	if country_codeNEGex=="KEN"
replace oecd=	0	if country_codeNEGex=="KIR"
replace oecd=	0	if country_codeNEGex=="XKX"
replace oecd=	0	if country_codeNEGex=="KWT"
replace oecd=	0	if country_codeNEGex=="KGZ"
replace oecd=	0	if country_codeNEGex=="LAO"
replace oecd=	1	if country_codeNEGex=="LVA"
replace oecd=	0	if country_codeNEGex=="LBN"
replace oecd=	0	if country_codeNEGex=="LSO"
replace oecd=	0	if country_codeNEGex=="LBR"
replace oecd=	0	if country_codeNEGex=="LBY"
replace oecd=	0	if country_codeNEGex=="LIE"
replace oecd=	0	if country_codeNEGex=="LTH"
replace oecd=	1	if country_codeNEGex=="LUX"
replace oecd=	0	if country_codeNEGex=="MAC"
replace oecd=	0	if country_codeNEGex=="MKD"
replace oecd=	0	if country_codeNEGex=="MDG"
replace oecd=	0	if country_codeNEGex=="MWI"
replace oecd=	0	if country_codeNEGex=="MYS"
replace oecd=	0	if country_codeNEGex=="MDV"
replace oecd=	0	if country_codeNEGex=="MLI"
replace oecd=	0	if country_codeNEGex=="MLT"
replace oecd=	0	if country_codeNEGex=="MTQ"
replace oecd=	0	if country_codeNEGex=="MRT"
replace oecd=	0	if country_codeNEGex=="MUS"
replace oecd=	0	if country_codeNEGex=="MYT"
replace oecd=	1	if country_codeNEGex=="MEX"
replace oecd=	0	if country_codeNEGex=="MDV"
replace oecd=	0	if country_codeNEGex=="MCO"
replace oecd=	0	if country_codeNEGex=="MON"
replace oecd=	0	if country_codeNEGex=="MTN"
replace oecd=	0	if country_codeNEGex=="MSR"
replace oecd=	0	if country_codeNEGex=="MRC"
replace oecd=	0	if country_codeNEGex=="MOZ"
replace oecd=	0	if country_codeNEGex=="MMR"
replace oecd=	0	if country_codeNEGex=="NAM"
replace oecd=	0	if country_codeNEGex=="NRU"
replace oecd=	0	if country_codeNEGex=="NPL"
replace oecd=	1	if country_codeNEGex=="NLD"
replace oecd=	0	if country_codeNEGex=="ANT"
replace oecd=	0	if country_codeNEGex=="NCL"
replace oecd=	1	if country_codeNEGex=="NZL"
replace oecd=	0	if country_codeNEGex=="NIC"
replace oecd=	0	if country_codeNEGex=="NER"
replace oecd=	0	if country_codeNEGex=="NGA"
replace oecd=	0	if country_codeNEGex=="NIU"
replace oecd=	0	if country_codeNEGex=="NFK"
replace oecd=	1	if country_codeNEGex=="NOR"
replace oecd=	0	if country_codeNEGex=="OMN"
replace oecd=	0	if country_codeNEGex=="PAK"
replace oecd=	0	if country_codeNEGex=="PLW"
replace oecd=	0	if country_codeNEGex=="PSE"
replace oecd=	0	if country_codeNEGex=="PAN"
replace oecd=	0	if country_codeNEGex=="PNG"
replace oecd=	0	if country_codeNEGex=="PRY"
replace oecd=	0	if country_codeNEGex=="PER"
replace oecd=	0	if country_codeNEGex=="PHL"
replace oecd=	0	if country_codeNEGex=="PCN"
replace oecd=	1	if country_codeNEGex=="POL"
replace oecd=	1	if country_codeNEGex=="PRT"
replace oecd=	0	if country_codeNEGex=="PRI"
replace oecd=	0	if country_codeNEGex=="QAT"
replace oecd=	0	if country_codeNEGex=="REU"
replace oecd=	0	if country_codeNEGex=="ROU"
replace oecd=	0	if country_codeNEGex=="RUS"
replace oecd=	0	if country_codeNEGex=="RWA"
replace oecd=	0	if country_codeNEGex=="SHN"
replace oecd=	0	if country_codeNEGex=="KNA"
replace oecd=	0	if country_codeNEGex=="LCA"
replace oecd=	0	if country_codeNEGex=="SPM"
replace oecd=	0	if country_codeNEGex=="VCT"
replace oecd=	0	if country_codeNEGex=="BLM"
replace oecd=	0	if country_codeNEGex=="MAF"
replace oecd=	0	if country_codeNEGex=="WSM"
replace oecd=	0	if country_codeNEGex=="SMR"
replace oecd=	0	if country_codeNEGex=="STP"
replace oecd=	0	if country_codeNEGex=="SAU"
replace oecd=	0	if country_codeNEGex=="SEN"
replace oecd=	0	if country_codeNEGex=="SRB"
replace oecd=	0	if country_codeNEGex=="SYC"
replace oecd=	0	if country_codeNEGex=="SLE"
replace oecd=	0	if country_codeNEGex=="SGP"
replace oecd=	1	if country_codeNEGex=="SVK"
replace oecd=	1	if country_codeNEGex=="SVN"
replace oecd=	0	if country_codeNEGex=="SLB"
replace oecd=	0	if country_codeNEGex=="SOM"
replace oecd=	0	if country_codeNEGex=="ZAF"
replace oecd=	1	if country_codeNEGex=="KOR"
replace oecd=	0	if country_codeNEGex=="SSD"
replace oecd=	1	if country_codeNEGex=="ESP"
replace oecd=	0	if country_codeNEGex=="LKA"
replace oecd=	0	if country_codeNEGex=="SDN"
replace oecd=	0	if country_codeNEGex=="SUR"
replace oecd=	0	if country_codeNEGex=="SWZ"
replace oecd=	1	if country_codeNEGex=="SWE"
replace oecd=	1	if country_codeNEGex=="CHE"
replace oecd=	0	if country_codeNEGex=="SYR"
replace oecd=	0	if country_codeNEGex=="TWN"
replace oecd=	0	if country_codeNEGex=="TJK"
replace oecd=	0	if country_codeNEGex=="TZA"
replace oecd=	0	if country_codeNEGex=="THA"
replace oecd=	0	if country_codeNEGex=="TLS"
replace oecd=	0	if country_codeNEGex=="TGO"
replace oecd=	0	if country_codeNEGex=="TKL"
replace oecd=	0	if country_codeNEGex=="TON"
replace oecd=	0	if country_codeNEGex=="TTO"
replace oecd=	0	if country_codeNEGex=="TUN"
replace oecd=	1	if country_codeNEGex=="TUR"
replace oecd=	0	if country_codeNEGex=="TKM"
replace oecd=	0	if country_codeNEGex=="TCA"
replace oecd=	0	if country_codeNEGex=="TUV"
replace oecd=	0	if country_codeNEGex=="UGA"
replace oecd=	0	if country_codeNEGex=="UKR"
replace oecd=	0	if country_codeNEGex=="ARE"
replace oecd=	1	if country_codeNEGex=="GBR"
replace oecd=	1	if country_codeNEGex=="USA"
replace oecd=	0	if country_codeNEGex=="URY"
replace oecd=	0	if country_codeNEGex=="UZB"
replace oecd=	0	if country_codeNEGex=="VUT"
replace oecd=	0	if country_codeNEGex=="VEN"
replace oecd=	0	if country_codeNEGex=="VNM"
replace oecd=	0	if country_codeNEGex=="WLF"
replace oecd=	0	if country_codeNEGex=="YEM"
replace oecd=	0	if country_codeNEGex=="ZAM"
replace oecd=	0	if country_codeNEGex=="ZWE"
replace oecd=	0	if country_codeNEGex=="NIR"

tab oecd



* geographical region

generate country_region2 = country_region
recode country_region2 (1 10=1)(2=2)(3 4=3)(5=4)(6 9=5)(7 8=6)(11=7)(12 14 15=8)(13=9)(16=10)

label define country_region2 ///
1 "MENA" ///
2 "Sub-Saharan Africa" ///
3 "Latin America and Caribbean" ///
4 "North America" ///
5 "Central and South Asia" ///
6 "East and South-East Asia" ///
7 "Eastern Europe" ///
8 "Western and Northern Europe (incl AUS NZ)" ///
9 "Southern Europe" ///
10 "Melanesia, Micronesia and Polinesia", modify

label value country_region2 country_region2

tab country_region2

replace country_region2=9 if country=="Macedonia"


generate country_region3 = country_region2
recode country_region3 (10=6)(4=8)

label define country_region3 ///
1 "MENA" ///
2 "Sub-Saharan Africa" ///
3 "Latin America and Caribbean" ///
5 "Central and South Asia" ///
6 "East and South-East Asia (incl mel micr polin)" ///
7 "Eastern Europe" ///
8 "Western and Northern Europe (incl USA AUS NZ)" ///
9 "Southern Europe", modify

label value country_region3 country_region3

tab country_region3

replace country_region3=9 if electID=="MKD_L_20161211"





* Economic fitness

gen EcoFit=.

replace EcoFit=	0.37	if country=="Albania"
replace EcoFit=	0.00	if country=="Algeria"
replace EcoFit=	0.62	if country=="Argentina"
replace EcoFit=	0.32	if country=="Armenia"
replace EcoFit=	0.39	if country=="Australia"
replace EcoFit=	3.34	if country=="Austria"
replace EcoFit=	0.97	if country=="Belarus"
replace EcoFit=	1.77	if country=="Bulgaria"
replace EcoFit=	.		if country=="Cape Verde"
replace EcoFit=	0.42	if country=="Chile"
replace EcoFit=	0.41	if country=="Costa Rica"
replace EcoFit=	0.06	if country=="Côte d'Ivoire"
replace EcoFit=	1.33	if country=="Croatia"
replace EcoFit=	0.84	if country=="Cyprus"
replace EcoFit=	3.11	if country=="Czech Republic"
replace EcoFit=	0.08	if country=="Ecuador"
replace EcoFit=	1.71	if country=="Finland"
replace EcoFit=	4.40	if country=="France"
replace EcoFit=	0.00	if country=="Gabon"
replace EcoFit=	0.28	if country=="Georgia"
replace EcoFit=	6.67	if country=="Germany"
replace EcoFit=	0.01	if country=="Ghana"
replace EcoFit=	.		if country=="Haiti"
replace EcoFit=	.		if country=="Hong Kong"
replace EcoFit=	0.13	if country=="Iceland"
replace EcoFit=	0.00	if country=="Iran"
replace EcoFit=	5.62	if country=="Italy"
replace EcoFit=	7.54	if country=="Japan"
replace EcoFit=	0.46	if country=="Jordan"
replace EcoFit=	0.29	if country=="Kenya"
replace EcoFit=	.		if country=="Kosovo"
replace EcoFit=	0.29	if country=="Kyrgyzstan"
replace EcoFit=	.		if country=="Lesotho"
replace EcoFit=	1.73	if country=="Lithuania"
replace EcoFit=	0.42	if country=="Macedonia"
replace EcoFit=	0.34	if country=="Malta"
replace EcoFit=	.		if country=="Moldova"
replace EcoFit=	0.03	if country=="Mongolia"
replace EcoFit=	0.26	if country=="Montenegro"
replace EcoFit=	0.52	if country=="Morocco"
replace EcoFit=	0.65	if country=="New Zealand"
replace EcoFit=	0.10	if country=="Nicaragua"
replace EcoFit=	.		if country=="Northern Ireland"
replace EcoFit=	0.60	if country=="Norway"
replace EcoFit=	.		if country=="Papua New Guinea"
replace EcoFit=	1.75	if country=="Romania"
replace EcoFit=	0.85	if country=="Russia"
replace EcoFit=	0.12	if country=="Rwanda"
replace EcoFit=	.		if country=="São Tomé and Príncipe"
replace EcoFit=	0.16	if country=="Senegal"
replace EcoFit=	1.04	if country=="Serbia"
replace EcoFit=	2.27	if country=="Slovenia"
replace EcoFit=	3.45	if country=="South Korea"
replace EcoFit=	3.67	if country=="Spain"
replace EcoFit=	.		if country=="The Bahamas"
replace EcoFit=	0.00	if country=="The Gambia"
replace EcoFit=	3.81	if country=="The Netherlands"
replace EcoFit=	.		if country=="Timor Leste"
replace EcoFit=	3.61	if country=="UK"
replace EcoFit=	5.26	if country=="USA"
replace EcoFit=	0.19	if country=="Uzbekistan"
replace EcoFit=	0.07	if country=="Zambia"

sum EcoFit





* compute the average of all traits per election

gen AVG_bfi_extrav=.
replace AVG_bfi_extrav=	2.25	if electID=="ALB_L_20170625"
replace AVG_bfi_extrav=	2.71	if electID=="ARG_L_20171022"
replace AVG_bfi_extrav=	1.53	if electID=="ARM_L_20170402"
replace AVG_bfi_extrav=	2.58	if electID=="AUS_L_20160702"
replace AVG_bfi_extrav=	2.72	if electID=="AUT_L_20171015"
replace AVG_bfi_extrav=	1.71	if electID=="AUT_P_20161204"
replace AVG_bfi_extrav=	3.05	if electID=="BGR_L_20170326"
replace AVG_bfi_extrav=	1.58	if electID=="BGR_P_20161106"
replace AVG_bfi_extrav=	2.23	if electID=="BHS_L_20170510"
replace AVG_bfi_extrav=	2.18	if electID=="CHL_P_20171119"
replace AVG_bfi_extrav=	2.20	if electID=="CRI_P_20180204"
replace AVG_bfi_extrav=	2.46	if electID=="CRO_L_20160911"
replace AVG_bfi_extrav=	1.63	if electID=="CYP_P_20180128"
replace AVG_bfi_extrav=	2.72	if electID=="CZE_L_20171020"
replace AVG_bfi_extrav=	2.65	if electID=="CZE_P_20180112"
replace AVG_bfi_extrav=	1.65	if electID=="DEU_L_20170924"
replace AVG_bfi_extrav=	1.94	if electID=="DZA_L_20170504"
replace AVG_bfi_extrav=	1.99	if electID=="ECU_P_20170219"
replace AVG_bfi_extrav=	0.13	if electID=="ESP_L_20160626"
replace AVG_bfi_extrav=	1.85	if electID=="FIN_P_20180128"
replace AVG_bfi_extrav=	1.72	if electID=="FRA_L_20170611"
replace AVG_bfi_extrav=	2.52	if electID=="FRA_P_20170423"
replace AVG_bfi_extrav=	1.81	if electID=="GBR_L_20170608"
replace AVG_bfi_extrav=	2.88	if electID=="GHA_P_20161207"
replace AVG_bfi_extrav=	1.58	if electID=="GRG_L_20161008"
replace AVG_bfi_extrav=	3.04	if electID=="ICE_L_20161029"
replace AVG_bfi_extrav=	2.78	if electID=="ICE_L_20171028"
replace AVG_bfi_extrav=	2.58	if electID=="ICE_P_20160625"
replace AVG_bfi_extrav=	1.71	if electID=="IRN_P_20170519"
replace AVG_bfi_extrav=	3.07	if electID=="ITA_L_20180304"
replace AVG_bfi_extrav=	1.86	if electID=="JAP_L_20160710"
replace AVG_bfi_extrav=	2.53	if electID=="JAP_L_20171022"
replace AVG_bfi_extrav=	2.75	if electID=="KEN_P_20170808"
replace AVG_bfi_extrav=	2.05	if electID=="LTH_L_20161009"
replace AVG_bfi_extrav=	2.33	if electID=="MDV_P_20161030"
replace AVG_bfi_extrav=	2.56	if electID=="MKD_L_20161211"
replace AVG_bfi_extrav=	2.57	if electID=="MLT_L_20170603"
replace AVG_bfi_extrav=	2.00	if electID=="MON_L_20160630"
replace AVG_bfi_extrav=	3.33	if electID=="MRC_L_20161007"
replace AVG_bfi_extrav=	2.00	if electID=="MTN_L_20161016"
replace AVG_bfi_extrav=	0.83	if electID=="NIC_P_20161106"
replace AVG_bfi_extrav=	2.33	if electID=="NIR_L_20170302"
replace AVG_bfi_extrav=	2.42	if electID=="NLD_L_20170315"
replace AVG_bfi_extrav=	2.27	if electID=="NOR_L_20170911"
replace AVG_bfi_extrav=	2.23	if electID=="NZL_L_20170923"
replace AVG_bfi_extrav=	2.22	if electID=="ROU_L_20161211"
replace AVG_bfi_extrav=	2.16	if electID=="RUS_L_20160918"
replace AVG_bfi_extrav=	2.79	if electID=="RUS_P_20180318"
replace AVG_bfi_extrav=	2.58	if electID=="RWA_P_20170804"
replace AVG_bfi_extrav=	2.10	if electID=="SRB_P_20170402"
replace AVG_bfi_extrav=	1.60	if electID=="TLS_L_20170722"
replace AVG_bfi_extrav=	1.67	if electID=="TLS_P_20170320"
replace AVG_bfi_extrav=	2.80	if electID=="USA_P_20161108"
replace AVG_bfi_extrav=	2.38	if electID=="UZB_P_20161204"
replace AVG_bfi_extrav=	2.14	if electID=="XKX_L_20170611"

gen AVG_bfi_agree=.
replace AVG_bfi_agree=	2.08	if electID=="ALB_L_20170625"
replace AVG_bfi_agree=	1.20	if electID=="ARG_L_20171022"
replace AVG_bfi_agree=	2.22	if electID=="ARM_L_20170402"
replace AVG_bfi_agree=	2.25	if electID=="AUS_L_20160702"
replace AVG_bfi_agree=	1.91	if electID=="AUT_L_20171015"
replace AVG_bfi_agree=	1.82	if electID=="AUT_P_20161204"
replace AVG_bfi_agree=	1.25	if electID=="BGR_L_20170326"
replace AVG_bfi_agree=	1.88	if electID=="BGR_P_20161106"
replace AVG_bfi_agree=	2.57	if electID=="BHS_L_20170510"
replace AVG_bfi_agree=	2.25	if electID=="CHL_P_20171119"
replace AVG_bfi_agree=	2.41	if electID=="CRI_P_20180204"
replace AVG_bfi_agree=	1.28	if electID=="CRO_L_20160911"
replace AVG_bfi_agree=	1.76	if electID=="CYP_P_20180128"
replace AVG_bfi_agree=	1.15	if electID=="CZE_L_20171020"
replace AVG_bfi_agree=	1.52	if electID=="CZE_P_20180112"
replace AVG_bfi_agree=	1.60	if electID=="DEU_L_20170924"
replace AVG_bfi_agree=	1.75	if electID=="DZA_L_20170504"
replace AVG_bfi_agree=	2.10	if electID=="ECU_P_20170219"
replace AVG_bfi_agree=	1.63	if electID=="ESP_L_20160626"
replace AVG_bfi_agree=	2.75	if electID=="FIN_P_20180128"
replace AVG_bfi_agree=	2.08	if electID=="FRA_L_20170611"
replace AVG_bfi_agree=	1.60	if electID=="FRA_P_20170423"
replace AVG_bfi_agree=	1.61	if electID=="GBR_L_20170608"
replace AVG_bfi_agree=	2.75	if electID=="GHA_P_20161207"
replace AVG_bfi_agree=	2.92	if electID=="GRG_L_20161008"
replace AVG_bfi_agree=	2.38	if electID=="ICE_L_20161029"
replace AVG_bfi_agree=	3.00	if electID=="ICE_L_20171028"
replace AVG_bfi_agree=	0.64	if electID=="ICE_P_20160625"
replace AVG_bfi_agree=	1.85	if electID=="IRN_P_20170519"
replace AVG_bfi_agree=	1.68	if electID=="ITA_L_20180304"
replace AVG_bfi_agree=	1.71	if electID=="JAP_L_20160710"
replace AVG_bfi_agree=	1.49	if electID=="JAP_L_20171022"
replace AVG_bfi_agree=	1.50	if electID=="KEN_P_20170808"
replace AVG_bfi_agree=	2.50	if electID=="LTH_L_20161009"
replace AVG_bfi_agree=	1.80	if electID=="MDV_P_20161030"
replace AVG_bfi_agree=	1.65	if electID=="MKD_L_20161211"
replace AVG_bfi_agree=	2.24	if electID=="MLT_L_20170603"
replace AVG_bfi_agree=	1.25	if electID=="MON_L_20160630"
replace AVG_bfi_agree=	2.17	if electID=="MRC_L_20161007"
replace AVG_bfi_agree=	1.47	if electID=="MTN_L_20161016"
replace AVG_bfi_agree=	0.33	if electID=="NIC_P_20161106"
replace AVG_bfi_agree=	1.60	if electID=="NIR_L_20170302"
replace AVG_bfi_agree=	1.56	if electID=="NLD_L_20170315"
replace AVG_bfi_agree=	1.88	if electID=="NOR_L_20170911"
replace AVG_bfi_agree=	2.23	if electID=="NZL_L_20170923"
replace AVG_bfi_agree=	1.25	if electID=="ROU_L_20161211"
replace AVG_bfi_agree=	1.57	if electID=="RUS_L_20160918"
replace AVG_bfi_agree=	1.54	if electID=="RUS_P_20180318"
replace AVG_bfi_agree=	2.75	if electID=="RWA_P_20170804"
replace AVG_bfi_agree=	1.60	if electID=="SRB_P_20170402"
replace AVG_bfi_agree=	1.40	if electID=="TLS_L_20170722"
replace AVG_bfi_agree=	2.50	if electID=="TLS_P_20170320"
replace AVG_bfi_agree=	1.10	if electID=="USA_P_20161108"
replace AVG_bfi_agree=	1.50	if electID=="UZB_P_20161204"
replace AVG_bfi_agree=	1.97	if electID=="XKX_L_20170611"

gen AVG_bfi_consc=.
replace AVG_bfi_consc=	2.25	if electID=="ALB_L_20170625"
replace AVG_bfi_consc=	2.73	if electID=="ARG_L_20171022"
replace AVG_bfi_consc=	3.33	if electID=="ARM_L_20170402"
replace AVG_bfi_consc=	3.17	if electID=="AUS_L_20160702"
replace AVG_bfi_consc=	3.21	if electID=="AUT_L_20171015"
replace AVG_bfi_consc=	3.00	if electID=="AUT_P_20161204"
replace AVG_bfi_consc=	2.10	if electID=="BGR_L_20170326"
replace AVG_bfi_consc=	3.16	if electID=="BGR_P_20161106"
replace AVG_bfi_consc=	2.00	if electID=="BHS_L_20170510"
replace AVG_bfi_consc=	2.64	if electID=="CHL_P_20171119"
replace AVG_bfi_consc=	2.43	if electID=="CRI_P_20180204"
replace AVG_bfi_consc=	2.50	if electID=="CRO_L_20160911"
replace AVG_bfi_consc=	2.62	if electID=="CYP_P_20180128"
replace AVG_bfi_consc=	2.55	if electID=="CZE_L_20171020"
replace AVG_bfi_consc=	2.65	if electID=="CZE_P_20180112"
replace AVG_bfi_consc=	2.94	if electID=="DEU_L_20170924"
replace AVG_bfi_consc=	2.00	if electID=="DZA_L_20170504"
replace AVG_bfi_consc=	2.59	if electID=="ECU_P_20170219"
replace AVG_bfi_consc=	2.38	if electID=="ESP_L_20160626"
replace AVG_bfi_consc=	3.34	if electID=="FIN_P_20180128"
replace AVG_bfi_consc=	3.44	if electID=="FRA_L_20170611"
replace AVG_bfi_consc=	2.67	if electID=="FRA_P_20170423"
replace AVG_bfi_consc=	2.09	if electID=="GBR_L_20170608"
replace AVG_bfi_consc=	2.67	if electID=="GHA_P_20161207"
replace AVG_bfi_consc=	3.50	if electID=="GRG_L_20161008"
replace AVG_bfi_consc=	2.85	if electID=="ICE_L_20161029"
replace AVG_bfi_consc=	3.60	if electID=="ICE_L_20171028"
replace AVG_bfi_consc=	2.64	if electID=="ICE_P_20160625"
replace AVG_bfi_consc=	3.10	if electID=="IRN_P_20170519"
replace AVG_bfi_consc=	2.14	if electID=="ITA_L_20180304"
replace AVG_bfi_consc=	2.53	if electID=="JAP_L_20160710"
replace AVG_bfi_consc=	2.28	if electID=="JAP_L_20171022"
replace AVG_bfi_consc=	2.00	if electID=="KEN_P_20170808"
replace AVG_bfi_consc=	2.68	if electID=="LTH_L_20161009"
replace AVG_bfi_consc=	2.23	if electID=="MDV_P_20161030"
replace AVG_bfi_consc=	2.23	if electID=="MKD_L_20161211"
replace AVG_bfi_consc=	2.90	if electID=="MLT_L_20170603"
replace AVG_bfi_consc=	1.75	if electID=="MON_L_20160630"
replace AVG_bfi_consc=	2.75	if electID=="MRC_L_20161007"
replace AVG_bfi_consc=	3.13	if electID=="MTN_L_20161016"
replace AVG_bfi_consc=	2.17	if electID=="NIC_P_20161106"
replace AVG_bfi_consc=	2.61	if electID=="NIR_L_20170302"
replace AVG_bfi_consc=	2.94	if electID=="NLD_L_20170315"
replace AVG_bfi_consc=	3.19	if electID=="NOR_L_20170911"
replace AVG_bfi_consc=	3.29	if electID=="NZL_L_20170923"
replace AVG_bfi_consc=	2.46	if electID=="ROU_L_20161211"
replace AVG_bfi_consc=	2.07	if electID=="RUS_L_20160918"
replace AVG_bfi_consc=	2.17	if electID=="RUS_P_20180318"
replace AVG_bfi_consc=	3.25	if electID=="RWA_P_20170804"
replace AVG_bfi_consc=	2.80	if electID=="SRB_P_20170402"
replace AVG_bfi_consc=	3.10	if electID=="TLS_L_20170722"
replace AVG_bfi_consc=	2.67	if electID=="TLS_P_20170320"
replace AVG_bfi_consc=	2.08	if electID=="USA_P_20161108"
replace AVG_bfi_consc=	3.35	if electID=="UZB_P_20161204"
replace AVG_bfi_consc=	3.08	if electID=="XKX_L_20170611"

gen AVG_bfi_emot=.
replace AVG_bfi_emot=	1.75	if electID=="ALB_L_20170625"
replace AVG_bfi_emot=	1.50	if electID=="ARG_L_20171022"
replace AVG_bfi_emot=	2.67	if electID=="ARM_L_20170402"
replace AVG_bfi_emot=	2.84	if electID=="AUS_L_20160702"
replace AVG_bfi_emot=	2.57	if electID=="AUT_L_20171015"
replace AVG_bfi_emot=	2.75	if electID=="AUT_P_20161204"
replace AVG_bfi_emot=	1.53	if electID=="BGR_L_20170326"
replace AVG_bfi_emot=	2.57	if electID=="BGR_P_20161106"
replace AVG_bfi_emot=	2.30	if electID=="BHS_L_20170510"
replace AVG_bfi_emot=	2.78	if electID=="CHL_P_20171119"
replace AVG_bfi_emot=	2.08	if electID=="CRI_P_20180204"
replace AVG_bfi_emot=	1.85	if electID=="CRO_L_20160911"
replace AVG_bfi_emot=	2.61	if electID=="CYP_P_20180128"
replace AVG_bfi_emot=	1.46	if electID=="CZE_L_20171020"
replace AVG_bfi_emot=	2.27	if electID=="CZE_P_20180112"
replace AVG_bfi_emot=	2.65	if electID=="DEU_L_20170924"
replace AVG_bfi_emot=	2.08	if electID=="DZA_L_20170504"
replace AVG_bfi_emot=	2.37	if electID=="ECU_P_20170219"
replace AVG_bfi_emot=	2.75	if electID=="ESP_L_20160626"
replace AVG_bfi_emot=	3.46	if electID=="FIN_P_20180128"
replace AVG_bfi_emot=	3.36	if electID=="FRA_L_20170611"
replace AVG_bfi_emot=	2.03	if electID=="FRA_P_20170423"
replace AVG_bfi_emot=	2.06	if electID=="GBR_L_20170608"
replace AVG_bfi_emot=	2.17	if electID=="GHA_P_20161207"
replace AVG_bfi_emot=	3.33	if electID=="GRG_L_20161008"
replace AVG_bfi_emot=	2.71	if electID=="ICE_L_20161029"
replace AVG_bfi_emot=	2.93	if electID=="ICE_L_20171028"
replace AVG_bfi_emot=	1.57	if electID=="ICE_P_20160625"
replace AVG_bfi_emot=	2.67	if electID=="IRN_P_20170519"
replace AVG_bfi_emot=	1.69	if electID=="ITA_L_20180304"
replace AVG_bfi_emot=	2.45	if electID=="JAP_L_20160710"
replace AVG_bfi_emot=	2.14	if electID=="JAP_L_20171022"
replace AVG_bfi_emot=	0.75	if electID=="KEN_P_20170808"
replace AVG_bfi_emot=	2.57	if electID=="LTH_L_20161009"
replace AVG_bfi_emot=	2.26	if electID=="MDV_P_20161030"
replace AVG_bfi_emot=	1.93	if electID=="MKD_L_20161211"
replace AVG_bfi_emot=	2.84	if electID=="MLT_L_20170603"
replace AVG_bfi_emot=	2.25	if electID=="MON_L_20160630"
replace AVG_bfi_emot=	2.25	if electID=="MRC_L_20161007"
replace AVG_bfi_emot=	2.47	if electID=="MTN_L_20161016"
replace AVG_bfi_emot=	0.67	if electID=="NIC_P_20161106"
replace AVG_bfi_emot=	2.41	if electID=="NIR_L_20170302"
replace AVG_bfi_emot=	2.37	if electID=="NLD_L_20170315"
replace AVG_bfi_emot=	2.88	if electID=="NOR_L_20170911"
replace AVG_bfi_emot=	3.33	if electID=="NZL_L_20170923"
replace AVG_bfi_emot=	2.15	if electID=="ROU_L_20161211"
replace AVG_bfi_emot=	1.69	if electID=="RUS_L_20160918"
replace AVG_bfi_emot=	1.73	if electID=="RUS_P_20180318"
replace AVG_bfi_emot=	2.50	if electID=="RWA_P_20170804"
replace AVG_bfi_emot=	2.00	if electID=="SRB_P_20170402"
replace AVG_bfi_emot=	2.90	if electID=="TLS_L_20170722"
replace AVG_bfi_emot=	3.00	if electID=="TLS_P_20170320"
replace AVG_bfi_emot=	1.77	if electID=="USA_P_20161108"
replace AVG_bfi_emot=	2.05	if electID=="UZB_P_20161204"
replace AVG_bfi_emot=	2.54	if electID=="XKX_L_20170611"

gen AVG_bfi_open=.
replace AVG_bfi_open=	2.42	if electID=="ALB_L_20170625"
replace AVG_bfi_open=	2.22	if electID=="ARG_L_20171022"
replace AVG_bfi_open=	1.77	if electID=="ARM_L_20170402"
replace AVG_bfi_open=	2.33	if electID=="AUS_L_20160702"
replace AVG_bfi_open=	1.85	if electID=="AUT_L_20171015"
replace AVG_bfi_open=	1.89	if electID=="AUT_P_20161204"
replace AVG_bfi_open=	2.11	if electID=="BGR_L_20170326"
replace AVG_bfi_open=	1.52	if electID=="BGR_P_20161106"
replace AVG_bfi_open=	1.75	if electID=="BHS_L_20170510"
replace AVG_bfi_open=	1.69	if electID=="CHL_P_20171119"
replace AVG_bfi_open=	1.23	if electID=="CRI_P_20180204"
replace AVG_bfi_open=	2.33	if electID=="CRO_L_20160911"
replace AVG_bfi_open=	2.06	if electID=="CYP_P_20180128"
replace AVG_bfi_open=	1.84	if electID=="CZE_L_20171020"
replace AVG_bfi_open=	1.90	if electID=="CZE_P_20180112"
replace AVG_bfi_open=	1.73	if electID=="DEU_L_20170924"
replace AVG_bfi_open=	1.63	if electID=="DZA_L_20170504"
replace AVG_bfi_open=	1.33	if electID=="ECU_P_20170219"
replace AVG_bfi_open=	0.13	if electID=="ESP_L_20160626"
replace AVG_bfi_open=	2.04	if electID=="FIN_P_20180128"
replace AVG_bfi_open=	2.08	if electID=="FRA_L_20170611"
replace AVG_bfi_open=	2.44	if electID=="FRA_P_20170423"
replace AVG_bfi_open=	1.62	if electID=="GBR_L_20170608"
replace AVG_bfi_open=	2.46	if electID=="GHA_P_20161207"
replace AVG_bfi_open=	2.17	if electID=="GRG_L_20161008"
replace AVG_bfi_open=	2.92	if electID=="ICE_L_20161029"
replace AVG_bfi_open=	2.20	if electID=="ICE_L_20171028"
replace AVG_bfi_open=	1.64	if electID=="ICE_P_20160625"
replace AVG_bfi_open=	1.35	if electID=="IRN_P_20170519"
replace AVG_bfi_open=	2.12	if electID=="ITA_L_20180304"
replace AVG_bfi_open=	1.99	if electID=="JAP_L_20160710"
replace AVG_bfi_open=	1.88	if electID=="JAP_L_20171022"
replace AVG_bfi_open=	2.75	if electID=="KEN_P_20170808"
replace AVG_bfi_open=	2.26	if electID=="LTH_L_20161009"
replace AVG_bfi_open=	2.62	if electID=="MDV_P_20161030"
replace AVG_bfi_open=	1.92	if electID=="MKD_L_20161211"
replace AVG_bfi_open=	2.48	if electID=="MLT_L_20170603"
replace AVG_bfi_open=	2.25	if electID=="MON_L_20160630"
replace AVG_bfi_open=	2.42	if electID=="MRC_L_20161007"
replace AVG_bfi_open=	1.50	if electID=="MTN_L_20161016"
replace AVG_bfi_open=	0.67	if electID=="NIC_P_20161106"
replace AVG_bfi_open=	1.73	if electID=="NIR_L_20170302"
replace AVG_bfi_open=	1.66	if electID=="NLD_L_20170315"
replace AVG_bfi_open=	1.86	if electID=="NOR_L_20170911"
replace AVG_bfi_open=	2.14	if electID=="NZL_L_20170923"
replace AVG_bfi_open=	1.59	if electID=="ROU_L_20161211"
replace AVG_bfi_open=	1.50	if electID=="RUS_L_20160918"
replace AVG_bfi_open=	2.02	if electID=="RUS_P_20180318"
replace AVG_bfi_open=	2.50	if electID=="RWA_P_20170804"
replace AVG_bfi_open=	2.15	if electID=="SRB_P_20170402"
replace AVG_bfi_open=	1.90	if electID=="TLS_L_20170722"
replace AVG_bfi_open=	2.33	if electID=="TLS_P_20170320"
replace AVG_bfi_open=	2.04	if electID=="USA_P_20161108"
replace AVG_bfi_open=	2.33	if electID=="UZB_P_20161204"
replace AVG_bfi_open=	2.20	if electID=="XKX_L_20170611"

gen AVG_triad_narciss=.
replace AVG_triad_narciss=	3.13	if electID=="ALB_L_20170625"
replace AVG_triad_narciss=	2.63	if electID=="ARG_L_20171022"
replace AVG_triad_narciss=	2.25	if electID=="ARM_L_20170402"
replace AVG_triad_narciss=	2.82	if electID=="AUS_L_20160702"
replace AVG_triad_narciss=	3.14	if electID=="AUT_L_20171015"
replace AVG_triad_narciss=	2.38	if electID=="AUT_P_20161204"
replace AVG_triad_narciss=	2.81	if electID=="BGR_L_20170326"
replace AVG_triad_narciss=	2.12	if electID=="BGR_P_20161106"
replace AVG_triad_narciss=	3.00	if electID=="BHS_L_20170510"
replace AVG_triad_narciss=	2.39	if electID=="CHL_P_20171119"
replace AVG_triad_narciss=	3.48	if electID=="CRI_P_20180204"
replace AVG_triad_narciss=	2.86	if electID=="CRO_L_20160911"
replace AVG_triad_narciss=	2.46	if electID=="CYP_P_20180128"
replace AVG_triad_narciss=	2.93	if electID=="CZE_L_20171020"
replace AVG_triad_narciss=	2.89	if electID=="CZE_P_20180112"
replace AVG_triad_narciss=	2.40	if electID=="DEU_L_20170924"
replace AVG_triad_narciss=	2.33	if electID=="DZA_L_20170504"
replace AVG_triad_narciss=	2.69	if electID=="ECU_P_20170219"
replace AVG_triad_narciss=	0.63	if electID=="ESP_L_20160626"
replace AVG_triad_narciss=	2.33	if electID=="FIN_P_20180128"
replace AVG_triad_narciss=	2.83	if electID=="FRA_L_20170611"
replace AVG_triad_narciss=	3.07	if electID=="FRA_P_20170423"
replace AVG_triad_narciss=	2.67	if electID=="GBR_L_20170608"
replace AVG_triad_narciss=	2.97	if electID=="GHA_P_20161207"
replace AVG_triad_narciss=	0.86	if electID=="GRG_L_20161008"
replace AVG_triad_narciss=	1.97	if electID=="ICE_L_20161029"
replace AVG_triad_narciss=	1.96	if electID=="ICE_L_20171028"
replace AVG_triad_narciss=	3.67	if electID=="ICE_P_20160625"
replace AVG_triad_narciss=	1.92	if electID=="IRN_P_20170519"
replace AVG_triad_narciss=	3.16	if electID=="ITA_L_20180304"
replace AVG_triad_narciss=	2.43	if electID=="JAP_L_20160710"
replace AVG_triad_narciss=	2.80	if electID=="JAP_L_20171022"
replace AVG_triad_narciss=	2.25	if electID=="KEN_P_20170808"
replace AVG_triad_narciss=	2.98	if electID=="LTH_L_20161009"
replace AVG_triad_narciss=	2.92	if electID=="MDV_P_20161030"
replace AVG_triad_narciss=	3.17	if electID=="MKD_L_20161211"
replace AVG_triad_narciss=	2.13	if electID=="MLT_L_20170603"
replace AVG_triad_narciss=	2.83	if electID=="MON_L_20160630"
replace AVG_triad_narciss=	3.33	if electID=="MRC_L_20161007"
replace AVG_triad_narciss=	2.98	if electID=="MTN_L_20161016"
replace AVG_triad_narciss=	3.33	if electID=="NIC_P_20161106"
replace AVG_triad_narciss=	2.57	if electID=="NIR_L_20170302"
replace AVG_triad_narciss=	2.59	if electID=="NLD_L_20170315"
replace AVG_triad_narciss=	2.06	if electID=="NOR_L_20170911"
replace AVG_triad_narciss=	2.35	if electID=="NZL_L_20170923"
replace AVG_triad_narciss=	3.14	if electID=="ROU_L_20161211"
replace AVG_triad_narciss=	2.76	if electID=="RUS_L_20160918"
replace AVG_triad_narciss=	3.38	if electID=="RUS_P_20180318"
replace AVG_triad_narciss=	2.83	if electID=="RWA_P_20170804"
replace AVG_triad_narciss=	2.90	if electID=="SRB_P_20170402"
replace AVG_triad_narciss=	2.50	if electID=="TLS_L_20170722"
replace AVG_triad_narciss=	1.50	if electID=="TLS_P_20170320"
replace AVG_triad_narciss=	3.39	if electID=="USA_P_20161108"
replace AVG_triad_narciss=	2.67	if electID=="UZB_P_20161204"
replace AVG_triad_narciss=	3.21	if electID=="XKX_L_20170611"

gen AVG_triad_psycho=.
replace AVG_triad_psycho=	2.31	if electID=="ALB_L_20170625"
replace AVG_triad_psycho=	1.68	if electID=="ARG_L_20171022"
replace AVG_triad_psycho=	2.20	if electID=="ARM_L_20170402"
replace AVG_triad_psycho=	2.10	if electID=="AUS_L_20160702"
replace AVG_triad_psycho=	1.79	if electID=="AUT_L_20171015"
replace AVG_triad_psycho=	1.94	if electID=="AUT_P_20161204"
replace AVG_triad_psycho=	2.22	if electID=="BGR_L_20170326"
replace AVG_triad_psycho=	1.97	if electID=="BGR_P_20161106"
replace AVG_triad_psycho=	2.02	if electID=="BHS_L_20170510"
replace AVG_triad_psycho=	1.96	if electID=="CHL_P_20171119"
replace AVG_triad_psycho=	2.41	if electID=="CRI_P_20180204"
replace AVG_triad_psycho=	2.14	if electID=="CRO_L_20160911"
replace AVG_triad_psycho=	1.08	if electID=="CYP_P_20180128"
replace AVG_triad_psycho=	2.54	if electID=="CZE_L_20171020"
replace AVG_triad_psycho=	2.19	if electID=="CZE_P_20180112"
replace AVG_triad_psycho=	2.37	if electID=="DEU_L_20170924"
replace AVG_triad_psycho=	2.42	if electID=="DZA_L_20170504"
replace AVG_triad_psycho=	2.12	if electID=="ECU_P_20170219"
replace AVG_triad_psycho=	3.03	if electID=="ESP_L_20160626"
replace AVG_triad_psycho=	1.16	if electID=="FIN_P_20180128"
replace AVG_triad_psycho=	1.61	if electID=="FRA_L_20170611"
replace AVG_triad_psycho=	2.55	if electID=="FRA_P_20170423"
replace AVG_triad_psycho=	2.52	if electID=="GBR_L_20170608"
replace AVG_triad_psycho=	1.42	if electID=="GHA_P_20161207"
replace AVG_triad_psycho=	1.50	if electID=="GRG_L_20161008"
replace AVG_triad_psycho=	1.94	if electID=="ICE_L_20161029"
replace AVG_triad_psycho=	1.21	if electID=="ICE_L_20171028"
replace AVG_triad_psycho=	3.83	if electID=="ICE_P_20160625"
replace AVG_triad_psycho=	2.42	if electID=="IRN_P_20170519"
replace AVG_triad_psycho=	2.50	if electID=="ITA_L_20180304"
replace AVG_triad_psycho=	1.82	if electID=="JAP_L_20160710"
replace AVG_triad_psycho=	2.00	if electID=="JAP_L_20171022"
replace AVG_triad_psycho=	1.25	if electID=="KEN_P_20170808"
replace AVG_triad_psycho=	1.68	if electID=="LTH_L_20161009"
replace AVG_triad_psycho=	2.25	if electID=="MDV_P_20161030"
replace AVG_triad_psycho=	2.67	if electID=="MKD_L_20161211"
replace AVG_triad_psycho=	1.32	if electID=="MLT_L_20170603"
replace AVG_triad_psycho=	2.92	if electID=="MON_L_20160630"
replace AVG_triad_psycho=	2.67	if electID=="MRC_L_20161007"
replace AVG_triad_psycho=	1.87	if electID=="MTN_L_20161016"
replace AVG_triad_psycho=	3.50	if electID=="NIC_P_20161106"
replace AVG_triad_psycho=	2.79	if electID=="NIR_L_20170302"
replace AVG_triad_psycho=	2.44	if electID=="NLD_L_20170315"
replace AVG_triad_psycho=	1.84	if electID=="NOR_L_20170911"
replace AVG_triad_psycho=	1.33	if electID=="NZL_L_20170923"
replace AVG_triad_psycho=	2.91	if electID=="ROU_L_20161211"
replace AVG_triad_psycho=	2.72	if electID=="RUS_L_20160918"
replace AVG_triad_psycho=	2.46	if electID=="RUS_P_20180318"
replace AVG_triad_psycho=	0.83	if electID=="RWA_P_20170804"
replace AVG_triad_psycho=	1.76	if electID=="SRB_P_20170402"
replace AVG_triad_psycho=	2.10	if electID=="TLS_L_20170722"
replace AVG_triad_psycho=	1.00	if electID=="TLS_P_20170320"
replace AVG_triad_psycho=	2.68	if electID=="USA_P_20161108"
replace AVG_triad_psycho=	2.33	if electID=="UZB_P_20161204"
replace AVG_triad_psycho=	1.91	if electID=="XKX_L_20170611"

gen AVG_triad_machiav=.
replace AVG_triad_machiav=	2.38	if electID=="ALB_L_20170625"
replace AVG_triad_machiav=	1.98	if electID=="ARG_L_20171022"
replace AVG_triad_machiav=	1.90	if electID=="ARM_L_20170402"
replace AVG_triad_machiav=	2.48	if electID=="AUS_L_20160702"
replace AVG_triad_machiav=	2.15	if electID=="AUT_L_20171015"
replace AVG_triad_machiav=	2.17	if electID=="AUT_P_20161204"
replace AVG_triad_machiav=	2.50	if electID=="BGR_L_20170326"
replace AVG_triad_machiav=	2.00	if electID=="BGR_P_20161106"
replace AVG_triad_machiav=	2.43	if electID=="BHS_L_20170510"
replace AVG_triad_machiav=	2.02	if electID=="CHL_P_20171119"
replace AVG_triad_machiav=	2.92	if electID=="CRI_P_20180204"
replace AVG_triad_machiav=	2.10	if electID=="CRO_L_20160911"
replace AVG_triad_machiav=	0.98	if electID=="CYP_P_20180128"
replace AVG_triad_machiav=	2.30	if electID=="CZE_L_20171020"
replace AVG_triad_machiav=	2.21	if electID=="CZE_P_20180112"
replace AVG_triad_machiav=	1.86	if electID=="DEU_L_20170924"
replace AVG_triad_machiav=	2.50	if electID=="DZA_L_20170504"
replace AVG_triad_machiav=	2.64	if electID=="ECU_P_20170219"
replace AVG_triad_machiav=	1.50	if electID=="ESP_L_20160626"
replace AVG_triad_machiav=	1.32	if electID=="FIN_P_20180128"
replace AVG_triad_machiav=	1.85	if electID=="FRA_L_20170611"
replace AVG_triad_machiav=	2.59	if electID=="FRA_P_20170423"
replace AVG_triad_machiav=	1.80	if electID=="GBR_L_20170608"
replace AVG_triad_machiav=	1.98	if electID=="GHA_P_20161207"
replace AVG_triad_machiav=	1.29	if electID=="GRG_L_20161008"
replace AVG_triad_machiav=	1.74	if electID=="ICE_L_20161029"
replace AVG_triad_machiav=	1.71	if electID=="ICE_L_20171028"
replace AVG_triad_machiav=	3.50	if electID=="ICE_P_20160625"
replace AVG_triad_machiav=	1.63	if electID=="IRN_P_20170519"
replace AVG_triad_machiav=	2.62	if electID=="ITA_L_20180304"
replace AVG_triad_machiav=	1.28	if electID=="JAP_L_20160710"
replace AVG_triad_machiav=	2.13	if electID=="JAP_L_20171022"
replace AVG_triad_machiav=	1.25	if electID=="KEN_P_20170808"
replace AVG_triad_machiav=	2.49	if electID=="LTH_L_20161009"
replace AVG_triad_machiav=	2.46	if electID=="MDV_P_20161030"
replace AVG_triad_machiav=	2.53	if electID=="MKD_L_20161211"
replace AVG_triad_machiav=	1.90	if electID=="MLT_L_20170603"
replace AVG_triad_machiav=	2.50	if electID=="MON_L_20160630"
replace AVG_triad_machiav=	3.00	if electID=="MRC_L_20161007"
replace AVG_triad_machiav=	1.96	if electID=="MTN_L_20161016"
replace AVG_triad_machiav=	2.50	if electID=="NIC_P_20161106"
replace AVG_triad_machiav=	2.42	if electID=="NIR_L_20170302"
replace AVG_triad_machiav=	2.06	if electID=="NLD_L_20170315"
replace AVG_triad_machiav=	1.51	if electID=="NOR_L_20170911"
replace AVG_triad_machiav=	1.30	if electID=="NZL_L_20170923"
replace AVG_triad_machiav=	2.82	if electID=="ROU_L_20161211"
replace AVG_triad_machiav=	2.61	if electID=="RUS_L_20160918"
replace AVG_triad_machiav=	2.69	if electID=="RUS_P_20180318"
replace AVG_triad_machiav=	0.67	if electID=="RWA_P_20170804"
replace AVG_triad_machiav=	1.96	if electID=="SRB_P_20170402"
replace AVG_triad_machiav=	2.03	if electID=="TLS_L_20170722"
replace AVG_triad_machiav=	1.00	if electID=="TLS_P_20170320"
replace AVG_triad_machiav=	2.83	if electID=="USA_P_20161108"
replace AVG_triad_machiav=	2.40	if electID=="UZB_P_20161204"
replace AVG_triad_machiav=	2.19	if electID=="XKX_L_20170611"




** standardized variables

egen std_bfi_extrav = std(bfi_extrav)
egen std_bfi_agree = std(bfi_agree)
egen std_bfi_consc = std(bfi_consc)
egen std_bfi_emot = std(bfi_emot)
egen std_bfi_open = std(bfi_open)
egen std_triad_narciss = std(triad_narciss)
egen std_triad_psycho = std(triad_psycho)
egen std_triad_machiav = std(triad_machiav)

egen std_c_independent = std(c_independent)
egen std_c_incumbent = std(c_incumbent)
egen std_c_positionr = std(c_positionr)
egen std_c_female = std(c_female)
egen std_c_yearborn = std(c_yearborn)
egen std_tone_CP = std(tone_CP)
egen std_feelgood = std(feelgood)
egen std_fear = std(fear)
egen std_cntry_elsys_pr = std(cntry_elsys_pr)
egen std_e_ENPvotes = std(e_ENPvotes)
egen std_compet = std(compet)
egen std_election_type = std(election_type)
egen std_oecd = std(oecd)


label variable std_bfi_extrav "Extraversion"
label variable std_bfi_agree "Agreeableness"
label variable std_bfi_consc "Conscientiousness"
label variable std_bfi_emot "Emotional stability"
label variable std_bfi_open "Openness"
label variable std_triad_narciss "Narcissism"
label variable std_triad_psycho "Psychopathy"
label variable std_triad_machiav "Machiavellianism"

label variable std_c_independent "Independent"
label variable std_c_incumbent "Incumbent"
label variable std_c_positionr "Left-right"
label variable std_c_female "Female"
label variable std_c_yearborn "Year born"
label variable std_tone_CP "Negative tone"
label variable std_feelgood "Ethusiasm appeals"
label variable std_fear "Fear appeals"
label variable std_cntry_elsys_pr "PR"
label variable std_e_ENPvotes "EN candidates"
label variable std_compet "Competitiveness"
label variable std_election_type "Presidential election"
label variable std_oecd "OECD"






** candcheck (minimum two experts per candidate)

generate candcheck=0
replace candcheck=1 if (numrespt_bfi>=2 & numrespt_triad>=2 & SUCCESS_abs!=. & bfi_extrav!=. & bfi_agree!=. & bfi_consc!=. & bfi_emot!=. & bfi_open!=. & triad_narciss!=. & triad_psycho!=. & triad_machiav!=. & c_independent!=. & c_incumbent!=. & c_positionr!=. & c_female!=. & c_yearborn!=. & cntry_elsys_pr!=. & e_ENPvotes!=. & compet!=. & election_type!=. & oecd!=. & tone_CP!=. & ft!=. & feelgood!=. & fear!=.) 
tab candcheck 



** second-order factors of personality

pca bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1
loadingplot
predict comp1 comp2

gen perspca_factor1 = comp1
gen perspca_factor2 = comp2

gen perspca_factor1r = perspca_factor1 * -1

drop comp1 comp2


gen perspca_factor1r_2 = perspca_factor1r^2
gen perspca_factor2_2 = perspca_factor2^2







***** B. MAIN ANALYSES
****************************************


** Table 2. Correlations

pwcorr bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, sig obs



** Table 4. Personality and electoral success

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, fe

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1


			
** Table 5. Profile effects

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			c.c_incumbent#c.bfi_extrav c.c_incumbent#c.bfi_agree c.c_incumbent#c.bfi_consc c.c_incumbent#c.bfi_emot c.c_incumbent#c.bfi_open c.c_incumbent#c.triad_narciss c.c_incumbent#c.triad_psycho c.c_incumbent#c.triad_machiav if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			c.c_positionr#c.bfi_extrav c.c_positionr#c.bfi_agree c.c_positionr#c.bfi_consc c.c_positionr#c.bfi_emot c.c_positionr#c.bfi_open c.c_positionr#c.triad_narciss c.c_positionr#c.triad_psycho c.c_positionr#c.triad_machiav if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			c.c_female#c.bfi_extrav c.c_female#c.bfi_agree c.c_female#c.bfi_consc c.c_female#c.bfi_emot c.c_female#c.bfi_open c.c_female#c.triad_narciss c.c_female#c.triad_psycho c.c_female#c.triad_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			c.c_yearborn#c.bfi_extrav c.c_yearborn#c.bfi_agree c.c_yearborn#c.bfi_consc c.c_yearborn#c.bfi_emot c.c_yearborn#c.bfi_open c.c_yearborn#c.triad_narciss c.c_yearborn#c.triad_psycho c.c_yearborn#c.triad_machiav if candcheck==1



**** FIGURES


** Figure 1. Second-order factors (PCA)

gen EXTRA = bfi_extrav 
gen AGREE = bfi_agree 
gen CONSC = bfi_consc 
gen EMOSTAB = bfi_emot 
gen OPEN = bfi_open 
gen NARCISS = triad_narciss 
gen PSYCHO = triad_psycho 
gen MACHIAV = triad_machiav

pca EXTRA AGREE CONSC EMOSTAB OPEN NARCISS PSYCHO MACHIAV if candcheck==1

loadingplot, ///
xscale(range(-0.8 0.8)) xlabel(-0.8(0.2)0.8) ///
yscale(range(-0.8 0.8)) ylabel(-0.8(0.2)0.8)  ///
xline(0, lwidth(0.3) lpattern(dot)) yline(0, lwidth(0.3) lpattern(dot)) ///
xtitle(Factor 1, size(vsmall)) ytitle(Factor 2, size(vsmall)) ///
xlabel(, labsize(vsmall)) ylabel(, labsize(vsmall)) ///
mfcolor(black) mlcolor(g10) mlwidth(vthin) msize(small) ///
title ("", size(small)) subtitle ("", size(small)) ///
scheme(lean2) xsize(6) ysize(6) name(a, replace)

drop EXTRA AGREE CONSC EMOSTAB OPEN NARCISS PSYCHO MACHIAV



** Figure 2. Coefficient plot

quietly xtreg SUCCESS_abs ///
std_bfi_extrav std_bfi_agree std_bfi_consc std_bfi_emot std_bfi_open std_triad_narciss std_triad_psycho std_triad_machiav ///
std_c_independent std_c_incumbent std_c_positionr std_c_female std_c_yearborn ///
std_tone_CP std_feelgood std_fear ///
std_cntry_elsys_pr std_e_ENPvotes std_compet std_election_type std_oecd if candcheck==1
estimates store ABS

coefplot ///
(ABS, label(Absolute success) msymbol(D) mfcolor(black) mlcolor(g10) mlwidth(vthin) msize(small)), ///
drop(_cons) xline(0, lwidth(0.3) lpattern(dot)) xtitle(Coefficient, size(vsmall)) name(c, replace) ///
xscale(range(-15 15)) xlabel(-15(5)15) ytitle (, size(vsmall)) xlabel(, labsize(vsmall)) ylabel(, labsize(vsmall)) ///
subtitle ("", size(small)) ///
levels(95 90) ciopts(lwidth(0.1 0.1 .) lcolor(*1 *1) recast(rcap rbar) barwidth(. 0.5) lwidth(. vvthin)) msize(small) ///
headings(std_triad_narciss = "{bf:}" std_c_independent = "{bf:}", labsize(vsmall)) ///
xsize(6) ysize(8) legend(off) scheme(lean2) 



** Figure 3. Electoral success by incumbency status * Extraversion; marginal effects.

xtset election_count

xtreg SUCCESS_abs ///
c_independent c_incumbent c_positionr c_female c_yearborn ///
tone_CP feelgood fear ///
cntry_elsys_pr e_ENPvotes compet election_type oecd ///
bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
c.c_incumbent#c.bfi_extrav c.c_incumbent#c.bfi_agree c.c_incumbent#c.bfi_consc c.c_incumbent#c.bfi_emot c.c_incumbent#c.bfi_open c.c_incumbent#c.triad_narciss c.c_incumbent#c.triad_psycho c.c_incumbent#c.triad_machiav if candcheck==1

margins, at (bfi_extrav=(0(0.5)4) c_incumbent=(0(1)1) c_independent=0.07 c_positionr=4.25 c_female=0.16 c_yearborn=1961.22 tone_CP=4.02 feelgood=5.35 fear=4.93 cntry_elsys_pr=0.65 e_ENPvotes=3.96 compet=2.11 election_type=1.38 oecd=0.4 bfi_agree=1.82 bfi_consc=2.68 bfi_emot=2.31 bfi_open=1.97 triad_narciss=2.7 triad_psycho=2.12 triad_machiav=2.13) level(95)
marginsplot, ///
title ("", size(medsmall) span) ///
subtitle ("", size(vsmall) span) ///
xtitle(Extraversion, size(small)) xlabel(, labsize(small)) xscale(range(0 4)) xlabel(0(0.5)4) ///
ytitle(Electoral success, size(small)) ylabel(, labsize(small)) yscale(range(0 100)) ylabel(0(20)100, nogrid) ///
ciopts(recast(rcap) lpattern(solid) lwidth(thin)) ///
plot1opts(msize(small) msymbol(diamond) mfcolor(black) lwidth(vthin) lpattern(dot)) ///
plot2opts(msize(small) msymbol(circle) mfcolor(black) lwidth(vthin) lpattern(dash)) ///
scheme(lean2) legend(pos(3) size(vsmall) rows(2)) name(a, replace) 



* Figure 4. Electoral success by left-right * Conscientiousness; marginal effects
*c_positionr= M=4.10, SD=1.55 -> left (M-SD)=4.10-1.55=2.55, right (M+SD)=5.65

xtreg SUCCESS_abs ///
c_independent c_incumbent c_positionr c_female c_yearborn ///
tone_CP feelgood fear ///
cntry_elsys_pr e_ENPvotes compet election_type oecd ///
bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
c.c_positionr#c.bfi_extrav c.c_positionr#c.bfi_agree c.c_positionr#c.bfi_consc c.c_positionr#c.bfi_emot c.c_positionr#c.bfi_open c.c_positionr#c.triad_narciss c.c_positionr#c.triad_psycho c.c_positionr#c.triad_machiav if candcheck==1

margins, at (bfi_consc=(0(0.5)4) c_positionr=(2.55(1.55)6) c_incumbent=0.34 c_independent=0.07 c_female=0.16 c_yearborn=1961.22 tone_CP=4.02 feelgood=5.35 fear=4.93 cntry_elsys_pr=0.65 e_ENPvotes=3.96 compet=2.11 election_type=1.38 oecd=0.4 bfi_agree=1.82 bfi_extrav=2.27 bfi_emot=2.31 bfi_open=1.97 triad_narciss=2.7 triad_psycho=2.12 triad_machiav=2.13) level(95)
marginsplot, ///
title ("", size(medsmall) span) ///
subtitle ("", size(vsmall) span) ///
xtitle(Conscientiousness, size(small)) xlabel(, labsize(small)) xscale(range(0 4)) xlabel(0(0.5)4) ///
ytitle(Electoral success, size(small)) ylabel(, labsize(small)) yscale(range(0 100)) ylabel(0(20)100, nogrid) ///
ciopts(recast(rcap) lpattern(solid) lwidth(thin)) ///
plot1opts(msize(small) msymbol(diamond) mfcolor(black) lwidth(vthin) lpattern(dot)) ///
plot2opts(msize(small) msymbol(circle) mfcolor(black) lwidth(vthin) lpattern(dash)) ///
plot3opts(msize(small) msymbol(square) mfcolor(black) lwidth(vthin) lpattern(solid)) ///
scheme(lean2) legend(pos(3) size(vsmall) rows(3)) name(a, replace) 



* Figure 5. Electoral success by left-right * Narcissism; marginal effects
*c_positionr= M=4.10, SD=1.55 -> left (M-SD)=4.10-1.55=2.55, right (M+SD)=5.65

xtreg SUCCESS_abs ///
c_independent c_incumbent c_positionr c_female c_yearborn ///
tone_CP feelgood fear ///
cntry_elsys_pr e_ENPvotes compet election_type oecd ///
bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
c.c_positionr#c.bfi_extrav c.c_positionr#c.bfi_agree c.c_positionr#c.bfi_consc c.c_positionr#c.bfi_emot c.c_positionr#c.bfi_open c.c_positionr#c.triad_narciss c.c_positionr#c.triad_psycho c.c_positionr#c.triad_machiav if candcheck==1

margins, at (triad_narciss=(0(0.5)4) c_positionr=(2.55(1.55)6) c_incumbent=0.34 c_independent=0.07 c_female=0.16 c_yearborn=1961.22 tone_CP=4.02 feelgood=5.35 fear=4.93 cntry_elsys_pr=0.65 e_ENPvotes=3.96 compet=2.11 election_type=1.38 oecd=0.4 bfi_agree=1.82 bfi_extrav=2.27 bfi_consc=2.68 bfi_emot=2.31 bfi_open=1.97 triad_psycho=2.12 triad_machiav=2.13) level(95)
marginsplot, ///
title ("", size(medsmall) span) ///
subtitle ("", size(vsmall) span) ///
xtitle(Narcissism, size(small)) xlabel(, labsize(small)) xscale(range(0 4)) xlabel(0(0.5)4) ///
ytitle(Electoral success, size(small)) ylabel(, labsize(small)) yscale(range(0 100)) ylabel(0(20)100, nogrid) ///
ciopts(recast(rcap) lpattern(solid) lwidth(thin)) ///
plot1opts(msize(small) msymbol(diamond) mfcolor(black) lwidth(vthin) lpattern(dot)) ///
plot2opts(msize(small) msymbol(circle) mfcolor(black) lwidth(vthin) lpattern(dash)) ///
plot3opts(msize(small) msymbol(square) mfcolor(black) lwidth(vthin) lpattern(solid)) ///
scheme(lean2) legend(pos(3) size(vsmall) rows(3)) name(a, replace) 



* Figure 6. Electoral success by gender * Openness; marginal effects

xtreg SUCCESS_abs ///
c_independent c_incumbent c_positionr c_female c_yearborn ///
tone_CP feelgood fear ///
cntry_elsys_pr e_ENPvotes compet election_type oecd ///
bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
c.c_female#c.bfi_extrav c.c_female#c.bfi_agree c.c_female#c.bfi_consc c.c_female#c.bfi_emot c.c_female#c.bfi_open c.c_female#c.triad_narciss c.c_female#c.triad_psycho c.c_female#c.triad_machiav if candcheck==1

margins, at (bfi_open=(0(0.5)4) c_female=(0(1)1) c_incumbent=0.34 c_independent=0.07 c_positionr=4.25 c_yearborn=1961.22 tone_CP=4.02 feelgood=5.35 fear=4.93 cntry_elsys_pr=0.65 e_ENPvotes=3.96 compet=2.11 election_type=1.38 oecd=0.4 bfi_agree=1.82 bfi_extrav=2.27 bfi_consc=2.68 bfi_emot=2.31 triad_narciss=2.7 triad_psycho=2.12 triad_machiav=2.13) level(95)
marginsplot, ///
title ("", size(medsmall) span) ///
subtitle ("", size(vsmall) span) ///
xtitle(Openness, size(small)) xlabel(, labsize(small)) xscale(range(0 4)) xlabel(0(0.5)4) ///
ytitle(Electoral success, size(small)) ylabel(, labsize(small)) yscale(range(0 100)) ylabel(0(20)100, nogrid) ///
ciopts(recast(rcap) lpattern(solid) lwidth(thin)) ///
plot1opts(msize(small) msymbol(diamond) mfcolor(black) lwidth(vthin) lpattern(dot)) ///
plot2opts(msize(small) msymbol(circle) mfcolor(black) lwidth(vthin) lpattern(dash)) ///
scheme(lean2) legend(pos(3) size(vsmall) rows(2)) name(a, replace) 








***** C. ROBUSTNESS CHECKS
****************************************


** Table B1. Personality and electoral success (second-order factors)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			perspca_factor1r perspca_factor2 if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			perspca_factor1r perspca_factor2 ///
			perspca_factor1r_2 perspca_factor2_2 if candcheck==1



** Table B2. Personality and electoral success (consistency of perceived profile)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			sd_extrav sd_agree sd_consc sd_emot sd_open sd_narciss sd_psycho sd_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			sd_alltraits if candcheck==1


			
** Table B3. Personality and electoral success (trait components)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_c1 bfi_c2 bfi_c3 bfi_c4 bfi_c5 bfi_c6 bfi_c7 bfi_c8 bfi_c9 bfi_c10 triad_c1 triad_c2 triad_c3 triad_c4 triad_c5 triad_c6 if candcheck==1


			
** Table B4. Personality and electoral success (alternatives measures of electoral success)

xtset election_count

/* M1 */	xtreg SUCCESS_relENP ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M2 */	xtreg SUCCESS_relENP ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1

/* M3 */	xtreg SUCCESS_devENP ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_devENP ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1



** Table B5. Personality and electoral success (fractional logit models)

/* M1 */	fracreg logit SUCCESS_abs01 ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	fracreg logit SUCCESS_abs01 ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd if candcheck==1

/* M3 */	fracreg logit SUCCESS_abs01 ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M4 */	fracreg logit SUCCESS_abs01 ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1


			
** Table B6. Personality and electoral success (additional controls at the country level)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd EcoFit b8.country_region3 if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd EcoFit b8.country_region3 ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd EcoFit b8.country_region3 ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1



** Table B7. Personality and electoral success (interactions with winning/losing)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			c.SUCCESS_win##c.bfi_extrav c.SUCCESS_win##c.bfi_agree c.SUCCESS_win##c.bfi_consc c.SUCCESS_win##c.bfi_emot c.SUCCESS_win##c.bfi_open c.SUCCESS_win##c.triad_narciss c.SUCCESS_win##c.triad_psycho c.SUCCESS_win##c.triad_machiav if candcheck==1



** Table B8. Personality and electoral success (interactions with type of election)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			c.election_type#c.bfi_extrav c.election_type#c.bfi_agree c.election_type#c.bfi_consc c.election_type#c.bfi_emot c.election_type#c.bfi_open c.election_type#c.triad_narciss c.election_type#c.triad_psycho c.election_type#c.triad_machiav if candcheck==1



** Table B9. Personality and electoral success (Corrected measurement errors, Big Five)

/* M1 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(bfi_extrav .74)

/* M2 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(bfi_consc .78)

/* M3 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(bfi_emot .84)

*eivreg SUCCESS_abs ///
*c_independent c_incumbent c_positionr c_female c_yearborn ///
*tone_CP feelgood fear ///
*cntry_elsys_pr e_ENPvotes compet election_type oecd ///
*bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
*r(bfi_agree .66)

*eivreg SUCCESS_abs /// ***
*c_independent c_incumbent c_positionr c_female c_yearborn ///
*tone_CP feelgood fear ///
*cntry_elsys_pr e_ENPvotes compet election_type oecd ///
*bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
*r(bfi_open .63)



** Table B10. Personality and electoral success (Corrected measurement errors, Dark Triad)

/* M1 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(triad_narciss .86)

/* M2 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(triad_psycho .89)

/* M3 */	eivreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1, ///
			r(triad_machiav .78)



** Table B11. Personality and electoral success (controlling for the experts’ profile)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			familiar easy domestic lrscale gender if candcheck==1

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 ///
			familiar easy domestic lrscale gender if candcheck==1



** Table B12. Personality and electoral success (controlling for average personality traits per election) (Mundlak procedure)

xtset election_count

/* M1 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear if candcheck==1

/* M2 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd AVG_bfi_extrav AVG_bfi_agree AVG_bfi_consc AVG_bfi_emot AVG_bfi_open AVG_triad_narciss AVG_triad_psycho AVG_triad_machiav if candcheck==1

/* M3 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd AVG_bfi_extrav AVG_bfi_agree AVG_bfi_consc AVG_bfi_emot AVG_bfi_open AVG_triad_narciss AVG_triad_psycho AVG_triad_machiav ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1

/* M4 */	xtreg SUCCESS_abs ///
			c_independent c_incumbent c_positionr c_female c_yearborn ///
			tone_CP feelgood fear ///
			cntry_elsys_pr e_ENPvotes compet election_type oecd AVG_bfi_extrav AVG_bfi_agree AVG_bfi_consc AVG_bfi_emot AVG_bfi_open AVG_triad_narciss AVG_triad_psycho AVG_triad_machiav ///
			bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
			bfi_extrav2 bfi_agree2 bfi_consc2 bfi_emot2 bfi_open2 triad_narciss2 triad_psycho2 triad_machiav2 if candcheck==1



** Table B13. PCA personality

pca bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav if candcheck==1
loadingplot



** Table B14. Profile effects (by independent status of candidate)

xtset election_count

xtreg SUCCESS_abs ///
c_independent c_incumbent c_positionr c_female c_yearborn ///
tone_CP feelgood fear ///
cntry_elsys_pr e_ENPvotes compet election_type oecd ///
bfi_extrav bfi_agree bfi_consc bfi_emot bfi_open triad_narciss triad_psycho triad_machiav ///
c.c_independent#c.bfi_extrav c.c_independent#c.bfi_agree c.c_independent#c.bfi_consc c.c_independent#c.bfi_emot c.c_independent#c.bfi_open c.c_independent#c.triad_narciss c.c_independent#c.triad_psycho c.c_independent#c.triad_machiav if candcheck==1






