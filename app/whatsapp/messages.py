"""All user-facing text, in 5 languages. Edit wording HERE, not in the logic.
NOTE: Pidgin/Yoruba/Hausa/Igbo texts are a first draft: have a native speaker review them before launch.
Field labels (Product, Manufacturer...) stay in English on purpose: short and widely understood."""
from ..core.engine import CheckResult, Verdict
from ..core.parsing import format_nafdac

LANG_NAMES = {"en": "English", "pcm": "Pidgin", "yo": "Yorùbá", "ha": "Hausa", "ig": "Igbo"}
LANG_CHOICES = {"1": "en", "2": "pcm", "3": "yo", "4": "ha", "5": "ig"}

LANG_MENU = (
    "Welcome to NAFDAC Checker 🇳🇬\n"
    "Choose language / Yan harshe / Yan asụsụ:\n"
    "1 English\n2 Pidgin\n3 Yorùbá\n4 Hausa\n5 Igbo\n\n"
    "ℹ️ Independent checker. We are NOT NAFDAC."
)

TEXT = {
"en": {
 "menu": "What would you like to do?\n1️⃣ Check a product\n2️⃣ Report a fake\n3️⃣ Help\n\nReply 1, 2 or 3. Send LANG to change language.",
 "ask_check": "Send ONE of these:\n• NAFDAC number, e.g. A4-1001\n• Product name | Manufacturer\n• Add batch and expiry if you have them: BATCH 123 EXP 12/2026\n\nNo NAFDAC number on the pack? Reply NONE.\nSend MENU to go back.",
 "help": "How it works: send a NAFDAC number or product name and we check it against our database, free, in under a minute. Barcode is NOT needed. We are not NAFDAC. Reply MENU to start.",
 "report_soon": "Fake-product reporting is coming very soon. For now, please report to NAFDAC directly. Reply MENU to go back.",
 "photo_later": "Photo checking is coming soon. For now please type the NAFDAC number from the pack.",
 "rate_limited": "You have reached the limit of 20 checks this hour. Please try again later.",
 "error": "Sorry, something went wrong. Please try again.",
 "did_you_mean": "Did you mean", "closest": "Closest match", "record": "Our record",
 "next_hint": "Send another product to check, or MENU.",
 "disclaimer": "ℹ️ We are an independent checker using public data. We are NOT NAFDAC. This is a check against our database, not official NAFDAC confirmation. Checking is free.",
 "v_VERIFIED": "✅ VERIFIED\nThis product matches a record in our database. Still check the pack: seal not broken, print clear, expiry date and batch number present.",
 "v_NOT_FOUND": "❌ NOT FOUND\nWe found no record for this. It may be a typing mistake, an unregistered product, a product not yet in our database, or a fake. If anything looks suspicious, do not use it. Reply 2 to report it.",
 "v_EXPIRED": "⛔ EXPIRED\nThis product is registered but this batch is past its expiry date. Do NOT use it. Return it to the seller.",
 "v_RECALLED": "🚨 RECALLED\nThis product or batch has been recalled. Do NOT use it. Stop selling or using it and report it (reply 2).",
 "v_SUSPICIOUS": "⚠️ SUSPICIOUS\nThe details do not add up (for example the name and manufacturer do not match our record, or there is no NAFDAC number on the pack). Be careful. Do not use it until it is checked. Reply 2 to report; our team will review.",
 "v_NEED_MORE_INFO": "❓ NEED MORE INFO\nWe cannot be sure from what you sent. Please send the NAFDAC number typed from the pack (or a clearer photo), or product name | manufacturer.",
},
"pcm": {
 "menu": "Wetin you wan do?\n1️⃣ Check product\n2️⃣ Report fake product\n3️⃣ Help\n\nReply 1, 2 or 3. Send LANG make you change language.",
 "ask_check": "Send ONE of dem:\n• NAFDAC number, like A4-1001\n• Product name | Manufacturer\n• Add batch and expiry if you get: BATCH 123 EXP 12/2026\n\nNo NAFDAC number dey di pack? Reply NONE.\nSend MENU make you go back.",
 "help": "How e dey work: send NAFDAC number or product name, we go check am for our database, free, under one minute. You no need barcode. We no be NAFDAC. Reply MENU to start.",
 "report_soon": "Fake product report dey come soon. For now, abeg report am to NAFDAC directly. Reply MENU make you go back.",
 "photo_later": "Photo check dey come soon. For now, abeg type di NAFDAC number wey dey di pack.",
 "rate_limited": "You don reach 20 checks for dis hour. Abeg try again later.",
 "error": "Sorry, wahala happen. Abeg try again.",
 "did_you_mean": "You mean", "closest": "Di one wey near pass", "record": "Our record",
 "next_hint": "Send another product wey you wan check, or MENU.",
 "disclaimer": "ℹ️ We be independent checker wey dey use public data. We NO be NAFDAC. Dis na check for our database, e no be official NAFDAC confirmation. Checking na free.",
 "v_VERIFIED": "✅ E DEY (VERIFIED)\nDis product match one record for our database. Still look di pack well: make sure seal no open, print clear, and expiry date and batch number dey.",
 "v_NOT_FOUND": "❌ NO DEY FOR RECORD (NOT FOUND)\nWe no see record for dis one. E fit be say you type am wrong, di product no register, e never enter our database, or e be fake. If anything dey look strange, no use am. Reply 2 make you report am.",
 "v_EXPIRED": "⛔ E DON EXPIRE\nDis product dey registered but dis batch don pass expiry date. NO use am. Carry am go back to di seller.",
 "v_RECALLED": "🚨 DEM DON CALL AM BACK (RECALLED)\nDem don recall dis product or batch. NO use am. Stop to sell or use am and report am (reply 2).",
 "v_SUSPICIOUS": "⚠️ E DEY SMELL (SUSPICIOUS)\nDi details no match well (like say name and manufacturer no tally with our record, or NAFDAC number no dey for pack). Be careful. No use am until dem check am well. Reply 2 to report; our team go look am.",
 "v_NEED_MORE_INFO": "❓ WE NEED MORE INFO\nWetin you send no clear enough. Abeg type di NAFDAC number wey dey di pack (or send better photo), or write product name | manufacturer.",
},
"yo": {
 "menu": "Kí lo fẹ́ ṣe?\n1️⃣ Ṣàyẹ̀wò ọjà\n2️⃣ Ròyìn ọjà ayédèrú\n3️⃣ Ìrànlọ́wọ́\n\nFèsì 1, 2 tàbí 3. Fi LANG ránṣẹ́ láti yí èdè padà.",
 "ask_check": "Fi ọ̀kan nínú wọ̀nyí ránṣẹ́:\n• Nọ́ńbà NAFDAC, bíi A4-1001\n• Orúkọ ọjà | Olùṣe\n• Fi batch àti ọjọ́ ìparí kún un tí o bá ní: BATCH 123 EXP 12/2026\n\nKò sí nọ́ńbà NAFDAC lórí páàkì? Fèsì NONE.\nFi MENU ránṣẹ́ láti padà.",
 "help": "Bí ó ṣe ń ṣiṣẹ́: fi nọ́ńbà NAFDAC tàbí orúkọ ọjà ránṣẹ́, a ó ṣàyẹ̀wò rẹ̀ nínú ibi ìpamọ́ ìròyìn wa, lọ́fẹ̀ẹ́, láàárín ìṣẹ́jú kan. Kò ṣe pàtàkì láti ní barcode. A kì í ṣe NAFDAC. Fèsì MENU láti bẹ̀rẹ̀.",
 "report_soon": "Ìròyìn ọjà ayédèrú ń bọ̀ láìpẹ́. Fún ìsinsìnyí, jọ̀wọ́ ròyìn fún NAFDAC taara. Fèsì MENU láti padà.",
 "photo_later": "Àyẹ̀wò fọ́tò ń bọ̀ láìpẹ́. Fún ìsinsìnyí, jọ̀wọ́ tẹ nọ́ńbà NAFDAC tó wà lórí páàkì.",
 "rate_limited": "O ti dé ààlà ìṣàyẹ̀wò 20 ní wákàtí yìí. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i lẹ́yìn náà.",
 "error": "Má bínú, àṣìṣe kan ṣẹlẹ̀. Jọ̀wọ́ gbìyànjú lẹ́ẹ̀kan sí i.",
 "did_you_mean": "Ṣé o fẹ́ sọ", "closest": "Èyí tó súnmọ́ jùlọ", "record": "Àkọsílẹ̀ wa",
 "next_hint": "Fi ọjà mìíràn ránṣẹ́ láti ṣàyẹ̀wò, tàbí MENU.",
 "disclaimer": "ℹ️ Olùṣàyẹ̀wò aláìdásí tọ̀túntòsì ni wá tó ń lo ìròyìn gbogbo ènìyàn. A KÒ jẹ́ NAFDAC. Ṣíṣàyẹ̀wò yìí wà lára ibi ìpamọ́ ìròyìn wa, kì í ṣe ìmúdájú NAFDAC. Ọ̀fẹ́ ni ṣíṣàyẹ̀wò.",
 "v_VERIFIED": "✅ A RÍ I (VERIFIED)\nỌjà yìí bá àkọsílẹ̀ kan mu nínú ibi ìpamọ́ ìròyìn wa. Ṣì ṣàyẹ̀wò páàkì náà dáadáa: kí èdìdì má ṣí, kí ìkọ̀wé hàn kedere, kí ọjọ́ ìparí àti nọ́ńbà batch wà níbẹ̀.",
 "v_NOT_FOUND": "❌ A KÒ RÍ I (NOT FOUND)\nA kò rí àkọsílẹ̀ fún èyí. Ó lè jẹ́ pé a kọ nọ́ńbà náà ní àṣìṣe, ọjà náà kò forúkọ sílẹ̀, kò tíì dé ibi ìpamọ́ ìròyìn wa, tàbí ayédèrú ni. Tí nǹkan bá dà bí ohun tí kò tọ́, má lò ó. Fèsì 2 láti ròyìn rẹ̀.",
 "v_EXPIRED": "⛔ Ó TI KÚ (EXPIRED)\nỌjà yìí ti forúkọ sílẹ̀ ṣùgbọ́n ọjọ́ ìparí batch yìí ti kọjá. MÁ ṢE lò ó. Dá a padà fún olùtajà.",
 "v_RECALLED": "🚨 WỌ́N TI PE É PADÀ (RECALLED)\nWọ́n ti pe ọjà tàbí batch yìí padà. MÁ ṢE lò ó. Dúró títà tàbí lílò rẹ̀, kí o sì ròyìn (fèsì 2).",
 "v_SUSPICIOUS": "⚠️ Ó DÁNI LÓJÚ (SUSPICIOUS)\nÀwọn àlàyé kò bára mu (fún àpẹẹrẹ orúkọ àti olùṣe kò bá àkọsílẹ̀ wa mu, tàbí kò sí nọ́ńbà NAFDAC lórí páàkì). Ṣọ́ra. Má lò ó títí a ó fi ṣàyẹ̀wò rẹ̀. Fèsì 2 láti ròyìn; ẹgbẹ́ wa yóò ṣàyẹ̀wò.",
 "v_NEED_MORE_INFO": "❓ À NÍLÒ ÀLÀYÉ DIẸ̀ SÍI\nA kò lè mọ̀ dáadáa látinú ohun tí o fi ránṣẹ́. Jọ̀wọ́ tẹ nọ́ńbà NAFDAC láti ara páàkì (tàbí fọ́tò tó mọ́ gaara), tàbí orúkọ ọjà | olùṣe.",
},
"ha": {
 "menu": "Me kake so ka yi?\n1️⃣ Duba samfur\n2️⃣ Kai rahoton jabu\n3️⃣ Taimako\n\nAmsa 1, 2 ko 3. Aika LANG don canza harshe.",
 "ask_check": "Aika ɗaya daga cikin waɗannan:\n• Lambar NAFDAC, misali A4-1001\n• Sunan samfur | Masana'anta\n• Ƙara batch da ranar karewa idan kana da su: BATCH 123 EXP 12/2026\n\nBabu lambar NAFDAC a kunshin? Amsa NONE.\nAika MENU don komawa.",
 "help": "Yadda yake aiki: aika lambar NAFDAC ko sunan samfur, za mu duba a bayanan mu, kyauta, cikin ƙasa da minti ɗaya. Ba sai da barcode ba. Mu ba NAFDAC ba ne. Amsa MENU don farawa.",
 "report_soon": "Rahoton samfur na jabu yana zuwa nan ba da daɗewa ba. Yanzu, da fatan ka kai rahoto ga NAFDAC kai tsaye. Amsa MENU don komawa.",
 "photo_later": "Duba hoto yana zuwa nan ba da daɗewa ba. Yanzu, da fatan ka rubuta lambar NAFDAC da ke kan kunshin.",
 "rate_limited": "Ka kai iyakar bincike 20 a wannan sa'a. Da fatan ka sake gwadawa daga baya.",
 "error": "Yi hakuri, an samu matsala. Da fatan ka sake gwadawa.",
 "did_you_mean": "Ko kana nufin", "closest": "Mafi kusa", "record": "Rikodin mu",
 "next_hint": "Aika wani samfur don dubawa, ko MENU.",
 "disclaimer": "ℹ️ Mu masu bincike ne masu zaman kansu da ke amfani da bayanan jama'a. Mu BA NAFDAC ba ne. Wannan bincike ne a bayanan mu, ba tabbacin NAFDAC na hukuma ba. Bincike kyauta ne.",
 "v_VERIFIED": "✅ AN TABBATAR (VERIFIED)\nWannan samfurin ya yi daidai da wani rikodi a bayanan mu. Duk da haka, duba kunshin da kyau: hatimi kada ya zama a buɗe, rubutu ya fito fili, kuma ranar karewa da lambar batch su kasance.",
 "v_NOT_FOUND": "❌ BA A SAMU BA (NOT FOUND)\nBa mu sami rikodi ba. Wataƙila an yi kuskure wajen rubuta lambar, samfurin ba a yi masa rajista ba, bai riga ya shiga bayanan mu ba, ko kuma jabu ne. Idan akwai abin da ke ba da shakku, kada ka yi amfani da shi. Aika 2 don kai rahoto.",
 "v_EXPIRED": "⛔ YA ƘARE (EXPIRED)\nAn yi wa samfurin rajista amma wannan batch ya wuce ranar karewa. KADA ka yi amfani da shi. Mayar da shi ga mai sayarwa.",
 "v_RECALLED": "🚨 AN JANYE SHI (RECALLED)\nAn janye wannan samfur ko batch. KADA ka yi amfani da shi. Daina sayarwa ko amfani da shi, kuma ka kai rahoto (aika 2).",
 "v_SUSPICIOUS": "⚠️ MAI SHAKKA (SUSPICIOUS)\nBayanan ba su dace ba (misali suna da masana'anta ba su yi daidai da rikodin mu ba, ko babu lambar NAFDAC a kunshin). Ka yi hankali. Kada ka yi amfani da shi har sai an duba. Aika 2 don kai rahoto; ƙungiyarmu za ta duba.",
 "v_NEED_MORE_INFO": "❓ ANA BUKATAR ƘARIN BAYANI\nBa za mu iya tabbatarwa daga abin da ka aiko ba. Da fatan ka rubuta lambar NAFDAC daga kunshin (ko aiko hoto mai haske), ko sunan samfur | masana'anta.",
},
"ig": {
 "menu": "Gịnị ka ịchọrọ ime?\n1️⃣ Lelee ngwaahịa\n2️⃣ Kọọ ngwaahịa ụgha\n3️⃣ Enyemaka\n\nZaghachi 1, 2 ma ọ bụ 3. Zipu LANG ka ị gbanwee asụsụ.",
 "ask_check": "Zipu otu n'ime ndị a:\n• Nọmba NAFDAC, dịka A4-1001\n• Aha ngwaahịa | Onye mepụtara\n• Tinye batch na ụbọchị ngwụcha ma ị nwere ha: BATCH 123 EXP 12/2026\n\nEnweghị nọmba NAFDAC na ngwugwu? Zaghachi NONE.\nZipu MENU ka ị laghachi.",
 "help": "Otu o si arụ ọrụ: zipu nọmba NAFDAC ma ọ bụ aha ngwaahịa, anyị ga-elele ya na data anyị, n'efu, n'ime nkeji erughị otu. Ọ dịghị mkpa barcode. Anyị abụghị NAFDAC. Zaghachi MENU ka ịmalite.",
 "report_soon": "Ịkọ ngwaahịa ụgha na-abịa n'oge na-adịghị anya. Ugbu a, biko kọọrọ NAFDAC ozugbo. Zaghachi MENU ka ị laghachi.",
 "photo_later": "Nyocha foto na-abịa n'oge na-adịghị anya. Ugbu a, biko dee nọmba NAFDAC dị na ngwugwu.",
 "rate_limited": "Ị ruola oke nyocha 20 n'otu awa a. Biko nwaa ọzọ mgbe e mesịrị.",
 "error": "Ndo, nsogbu mere. Biko nwaa ọzọ.",
 "did_you_mean": "Ị chọrọ ịsị", "closest": "Nke kacha nso", "record": "Ndekọ anyị",
 "next_hint": "Zipu ngwaahịa ọzọ ka e lelee, ma ọ bụ MENU.",
 "disclaimer": "ℹ️ Anyị bụ ndị nyocha nọọrọ onwe ha na-eji data ọha. Anyị abụghị NAFDAC. Nke a bụ nyocha na data anyị, ọ bụghị nkwenye NAFDAC. Nyocha bụ n'efu.",
 "v_VERIFIED": "✅ A HỤRỤ YA (VERIFIED)\nNgwaahịa a kwekọrọ na ndekọ dị na data anyị. Ma lee ngwugwu ahụ nke ọma: akara mmechi ya ghara imeghe, ihe e dere pụta ìhè, ụbọchị ngwụcha na nọmba batch dịkwa.",
 "v_NOT_FOUND": "❌ AHỤGHỊ YA (NOT FOUND)\nAnyị ahụghị ndekọ maka ya. Ọ nwere ike ịbụ na edeghị nọmba ahụ nke ọma, e debanyeghị aha ngwaahịa ahụ, ọ bụghị na data anyị ugbu a, ma ọ bụ ọ bụ ngwaahịa ụgha. Ọ bụrụ na ihe ọ bụla adịghị mma, ejila ya. Zaghachi 2 ka ị kọọ ya.",
 "v_EXPIRED": "⛔ O GWUGHỊ (EXPIRED)\nNgwaahịa a debanyere aha mana batch a agafeela ụbọchị ngwụcha ya. EJILA ya. Laghachi ya nye onye na-ere ya.",
 "v_RECALLED": "🚨 A KPỌLATA YA (RECALLED)\nA kpọlatala ngwaahịa ma ọ bụ batch a. EJILA ya. Kwụsị ire ma ọ bụ iji ya, kọọ ya (zaghachi 2).",
 "v_SUSPICIOUS": "⚠️ NA-EME DỊ MGBAGWOJU ANYA (SUSPICIOUS)\nIhe ndị a adịghị ekwekọ (dịka aha na onye mepụtara adịghị ekwekọ na ndekọ anyị, ma ọ bụ enweghị nọmba NAFDAC na ngwugwu). Jiri nlezianya. Ejila ya ruo mgbe a nyochara ya. Zaghachi 2 ka ị kọọ; otu anyị ga-enyocha ya.",
 "v_NEED_MORE_INFO": "❓ ANYỊ CHỌRỌ ỊMA KARỊA\nAnyị enweghị ike ịmara site n'ihe i zigara. Biko dee nọmba NAFDAC site na ngwugwu (ma ọ bụ zite foto doro anya), ma ọ bụ aha ngwaahịa | onye mepụtara.",
},
}


