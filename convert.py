import pdfreader
from pdfreader import PDFDocument, SimplePDFViewer
import os
import re
import json

def open_pdf(path):
    fd = open(path, "rb")
    viewer = SimplePDFViewer(fd)
    doc = PDFDocument(fd)
    no_of_pages = len([p for p in doc.pages()])
    doc_text = ""
    for i in range(no_of_pages):
        viewer.navigate(i + 1)
        viewer.render()
        doc_text += "".join(viewer.canvas.strings)
    return doc_text, no_of_pages

def correct_encoding(text):
    re_grp_1 = [
        (r"(\u2013)", "-"),
        (r"õ", "ı"),
        (r"Đ", "İ"),
        (r"_{2,}", " "),
        (r"\-{2,}", " "),
        (r"(\xa0)", " "),
        (r"(\u2010)", "-"),
        ("Türkiye Cumhuriyet Merkez Bankası İdare Merkezi İstiklal Caddesi 10 06100 Ulus / Ankara 0312 507 50 00 www.tcmb.gov.tr", ""),
        ("Türkiye Cumhuriyet Merkez Bankası İdare Merkezi Anafartalar Mah. İstiklal Cad. No:10 06050 Ulus Altındağ Ankara 0312 507 50 00 www.tcmb.gov.tr", ""),
        ("Türkiye Cumhuriyet Merkez Bankası İdare Merkezi Hacı Bayram Mah. İstiklal Cad. No:10 06050 Ulus Altındağ Ankara 0312 507 50 00 www.tcmb.gov.tr", ""),
        ("Türkiye Cumhuriyet Merkez Bankası İdare Merkezi Hacı Bayram Mah. İstiklal Cad. No:10 06050  Ulus Altındağ Ankara 0312 507 50 00  www.tcmb.gov.tr", "")
    ]

    re_grp_2 = [
        (r"([a-zğüşıöçâîû])\x01|\x01([a-zğüşıöçâîû])", "\\1ş\\2"),
        (r"([A-ZĞÜŞİÖÇÂÎÛ])\x01|\x01([A-ZĞÜŞİÖÇÂÎÛ])", "\\1İ\\2"),
        (r"(\x02)", "ğ"),
        (r"(\x03)", "İ")
    ]

    re_grp_3 = [
        (r"(\x01)", "Ş"),
        (r"([a-zğüşıöçâîû])\x02|\x02([a-zğüşıöçâîû])", "\\1ş\\2"),
        (r"([A-ZĞÜŞİÖÇÂÎÛ])\x02|\x02([A-ZĞÜŞİÖÇÂÎÛ])", "\\1İ\\2"),
        (r"(\x03)", "İ"),
        (r"(\x04)", "ğ")
    ]

    re_grp_4 = [
        (r"([a-zğüşıöçâîû])\x01|\x01([a-zğüşıöçâîû])", "\\1ğ\\2"),
        (r"([A-ZĞÜŞİÖÇÂÎÛ])\x01|\x01([A-ZĞÜŞİÖÇÂÎÛ])", "\\1İ\\2"),
        (r"(\x02)", "ş"),
        (r"(\x03)", "İ")
    ]

    re_grp_5 = [
        (r"([a-zğüşıöçâîû])\x01|\x01([a-zğüşıöçâîû])", "\\1ş\\2"),
        (r"([A-ZĞÜŞİÖÇÂÎÛ])\x01|\x01([A-ZĞÜŞİÖÇÂÎÛ])", "\\1İ\\2"),
        (r"(\x02)", "İ"),
        (r"(\x03)", "ğ")
    ]

    re_grp_6 = [
        (r"(\s)\x01", "\\1Ş"),
        (r"([a-zğüşıöçâîû])\x01|\x01([a-zğüşıöçâîû])", "\\1ş\\2"),
        (r"([a-zğüşıöçâîû])\x02|\x02([a-zğüşıöçâîû])", "\\1ş\\2"),
        (r"([A-ZĞÜŞİÖÇÂÎÛ])\x02|\x02([A-ZĞÜŞİÖÇÂÎÛ])", "\\1İ\\2"),
        (r"(\x03)", "ğ"),
        (r"(\x04)", "İ")
    ]

    for regex in re_grp_1:
        text = re.sub(regex[0], regex[1], text)

    if len(re.findall(r"(\x04)", text)) > 0:
        if text.startswith("Sayı: 2008-07"):
            for regex in re_grp_6:
                text = re.sub(regex[0], regex[1], text)
        else:
            for regex in re_grp_3:
                text = re.sub(regex[0], regex[1], text)
    else:
        if text.startswith(" 1Sayı:2007-32"):
            for regex in re_grp_4:
                text = re.sub(regex[0], regex[1], text)
        elif text.startswith("Sayı:2007-24") or text.startswith("Sayı:2007-08"):
            for regex in re_grp_5:
                text = re.sub(regex[0], regex[1], text)
        else:
            for regex in re_grp_2:
                text = re.sub(regex[0], regex[1], text)

    return text

