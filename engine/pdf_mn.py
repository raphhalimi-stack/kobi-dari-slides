#!/usr/bin/env python3
"""PDF en mongol : 20 formats de reels pour Kobi (pour envoi KakaoTalk)."""
import os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Engine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = os.path.join(ROOT, "v2", "concepts")
TMP = os.path.join(ROOT, "v2", "concepts", "pdf_img"); os.makedirs(TMP, exist_ok=True)

F = [
 ("Цуглуулгын карт", "“Niacinamide #01” карт эргэж гарч ирнэ.", "Үзүүлэлт бүр (гэрэлтүүлэх, тос багасгах, улайлт намдаах) нэг өгүүлбэрээр дүүрнэ. Дараа нь картын “сул тал”: 10%-иас дээш бол арьсыг цочроож болно. Төгсгөл: “Дараагийн карт: Centella”.", "Цуглуулах сонирхол нь дараагийн ангийг үзэхийн тулд дагахад хүргэнэ. Апп-аар уншуулсан бүтээгдэхүүн бүр өөрийн карттай байж болно."),
 ("Микроскопоор", "Нүүрнээс арьсны дотор руу томруулж орно.", "Меланин (пигмент) дээш гарч толбо үүсгэнэ. Ниацинамид замыг нь хаана. Толбо хурдан бүдгэрнэ.", "“Харахад таатай шинжлэх ухаан”: хүмүүс эцсээ хүртэл үздэг тул үзэх хугацаа урт. Хийхэд арай удна."),
 ("Домог ба үнэн", "Улаан дэвсгэр дээр: “Never mix niacinamide with vitamin C”.", "2 секунд хүлээлгэнэ, дэлгэц ногоон болж үнэнийг 2 мөрөөр тайлбарлана. Нэг ангид 3 домог.", "Хүмүүсийн итгэдэг зүйлийг үгүйсгэхээр сэтгэгдэл, хуваалцалт их гардаг. Шинэ хүмүүст хүрэх хамгийн сайн загвар."),
 ("“+ юутай?”", "“Niacinamide + what?”", "Орц бүр “дин” дуутай жагсаалтад нэмэгдэж, тэмдэг авна. Сүүлийнх нь улбар шар: цорын ганц анхааруулга.", "Хадгалах (save) их: богино санамж хуудас шиг. Орц бүрт амархан давтана."),
 ("Үелэх систем", "Том химийн элементийн нүд: “Nc, Niacinamide, 01”.", "Нүд бүтэж, шинж чанар бүр асна. Дараа нь 29 хоосон нүдтэй бүх хүснэгт харагдана. Анги бүр нэг нүдийг бөглөнө.", "Цувралын хүчтэй өнгө төрх. Профайл дээрх нүүр зургууд нийлээд хүснэгт болно. Хүснэгтийг дуусгахын тулд хүмүүс эргэж ирнэ."),
 ("Мессеж", "Цэнхэр мессеж: “is niacinamide actually worth it??”", "Kobi-ийн хариунууд бичиж буй гурван цэг, мессежийн дуутай гарч ирнэ. Төгсгөлд хөгжилтэй дүгнэлт.", "Найзтайгаа чатлаж байгаа мэт. Хийхэд хурдан, DM-ээр их хуваалцагдана. Алгоритм үүнийг хамгийн их үнэлдэг."),
 ("Tier list", "Хоосон S, A, B, C жагсаалт.", "Орц бүрийг шалтгаантай нь зэрэглэлд байрлуулна. Төгсгөлд маргаантай байрлал.", "Санал зөрөхөөр сэтгэгдэл олширч, видео дээшилнэ. Анхаарах: энэ бол хувийн үзэл гэдгийг тодорхой хэлэх."),
 ("Супер баатрууд", "“Niacinamide is your skin's bodyguard”: костюмтай дүр.", "Гурван муу санаатан (Улайлт, Гялалзалт, Толбо) ирж, хамгаалагч нэг нэгээр нь зогсооно. Анги бүр шинэ баатар: Centella сувилагч, Retinol дасгалжуулагч, SPF бамбай.", "Зүйрлэл амархан тогтдог, дүрүүдийн ертөнц жинхэнэ цуврал болно. Баатрууд Матильдатай уулзаж болно."),
 ("Шошгыг томруулах", "Жинхэнэ орцын жагсаалт, дээгүүр нь шар тэмдэглэгч гүйнэ.", "Хуруу жагсаалтаар доош гүйж Niacinamide дээр зогсоно. Хувь нь томоор гарч ирнэ.", "Аппын гол үйлдлийг (шошго унших) яг харуулна. Хүлээлгийн жагсаалтад хамгийн их бүртгүүлэх загвар."),
 ("Асуулт хариулт", "Том асуулт: “Can you use niacinamide with vitamin C?” YES / NO.", "3 секундын тоолол, зөв хариулт асна, нэг өгүүлбэр тайлбар.", "Хүмүүс сэтгэгдэлд хариулж, шалгахын тулд дахин үзнэ. Тэр өдөр сторид санал асуулга нэмнэ."),
 ("Тун хэмжигч", "Хурд заагч мэт хэмжүүр: 2–5% / 5–10% / 10%+.", "Зүү ногооноос улаан руу хөдөлж, бүс бүрийг тайлбарлана: “их байх тусам сайн биш”.", "Нэг харахад ойлгомжтой. Хүмүүсийн нийтлэг алдааг засна."),
 ("POV дэлгүүрт", "“POV: you finally understand the shelf”: Olive Young-ийн тавиур.", "Хүрээ бүтээгдэхүүнүүдийн дээгүүр гүйж, ниацинамидтай нэг дээр нь зогсоно.", "Солонгост ирсэн жуулчдын мэдрэмжийг барина. Хожим жинхэнэ бичлэгээр хийж болно."),
 ("Жор", "“Recipe: even-toned skin”: хоолны жорын карт.", "Орцууд нэг нэгээр нэмэгдэнэ. Төгсгөлд: “болгох хугацаа 4–8 долоо хоног”.", "Хөгжилтэй, хадгалахад тохиромжтой. Цуврал болгоход амархан (тайван арьсны жор, гэрэлтэх арьсны жор…)."),
 ("Яаралтай мэдээ", "Улаан “BREAKING” мэдээний хэлбэр.", "Мэдээний хөтлөгчийн хэв маяг, доор нь гүйдэг мөр.", "Танил хэлбэр тул анхаарал татна. Шинэ трэнд, судалгааг танилцуулахад тохиромжтой."),
 ("Танилцах профайл", "Tinder мэт профайл: “Niacinamide, 3”.", "Дуртай зүйлс, “dealbreaker”, хэнийг хайж байгаа. Төгсгөлд “match”.", "Хөгжилтэй, хуваалцахад таатай. Орц бүрийг хүн мэт танилцуулна."),
 ("Тэмдэглэл", "iPhone Notes: “things I wish I knew about niacinamide”.", "Мөр бүр бичигдэж гарч ирнэ.", "Маш түгээмэл, жинхэнэ мэдрэмжтэй загвар. Хийхэд хамгийн хурдан."),
 ("Солонгос хэлний хичээл", "“How do you say it in Korean?” 나이아신아마이드", "Duolingo мэт хичээл: дуудлага, дараа нь зөв хариултыг сонгоно.", "Солонгос хэл + гоо сайхан = Kobi-ийн онцлог. Солонгос шошгыг уншиж сургана."),
 ("Ногоон / улаан туг", "“green & red flags” жагсаалт.", "Эхлээд ногоон тугууд, дараа нь улаан тугууд нэг нэгээр гарна.", "Трэнд хэлбэр. Хүмүүс өөрийн бүтээгдэхүүнийг шалгаад сэтгэгдэл бичнэ."),
 ("Хэзээ үр дүн гарах вэ?", "“When will I see results?”", "1, 4, 8 дахь долоо хоногийн явц дүүрнэ.", "Хүмүүсийн хамгийн их асуудаг асуулт. Тэвчээртэй байхыг сануулж, хадгалуулна."),
 ("Аль нь вэ?", "Хоёр хуваасан дэлгэц: B3 эсвэл C.", "Арьсны асуудал бүрийг аль талд тохирохыг хуваарилна.", "Хүмүүс арьсаа таньж, сэтгэгдэлд “би B3” гэж бичнэ."),
]

