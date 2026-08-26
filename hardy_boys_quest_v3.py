#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys

def print_slow(text, delay=0.02):
    """Prints text slowly for a vintage text adventure feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_header(lang):
    title_text = {
        'uk': "     БРАТИ ХАРДІ ТА ТАЄМНИЦЯ ЗАТОНУЛОЇ ШХУНИ (ПРОДОВЖЕННЯ)     ",
        'en': "    THE HARDY BOYS AND THE MYSTERY OF THE SUNKEN SCHOONER     ",
        'ru': "    БРАТЬЯ ХАРДИ И ТАЙНА ЗАТОНУВШЕЙ ШХУНЫ (ПРОДОЛЖЕНИЕ)       "
    }
    subtitle_text = {
        'uk': "                 Інтерактивний текстовий квест                 ",
        'en': "                 Interactive Text-Based Quest                  ",
        'ru': "                 Интерактивный текстовый квест                 "
    }
    print("=" * 72)
    print(title_text[lang])
    print(subtitle_text[lang])
    print("=" * 72)
    print()

class GameState:
    def __init__(self):
        self.lang = 'uk'
        self.inventory = ["ліхтарик"]
        self.route_taken = None  # 'museum' or 'dive'
        self.hard_head_hit = False
        self.score = 0

LOCALIZATION = {
    'uk': {
        'select_lang': "Оберіть мову / Select Language / Выберите язык:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Ваш вибір (1-3): ",
        'press_enter': "Натисніть ENTER, щоб розпочати продовження пригод...",
        'invalid_input': "Будь ласка, введіть 1 або 2.",
        'intro_text': (
            "Ви знову граєте за відважних братів-детективів Френка та Джо Харді з Бейпорта!\n"
            "Після гучного арешту контрабандиста Ела «Краба» Берка на скелі Чорного Вовка,\n"
            "справа здавалася закритою. Проте справжні таємниці лише починають спливати на поверхню...\n"
            "Буквально у прямому сенсі — з глибин туманної Бейпортської бухти."
        ),
        'act1_title': "\n--- АКТ I: ДОПИТ ТА ГАРЯЧА ПІЦА ---",
        'act1_text': (
            "Ви перебуваєте у кабінеті шерифа Колліга в поліцейській дільниці Бейпорта.\n"
            "На столі перед вами — величезна коробка з гарячою піцою, яку Чет Мортон замовив\n"
            "на знак святкування вашої попередньої перемоги. Тягуча розплавлена моцарела,\n"
            "ароматні шматочки гострої пепероні, свіжий зелений базилік на хрусткому, ідеально\n"
            "підсмаженому тісті, що пахне дров'яною піччю... Ви ледве встигаєте проковтнути шматок,\n"
            "коли шериф Колліг заводить заарештованого Ела Берка.\n\n"
            "Берк виглядає похмурим, але єхидно посміхається:\n"
            "— Думаєте, ви схопили весь скарб? Золоті монети на скелі — це лише дріб'язок!\n"
            "Основна партія золота затонула разом із шхуною «Морська Німфа» в туманній бухті.\n"
            "Але вам її ніколи не знайти. Мої колишні спільники з банди «Акул» уже готують човни...\\n"
        ),
        'act1_q': "Як ви почнете пошук затонулої шхуни?",
        'act1_opt1': "1. [Шлях Френка] Вирушити до Морського музею Бейпорта, щоб знайти старі навігаційні карти та точні координати аварії.",
        'act1_opt2': "2. [Шлях Джо] Негайно підготувати акваланги, взяти катер «Нишпорка» і здійснити нічне занурення в туманній бухті.",
        'act1_out1': (
            "\nВи обираєте ретельну підготовку. У Морському музеї ви зустрічаєте Чета Мортона,\n"
            "який жує пончик із полуничною глазур'ю (класика!). Досліджуючи старі архіви,\n"
            "Френк розгадує логічну головоломку: за записами капітана, шхуна затонула навпроти\n"
            "маяка під кутом 45 градусів під час великого отливу. Ви отримуєте точні координати!\n"
            "Ви берете із собою: карту, акваланги та підводний ліхтар."
        ),
        'act1_out2': (
            "\nДжо наполягає на швидких діях! Ви завантажуєте важкі балони з киснем на ваш катер «Нишпорка».\n"
            "Нічний туман огортає воду, роблячи видимість майже нульовою. Чет Мортон залишається за штурвалом\n"
            "і нервово гризе яблуко. Ви одягаєте гідрокостюми і занурюєтесь у крижану чорну воду туманної бухти.\n"
            "Без точних координат вам доводиться шукати наосліп, покладаючись на інтуїцію Джо."
        ),
        'act2_title': "\n--- АКТ II: ЧОРНА БЕЗОДНЯ ТА КОНКУРЕНТИ ---",
        'act2_text': (
            "Під водою панує абсолютна тиша, порушувана лише шипінням ваших дихальних апаратів.\n"
            "Промені ваших підводних ліхтарів прорізають мутну зелену воду.\n"
            "Раптом з темряви виринає величний і моторошний силует затонулої шхуни «Морська Німфа».\n"
            "Її щогли порослі водоростями, а корпус наполовину засипаний піском.\n"
            "Проте ви помічаєте підводне світло з іншого боку корабля! Банда «Акул» уже тут!\n"
            "Двоє ворожих водолазів із гарпунними рушницями обстежують каюту капітана."
        ),
        'act2_q': "Який план дій під водою?",
        'act2_opt1': "1. Влаштувати диверсію: перекрити їм подачу повітря з балонів або перерізати їхні страхувальні троси.",
        'act2_opt2': "2. Непомітно прослизнути повз них через пробоїну в трюмі шхуни, щоб першими дістатися каюти зі скарбами.",
        'act2_out1': (
            "\nДжо сміливо підпливає ззаду до одного з бандитів і різко перекриває вентиль його балона!\n"
            "Виникає паніка! Ворожі водолази змушені терміново почати підйом на поверхню.\n"
            "Проте під час сутички один із них встигає вдарити Джо важким металевим ліхтарем прямо по шолому акваланга!"
        ),
        'act2_out2': (
            "\nФренк дає знак рукою. Ви обережно прослизаєте крізь розлом у правому борту шхуни.\n"
            "Ви опиняєтесь у занедбаному трюмі серед старих бочок. Проте підводна течія раптово\n"
            "зсуває хиткі дерев'яні конструкції палуби! Важка гнила балка падає прямо на Джо!"
        ),
        'act3_title': "\n--- АКТ III: ПАСТКА НА ДНІ ТА МІЦНА ГОЛОВА ---",
        'act3_text': (
            "Ви опиняєтесь заблокованими всередині капітанської каюти затонулої шхуни.\n"
            "Джо лежить на підлозі каюти під водою без тями. Повітря у ваших балонах обмежене.\n"
            "За хвилину Джо приходить до тями завдяки міцній голові Харді (класичний троп!):\n"
            "— Ох, мій шолом цілий, але в очах стрибають підводні морські зірки. Я в порядку, Френку!\n"
            "Перед вами стоїть закована залізом скриня капітана, в якій виблискують золоті злитки.\n"
            "Проте вихід завалений важкими уламками щогли, а датчик кисню починає тривожно блимати червоним!"
        ),
        'act3_q': "Кисень закінчується! Як ви виберетесь із затонулої каюти?",
        'act3_opt1': "1. [Варіант Джо] Використати аварійне продування жилетів компенсаторів плавучості та силу ніг, щоб різко виштовхнути уламки.",
        'act3_opt2': "2. [Варіант Френка] Спорудити важіль за допомогою старого штурвального ланцюга та застряглого анкера, щоб відсунути балку.",
        'act3_out1_success': (
            "\nВи наповнюєте жилети повітрям до межі! Величезна підйомна сила разом із потужним поштовхом\n"
            "ніг Джо зрушує уламки щогли вбік! Ви вириваєтесь назовні разом із капітанською скринею!"
        ),
        'act3_out1_fail': (
            "\nВи намагаєтесь штовхнути балку силою, але вона занадто важка. Ви лише витрачаєте дорогоцінний кисень.\n"
            "Потрібно спробувати логічніший підхід!"
        ),
        'act3_out2_success': (
            "\nФренк швидко обмотує іржавий ланцюг навколо балки і закріплює його на важкому анкері.\n"
            "Використовуючи закон важеля, ви без зайвих зусиль піднімаєте перешкоду! Шлях вільний!\n"
            "Ви забираєте скриню зі скарбами та починаєте підйом."
        ),
        'act4_title': "\n--- АКТ IV: ШАЛЕНА ГОНИТВА У ТУМАНІ ---",
        'act4_text': (
            "Ви виринаєте біля свого катера «Нишпорка». Чет Мортон допомагає вам підняти важку скриню на борт.\n"
            "Але туман розсіюється, і ви бачите швидкісний катер банди «Акул», який мчить прямо на вас!\n"
            "На його борту стоїть їхній ватажок, озброєний ракетницею.\n"
            "— Віддайте золото, Харді, або ми пустимо ваш корито на дно! — кричить він.\n"
            "Двигун вашого катера реве, починається шалена гонитва між скелями Бейпортської бухти!"
        ),
        'act4_q': "Як ви відірветесь від переслідувачів?",
        'act4_opt1': "1. [Рішення Джо] Зробити різкий віраж біля небезпечних Рифів Сирен, які ви знаєте як свої п'ять пальців.",
        'act4_opt2': "2. [Рішення Френка] Використати сигнальну ракетницю вашого катера, щоб засліпити водія ворожого човна.",
        'act4_out1': (
            "\nДжо хапає штурвал і спрямовує катер прямо на гострі скелі Рифів Сирен!\n"
            "«Нишпорка» пролітає в міліметрах від каменів. Бандити намагаються повторити маневр,\n"
            "але з гуркотом врізаються у риф! Їхній катер сідає на мілину, а ви мчите до безпечної гавані."
        ),
        'act4_out2': (
            "\nФренк спокійно цілиться і вистрілює яскраво-червоною сигнальною ракетою прямо перед ворожим катером!\n"
            "Водій бандитів на мить сліпне від спалаху, втрачає керування і різко повертає в бік,\n"
            "врізаючись у стару дерев'яну баржу. Вони нейтралізовані!"
        ),
        'final_header': "                 ФІНАЛ                       ",
        'final_high': (
            "Перемога! Справу про скарби «Морської Німфи» блискуче розкрито! Ваш рахунок: {score} очок.\n"
            "Скриню з іспанським золотом передано до Морського музею Бейпорта. Шериф Колліг у захваті!\n"
            "А ввечері вдома мама Лора Харді приготувала для вас неймовірну вечерю:\n"
            "величезну домашню запіканку з курятиною, грибами та золотистою сирною скоринкою,\n"
            "а на десерт — теплий яблучний штрудель з ванільним морозивом.\n"
            "Чет Мортон уже з'їв три шматки і каже, що ви — найкращі детективи у світі!"
        ),
        'final_normal': (
            "Справу завершено! Ваш рахунок: {score} очок.\n"
            "Хоча балони з киснем майже спорожніли, а потилиця Джо все ще ниє від удару ліхтарем,\n"
            "золото врятовано від бандитів. Попереду на братів Харді чекають нові захоплюючі розслідування!"
        ),
        'final_thanks': "\nДякуємо за гру! Френк та Джо пишалися б вашою сміливістю та розумом."
    },
    'en': {
        'select_lang': "Select Language / Оберіть мову / Выберите язык:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Your choice (1-3): ",
        'press_enter': "Press ENTER to start the continuation of the adventure...",
        'invalid_input': "Please enter 1 or 2.",
        'intro_text': (
            "You are playing once again as the famous detective brothers, Frank and Joe Hardy from Bayport!\n"
            "After the dramatic arrest of the smuggler Al 'Crab' Burke on Black Wolf Rock,\n"
            "the case seemed closed. But the real secrets are just beginning to surface...\n"
            "Literally — from the depths of the foggy Bayport harbor."
        ),
        'act1_title': "\n--- ACT I: THE INTERROGATION & HOT PIZZA ---",
        'act1_text': (
            "You are in Sheriff Collig's office at the Bayport Police Station.\n"
            "On the table before you is a huge box of hot pizza that Chet Morton ordered\n"
            "to celebrate your previous victory. Gooey melted mozzarella, flavorful slices\n"
            "of spicy pepperoni, fresh green basil on a crispy, perfectly baked crust smelling\n"
            "of a wood-fired oven... You barely manage to swallow a slice when Sheriff Collig\n"
            "brings in the arrested Al Burke.\n\n"
            "Burke looks gloomy but sneers jeeringly:\n"
            "— Think you got all the loot? The gold coins on the rock are just pocket change!\n"
            "The main shipment of gold sank with the schooner 'Sea Nymph' in the foggy bay.\n"
            "But you'll never find it. My former associates from the 'Shark' gang are already prepping boats...\\n"
        ),
        'act1_q': "How will you start your search for the sunken schooner?",
        'act1_opt1': "1. [Frank's Choice] Head to the Bayport Maritime Museum to find old charts and exact wreck coordinates.",
        'act1_opt2': "2. [Joe's Choice] Immediately prep scuba gear, take the motorboat 'Sleuth', and perform a night dive.",
        'act1_out1': (
            "\nYou choose careful preparation. At the Maritime Museum, you meet Chet Morton,\n"
            "who is munching on a strawberry-glazed donut (classic Chet!). Examining the archives,\n"
            "Frank solves a navigation riddle based on the captain's log: the ship sank opposite the lighthouse\n"
            "at a 45-degree angle during a low tide. You get the exact coordinates!\n"
            "You bring: a map, scuba gear, and an underwater flashlight."
        ),
        'act1_out2': (
            "\nJoe insists on immediate action! You load heavy oxygen tanks onto your speedboat 'Sleuth'.\n"
            "The night fog blankets the water, making visibility near zero. Chet Morton stays at the helm,\n"
            "nervously biting an apple. You put on wetsuits and plunge into the freezing black waters.\n"
            "Without exact coordinates, you search blindly, relying on Joe's gut feeling."
        ),
        'act2_title': "\n--- ACT II: THE BLACK ABYSS & RIVALS ---",
        'act2_text': (
            "Underwater, absolute silence reigns, broken only by the hissing of your regulators.\n"
            "Your flashlight beams slice through the murky green water.\n"
            "Suddenly, the majestic and eerie silhouette of the sunken schooner 'Sea Nymph' looms from the dark.\n"
            "Her masts are overgrown with kelp, her hull half-buried in sand.\n"
            "However, you spot underwater lights on the other side of the wreck! The 'Shark' gang is already here!\n"
            "Two rival divers with spear guns are investigating the captain's cabin."
        ),
        'act2_q': "What is your underwater plan?",
        'act2_opt1': "1. Sabotage them: shut off their air tank valves or cut their safety lines.",
        'act2_opt2': "2. Sneak past them through a breach in the hull to reach the treasure cabin first.",
        'act2_out1': (
            "\nJoe boldly swims up behind one of the thugs and sharply twists his air valve closed!\n"
            "Panic ensues! The rival divers are forced to perform an emergency ascent.\n"
            "However, during the scuffle, one of them manages to strike Joe's helmet with a heavy metal dive light!"
        ),
        'act2_out2': (
            "\nFrank signals. You carefully slip through a breach in the ship's starboard side.\n"
            "You find yourselves in a damp hold among old barrels. Suddenly, a strong underwater current\n"
            "shifts the unstable deck timbers! A heavy rotten beam falls right onto Joe!"
        ),
        'act3_title': "\n--- ACT III: THE SEA FLOOR TRAP & HARD HEAD ---",
        'act3_text': (
            "You find yourselves trapped inside the captain's cabin of the sunken schooner.\n"
            "Joe lies on the floor of the cabin underwater, unconscious. Your air levels are low.\n"
            "Within a minute, Joe wakes up, thanks to the classic Hardy hard head (classic trope!):\n"
            "— Ouch, my helmet is intact, but I'm seeing underwater starfish. I'm okay, Frank!\n"
            "Before you stands the iron-bound captain's chest, glittering with gold bars.\n"
            "However, the exit is blocked by fallen mast debris, and your oxygen gauge starts flashing red!"
        ),
        'act3_q': "Oxygen is running low! How will you escape?",
        'act3_opt1': "1. [Joe's Option] Perform an emergency BCD inflation and use leg power to forcefully push the debris.",
        'act3_opt2': "2. [Frank's Option] Rig a leverage system using an old steering chain and a wedged anchor to lift the beam.",
        'act3_out1_success': (
            "\nYou inflate your BCDs to the max! The massive buoyant force combined with a powerful kick\n"
            "from Joe's legs shifts the mast debris aside! You escape with the captain's chest!"
        ),
        'act3_out1_fail': (
            "\nYou try to push the beam with raw strength but it's too heavy. You only waste precious oxygen.\n"
            "You need to try a more logical approach!"
        ),
        'act3_out2_success': (
            "\nFrank quickly wraps the rusty chain around the beam and secures it to a heavy anchor.\n"
            "Using the law of leverage, you lift the obstacle effortlessly! The path is clear!\n"
            "You grab the treasure chest and begin your ascent."
        ),
        'act4_title': "\n--- ACT IV: WILD CHASE IN THE FOG ---",
        'act4_text': (
            "You surface next to your motorboat 'Sleuth'. Chet Morton helps you haul the heavy chest aboard.\n"
            "But the fog thins, and you see the 'Shark' gang's high-speed boat rushing straight at you!\n"
            "Their leader stands on the bow, armed with a flare gun.\n"
            "— Hand over the gold, Hardys, or we'll send your tub to the bottom! — he yells.\n"
            "Your engine roars as a wild chase begins through the rocks of Bayport harbor!"
        ),
        'act4_q': "How will you shake the pursuers?",
        'act4_opt1': "1. [Joe's Choice] Make a sharp turn near the dangerous Siren's Reefs, which you know like the back of your hand.",
        'act4_opt2': "2. [Frank's Choice] Use your boat's emergency flare gun to blind the driver of the enemy boat.",
        'act4_out1': (
            "\nJoe grabs the wheel and steers the boat straight toward the jagged rocks of Siren's Reefs!\n"
            "The 'Sleuth' zips inches away from the rocks. The thugs try to copy the maneuver\n"
            "but crash into the reef with a roar! Their boat is stranded, and you zoom to safety."
        ),
        'act4_out2': (
            "\nFrank aims calmly and fires a brilliant red flare directly in front of the enemy boat!\n"
            "The driver is temporarily blinded by the flash, loses control, and veers sharply,\n"
            "smashing into an old wooden barge. They are neutralized!"
        ),
        'final_header': "                THE END                      ",
        'final_high': (
            "Victory! The mystery of the 'Sea Nymph' treasure is solved brilliantly! Your score: {score} points.\n"
            "The chest of Spanish gold is donated to the Bayport Maritime Museum. Sheriff Collig is thrilled!\n"
            "In the evening at home, Mom Laura Hardy prepared an incredible dinner for you:\n"
            "a huge homemade casserole with chicken, mushrooms, and a golden cheese crust,\n"
            "and for dessert — warm apple strudel with vanilla ice cream.\n"
            "Chet Morton has already eaten three slices and says you are the best detectives in the world!"
        ),
        'final_normal': (
            "The case is closed! Your score: {score} points.\n"
            "Although your oxygen tanks were nearly empty and Joe's head still aches from the dive light blow,\n"
            "the gold is saved from the thugs. More exciting investigations await the Hardy Boys!"
        ),
        'final_thanks': "\nThanks for playing! Frank and Joe would be proud of your courage and wit."
        
    },
    'ru': {
        'select_lang': "Выберите язык / Oберіть мову / Select Language:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Ваш выбор (1-3): ",
        'press_enter': "Нажмите ENTER, чтобы начать продолжение приключений...",
        'invalid_input': "Пожалуйста, введите 1 или 2.",
        'intro_text': (
            "Вы снова играете за отважных братьев-детективов Фрэнка и Джо Харди из Бейпорта!\n"
            "После громкого ареста контрабандиста Эла «Краба» Берка на скале Черного Волка,\n"
            "дело казалось закрытым. Однако настоящие тайны только начинают всплывать на поверхность...\n"
            "Буквально в прямом смысле — из глубин туманной Бейпортской бухты."
        ),
        'act1_title': "\n--- АКТ I: ДОПРОС И ГОРЯЧАЯ ПИЦЦА ---",
        'act1_text': (
            "Вы находитесь в кабинете шерифа Коллига в полицейском участке Бейпорта.\n"
            "На столе перед вами — огромная коробка с горячей пиццей, которую Чет Мортон заказал\n"
            "в знак празднования вашей предыдущей победы. Тягучая расплавленная моцарелла,\n"
            "ароматные кусочки острой пепперони, свежий зеленый базилик на хрустящем, идеально\n"
            "поджаренном тесте, пахнущем дровяной печью... Вы едва успеваете проглотить кусок,\n"
            "когда шериф Коллиг заводит арестованного Эла Берка.\n\n"
            "Берк выглядит мрачным, но ехидно усмехается:\n"
            "— Думаете, вы прибрали к рукам все сокровища? Золотые монеты на скале — это лишь мелочь!\n"
            "Основная партия золота затонула вместе со шхуной «Морская Нимфа» в туманной бухте.\n"
            "Но вам её никогда не найти. Мои бывшие сообщники из банды «Акул» уже готовят лодки...\\n"
        ),
        'act1_q': "Как вы начнете поиск затонувшей шхуны?",
        'act1_opt1': "1. [Выбор Фрэнка] Отправиться в Морской музей Бейпорта, чтобы найти старые навигационные карты и точные координаты крушения.",
        'act1_opt2': "2. [Выбор Джо] Немедленно подготовить акваланги, взять катер «Ищейка» и совершить ночное погружение в туманной бухте.",
        'act1_out1': (
            "\nВы выбираете тщательную подготовку. В Морском музее вы встречаете Чета Мортона,\n"
            "который жует пончик с клубничной глазурью (классика!). Исследуя старые архивы,\n"
            "Фрэнк разгадывает логическую головоломку: по записям капитана, шхуна затонула напротив\n"
            "маяка под углом 45 градусов во время сильного отлива. Вы получаете точные координаты!\n"
            "Вы берете с собой: карту, акваланги и подводный фонарь."
        ),
        'act1_out2': (
            "\nДжо настаивает на быстрых действиях! Вы загружаете тяжелые баллоны с кислородом на ваш катер «Ищейка».\n"
            "Ночной туман окутывает воду, делая видимость почти нулевой. Чет Мортон остается за штурвалом\n"
            "и нервно грызет яблоко. Вы надеваете гидрокостюмы и погружаетесь в ледяную черную воду туманной бухты.\n"
            "Без точных координат вам приходится искать вслепую, полагаясь на интуицию Джо."
        ),
        'act2_title': "\n--- АКТ II: ЧЕРНАЯ БЕЗДНА И КОНКУРЕНТЫ ---",
        'act2_text': (
            "Под водой царит абсолютная тишина, нарушаемая лишь шипением ваших дыхательных аппаратов.\n"
            "Лучи ваших подводных фонарей прорезают мутную зеленую воду.\n"
            "Вдруг из темноты выплывает величественный и жуткий силуэт затонувшей шхуны «Морская Нимфа».\n"
            "Ее мачты поросли водорослями, а корпус наполовину засыпан песком.\n"
            "Однако вы замечаете подводный свет с другой стороны корабля! Банда «Акул» уже здесь!\n"
            "Двое вражеских водолазов с гарпунными ружьями обследуют каюту капитана."
        ),
        'act2_q': "Каков ваш план действий под водой?",
        'act2_opt1': "1. Устроить диверсию: перекрыть им подачу воздуха из баллонов или перерезать их страховочные тросы.",
        'act2_opt2': "2. Незаметно проскользнуть мимо них через пробоину в трюме шхуны, чтобы первыми добраться до каюты с сокровищами.",
        'act2_out1': (
            "\nДжо смело подплывает сзади к одному из бандитов и резко перекрывает вентиль его баллона!\n"
            "Возникает паника! Вражеские водолазы вынуждены срочно начать подъем на поверхность.\n"
            "Однако во время потасовки один из них успевает ударить Джо тяжелым металлическим фонарем прямо по шлему акваланга!"
        ),
        'act2_out2': (
            "\nФрэнк дает знак рукой. Вы осторожно проскальзываете через разлом в правом борту шхуны.\n"
            "Вы оказываетесь в заброшенном трюме среди старых бочек. Однако подводное течение внезапно\n"
            "сдвигает шаткие деревянные конструкции палубы! Тяжелая гнилая балка падает прямо на Джо!"
        ),
        'act3_title': "\n--- АКТ III: ЛОВУШКА НА ДНЕ И КРЕПКАЯ ГОЛОВА ---",
        'act3_text': (
            "Вы оказываетесь заблокированными внутри капитанской каюты затонувшей шхуны.\n"
            "Джо лежит на полу каюты под водой без сознания. Воздух в ваших баллонах ограничен.\n"
            "Через минуту Джо приходит в себя благодаря крепкой голове Харди (классический троп!):\n"
            "— Ох, мой шлем цел, но в глазах прыгают подводные морские звезды. Я в порядке, Фрэнк!\n"
            "Перед вами стоит окованный железом сундук капитана, в котором поблескивают золотые слитки.\n"
            "Однако выход завален тяжелыми обломками мачты, а датчик кислорода начинает тревожно мигать красным!"
        ),
        'act3_q': "Кислород заканчивается! Как вы выберетесь из затонувшей каюты?",
        'act3_opt1': "1. [Вариант Джо] Использовать аварийную продувку жилетов компенсаторов плавучести и силу ног, чтобы резко вытолкнуть обломки.",
        'act3_opt2': "2. [Вариант Фрэнка] Соорудить рычаг с помощью старой штурвальной цепи и застрявшего якоря, чтобы отодвинуть балку.",
        'act3_out1_success': (
            "\nВы наполняете жилеты воздухом до предела! Огромная подъемная сила вместе с мощным толчком\n"
            "ног Джо сдвигает обломки мачты в сторону! Вы вырываетесь наружу вместе с капитанским сундуком!"
        ),
        'act3_out1_fail': (
            "\nВы пытаетесь толкнуть балку силой, но она слишком тяжелая. Вы лишь тратите драгоценный кислород.\n"
            "Нужно попробовать более логичный подход!"
        ),
        'act3_out2_success': (
            "\nФрэнк быстро обматывает ржавую цепь вокруг балки и закрепляет ее на тяжелом якоре.\n"
            "Используя закон рычага, вы без лишних усилий поднимаете препятствие! Путь свободен!\n"
            "Вы забираете сундук с сокровищами и начинаете подъем."
        ),
        'act4_title': "\n--- АКТ IV: БЕШЕНАЯ ПОГОНЯ В ТУМАНЕ ---",
        'act4_text': (
            "Вы выныриваете возле своего катера «Ищейка». Чет Мортон помогает вам поднять тяжелый сундук на борт.\n"
            "Но туман рассеивается, и вы видите скоростной катер банды «Акул», мчащийся прямо на вас!\n"
            "На его борту стоит их главарь, вооруженный ракетницей.\n"
            "— Отдайте золото, Харди, или мы пустим ваше корыто на дно! — кричит он.\n"
            "Двигатель вашего катера ревет, начинается безумная погоня между скалами Бейпортской бухты!"
        ),
        'act4_q': "Как вы оторветесь от преследователей?",
        'act4_opt1': "1. [Решение Джо] Сделать резкий вираж возле опасных Рифов Сирен, которые вы знаете как свои пять пальцев.",
        'act4_opt2': "2. [Решение Фрэнка] Использовать сигнальную ракетницу вашего катера, чтобы ослепить водителя вражеской лодки.",
        'act4_out1': (
            "\nДжо хватает штурвал и направляет катер прямо на острые скалы Рифов Сирен!\n"
            "«Ищейка» пролетает в миллиметрах от камней. Бандиты пытаются повторить маневр,\n"
            "но с грохотом врезаются в риф! Их катер садится на мель, а вы мчитесь в безопасную гавань."
        ),
        'act4_out2': (
            "\nФрэнк спокойно целится и выстреливает ярко-красной сигнальной ракетой прямо перед вражеским катером!\n"
            "Водитель бандитов на мгновение слепнет от вспышки, теряет управление и резко сворачивает в сторону,\n"
            "врезаясь в старую деревянную баржу. Они нейтрализованы!"
        ),
        'final_header': "                 ФИНАЛ                       ",
        'final_high': (
            "Победа! Дело о сокровищах «Морской Нимфы» блестяще раскрыто! Ваш счет: {score} очков.\n"
            "Сундук с испанским золотом передан в Морской музей Бейпорта. Шериф Коллиг в восторге!\n"
            "А вечером дома мама Лора Харди приготовила для вас невероятный ужин:\n"
            "огромную домашнюю запеканку с курицей, грибами и золотистой сырной корочкой,\n"
            "а на десерт — теплый яблочный штрудель с ванильным мороженым.\n"
            "Чет Мортон уже съел три куска и говорит, что вы — лучшие детективы в мире!"
        ),
        'final_normal': (
            "Дело завершено! Ваш счет: {score} очок.\n"
            "Хотя баллоны с кислородом почти опустели, а затылок Джо все еще ноет от удара фонарем,\n"
            "золото спасено от бандитов. Впереди братьев Харди ждут новые захватывающие расследования!"
        ),
        'final_thanks': "\nСпасибо за игру! Фрэнк и Джо гордились бы вашей смелостью и умом."
    }
}

def intro(state):
    display_header(state.lang)
    print_slow(LOCALIZATION[state.lang]['intro_text'])
    print_slow("\n" + LOCALIZATION[state.lang]['press_enter'])
    input()
    act_1(state)

def act_1(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act1_title'])
    print_slow(loc['act1_text'])
    
    while True:
        print("\n" + loc['act1_q'])
        print(loc['act1_opt1'])
        print(loc['act1_opt2'])
        choice = input(loc.get('act1_choice_prompt', '\n-> ')).strip()
        
        if choice == '1':
            state.route_taken = 'museum'
            state.score += 20
            state.inventory.append('map')
            state.inventory.append('scuba_gear')
            state.inventory.append('underwater_flashlight')
            print_slow(loc['act1_out1'])
            break
        elif choice == '2':
            state.route_taken = 'dive'
            state.score += 10
            state.inventory.append('scuba_gear')
            print_slow(loc['act1_out2'])
            break
        else:
            print(loc['invalid_input'])
            
    act_2(state)

def act_2(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act2_title'])
    print_slow(loc['act2_text'])
    
    while True:
        print("\n" + loc['act2_q'])
        print(loc['act2_opt1'])
        print(loc['act2_opt2'])
        choice = input(loc.get('act1_choice_prompt', '\n-> ')).strip()
        
        if choice == '1':
            state.hard_head_hit = True
            state.score += 20
            print_slow(loc['act2_out1'])
            break
        elif choice == '2':
            state.hard_head_hit = True
            state.score += 15
            print_slow(loc['act2_out2'])
            break
        else:
            print(loc['invalid_input'])
            
    act_3(state)

def act_3(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act3_title'])
    print_slow(loc['act3_text'])
    
    while True:
        print("\n" + loc['act3_q'])
        print(loc['act3_opt1'])
        print(loc['act3_opt2'])
        choice = input(loc.get('act1_choice_prompt', '\n-> ')).strip()
        
        if choice == '1':
            if state.route_taken == 'dive':
                print_slow(loc['act3_out1_fail'])
                continue
            else:
                state.score += 20
                print_slow(loc['act3_out1_success'])
                break
        elif choice == '2':
            state.score += 25
            print_slow(loc['act3_out2_success'])
            break
        else:
            print(loc['invalid_input'])
            
    act_4(state)

def act_4(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act4_title'])
    print_slow(loc['act4_text'])
    
    while True:
        print("\n" + loc['act4_q'])
        print(loc['act4_opt1'])
        print(loc['act4_opt2'])
        choice = input(loc.get('act1_choice_prompt', '\n-> ')).strip()
        
        if choice == '1':
            state.score += 25
            print_slow(loc['act4_out1'])
            break
        elif choice == '2':
            state.score += 20
            print_slow(loc['act4_out2'])
            break
        else:
            print(loc['invalid_input'])
            
    # Final screen
    print_slow("\n=============================================")
    print_slow(loc['final_header'])
    print_slow("=============================================\n")
    
    if state.score >= 80:
        print_slow(loc['final_high'].format(score=state.score))
    else:
        print_slow(loc['final_normal'].format(score=state.score))
        
    print_slow(loc['final_thanks'])

def main():
    state = GameState()
    print(LOCALIZATION['uk']['select_lang'])
    while True:
        choice = input(LOCALIZATION['uk']['lang_choice_prompt']).strip()
        if choice == '1':
            state.lang = 'uk'
            break
        elif choice == '2':
            state.lang = 'en'
            break
        elif choice == '3':
            state.lang = 'ru'
            break
        else:
            print("1, 2, 3?")
            
    intro(state)

if __name__ == "__main__":
    main()