def discard_metadata(text, doc_name=None):
    regex3 = r"((Sayı|No)\s?:?\s?(\d{4}\s?\-\s?)?\d{1,2})"
    regex4 = r"((Para Politikası Kurulu Toplantı Özeti)|(PARA POLİTİKASI KURULU (TOPLANTI|DEĞERLENDİRMELERİ) ÖZETİ))"
    regex5 = r"(Toplantı Tarih(ler)?i: (\d{1,2} ve )?\d{1,2} [a-zA-ZşığüŞİĞÜ]{4,7} \d{4})"
    regex6 = r"(\d{1,2}\s{,2}[a-zA-ZşığüŞİĞÜ]{4,7}\s\d{4})"
    regex7 = r"BASIN DUYURUSU"

    res_0 = re.findall(regex3, text)
    res_1 = re.findall(regex4, text)
    res_2 = re.findall(regex5, text)
    res_4 = re.findall(regex7, text)
    # print(res_0)
    # print(res_1)
    # print(res_2)
    # print(res_4)

    text = re.sub(regex3, " ", text)
    text = re.sub(regex4, " ", text)
    text = re.sub(regex5, " ", text)

    res_3 = re.findall(regex6, text)
    # print(res_3[0])
    
    text = re.sub(regex6, " ", text, 1)
    text = re.sub(regex7, " ", text)

    if len(res_0) > 0:
        number = res_0[0][0].split(":")[1].replace(" ", "") if ":" in res_0[0][0] else res_0[0][0].replace("Sayı", "").replace(" ", "")
    else:
        number = doc_name.split(".")[0].replace("DUY", "")
    date = " ".join([r for r in res_2[0][0].split(":")[1].strip().split(" ") if r != ""])
    published = " ".join([r for r in res_3[0].strip().split(" ") if r != ""]) if len(res_3) > 0 else ""
    
    return text, (number, date, published)

def discard_page_numbers(text, no_of_pages, doc_name=None):
    re_1 = r"(^\s?1)"
    re_2 = r"((^\s?1)|(\s([2-9]|[1-9][0-9]))\s\s)"
    re_3 = r"((^\s?1\s\s)|((\s([2-9]|[1-9][0-9])\s\s)|(\s\s([2-9]|[1-9][0-9])\s)))"
    re_4 = r"((\s([1-9]|[1-9][0-9])\s\s)|(\s\s([2-9]|[1-9][0-9])\s)|(\s" + str(no_of_pages) + "\s$))"
    result = re.findall(re_2, text)
    test_numbers = "".join([r[0].strip()for r in result])
    test_truth = "".join([str(i + 1) for i in range(no_of_pages)])
    # print(result)
    if test_truth != test_numbers:
        result = re.findall(re_3, text)
        test_numbers = "".join([r[0].strip()for r in result])
        re_2 = re_3
        # print(result)
    if test_truth != test_numbers:
        result = re.findall(re_4, text)
        test_numbers = "".join([r[0].strip()for r in result])
        re_2 = re_4
        # print(result)

    if test_truth == test_numbers:
        # print(doc_name, "got page numbers, matched")
        text = re.sub(re_2, REGEX_0, text)
    elif len(re.findall(re_1, text)) > 0:
        # print(doc_name, "got page numbers, not matched")
        text = re.sub(r"(^\s?1)", "", text)
        for page in range(1, no_of_pages):
            res_seq = re.findall("(  %s[^\.])" % str(page + 1), text)
            # print(res_seq)
            text = re.sub("(  %s[^\.])" % str(page + 1), REGEX_0, text, 1)

    # print(doc_name, test_truth, test_numbers)

    return text