CSS = """
@font-face{font-family:Inter;src:url(file://ROOTDIR/engine/fonts/Inter.ttf);font-weight:100 900}
@page{size:A4;margin:0}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Inter,'Noto Sans CJK KR',sans-serif;color:#1d1718}
.pg{width:210mm;height:297mm;page-break-after:always;position:relative;overflow:hidden;background:#fbf6f3;padding:16mm 14mm}
.k{display:flex;align-items:center;gap:8px;font-size:11pt;font-weight:700;color:#c4706b;letter-spacing:.06em}
.logo{width:18px;height:18px;border-radius:5px;background:#ebc9c6;position:relative}
.logo:after{content:'';position:absolute;right:3px;bottom:3px;width:5px;height:5px;border-radius:50%;background:#181415}
h1{font-size:34pt;line-height:1.08;font-weight:900;letter-spacing:-.5px;margin-top:10mm}
.lead{font-size:13pt;line-height:1.55;color:#4a3f41;margin-top:7mm;max-width:160mm}
.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:3.5mm;margin-top:8mm}
.grid div{font-size:8.5pt;font-weight:700}
.grid img{width:100%;border-radius:2.5mm;display:block;margin-bottom:1.5mm}
.row{display:flex;gap:9mm;margin-top:8mm}
.row img{width:82mm;height:145.8mm;border-radius:4mm;object-fit:cover;box-shadow:0 2mm 6mm rgba(0,0,0,.12)}
.n{font-size:44pt;font-weight:900;color:#c4706b;line-height:1}
h2{font-size:22pt;font-weight:900;line-height:1.15;margin:2mm 0 6mm}
.b{margin-bottom:6mm}
.b span{display:block;font-size:9pt;font-weight:800;letter-spacing:.1em;color:#9a8b8d;text-transform:uppercase;margin-bottom:1.5mm}
.b p{font-size:11.5pt;line-height:1.55}
.box{background:#fff;border-radius:5mm;padding:7mm;margin-top:8mm;font-size:12pt;line-height:1.6}
.foot{position:absolute;bottom:10mm;left:14mm;right:14mm;font-size:9pt;color:#9a8b8d;display:flex;justify-content:space-between}
"""