def t(lang: str, key: str) -> str:
    return TEXT.get(lang, TEXT["en"])[key]


def _product_lines(p) -> list[str]:
    lines = [
        f"📦 Product: {p.product_name}",
        f"🏭 Manufacturer: {p.manufacturer}",
        f"🗂 Category: {p.category}",
        f"🔢 NAFDAC No: {p.nafdac_number}",
    ]
    if p.expiry_info:
        lines.append(f"📅 Registration: {p.expiry_info}")
    if p.is_sample:
        lines.append("⚠️ SAMPLE / TEST DATA, not a real NAFDAC record.")
    return lines


def render_verdict(lang: str, result: CheckResult) -> str:
    """Build the full verdict card: headline + advice + details + disclaimer."""
    parts = [t(lang, f"v_{result.verdict.value}")]
    p = result.product
    if p and result.verdict in (Verdict.VERIFIED, Verdict.EXPIRED, Verdict.RECALLED, Verdict.SUSPICIOUS):
        head = "" if result.verdict == Verdict.VERIFIED else f"{t(lang, 'record')}:\n"
        parts.append(head + "\n".join(_product_lines(p)))
    if result.verdict == Verdict.NOT_FOUND and result.suggestions:
        s = "\n".join(f"→ {x.nafdac_number}  {x.product_name}" for x in result.suggestions)
        parts.append(f"{t(lang, 'did_you_mean')}:\n{s}")
    if result.verdict == Verdict.NEED_MORE_INFO and result.suggestions:
        s = "\n".join(f"→ {x.product_name} ({x.manufacturer}) {x.nafdac_number}" for x in result.suggestions)
        parts.append(f"{t(lang, 'closest')}:\n{s}")
    parts.append(t(lang, "disclaimer"))
    parts.append(t(lang, "next_hint"))
    return "\n\n".join(parts)