def discard_references(text):
    re_1 = r"(([a-zğüşıöçâîû])(\.\d|\d\.)\s)"
    res_1 = re.findall(re_1, text)
    # print(res_1)
    text = re.sub(re_1, "\\2. ", text)

    # discard footnotes

    if len(res_1) > 0:    
        re_0 = r"(\s{2,}\d\s[^;]+(?=" + REGEX_0.strip() + "))"
        res_0 = re.findall(re_0, text)
        # print(res_0)
        text = re.sub(re_0, "", text)

        # re_0 = r"((\s){2,}[1-9][0-9]?\s[a-zA-Z0-9ğüşıöçĞÜŞİÖÇ:,\s\.“”]{50,}(\s([2-9]|[1-9][0-9])\s\s))"
        # res_0 = re.findall(re_0, text)
        # print(res_0)
        # text = re.sub(re_0, "\\4", text)
    
    text = text.replace(REGEX_0.strip(), "")
    return text

def parse_document(text):
    regex1 = r"(\d{1,2}\.\s{1,2}(?=[A-ZĞÜŞİÖÇÂÎÛ\d]))"
    regex2 = r"((^|\.)\s+([A-ZĞÜŞİÖÇÂÎÛ\d][a-zğüşıöçâîû\d]+\s{1,2})+(?=[a-zğüşıöçâîû]))"
    regex3 = r"([a-zA-Z0-9ğüşıöçĞÜŞİÖÇÂâÎîÛû:,;\-\*\+%/'’’“”\"\(\)\s]{2,}(\.|:))"
    regex4 = r"(^(Toplantıya Katılan Kurul Üyeleri)([a-zA-Z0-9ğüşıöçĞÜŞİÖÇÂâÎîÛû,\s\[\]]+)(\.|(\([^\)]+\))))"
    res = re.findall(regex1, text)
    
    # print(res)

    topics = [] 
    
    if len(res) > 0:
        text = re.sub(regex1, REGEX_0 + "\\1", text)
        parts = text.split(REGEX_0)

        topic = re.sub(r"(^,)", "", re.sub(regex4, "", parts[0].strip())).strip()     # in case of DUY2009-48.pdf and DUY2018-06.pdf
        topic_items = []

        for i in range(1, len(parts)):
            p = parts[i]
            p = re.sub(regex1, "", p)
            res2 = re.findall(regex3, p)
            p = re.sub(regex3, "", p)
            # print(p)
            item_idx = int(res[i - 1].split(".")[0])
            item_text = " ".join([r[0].strip() for r in res2])
            item_text = re.sub(r"\s{2,}", " ", item_text)
            topic_items.append({"index": item_idx, "text": item_text})

            if p.strip() == "":
                if i == len(parts) - 1:
                    topics.append({"title": topic, "items": topic_items})
            else:
                topics.append({"title": topic, "items": topic_items})
                topic = p.strip()
                topic_items = []
            
            
    else:
        res2 = re.findall(regex2, text)
        # print(res2)
        temp1 = [re.sub(r"\s{2,}", " ", r[0].replace(".", "").strip()) for r in res2]
        temp2 = [" ".join(r.split(" ")[0:-1]) for r in temp1 if len(r.split(" ")) > 1]
        temp3 = []
        
        for r in temp2:
            r_p = r.split(" ")
            if len(r_p) % 2 == 1:
                temp3.append(r)
                continue
            no_dup = False
            for j in range(int(len(r_p)/2)):
                if r_p[j] != r_p[j + int(len(r_p)/2)]:
                    no_dup = True
                    break
            if no_dup:
                temp3.append(r)
                continue
            r_n = " ".join([r_p[j] for j in range(int(len(r_p)/2))])
            temp3.append(r_n)
            
        # print(len(temp3), temp3)

        for r in res2:
            simplified = re.sub(r"\s{2,}", " ", r[0].replace(".", "").strip())
            if len(simplified.split(" ")) > 1:
                text = re.sub(r[0], r[1] + REGEX_0 + simplified + " ", text, 1)
            
        parts = text.split(REGEX_0)
        # print(len(parts), parts)
        for i, r in enumerate(parts):
            if i == 0:
                continue
            topics.append({"title": temp3[i - 1], "items": [{"index": 0, "text": re.sub(r"\s{2,}", " ", re.sub(temp3[i - 1], " ", r, 1)).strip()}]})
        

    # print([t["title"] for t in topics])

    return topics