def main():
    for i in range(1, 21):
        Image.open(os.path.join(CON, f"{i:02d}.jpg")).convert("RGB").resize((540, 960)).save(os.path.join(TMP, f"{i:02d}.jpg"), quality=84)
    img = lambda i: f"file://{TMP}/{i:02d}.jpg"
    pages = []
    pages.append(f"""<div class="pg"><div class="k"><div class="logo"></div>KOBI · REELS</div>
<h1>Reels цувралын<br>20 загвар</h1>
<p class="lead">Kobi бол К-гоо сайхны апп. Бид Instagram дээр “Ingredient Explained” гэсэн цуврал хийх гэж байна: <b>нэг анги = нэг орц</b>, 20–35 секунд. Энд бүх загвар нэг сэдэв дээр (ниацинамид, B3 витамин) хийгдсэн тул хооронд нь харьцуулахад амархан. Видео нь англи хэл дээр байна.</p>
<div class="grid">{''.join(f'<div><img src="{img(i)}">{i}. {F[i-1][0]}</div>' for i in range(1, 11))}</div>
<div class="foot"><span>Аль загвар хамгийн их таалагдаж байна? 1–3 дугаар сонгоорой.</span><span>1 / 23</span></div></div>""")
    pages.append(f"""<div class="pg"><div class="k"><div class="logo"></div>KOBI · REELS</div>
<div class="grid" style="margin-top:6mm">{''.join(f'<div><img src="{img(i)}">{i}. {F[i-1][0]}</div>' for i in range(11, 21))}</div>
<p class="lead">Дараагийн хуудсуудад загвар бүрийн дэлгэрэнгүй тайлбар байна.</p>
<div class="foot"><span>Kobi · kobiapp.cc</span><span>2 / 23</span></div></div>""")
    for i, (name, hook, story, strat) in enumerate(F, 1):
        pages.append(f"""<div class="pg"><div class="k"><div class="logo"></div>KOBI · INGREDIENT EXPLAINED</div>
<div class="row"><img src="{img(i)}"><div style="flex:1;min-width:0"><div class="n">{i}</div><h2>{name}</h2>
<div class="b"><span>Эхний 1 секунд</span><p>{hook}</p></div>
<div class="b"><span>Өрнөл</span><p>{story}</p></div>
<div class="b"><span>Яагаад үр дүнтэй вэ</span><p>{strat}</p></div></div></div>
<div class="foot"><span>Kobi · kobiapp.cc</span><span>{i+2} / 23</span></div></div>""")
    pages.append(f"""<div class="pg"><div class="k"><div class="logo"></div>KOBI · REELS</div>
<h1>Сонголтоо<br>бичээрэй</h1>
<div class="box"><b>Санал болгож буй хослол:</b><br>• <b>5 Үелэх систем</b>: цувралын өнгө төрх, профайл дээр гоё харагдана.<br>• <b>8 Супер баатрууд</b>: түүх, дүрүүд.<br>• <b>3 Домог ба үнэн</b>: шинэ хүмүүст хүрэх.<br><br>Гурвуулаа нэг цувралд багтаж болно.</div>
<div class="box">Хамгийн их таалагдсан <b>1–3 дугаараа</b> бичээд илгээгээрэй. Жишээ нь: “8, 5, 17”.<br>Мөн өөрчлөх зүйл байвал (өнгө, дүр, хэв маяг) бичээрэй.</div>
<div class="foot"><span>Kobi · kobiapp.cc</span><span>23 / 23</span></div></div>""")
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS.replace("ROOTDIR", ROOT)}</style></head><body>{''.join(pages)}</body></html>"
    p = os.path.join(ROOT, "engine", "_pdf.html"); open(p, "w", encoding="utf-8").write(html)
    eng = Engine(); pg = eng.br.new_page()
    pg.goto("file://" + p); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
    out = os.path.join(ROOT, "v2", "Kobi_Reels_20_zagvar.pdf")
    pg.pdf(path=out, format="A4", print_background=True, prefer_css_page_size=True)
    eng.close(); print(out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main()
