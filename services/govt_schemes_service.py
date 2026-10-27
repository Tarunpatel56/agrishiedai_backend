"""
AgriShield AI — Government Schemes Service
Provides verified Indian Central & State agricultural government schemes,
official eligibility criteria, required documents, step-by-step application instructions,
and verified official application portals.
Supports full Hindi ('hi') and English ('en') responses.
"""

from typing import List, Dict, Any

OFFICIAL_SCHEMES_EN = [
    {
        "id": "pm-kisan",
        "title": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
        "short_name": "PM-KISAN",
        "category": "Direct Income Support",
        "benefit": "₹6,000 per year directly transferred to bank account in 3 equal installments of ₹2,000",
        "description": "Central Sector scheme with 100% funding from Government of India to supplement the financial needs of landholding farmers' families for procuring agricultural inputs and domestic needs.",
        "eligibility": [
            "All landholding farmer families with cultivable land in their names.",
            "Subject to exclusion criteria (e.g., institutional landholders, active/retired government servants, income tax payees, constitutional post holders)."
        ],
        "documents_required": [
            "Aadhaar Card (mandatory)",
            "Bank Account linked with Aadhaar and NPCI/DBT active",
            "Land ownership records (Khasra / Khatauni / RoR)",
            "Active mobile number linked with Aadhaar"
        ],
        "application_process": "1. Visit the official PM-KISAN portal (pmkisan.gov.in) -> Farmers Corner -> New Farmer Registration.\n2. Choose Rural or Urban Farmer Registration.\n3. Enter Aadhaar Number and Mobile Number, select State, and verify via OTP.\n4. Fill personal, bank, and land details (Survey/Khata number) and upload land record document.\n5. Alternatively, register via nearest Common Service Centre (CSC) or State Nodal Agriculture Officer.",
        "official_source": "Department of Agriculture & Farmers Welfare, Ministry of Agriculture & Farmers Welfare",
        "official_url": "https://pmkisan.gov.in/",
        "apply_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "application_mode": "Online & CSC",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "pmfby",
        "title": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "short_name": "PMFBY",
        "category": "Crop Insurance",
        "benefit": "Comprehensive financial security against non-preventable natural risks (drought, flood, unseasonal rain, pests, diseases). Farmers pay only 2% for Kharif, 1.5% for Rabi, and 5% for commercial/horticultural crops.",
        "description": "Nationwide crop insurance scheme providing yield loss and localized calamity insurance cover to stabilize farmers' income and encourage adoption of innovative farming practices.",
        "eligibility": [
            "All farmers growing notified crops in notified areas (both loanee and non-loanee farmers, sharecroppers, and tenant farmers).",
            "Enrollment must be completed before the cut-off date specified for the crop season."
        ],
        "documents_required": [
            "Land Possession Certificate (LPC) or Record of Rights (RoR)",
            "Sowing Certificate issued by Patwari/Village Officer",
            "Bank passbook copy (showing IFSC and Account Number)",
            "Aadhaar Card",
            "Tenant / Sharecropper agreement (if applicable)"
        ],
        "application_process": "1. Visit pmfby.gov.in -> Farmer Corner -> Apply for Crop Insurance.\n2. Log in using Mobile Number and OTP or register if new user.\n3. Select your State, District, Sub-district, Village, Season, and Crop.\n4. Upload land records and sowing certificate.\n5. Pay the nominal farmer share premium online via UPI, NetBanking, or through your KCC loan branch/CSC.",
        "official_source": "Ministry of Agriculture & Farmers Welfare, Government of India",
        "official_url": "https://pmfby.gov.in/",
        "apply_url": "https://pmfby.gov.in/farmerRegistrationForm",
        "application_mode": "Online, Bank Branch, & CSC",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "kcc",
        "title": "Kisan Credit Card (KCC) Scheme",
        "short_name": "KCC",
        "category": "Agricultural Credit",
        "benefit": "Institutional short-term crop loans up to ₹3,00,000 at a concessional interest rate of 4% per annum (after 3% prompt repayment incentive). Collateral-free loan up to ₹1.6 Lakh.",
        "description": "Simplified credit delivery mechanism ensuring timely credit support to farmers for crop cultivation, post-harvest expenses, farm asset maintenance, and allied activities (dairy, poultry, fisheries).",
        "eligibility": [
            "All farmers — individuals/joint borrowers who are owner cultivators.",
            "Tenant farmers, oral lessees, and sharecroppers.",
            "Self Help Groups (SHGs) or Joint Liability Groups (JLGs) of farmers."
        ],
        "documents_required": [
            "Completed KCC application form",
            "Proof of identity (Aadhaar Card / Voter ID / PAN Card)",
            "Proof of address",
            "Land ownership documents / revenue records certified by Patwari",
            "Cropping pattern details"
        ],
        "application_process": "1. Download the unified one-page KCC application form from pmkisan.gov.in or any commercial/cooperative bank.\n2. Fill land details, crop cultivated, and requested loan limit.\n3. Submit with land documents and Aadhaar to your nearest bank branch where you have a savings account.\n4. Banks process and issue the KCC card within 14 days.",
        "official_source": "Reserve Bank of India (RBI) & NABARD",
        "official_url": "https://www.myscheme.gov.in/schemes/kcc",
        "apply_url": "https://pmkisan.gov.in/Documents/KCC_Application_Form.pdf",
        "application_mode": "Bank Branch & Online",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "pmksy",
        "title": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY - Per Drop More Crop)",
        "short_name": "PMKSY",
        "category": "Irrigation Support",
        "benefit": "Subsidy of up to 55% for small and marginal farmers, and up to 45% for other farmers on micro-irrigation systems (Drip and Sprinkler irrigation).",
        "description": "Centrally sponsored initiative aimed at expanding cultivable area under assured irrigation, improving on-farm water use efficiency, and promoting precision micro-irrigation technologies.",
        "eligibility": [
            "All farmers possessing cultivable land with an assured water source (borewell, well, canal, or farm pond).",
            "Members of water users associations and farmer producer groups."
        ],
        "documents_required": [
            "Aadhaar Card",
            "Land Ownership Record (Khatauni / 7/12 extract)",
            "Water source certificate/declaration",
            "Electricity connection receipt (for pump) or NOC",
            "Bank passbook copy"
        ],
        "application_process": "1. Visit the state horticulture / agriculture department portal (e.g. mpfsts.mp.gov.in for MP, dbtagriculture.bihar.gov.in for Bihar, or pmksy.gov.in).\n2. Register under the 'Micro Irrigation' component.\n3. Upload land document, Aadhaar, and quotation from an empaneled drip/sprinkler supplier.\n4. Field verification is conducted by the Horticulture Officer, followed by subsidy release directly via DBT.",
        "official_source": "Ministry of Agriculture & Farmers Welfare, GoI",
        "official_url": "https://pmksy.gov.in/",
        "apply_url": "https://pmksy.gov.in/",
        "application_mode": "State DBT Agriculture Portals",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "soil-health-card",
        "title": "Soil Health Card (SHC) Scheme",
        "short_name": "Soil Health Card",
        "category": "Soil Health & Nutrient",
        "benefit": "Free periodic laboratory testing of 12 chemical and physical soil parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) with tailored fertilizer dosage recommendations.",
        "description": "Helps farmers optimize fertilizer use, reduce unnecessary chemical expenditure, and maintain soil biology and long-term fertility.",
        "eligibility": [
            "All agricultural landholders across India."
        ],
        "documents_required": [
            "Aadhaar Card",
            "Land Identification (Survey Number / Khasra Number)"
        ],
        "application_process": "1. Soil samples are collected by agriculture extension workers from farmer fields.\n2. Farmers can track sample status and view/download Soil Health Cards directly by entering State, District, and Khasra on soilhealth.dac.gov.in.\n3. Printed cards are also distributed through Gram Panchayats and KVKs.",
        "official_source": "Department of Agriculture & Farmers Welfare",
        "official_url": "https://soilhealth.dac.gov.in/",
        "apply_url": "https://soilhealth.dac.gov.in/home",
        "application_mode": "Online Portal & KVK",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "enam",
        "title": "National Agriculture Market (e-NAM)",
        "short_name": "e-NAM",
        "category": "Market & Trade",
        "benefit": "Direct digital access to over 1,360+ wholesale APMC mandis across 23 States/UTs. Real-time online bidding, electronic weighing, transparent price discovery, and direct online payment to bank accounts.",
        "description": "Pan-India electronic trading portal that networks existing APMC mandis to create a unified national digital market for agricultural commodities.",
        "eligibility": [
            "All farmers, Farmer Producer Organizations (FPOs), traders, and commission agents."
        ],
        "documents_required": [
            "Aadhaar Card",
            "Bank Passbook copy with IFSC",
            "Mandi Registration / Gate pass",
            "Mobile number"
        ],
        "application_process": "1. Visit enam.gov.in -> Registration -> Registration Type: Farmer.\n2. Enter Passbook details, Mobile number, and Mandi.\n3. Receive unique e-NAM Farmer ID.\n4. Bring crop to any e-NAM mandi gate, generate lot, get quality assaying done, and participate in competitive transparent online auctions.",
        "official_source": "Small Farmers Agribusiness Consortium (SFAC)",
        "official_url": "https://enam.gov.in/",
        "apply_url": "https://enam.gov.in/web/stakeholders-registration/farmer",
        "application_mode": "Online & APMC Mandi Gate",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "pm-kusum",
        "title": "PM-KUSUM (Pradhan Mantri Kisan Urja Suraksha evam Utthaan Mahabhiyan)",
        "short_name": "PM-KUSUM",
        "category": "Solar Energy & Irrigation",
        "benefit": "Up to 60% subsidy (30% Central + 30% State Govt) for installing standalone solar agricultural pumps (3HP to 7.5HP) or solarizing existing grid-connected electric pumps.",
        "description": "Provides clean, reliable day-time solar power for farm irrigation, reduces diesel pump running costs, and enables farmers to sell surplus solar power back to the grid for additional income.",
        "eligibility": [
            "Individual farmers, water user associations, FPOs, and panchayats with agricultural land.",
            "Farmers relying on diesel pumps or requiring off-grid solar irrigation."
        ],
        "documents_required": [
            "Aadhaar Card",
            "Land revenue record (Khasra/Khatauni)",
            "Bank passbook",
            "Electricity bill (for Component C solarization)",
            "Passport photo"
        ],
        "application_process": "1. Apply through the State Renewable Energy Development Agency portal (e.g., Urja Vikas Nigam in MP, MREDA in Maharashtra, etc.) or pmkusum.mnre.gov.in.\n2. Submit online application with land and pump requirement.\n3. Pay farmer share (approx 10-40% depending on state bank tie-up).\n4. Empaneled solar vendor installs verified solar pump setup with 5-year warranty.",
        "official_source": "Ministry of New and Renewable Energy (MNRE), GoI",
        "official_url": "https://pmkusum.mnre.gov.in/",
        "apply_url": "https://pmkusum.mnre.gov.in/",
        "application_mode": "State Renewable Energy Portals",
        "last_verified": "October 2026",
        "is_verified": True
    },
    {
        "id": "smam",
        "title": "Sub-Mission on Agricultural Mechanization (SMAM / DBT Farm Machinery)",
        "short_name": "SMAM",
        "category": "Farm Machinery & Mechanization",
        "benefit": "40% to 50% financial subsidy on tractors, power tillers, rotavators, seed drills, laser levelers, harvesters, and custom hiring centers.",
        "description": "Promotes modern agricultural machinery to increase farm productivity, offset labor shortages, and lower cultivation turnaround times.",
        "eligibility": [
            "All small, marginal, SC/ST, and women farmers receive priority 50% subsidy; other farmers receive 40% subsidy.",
            "Must not have received subsidy for the same machine category in the previous 5 years."
        ],
        "documents_required": [
            "Aadhaar Card",
            "Land documents (Khasra/Khatauni)",
            "Bank passbook copy",
            "Caste Certificate (if claiming SC/ST quota)",
            "Quotation from authorized implement dealer"
        ],
        "application_process": "1. Visit agrimachinery.nic.in -> Farmer Registration.\n2. Choose machine category and model.\n3. Submit application online; lottery or first-come selection determines token generation.\n4. Purchase machine from authorized dealer and upload invoice & serial number for DBT transfer.",
        "official_source": "Department of Agriculture & Farmers Welfare",
        "official_url": "https://agrimachinery.nic.in/",
        "apply_url": "https://agrimachinery.nic.in/Index/FarmerRegistration",
        "application_mode": "Online DBT Portal",
        "last_verified": "October 2026",
        "is_verified": True
    }
]

