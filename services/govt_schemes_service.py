"""
Government Agricultural Schemes Service
=========================================
Provides verified official agricultural schemes from the Ministry of Agriculture & Farmers Welfare,
State Agriculture Departments, NABARD, and official Government of India portals.

CRITICAL RULES:
- Never invents schemes, subsidy amounts, or fake links.
- Clearly distinguishes Central Government vs State Government schemes.
- Provides complete eligibility, required documents, application steps, and official URLs.
"""

GOVERNMENT_SCHEMES = [
    {
        "id": "pm-kisan",
        "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "title_hi": "प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)",
        "category": "Income Support",
        "category_hi": "आय सहायता",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "₹6,000 per year in 3 equal installments of ₹2,000 directly via DBT",
        "benefit_hi": "₹6,000 प्रति वर्ष (₹2,000 की 3 समान किस्तों में सीधे बैंक खाते में DBT द्वारा)",
        "description": "Central sector scheme to supplement financial needs of all landholding farmer families for agricultural inputs and domestic needs.",
        "description_hi": "सभी भूमिधारक किसान परिवारों को कृषि आदानों और घरेलू जरूरतों के लिए ₹6,000 वार्षिक प्रत्यक्ष वित्तीय सहायता प्रदान करने की केंद्रीय योजना।",
        "eligibility": "All landholding farmer families with cultivable land in their name. Excludes institutional landholders, income-tax payers, and government employees.",
        "eligibility_hi": "अपने नाम पर कृषि भूमि रखने वाले सभी किसान परिवार। संस्थागत भूधारक, आयकर दाता और सरकारी कर्मचारी बाहर हैं।",
        "required_documents": [
            "Aadhaar Card linked with active mobile number",
            "Land ownership record (Khasra / Khatauni / RoR)",
            "Bank Passbook (Aadhaar and NPCI linked)",
            "Active mobile number for OTP e-KYC"
        ],
        "required_documents_hi": [
            "मोबाइल नंबर से लिंक आधार कार्ड",
            "जमीन के मालिकाना हक का दस्तावेज (खसरा / खतौनी / नकल)",
            "बैंक पासबुक (आधार व NPCI डीबीटी से लिंक)",
            "ई-केवाईसी के लिए चालू मोबाइल नंबर"
        ],
        "application_instructions": "Visit the official PM-KISAN portal (pmkisan.gov.in) -> Click 'New Farmer Registration' -> Enter Aadhaar and land details -> Complete biometric or OTP e-KYC -> Submit for State Verification.",
        "application_instructions_hi": "आधिकारिक पीएम-किसान पोर्टल (pmkisan.gov.in) पर जाएं -> 'New Farmer Registration' पर क्लिक करें -> आधार और जमीन का विवरण दर्ज करें -> ओटीपी/बायोमेट्रिक ई-केवाईसी पूरी करें।",
        "official_link": "https://pmkisan.gov.in/",
        "department": "Department of Agriculture & Farmers Welfare, MoA&FW",
        "state_applicability": "All India (All States & UTs)",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Ministry of Agriculture & Farmers Welfare, Govt of India"
    },
    {
        "id": "pmfby",
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "title_hi": "प्रधानमंत्री फसल बीमा योजना (PMFBY)",
        "category": "Crop Insurance",
        "category_hi": "फसल बीमा",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Comprehensive financial cover against crop failure; Farmer premium only 1.5% for Rabi, 2% for Kharif, 5% for Annual Horticultural crops",
        "benefit_hi": "फसल नुकसान पर पूर्ण बीमा सुरक्षा; किसान प्रीमियम केवल रबी हेतु 1.5%, खरीफ हेतु 2%, और बागवानी फसलों हेतु 5%",
        "description": "Yield-based and weather-index crop insurance protecting farmers against non-preventable natural calamities, pests, and plant diseases.",
        "description_hi": "प्राकृतिक आपदाओं, कीटों और बीमारियों के कारण फसल क्षति के विरुद्ध किसानों को न्यूनतम प्रीमियम पर व्यापक जोखिम सुरक्षा प्रदान करने वाली योजना।",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas are eligible.",
        "eligibility_hi": "अधिसूचित क्षेत्रों में अधिसूचित फसलें उगाने वाले सभी किसान (बटाईदार और पट्टेदार किसान सहित) पात्र हैं।",
        "required_documents": [
            "Aadhaar Card",
            "Land Possession Certificate / Land Record (Khasra number)",
            "Sowing Certificate issued by Patwari / Village Agriculture Officer",
            "Cancelled Bank Cheque or Bank Passbook copy"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "भू-स्वामित्व प्रमाण पत्र / खसरा खतौनी",
            "पटवारी या ग्राम कृषि विस्तार अधिकारी द्वारा जारी बुवाई प्रमाण पत्र",
            "बैंक पासबुक या कैंसिल चेक की प्रति"
        ],
        "application_instructions": "Apply via official PMFBY portal (pmfby.gov.in), through Common Service Centers (CSCs), or through your bank branch before the seasonal cutoff deadline.",
        "application_instructions_hi": "पीएमएफबीवाई पोर्टल (pmfby.gov.in), सीएससी (CSC) केंद्र या अपनी बैंक शाखा के माध्यम से बुवाई मौसम की अंतिम तिथि से पूर्व आवेदन करें।",
        "official_link": "https://pmfby.gov.in/",
        "department": "Ministry of Agriculture & Farmers Welfare",
        "state_applicability": "All participating States & UTs",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Government of India — PMFBY Portal"
    },
    {
        "id": "kcc",
        "title": "Kisan Credit Card (KCC) Scheme",
        "title_hi": "किसान क्रेडिट कार्ड (KCC) योजना",
        "category": "Agricultural Credit",
        "category_hi": "कृषि ऋण",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Subsidized short-term crop loans up to ₹3 Lakh at an effective interest rate of 4% per annum upon prompt repayment",
        "benefit_hi": "समय पर भुगतान करने पर मात्र 4% वार्षिक प्रभावी ब्याज दर पर ₹3 लाख तक का रियायती अल्पकालिक फसल ऋण",
        "description": "Provides timely and adequate credit to farmers for crop cultivation, post-harvest expenses, farm asset maintenance, and dairy/fisheries activities.",
        "description_hi": "किसानों को खाद, बीज, कीटनाशक और खेती की अन्य आवश्यकताओं तथा पशुपालन व मत्स्य पालन हेतु रियायती दरों पर आसान संस्थागत ऋण उपलब्ध कराना।",
        "eligibility": "Owner cultivators, tenant farmers, oral lessees, sharecroppers, and Self-Help Groups (SHGs) or Joint Liability Groups (JLGs) of farmers.",
        "eligibility_hi": "भूमि स्वामी किसान, बटाईदार, पट्टेदार और किसान स्वयं सहायता समूह (SHG) या संयुक्त देयता समूह (JLG)।",
        "required_documents": [
            "Duly completed KCC Application Form",
            "Aadhaar Card / Voter ID for KYC verification",
            "Land records (Khasra / Khatauni) certified by revenue authorities",
            "No Dues Certificate (NDC) from neighboring financial institutions"
        ],
        "required_documents_hi": [
            "विधिवत भरा हुआ केसीसी आवेदन पत्र",
            "केवाईसी पहचान हेतु आधार कार्ड / मतदाता पहचान पत्र",
            "राजस्व प्राधिकारी द्वारा प्रमाणित भू-अभिलेख (खसरा / खतौनी)",
            "क्षेत्रीय बैंकों से कोई बकाया न होने का प्रमाण पत्र (यदि आवश्यक हो)"
        ],
        "application_instructions": "Submit standard 1-page KCC form to your nearest Commercial Bank, Regional Rural Bank (RRB), or Primary Agricultural Cooperative Society (PACS).",
        "application_instructions_hi": "अपने नजदीकी ग्रामीण बैंक, सहकारी समिति (PACS) या राष्ट्रीयकृत बैंक में 1-पेज का सरल केसीसी फॉर्म भरकर आवश्यक दस्तावेजों सहित जमा करें।",
        "official_link": "https://www.myscheme.gov.in/schemes/kcc",
        "department": "Reserve Bank of India & NABARD / MoA&FW",
        "state_applicability": "All India",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Reserve Bank of India & NABARD"
    },
    {
        "id": "pmksy",
        "title": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY — Per Drop More Crop)",
        "title_hi": "प्रधानमंत्री कृषि सिंचाई योजना (प्रति बूंद अधिक फसल)",
        "category": "Irrigation Support",
        "category_hi": "सिंचाई सहायता",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Up to 55% subsidy for small & marginal farmers and up to 45% for other farmers for Drip and Sprinkler micro-irrigation installation",
        "benefit_hi": "ड्रिप (टपक) और स्प्रिंकलर (फव्वारा) सिंचाई प्रणालियों की स्थापना हेतु लघु एवं सीमांत किसानों को 55% तक तथा अन्य किसानों को 45% तक का अनुदान",
        "description": "Aims to expand cultivable area under assured irrigation, improve on-farm water use efficiency, and promote micro-irrigation technologies.",
        "description_hi": "खेतों में पानी की बर्बादी रोककर आधुनिक ड्रिप व स्प्रिंकलर तकनीक से सूक्ष्म सिंचाई को बढ़ावा देकर 'हर खेत को पानी' और 'प्रति बूंद अधिक फसल' सुनिश्चित करना।",
        "eligibility": "Farmers of all categories who possess cultivable land with an assured water source are eligible.",
        "eligibility_hi": "वे सभी श्रेणी के किसान जिनके पास स्वयं की कृषि भूमि तथा सुनिश्चित जल स्रोत उपलब्ध है।",
        "required_documents": [
            "Aadhaar Card",
            "Proof of Land Ownership (B-1 / Khasra copy)",
            "Electricity connection receipt or proof of water source (well/tubewell)",
            "Bank passbook copy with IFSC code"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "भू-स्वामित्व का प्रमाण (बी-1 / खसरा नकल)",
            "विद्युत कनेक्शन रसीद अथवा जल स्रोत (कुआं/बोरवेल) का प्रमाण",
            "आईएफएससी कोड युक्त बैंक पासबुक की प्रति"
        ],
        "application_instructions": "Register on the State Agriculture / Horticulture Department DBT portal (e.g., dbt.mpdage.org for MP) or contact your District Horticulture Officer.",
        "application_instructions_hi": "राज्य कृषि/उद्यानिकी विभाग के डीबीटी पोर्टल पर ऑनलाइन पंजीकरण करें या जिला उद्यानिकी अधिकारी के कार्यालय में संपर्क करें।",
        "official_link": "https://pmksy.gov.in/",
        "department": "Ministry of Agriculture & Farmers Welfare / Ministry of Jal Shakti",
        "state_applicability": "All India",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "PMKSY Official Portal (pmksy.gov.in)"
    },
    {
        "id": "soil-health-card",
        "title": "Soil Health Card Scheme",
        "title_hi": "मृदा स्वास्थ्य कार्ड योजना (Soil Health Card)",
        "category": "Soil Health",
        "category_hi": "मृदा स्वास्थ्य",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Free soil testing and customized Soil Health Card with exact N-P-K and micronutrient dosage recommendations every 2 years",
        "benefit_hi": "निःशुल्क मिट्टी परीक्षण तथा प्रत्येक 2 वर्ष में खेत के लिए आवश्यक N-P-K और सूक्ष्म पोषक तत्वों की सटीक मात्रा का स्वास्थ्य कार्ड",
        "description": "Assists state governments to issue soil health cards to all farmers, reporting 12 parameters: N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, and OC.",
        "description_hi": "किसानों की मिट्टी के 12 प्रमुख पोषक तत्वों और पीएच स्तर की जांच कर संतुलित उर्वरक उपयोग की सिफारिशें उपलब्ध कराना।",
        "eligibility": "All landholding farmers in India.",
        "eligibility_hi": "भारत के सभी भूमिधारक किसान।",
        "required_documents": [
            "Aadhaar Card",
            "Land details (Survey / Khasra number and GPS location)",
            "Soil sample collected following official zigzag sampling method"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "खेत का खसरा नंबर व क्षेत्रफल",
            "जिग-जैग विधि से एकत्रित किया गया मिट्टी का नमूना"
        ],
        "application_instructions": "Submit soil samples through Village Agriculture Extension Officers or directly at your nearest District Soil Testing Laboratory.",
        "application_instructions_hi": "ग्राम कृषि विस्तार अधिकारी के माध्यम से या सीधे निकटतम जिला मृदा परीक्षण प्रयोगशाला में मिट्टी का नमूना जमा करें।",
        "official_link": "https://soilhealth.dac.gov.in/",
        "department": "Department of Agriculture & Farmers Welfare",
        "state_applicability": "All India",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "National Soil Health Portal (soilhealth.dac.gov.in)"
    },
    {
        "id": "pkvy",
        "title": "Paramparagat Krishi Vikas Yojana (PKVY)",
        "title_hi": "परंपरागत कृषि विकास योजना (PKVY)",
        "category": "Organic Farming",
        "category_hi": "जैविक खेती",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Financial assistance of ₹50,000 per hectare over 3 years, of which ₹31,000/ha is given directly to farmers for organic inputs",
        "benefit_hi": "3 वर्षों में ₹50,000 प्रति हेक्टेयर की वित्तीय सहायता, जिसमें से ₹31,000/हेक्टेयर सीधे किसानों को जैविक आदानों हेतु डीबीटी द्वारा",
        "description": "Sub-component of Soil Health Management under NMSA aimed at promoting organic farming through cluster approach and PGS-India certification.",
        "description_hi": "क्लस्टर पद्धति और पीजीएस-इंडिया प्रमाणीकरण के माध्यम से रासायनिक मुक्त जैविक खेती और टिकाऊ मृदा उर्वरता को बढ़ावा देने की योजना।",
        "eligibility": "Farmer groups or individual farmers willing to form a 20-hectare cluster for chemical-free organic farming.",
        "eligibility_hi": "रासायनिक मुक्त जैविक खेती करने के इच्छुक 20 या अधिक हेक्टेयर के क्लस्टर समूह में शामिल किसान।",
        "required_documents": [
            "Aadhaar Card",
            "Land title documents",
            "Bank Account linked to Aadhaar",
            "PGS-India cluster commitment agreement"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "भूमि अभिलेख दस्तावेज",
            "आधार लिंक बैंक खाता",
            "पीजीएस-इंडिया क्लस्टर सहमति पत्र"
        ],
        "application_instructions": "Apply through your Regional Council or District Agriculture Office for cluster sanction under PGS-India organic certification.",
        "application_instructions_hi": "पीजीएस-इंडिया पोर्टल या जिला कृषि अधिकारी के माध्यम से क्लस्टर अनुमोदन हेतु आवेदन करें।",
        "official_link": "https://dapgd.gov.in/",
        "department": "Department of Agriculture & Farmers Welfare",
        "state_applicability": "All India",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Ministry of Agriculture & Farmers Welfare"
    },
    {
        "id": "e-nam",
        "title": "National Agriculture Market (e-NAM)",
        "title_hi": "राष्ट्रीय कृषि बाजार (e-NAM)",
        "category": "Market & Trade",
        "category_hi": "बाजार एवं विपणन",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "Direct online electronic trading across 1,300+ connected mandis across India with transparent price bidding and prompt online payment",
        "benefit_hi": "देश की 1,300 से अधिक मंडियों में पारदर्शी ऑनलाइन ई-नीलामी, प्रतिस्पर्धी मूल्य और सीधे बैंक खाते में ऑनलाइन भुगतान की सुविधा",
        "description": "Pan-India electronic trading portal that networks existing APMC mandis to create a unified national digital market for agricultural commodities.",
        "description_hi": "देश की प्रमुख एपीएमसी मंडियों को ऑनलाइन जोड़कर किसानों को अपनी उपज का देशव्यापी सर्वोत्तम मूल्य दिलाने वाला डिजिटल बाजार।",
        "eligibility": "Any farmer having agricultural produce to sell at any participating APMC mandi.",
        "eligibility_hi": "कोई भी किसान जिसके पास ई-नाम से जुड़ी मंडी में बेचने हेतु कृषि उपज उपलब्ध है।",
        "required_documents": [
            "Aadhaar Card",
            "Bank Account details (Passbook copy)",
            "Active mobile number for SMS lot alerts",
            "Mandi Gate Entry pass"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "बैंक पासबुक की प्रति",
            "एसएमएस अलर्ट हेतु चालू मोबाइल नंबर",
            "मंडी गेट प्रवेश पर्ची"
        ],
        "application_instructions": "Register free online at enam.gov.in or directly at the e-NAM help desk located at your local APMC mandi gate.",
        "application_instructions_hi": "enam.gov.in पोर्टल पर अथवा अपनी स्थानीय एपीएमसी मंडी के ई-नाम सहायता केंद्र पर निःशुल्क पंजीकरण कराएं।",
        "official_link": "https://enam.gov.in/",
        "department": "Small Farmers Agribusiness Consortium (SFAC), MoA&FW",
        "state_applicability": "All participating States (23+ States & UTs)",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Small Farmers Agribusiness Consortium (SFAC)"
    },
    {
        "id": "smam",
        "title": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "title_hi": "कृषि यंत्रीकरण पर उप-मिशन (SMAM)",
        "category": "Equipment Subsidy",
        "category_hi": "कृषि यंत्र अनुदान",
        "level": "Central Government",
        "level_hi": "केंद्र सरकार",
        "benefit": "40% to 50% subsidy on procurement of tractors, rotavators, seed drills, laser levelers, and custom hiring centers",
        "benefit_hi": "ट्रैक्टर, रोटावेटर, सीड ड्रिल, लेजर लैंड लेवलर व कस्टम हायरिंग केंद्र की स्थापना हेतु 40% से 50% तक का सरकारी अनुदान",
        "description": "Promotes farm mechanization to increase productivity and reduce production costs, with preferential subsidies for SC, ST, women, and small farmers.",
        "description_hi": "किसानों को आधुनिक कृषि यंत्रों की खरीद पर 40-50% तक की भारी सब्सिडी प्रदान करने वाला राष्ट्रीय मिशन।",
        "eligibility": "Small, marginal, SC/ST, women, and general category farmers holding valid land records.",
        "eligibility_hi": "वैध भू-अभिलेख रखने वाले लघु, सीमांत, महिला एवं सभी श्रेणी के किसान।",
        "required_documents": [
            "Aadhaar Card",
            "Land Record (Khasra B-1)",
            "Bank Passbook copy",
            "Caste Certificate (for SC/ST higher subsidy quota)"
        ],
        "required_documents_hi": [
            "आधार कार्ड",
            "खसरा बी-1 की नकल",
            "बैंक पासबुक की प्रति",
            "जाति प्रमाण पत्र (अतिरिक्त अनुदान हेतु)"
        ],
        "application_instructions": "Register on the Central Agri Mechanization portal (agrimachinery.nic.in) or state DBT portals during the open lottery application window.",
        "application_instructions_hi": "agrimachinery.nic.in या राज्य के कृषि यंत्र डीबीटी पोर्टल पर आवेदन विंडो खुलने पर लॉटरी हेतु ऑनलाइन आवेदन करें।",
        "official_link": "https://agrimachinery.nic.in/",
        "department": "Department of Agriculture & Farmers Welfare",
        "state_applicability": "All India",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Ministry of Agriculture & Farmers Welfare (agrimachinery.nic.in)"
    },
    {
        "id": "mp-kisan-kalyan",
        "title": "Mukhyamantri Kisan Kalyan Yojana (Madhya Pradesh)",
        "title_hi": "मुख्यमंत्री किसान कल्याण योजना (मध्य प्रदेश)",
        "category": "Income Support",
        "category_hi": "आय सहायता",
        "level": "State Government",
        "level_hi": "राज्य सरकार (मध्य प्रदेश)",
        "benefit": "Additional ₹6,000 per year in two installments from the MP State Government (Totaling ₹12,000/year with PM-KISAN)",
        "benefit_hi": "मध्य प्रदेश शासन द्वारा ₹6,000 प्रति वर्ष की अतिरिक्त सहायता (पीएम-किसान मिलाकर कुल ₹12,000 प्रति वर्ष)",
        "description": "State income support scheme for registered PM-KISAN beneficiary farmers in Madhya Pradesh to foster agricultural development and livelihood security.",
        "description_hi": "मध्य प्रदेश के पीएम-किसान लाभार्थी किसानों को राज्य सरकार द्वारा दी जाने वाली अतिरिक्त ₹6,000 वार्षिक सम्मान राशि।",
        "eligibility": "Resident farmers of Madhya Pradesh who are actively registered and approved beneficiaries under PM-KISAN.",
        "eligibility_hi": "मध्य प्रदेश के मूल निवासी किसान जो पीएम-किसान योजना के सक्रिय एवं स्वीकृत हितग्राही हैं।",
        "required_documents": [
            "PM-KISAN Registration ID",
            "Samagra ID of Madhya Pradesh",
            "Aadhaar Card",
            "Land Khasra details in MP"
        ],
        "required_documents_hi": [
            "पीएम-किसान पंजीकरण संख्या",
            "मध्य प्रदेश समग्र परिवार व सदस्य आईडी",
            "आधार कार्ड",
            "मध्य प्रदेश भू-अभिलेख खसरा"
        ],
        "application_instructions": "Eligible PM-KISAN beneficiaries in MP are automatically verified through the SAARA portal (saara.mp.gov.in) via local Patwari verification.",
        "application_instructions_hi": "पीएम-किसान पात्र हितग्राहियों का सारा पोर्टल (saara.mp.gov.in) पर हल्का पटवारी द्वारा स्वतः सत्यापन किया जाता है।",
        "official_link": "https://saara.mp.gov.in/",
        "department": "Revenue Department & Department of Farmers Welfare, Govt of MP",
        "state_applicability": "Madhya Pradesh",
        "status": "Active & Ongoing",
        "last_verified_date": "October 2026",
        "source": "Government of Madhya Pradesh — SAARA Portal"
    }
]


def get_all_schemes(category: str = None, level: str = None, state: str = None, search: str = None) -> list:
    """Filter and return verified government agricultural schemes."""
    results = GOVERNMENT_SCHEMES

    if category and category.lower() != "all":
        results = [s for s in results if s["category"].lower() == category.lower()]

    if level and level.lower() != "all":
        results = [s for s in results if level.lower() in s["level"].lower()]

    if state and state.lower() != "all":
        results = [
            s for s in results
            if s["state_applicability"].lower() == "all india"
            or state.lower() in s["state_applicability"].lower()
        ]

    if search:
        s_term = search.strip().lower()
        results = [
            s for s in results
            if s_term in s["title"].lower()
            or s_term in s["title_hi"].lower()
            or s_term in s["description"].lower()
            or s_term in s["description_hi"].lower()
            or s_term in s["category"].lower()
            or s_term in s["benefit"].lower()
        ]

    return results