def specific_changes(text, reverse=False):
    changes = [
        ("Beklenti Anketi", "Beklenti anketi"),
        ("Riskler ve Para Politikası", "Riskler Ve Para Politikası"),
        ("İktisadi Yönelim Anketi", "İktisadi yönelim anketi"),
        ("Para Politikası Kurulu,", "Para Politikası Kurulu"),
        ("Para Politikası Kurulu 23 Şubat", "Para Politikası Kurulu, 23 Şubat"),
        ("M. İbrahim Turhan", "İbrahim Mustafa Turhan"),
        ("(Başkan)", "[Başkan]"),
        ("tutulmasınakarar", "tutulmasına karar"),
        ("Ocak-Nisan 2006 10.", "10. Ocak-Nisan 2006:"),
        ("Mayıs 2006 ve Sonrası 11.", "11. Mayıs 2006 ve Sonrası:"),
        ("Mehmet Yörükoğlu  Para Politikası", "Mehmet Yörükoğlu.  Para Politikası"),
        ("Mehmet Yörükoğlu      Enflasyon Gelişmeleri", "Mehmet Yörükoğlu.      Enflasyon Gelişmeleri"),
        ("İbrahim Mustafa Turhan Abdullah Yavaş", "İbrahim Mustafa Turhan, Abdullah Yavaş"),
        ("Mehmet Yörükoğlu Katılmayan", "Mehmet Yörükoğlu. Katılmayan"),
        ("Mehmet Yörükoğlu  Toplantıya", "Mehmet Yörükoğlu.  Toplantıya"),
        ("6. Özetle, enflasyonda Ağustos ayından itibaren düşüşün başlayacağı öngörülmekle birlikte, fiyatlama davranışları dikkatle takip edilmektedir", "6. Özetle, enflasyonda Ağustos ayından itibaren düşüşün başlayacağı öngörülmekle birlikte, fiyatlama davranışları dikkatle takip edilmektedir."),
        ("Yatırım eğiliminin düşük seviyelerde seyretmesi ve sanayi üretimindeki ılımlı artış eğilimi istihdam piyasasındaki iyileşmenin zaman alabileceğine işaret etmektedir", "Yatırım eğiliminin düşük seviyelerde seyretmesi ve sanayi üretimindeki ılımlı artış eğilimi istihdam piyasasındaki iyileşmenin zaman alabileceğine işaret etmektedir."),
        ("Toplantıya Katılan Kurul ÜyeleriToplantıya Katılan Kurul ÜyeleriToplantıya Katılan Kurul ÜyeleriToplantıya Katılan Kurul Üyeleri", "Toplantıya Katılan Kurul Üyeleri"),
        ("Bu çerçevede, yılın son çeyreğinde fiyat indirim kampanyaları ile beklenen ücret güncellemeleri kaynaklı öne çekilen talep güdüsünün talepteki dengelenmeyi zayıflattığı değerlendirilmektedir", "Bu çerçevede, yılın son çeyreğinde fiyat indirim kampanyaları ile beklenen ücret güncellemeleri kaynaklı öne çekilen talep güdüsünün talepteki dengelenmeyi zayıflattığı değerlendirilmektedir.")
    ]
    for ch in changes:
        text = text.replace(ch[0], ch[1]) if not reverse else text.replace(ch[1], ch[0])

    return text

def process_document(text, no_of_pages, doc_name):
    text = correct_encoding(text)
    text, meta = discard_metadata(text, doc_name)
    # print(meta)
    text = discard_page_numbers(text, no_of_pages, doc_name)
    text = discard_references(text)
    text = specific_changes(text)
    topics = parse_document(text)
    
    return {
        "number": meta[0],
        "date": meta[1],
        "published": meta[2],
        "topics": topics
    }