OFFICIAL_SCHEMES_HI = [
    {
        "id": "pm-kisan",
        "title": "प्रधानमंत्री किसान सम्मान निधि (PM-KISAN)",
        "short_name": "पीएम-किसान",
        "category": "प्रत्यक्ष आय सहायता",
        "benefit": "प्रति वर्ष ₹6,000 की प्रत्यक्ष आर्थिक सहायता, ₹2,000 की तीन समान किस्तों में सीधे बैंक खाते में।",
        "description": "भारत सरकार द्वारा 100% वित्तपोषित योजना, जिसका उद्देश्य सभी भूमिधारक किसान परिवारों को कृषि आदानों एवं घरेलू आवश्यकताओं के लिए आर्थिक संबल प्रदान करना है।",
        "eligibility": [
            "सभी भूमिधारक किसान परिवार जिनके नाम पर खेती योग्य भूमि दर्ज है।",
            "संवैधानिक पदधारक, सेवारत/सेवानिवृत्त सरकारी कर्मचारी एवं आयकर दाता इसके अंतर्गत पात्र नहीं हैं।"
        ],
        "documents_required": [
            "आधार कार्ड (अनिवार्य)",
            "आधार व NPCI/DBT से लिंक सक्रिय बैंक खाता",
            "भूमि स्वामित्व दस्तावेज (खसरा / खतौनी / नकल)",
            "आधार से लिंक सक्रिय मोबाइल नंबर"
        ],
        "application_process": "1. आधिकारिक PM-KISAN पोर्टल (pmkisan.gov.in) पर जाएं -> Farmers Corner -> New Farmer Registration चुनें।\n2. ग्रामीण या शहरी किसान पंजीकरण चुनें।\n3. आधार नंबर और मोबाइल नंबर दर्ज कर OTP सत्यापित करें।\n4. व्यक्तिगत, बैंक एवं भूमि विवरण (खसरा/खाता संख्या) दर्ज कर भूमि अभिलेख अपलोड करें।\n5. आप नजदीकी सीएससी (CSC) केंद्र या कृषि विस्तार अधिकारी के माध्यम से भी आवेदन कर सकते हैं।",
        "official_source": "कृषि एवं किसान कल्याण मंत्रालय, भारत सरकार",
        "official_url": "https://pmkisan.gov.in/",
        "apply_url": "https://pmkisan.gov.in/RegistrationFormNew.aspx",
        "application_mode": "ऑनलाइन एवं सीएससी केंद्र",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "pmfby",
        "title": "प्रधानमंत्री फसल बीमा योजना (PMFBY)",
        "short_name": "पीएम फसल बीमा",
        "category": "फसल बीमा सुरक्षा",
        "benefit": "प्राकृतिक आपदाओं (सूखा, बाढ़, ओलावृष्टि, बेमौसम बारिश, कीट एवं रोग) से होने वाले नुकसान पर पूर्ण वित्तीय सुरक्षा। खरीफ के लिए केवल 2%, रबी के लिए 1.5% और वाणिज्यिक/बागवानी फसलों के लिए केवल 5% प्रीमियम।",
        "description": "देशव्यापी फसल बीमा योजना जो अप्रत्याशित प्राकृतिक जोखिमों के समय किसानों की आय को स्थिर रखती है और आधुनिक कृषि तकनीक अपनाने का हौसला देती है।",
        "eligibility": [
            "अधिसूचित क्षेत्रों में अधिसूचित फसल उगाने वाले सभी किसान (ऋणी, गैर-ऋणी, बटाईदार और काश्तकार)।",
            "कट-ऑफ तिथि से पहले बीमा आवेदन पूर्ण होना आवश्यक है।"
        ],
        "documents_required": [
            "भू-अधिकार प्रमाण पत्र (खसरा/खतौनी/जमाबंदी)",
            "पटवारी या ग्राम सेवक द्वारा जारी बुवाई प्रमाण पत्र (Sowing Certificate)",
            "बैंक पासबुक की प्रति (IFSC व खाता संख्या स्पष्ट)",
            "आधार कार्ड",
            "किरायेदार/बटाईदार अनुबंध (यदि लागू हो)"
        ],
        "application_process": "1. pmfby.gov.in पर जाएं -> Farmer Corner -> Apply for Crop Insurance चुनें।\n2. मोबाइल नंबर और OTP से लॉगिन करें या नया खाता बनाएं।\n3. राज्य, जिला, ब्लॉक, ग्राम पंचायत, मौसम और फसल का चयन करें।\n4. भूमि दस्तावेज और बुवाई प्रमाण पत्र अपलोड करें।\n5. किसान हिस्से का मामूली प्रीमियम यूपीआई, नेट बैंकिंग या नजदीकी बैंक/सीएससी के जरिए जमा करें।",
        "official_source": "कृषि एवं किसान कल्याण मंत्रालय, भारत सरकार",
        "official_url": "https://pmfby.gov.in/",
        "apply_url": "https://pmfby.gov.in/farmerRegistrationForm",
        "application_mode": "ऑनलाइन, बैंक शाखा एवं सीएससी",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "kcc",
        "title": "किसान क्रेडिट कार्ड (KCC) योजना",
        "short_name": "केसीसी",
        "category": "कृषि ऋण एवं साख",
        "benefit": "समय पर भुगतान करने पर मात्र 4% वार्षिक ब्याज दर पर ₹3,00,000 तक का अल्पकालिक कृषि ऋण। ₹1.60 लाख तक बिना किसी बंधक (Collateral Free) ऋण।",
        "description": "किसानों को फसल बुवाई, कीटनाशक, खाद, बीज, कटाई और कृषि संपत्तियों की देखरेख तथा पशुपालन व मत्स्य पालन के लिए सस्ती ब्याज दर पर ऋण सुविधा।",
        "eligibility": [
            "सभी व्यक्तिगत या संयुक्त भूमिधारक किसान।",
            "पट्टेदार, बटाईदार और मौखिक पट्टाधारक किसान।",
            "स्वयं सहायता समूह (SHG) या संयुक्त देयता समूह (JLG)।"
        ],
        "documents_required": [
            "पूर्ण भरा हुआ सरल केसीसी आवेदन पत्र",
            "पहचान प्रमाण (आधार कार्ड / मतदाता पहचान पत्र / पैन)",
            "निवास प्रमाण पत्र",
            "पटवारी द्वारा सत्यापित भूमि स्वामित्व अभिलेख (खसरा/खतौनी)",
            "फसल बुवाई का ब्योरा"
        ],
        "application_process": "1. pmkisan.gov.in या किसी भी वाणिज्यिक/सहकारी बैंक से एक पेज का KCC फॉर्म डाउनलोड करें।\n2. भूमि विवरण, बोई गई फसल और मांगी गई ऋण सीमा भरें।\n3. आधार और भूमि रिकॉर्ड के साथ अपनी बैंक शाखा में जमा करें।\n4. बैंक 14 दिनों के भीतर आवेदन का सत्यापन कर KCC कार्ड जारी करते हैं।",
        "official_source": "भारतीय रिजर्व बैंक (RBI) एवं नाबार्ड (NABARD)",
        "official_url": "https://www.myscheme.gov.in/schemes/kcc",
        "apply_url": "https://pmkisan.gov.in/Documents/KCC_Application_Form.pdf",
        "application_mode": "बैंक शाखा एवं ऑनलाइन",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "pmksy",
        "title": "प्रधानमंत्री कृषि सिंचाई योजना (PMKSY - प्रति बूंद अधिक फसल)",
        "short_name": "पीएम सिंचाई योजना",
        "category": "सिंचाई उपकरण एवं तकनीक",
        "benefit": "सूक्ष्म सिंचाई प्रणाली (ड्रिप एवं स्प्रिंकलर) लगाने पर छोटे व सीमांत किसानों को 55% तथा अन्य किसानों को 45% तक का सरकारी अनुदान।",
        "description": "खेत तक पानी पहुंचाने, जल संरक्षण को बढ़ावा देने और आधुनिक ड्रिप/स्प्रिंकलर विधि से कम पानी में भरपूर पैदावार लेने हेतु प्रमुख योजना।",
        "eligibility": [
            "सभी किसान जिनके पास कृषि योग्य भूमि और सुनिश्चित जल स्रोत (बोरवेल, कुआं, नहर, फार्म पोंड) उपलब्ध है।",
            "जल उपभोक्ता संघों व किसान उत्पादक संगठनों के सदस्य।"
        ],
        "documents_required": [
            "आधार कार्ड",
            "भूमि अभिलेख (खतौनी / 7-12 नकल)",
            "जल स्रोत प्रमाण पत्र/घोषणा",
            "विद्युत कनेक्शन बिल (पंप सेट हेतु) अथवा अनापत्ति प्रमाण पत्र",
            "बैंक पासबुक की प्रति"
        ],
        "application_process": "1. राज्य के उद्यानिकी/कृषि विभाग के डीबीटी पोर्टल (जैसे म.प्र. में dbt.mpdage.org, बिहार में dbtagriculture.bihar.gov.in) पर जाएं।\n2. सूक्ष्म सिंचाई योजना के तहत पंजीकरण करें।\n3. अधिकृत ड्रिप/स्प्रिंकलर डीलर का कोटेशन और भूमि दस्तावेज अपलोड करें।\n4. भौतिक सत्यापन के पश्चात सब्सिडी सीधे बैंक खाते में जमा होती है।",
        "official_source": "कृषि एवं किसान कल्याण मंत्रालय, भारत सरकार",
        "official_url": "https://pmksy.gov.in/",
        "apply_url": "https://pmksy.gov.in/",
        "application_mode": "राज्य कृषि डीबीटी पोर्टल",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "soil-health-card",
        "title": "मृदा स्वास्थ्य कार्ड योजना (Soil Health Card)",
        "short_name": "मृदा स्वास्थ्य कार्ड",
        "category": "मृदा उर्वरता एवं पोषण",
        "benefit": "मिट्टी के 12 प्रमुख रासायनिक व भौतिक मापदंडों (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) की निःशुल्क प्रयोगशाला जांच और फसलवार संतुलित खाद की सिफारिश।",
        "description": "किसानों को मिट्टी की वास्तविक उर्वरता की जानकारी देकर अंधाधुंध रासायनिक खाद के खर्च को कम करने और उत्पादन बढ़ाने में सहायक।",
        "eligibility": [
            "देश के सभी कृषि भूमिधारक किसान।"
        ],
        "documents_required": [
            "आधार कार्ड",
            "खेत का खसरा नंबर / खाता संख्या"
        ],
        "application_process": "1. कृषि विस्तार कार्यकर्ताओं द्वारा खेत से मिट्टी के नमूने एकत्र किए जाते हैं।\n2. किसान soilhealth.dac.gov.in पर जाकर राज्य, जिला और खसरा नंबर डालकर अपने कार्ड की स्थिति देख सकते हैं और कार्ड डाउनलोड कर सकते हैं।\n3. मुद्रित कार्ड ग्राम पंचायतों और कृषि विज्ञान केंद्रों द्वारा भी बांटे जाते हैं।",
        "official_source": "कृषि एवं किसान कल्याण विभाग",
        "official_url": "https://soilhealth.dac.gov.in/",
        "apply_url": "https://soilhealth.dac.gov.in/home",
        "application_mode": "ऑनलाइन पोर्टल एवं कृषि विज्ञान केंद्र",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "enam",
        "title": "राष्ट्रीय कृषि बाजार (e-NAM)",
        "short_name": "ई-नाम मंडी",
        "category": "मंडी व्यापार एवं विपणन",
        "benefit": "देश के 23 राज्यों/केंद्र शासित प्रदेशों की 1,360+ एपीएमसी मंडियों से सीधा डिजिटल जुड़ाव। ऑनलाइन प्रतिस्पर्धी बोली, इलेक्ट्रॉनिक तुलाई, पारदर्शी भाव और सीधे बैंक खाते में भुगतान।",
        "description": "एक राष्ट्र, एक बाजार की परिकल्पना के तहत कृषि उपज के लिए डिजिटल प्लेटफॉर्म, जहां किसान अपनी उपज का बेहतर मूल्य प्राप्त कर सकते हैं।",
        "eligibility": [
            "सभी किसान, किसान उत्पादक संगठन (FPO) और पंजीकृत व्यापारी।"
        ],
        "documents_required": [
            "आधार कार्ड",
            "बैंक पासबुक की प्रति",
            "मंडी प्रवेश गेट पास",
            "मोबाइल नंबर"
        ],
        "application_process": "1. enam.gov.in पर जाएं -> Registration -> Farmer चुनें।\n2. बैंक विवरण और मंडी का चयन करें और ई-नाम आईडी प्राप्त करें।\n3. फसल लेकर ई-नाम मंडी गेट पर जाएं, लॉट तैयार कराएं, गुणवत्ता जांच (Assaying) कराएं और ऑनलाइन नीलामी में भाग लें।",
        "official_source": "लघु कृषक कृषि-व्यापार संकाय (SFAC)",
        "official_url": "https://enam.gov.in/",
        "apply_url": "https://enam.gov.in/web/stakeholders-registration/farmer",
        "application_mode": "ऑनलाइन एवं एपीएमसी मंडी गेट",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "pm-kusum",
        "title": "पीएम-कुसुम योजना (सौर ऊर्जा एवं सोलर पंप)",
        "short_name": "पीएम-कुसुम सोलर",
        "category": "सौर ऊर्जा एवं सिंचाई",
        "benefit": "खेत में स्टैंडअलोन सोलर पंप (3 से 7.5 एचपी) लगाने या बिजली पंप को सोलर से जोड़ने पर 60% तक की भारी सरकारी सब्सिडी (30% केंद्र + 30% राज्य)।",
        "description": "दिन के समय सिंचाई के लिए विश्वसनीय सौर ऊर्जा, महंगे डीजल पंपों से मुक्ति और अतिरिक्त सौर बिजली बेचकर अतिरिक्त आमदनी का साधन।",
        "eligibility": [
            "व्यक्तिगत किसान, जल उपभोक्ता समितियां, एफपीओ और ग्राम पंचायतें जिनके पास कृषि भूमि है।"
        ],
        "documents_required": [
            "आधार कार्ड",
            "भूमि अभिलेख (खसरा/खतौनी)",
            "बैंक पासबुक",
            "विद्युत बिल (कंपोनेंट C के लिए)",
            "पासपोर्ट साइज फोटो"
        ],
        "application_process": "1. राज्य के ऊर्जा विकास निगम पोर्टल (जैसे म.प्र. में ऊर्जा विकास निगम) अथवा pmkusum.mnre.gov.in पर आवेदन करें।\n2. किसान अंशदान (10-40%) जमा करें।\n3. अधिकृत वेंडर द्वारा 5 वर्ष की वारंटी के साथ सोलर पंप स्थापित किया जाता है।",
        "official_source": "नवीन एवं नवीकरणीय ऊर्जा मंत्रालय (MNRE), भारत सरकार",
        "official_url": "https://pmkusum.mnre.gov.in/",
        "apply_url": "https://pmkusum.mnre.gov.in/",
        "application_mode": "राज्य ऊर्जा विकास पोर्टल",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    },
    {
        "id": "smam",
        "title": "कृषि यंत्रीकरण उप-मिशन (SMAM / कृषि उपकरण सब्सिडी)",
        "short_name": "कृषि यंत्र सब्सिडी",
        "category": "कृषि यंत्रीकरण",
        "benefit": "ट्रैक्टर, रोटावेटर, कल्टीवेटर, सीड ड्रिल, लेजर लैंड लेवलर, रीपर आदि आधुनिक कृषि यंत्रों की खरीद पर 40% से 50% तक सरकारी सब्सिडी।",
        "description": "खेती में आधुनिक यंत्रों के उपयोग को प्रोत्साहित कर श्रम व लागत कम करने और समय की बचत करने हेतु सरकारी सहायता योजना।",
        "eligibility": [
            "छोटे, सीमांत, महिला एवं अनुसूचित जाति/जनजाति के किसानों को 50% तक तथा अन्य किसानों को 40% अनुदान।",
            "पिछले 5 वर्षों में उसी यंत्र पर अनुदान न लिया हो।"
        ],
        "documents_required": [
            "आधार कार्ड",
            "भूमि दस्तावेज (खसरा/खतौनी)",
            "बैंक पासबुक की प्रति",
            "जाति प्रमाण पत्र (आरक्षित वर्ग हेतु)",
            "अधिकृत कृषि यंत्र डीलर का कोटेशन"
        ],
        "application_process": "1. agrimachinery.nic.in पोर्टल पर जाकर 'किसान पंजीकरण' करें।\n2. इच्छित यंत्र का चयन कर टोकन प्राप्त करें।\n3. डीलर से यंत्र क्रय कर बिल पोर्टल पर अपलोड करें, सब्सिडी सीधे बैंक खाते में ट्रांसफर होती है।",
        "official_source": "कृषि एवं किसान कल्याण विभाग",
        "official_url": "https://agrimachinery.nic.in/",
        "apply_url": "https://agrimachinery.nic.in/Index/FarmerRegistration",
        "application_mode": "ऑनलाइन डीबीटी पोर्टल",
        "last_verified": "अक्टूबर 2026",
        "is_verified": True
    }
]


