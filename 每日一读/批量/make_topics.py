"""生成每日一读 50 篇的选题表（选题表.json / 选题表.md）。标题避开分级阅读第一批、第二批已有的题目。"""
import json
from pathlib import Path

T = [
    # A1
    ("A1", 1, "Mi abuela", "我的奶奶", "温馨的客厅：扶手椅、装着毛线和织针的篮子、茶壶和茶杯、挂着窗帘的窗户、墙上的挂钟（钟面不画数字）"),
    ("A1", 2, "El mercado del sábado", "周六的集市", "露天集市：带条纹遮阳棚的摊位，箱子里装满水果蔬菜（橙子、番茄、苹果、生菜），远处有房子"),
    ("A1", 3, "Mi bicicleta", "我的自行车", "公园小路边，一辆自行车靠在树旁，车筐里有花，草地和花丛"),
    ("A1", 4, "La cocina de mi casa", "我家的厨房", "明亮的厨房：餐桌、果盘、灶台上的锅、挂着的厨具、窗台上的小盆栽"),
    ("A1", 5, "Un día de lluvia", "下雨天", "从室内看窗外下雨：雨丝、窗边的热茶、门边的雨伞和雨靴，窗外湿漉漉的街道"),
    ("A1", 6, "Mi cafetería favorita", "我最喜欢的咖啡馆", "咖啡馆一角：小圆桌上的咖啡杯和蛋糕、木架上的杯子、吊灯、绿植"),
    ("A1", 7, "El parque de mi barrio", "我们街区的公园", "街区公园：长椅、几棵树、小喷泉、池塘里的鸭子、远处的楼房"),
    ("A1", 8, "Mi mochila", "我的书包", "书桌上：一个书包、几本本子、笔袋、台灯、窗外的天空"),
    ("A1", 9, "La panadería de la esquina", "街角的面包店", "面包店柜台：篮子里的长棍面包和圆面包、玻璃柜里的点心、木架"),
    ("A1", 10, "Llega el invierno", "冬天来了", "窗外下雪的街道，室内椅子上搭着围巾和手套，桌上一杯热巧克力"),
    # A2
    ("A2", 1, "Mi primer día de universidad", "我上大学的第一天", "大学校园：老教学楼、台阶、树、草坪、远处的钟楼（钟面不画数字）"),
    ("A2", 2, "Comer al aire libre", "在户外吃饭", "大树下的野餐布、藤编野餐篮、三明治和水果、远处的小山"),
    ("A2", 3, "La casa de mis abuelos", "爷爷奶奶家", "乡间的小房子：白墙红瓦、木栅栏、花园小路、一棵大树、远处的田野"),
    ("A2", 4, "Una noche bajo las estrellas", "星空下的一夜", "夜晚的山间营地：帐篷、篝火、满天星星、远处的山影（深蓝色调但保持柔和）"),
    ("A2", 5, "Mi primer viaje en avión", "第一次坐飞机", "从飞机舷窗往外看：机翼、白云、远处的地面和蓝天"),
    ("A2", 6, "El regalo perfecto", "完美的礼物", "桌上一个系着丝带的礼物盒、一束花、一张空白卡片（不写字）、柔和的灯光"),
    ("A2", 7, "Una visita al acuario", "参观水族馆", "水族馆大玻璃缸：各色的鱼、珊瑚、水草、气泡，前面有一条长椅"),
    ("A2", 8, "Un día de pesca con mi padre", "和爸爸去钓鱼", "湖边：一条小木船、两根钓竿、芦苇、远处的树林和山"),
    ("A2", 9, "Me perdí en la ciudad", "我在城里迷路了", "老城区的小街：彩色房子、阳台、路灯、地上一张打开的地图（地图上不写字）"),
    ("A2", 10, "Una cena para mis amigos", "为朋友们做的晚饭", "餐桌：几盘菜、一锅炖菜、蜡烛、杯子、餐具，背景是温暖的厨房"),
    # B1
    ("B1", 1, "Viajar solo", "独自旅行", "山间观景台：一个背包、一张地图、一顶帽子，远处是海边小镇"),
    ("B1", 2, "Las cartas escritas a mano", "手写的信", "书桌：几封信和信封、钢笔、墨水瓶、邮票（不画文字）"),
    ("B1", 3, "Caminar por la ciudad", "在城市里散步", "两旁有树的人行道、老楼房、长椅、几只鸽子"),
    ("B1", 4, "Aprender a hacer fotos", "学拍照", "桌上一台相机、几张冲洗出来的风景照片、镜头、笔记本"),
    ("B1", 5, "La radio de mi abuelo", "爷爷的收音机", "木架上一台老式收音机、扶手椅、台灯、一杯咖啡"),
    ("B1", 6, "Los mayores y la tecnología", "老年人与科技", "桌上一台平板电脑（屏幕不显示文字）、一副老花镜、一杯茶、一盆绿植"),
    ("B1", 7, "El mar en invierno", "冬天的大海", "冬天空荡荡的海滩：灰蓝色的海、浪花、几只海鸥、一把收起来的遮阳伞"),
    ("B1", 8, "Trabajar desde casa", "在家工作", "窗边的书桌：笔记本电脑（屏幕不显示文字）、马克杯、绿植、窗外的树"),
    ("B1", 9, "Los juegos de mesa", "桌游", "桌上一盘棋盘游戏、骰子（只画圆点）、棋子、几张卡片（不写字）、一碗零食"),
    ("B1", 10, "Un mercado de segunda mano", "二手市场", "跳蚤市场：摊位上的旧书、旧相机、花瓶、旧椅子、挂着的灯串"),
    # B2
    ("B2", 1, "La moda rápida", "快时尚", "挂满衣服的衣架、几个购物袋（不印字）、一面镜子"),
    ("B2", 2, "El ruido de las ciudades", "城市的噪音", "城市街道：车流、高楼、从公寓窗户往外看的视角"),
    ("B2", 3, "La vuelta al campo", "回归乡村", "乡村小屋的院子：院子里的桌上放着笔记本电脑，周围是山丘和田野"),
    ("B2", 4, "El valor del trabajo manual", "手工劳动的价值", "木工工作台：刨子、锤子、木料、刨花、挂在墙上的工具"),
    ("B2", 5, "Los museos en la era digital", "数字时代的博物馆", "博物馆展厅：墙上几幅抽象画（不画具体名画）、长椅、一个立着的导览屏（不显示文字）"),
    ("B2", 6, "El agua, un bien escaso", "水：一种稀缺资源", "干涸的水库：开裂的土地、低水位，前景一个滴水的水龙头"),
    ("B2", 7, "El tren frente al avión", "火车与飞机", "火车穿过田野，天上有一架飞机，远处有山"),
    ("B2", 8, "La amistad en la edad adulta", "成年后的友谊", "咖啡馆窗边的桌上两杯咖啡、一小盘点心，窗外的街景"),
    ("B2", 9, "Aprender idiomas de adulto", "成年后学外语", "书桌：几本书、打开的笔记本（不写字）、地球仪、耳机"),
    ("B2", 10, "Las mascotas en la ciudad", "城市里的宠物", "城市公园：长椅旁一只拴着牵引绳的狗、远处的公寓楼"),
    # C1
    ("C1", 1, "El ocio como necesidad", "闲暇是一种需要", "两棵树之间的吊床、吊床上一本书、草地、斑驳的阳光"),
    ("C1", 2, "La belleza de lo imperfecto", "不完美之美", "一只用金线修补过裂纹的陶碗、架子上几件手工陶器"),
    ("C1", 3, "Elogio de la lentitud", "慢的颂歌", "窗边桌上的沙漏和茶杯、窗外缓缓飘过的云"),
    ("C1", 4, "Los mapas y nuestra mirada", "地图与我们的眼光", "桌上一张旧地图（只画海岸线，不写字）、指南针、放大镜"),
    ("C1", 5, "Cooperar o competir", "合作还是竞争", "湖上一条多人划的长船、几支桨、平静的水面和远处的树"),
    ("C1", 6, "El paisaje como patrimonio", "作为遗产的风景", "层层梯田、橄榄树、山坡上的小村庄"),
    ("C1", 7, "El arte de conversar", "谈话的艺术", "两把面对面的扶手椅、中间的小茶几上两杯茶、落地灯"),
    ("C1", 8, "La curiosidad científica", "科学的好奇心", "显微镜、几本书、植物标本、放大镜"),
    ("C1", 9, "La memoria de los objetos", "物件的记忆", "旧皮箱、几张旧照片（照片里只画风景色块）、一块怀表、一副眼镜"),
    ("C1", 10, "La plaza, lugar de encuentro", "广场：相遇之地", "小城广场：喷泉、长椅、树、四周带拱廊的房子"),
]
VOICE = {"A1": "qwen3_M1F5_25_slow", "A2": "qwen3_M1F5_25_slow", "B1": "qwen3_M1F5_25", "B2": "qwen3_M1F5_25", "C1": "qwen3_M1F5_25"}
out = [{"id": f"daily_{lv.lower()}_{n:02d}", "level": lv, "no": n, "title_es": es, "title_zh": zh, "voice": VOICE[lv], "scene": sc}
       for lv, n, es, zh, sc in T]
assert len(out) == 50 and len({o['id'] for o in out}) == 50 and len({o['title_es'] for o in out}) == 50
bad = [o['title_es'] for o in out if len(o['title_es']) > 30 or len(o['title_zh']) > 9]
assert not bad, bad
here = Path(__file__).parent
(here / '选题表.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), 'utf-8')
md = ['# 每日一读（50 篇）选题表', '',
      'A1—A2 用 `qwen3_M1F5_25_slow`（0.8 倍速），B1—C1 用 `qwen3_M1F5_25`（原速）。标题避开了分级阅读第一批、第二批的题目。插图提示只写画面内容，画面上不出现文字。', '',
      '| 编号 | 级别 | 标题 | 中文 | 插图画面 |', '|---|---|---|---|---|']
md += [f"| {o['id']} | {o['level']} | {o['title_es']} | {o['title_zh']} | {o['scene']} |" for o in out]
(here / '选题表.md').write_text('\n'.join(md) + '\n', 'utf-8')
print(len(out), '篇')