def process_brief(text, no_of_pages, doc_name=None):
    text = correct_encoding(text)
    text = specific_changes(text)
    
    # print(text)

    re_0 = r"((^\s?1)|(\s[2-9])\s\s)"
    result = re.findall(re_0, text)
    
    # print(no_of_pages, len(result), doc_name)

    text = re.sub(re_0, "", text)

    regex1 = "[Başkan]"
    regex3 = r"((Sayı|No)\s?:?\s?(\d{4}\s?\-\s?)?\d{1,2})"
    regex4 = r"((Para Politikası Kurulu Kararı)|(PARA POLİTİKASI KURULU KARARI))" 
    regex6 = r"(\d{1,2}\s{1,2}[a-zA-ZşığüŞİĞÜ]{4,7}\s\d{4})"
    regex7 = r"BASIN DUYURUSU"
    regex8 = r"((Toplantıya Katılan Kurul Üyeleri)([a-zA-Z0-9ğüşıöçĞÜŞİÖÇÂâÎîÛû,\s\[\]]+)(\.|(\([^\)]+\))))"
    regex9 = r"(^\([^\)]+\))"
    regex10 = r"(^((Toplantıya )?Katıla?mayan Kurul Üyesi:?)([a-zA-Z0-9ğüşıöçĞÜŞİÖÇÂâÎîÛû,\s\[\]]+)(\([^\)]+\)))"

    res = re.findall(regex8, text)
    # print(res)
    new_text = re.sub(regex8, REGEX_0 + "\\1", text)
    new_text_parts = new_text.split(REGEX_0)
    parsed = {
        "number": "",
        "text": "",
        "date": "",
        "governor": "",
        "board": []
    }
    ress_0 = re.findall(regex4, new_text_parts[0])
    # print(ress_0)
    new_text_parts[0] = re.sub(regex4, "", new_text_parts[0])

    ress_1 = re.findall(regex7, new_text_parts[0])
    # print(ress_1)
    new_text_parts[0] = re.sub(regex7, "", new_text_parts[0])

    if doc_name == "DUY2018-01.pdf":
        parsed["number"] = "2018-01"
        parsed["date"] = "18 Ocak 2018"
    elif doc_name == "DUY2018-10.pdf":
        parsed["number"] = "2018-10"
        parsed["date"] = "25 Nisan 2018"
    else:
        res_0_0 = re.findall(regex3, new_text_parts[0])
        if len(res_0_0) > 0:
            # print(res_0_0)
            parsed["number"] = res_0_0[0][0].split(":")[1].replace(" ", "") if ":" in res_0_0[0][0] else res_0_0[0][0].replace("Sayı", "").replace(" ", "")
            new_text_parts[0] = re.sub(regex3, "", new_text_parts[0])
        else:
            res_1_0 = re.findall(regex3, new_text_parts[1])
            # print(res_1_0)
            if len(res_1_0) > 0:
                parsed["number"] = res_1_0[0][0].split(":")[1].replace(" ", "") if ":" in res_1_0[0][0] else res_1_0[0][0].replace("Sayı", "").replace(" ", "")
                new_text_parts[1] = re.sub(regex3, "", new_text_parts[1])
                new_text_parts[1] = re.sub(regex6, "", new_text_parts[1])
            else:
                parsed["number"] = doc_name.split(".")[0].replace("DUY", "")
    

        res_0_1 = re.findall(regex6, new_text_parts[0])
        # print(res_0_1)
        parsed["date"] = " ".join([r for r in res_0_1[0].strip().split(" ") if r != ""])
    
    
    new_text_parts[1] = re.sub(regex8, "", new_text_parts[1])
    members = res[0][2]
    remainder = re.sub(r"(^\.)", "", re.sub(regex10, "", re.sub(regex9, "", new_text_parts[1].strip())))   # in case of karar/2010/1.pdf karar/2010/1.pdf karar/2010/2.pdf karar/2010/5.pdf
    parsed["text"] = re.sub(r"\s{2,}", " ", remainder).strip()
    parsed["governor"] = [m.replace(regex1, "").strip() for m in members.split(",") if regex1 in m][0]
    parsed["board"] = [m.strip() for m in members.split(",") if regex1 not in m]
    # print(parsed["governor"], parsed["board"])
    # print(parsed["text"])

    return parsed


REGEX_0 = " ;;;;; "   # simple placeholder
FOLDER_NAME = "ppk"
OUTPUT_FOLDER = "output"
PATH_EXT_0 = "karar"
PATH_EXT_1 = "özet"

brief_data = []
for path, dirs, files in os.walk(f"{FOLDER_NAME}/{PATH_EXT_0}"):
    for file in files:
        if not file.endswith(".pdf"):
            continue
        print("\n",file)
        doc_text, no_of_pages = open_pdf(os.path.join(path, file))
        processed_text = process_brief(doc_text, no_of_pages, file)
        brief_data.append(processed_text)

for path, dirs, files in os.walk(f"{FOLDER_NAME}/{PATH_EXT_1}"):
    for file in files:
        if not file.endswith(".pdf"):
            continue
        print("\n",file)
        doc_text, no_of_pages = open_pdf(os.path.join(path, file))
        processed_text = process_document(doc_text, no_of_pages, file)
        related_decision = [data for data in brief_data if data["date"].endswith(processed_text["date"]) or processed_text["date"].endswith(data["date"])][0]
        processed_text["decision"] = related_decision["number"]
        processed_text["governor"] = related_decision["governor"]
        processed_text["board"] = related_decision["board"]
        processed_text["abstract"] = related_decision["text"]

        # dump json
        output_path = path.replace(FOLDER_NAME, OUTPUT_FOLDER).replace(PATH_EXT_1, "")
        if not os.path.isdir(output_path):
            os.makedirs(output_path)
        with open(os.path.join(output_path, file.replace("pdf", "json")), "w", encoding="utf-8") as f:
            json.dump(processed_text, f, ensure_ascii=False, indent=4)