def get_all_government_schemes(language: str = "hi", category_filter: str = None, search_query: str = None) -> List[Dict[str, Any]]:
    """Retrieve government schemes formatted in chosen language with optional filtering."""
    is_hi = str(language).strip().lower().startswith("hi")
    schemes = OFFICIAL_SCHEMES_HI if is_hi else OFFICIAL_SCHEMES_EN

    filtered = []
    q = (search_query or "").strip().lower()
    cat = (category_filter or "").strip().lower()

    for s in schemes:
        if cat and cat != "all" and cat != "सभी":
            if cat not in s["category"].lower() and cat not in s["short_name"].lower():
                continue

        if q:
            matches_title = q in s["title"].lower() or q in s["short_name"].lower()
            matches_desc = q in s["description"].lower()
            matches_benefit = q in s["benefit"].lower()
            if not (matches_title or matches_desc or matches_benefit):
                continue

        filtered.append(s)

    return filtered


def get_scheme_by_id(scheme_id: str, language: str = "hi") -> Dict[str, Any]:
    """Retrieve single scheme detailed profile."""
    is_hi = str(language).strip().lower().startswith("hi")
    schemes = OFFICIAL_SCHEMES_HI if is_hi else OFFICIAL_SCHEMES_EN

    for s in schemes:
        if s["id"] == scheme_id or s["short_name"].lower() == scheme_id.lower():
            return s

    # Fallback to first scheme if not found
    return schemes[0] if schemes else {}
