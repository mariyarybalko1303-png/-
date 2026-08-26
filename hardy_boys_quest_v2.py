#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys

# Localization Dictionary containing Ukrainian, English, and Russian languages.
LOCALIZATION = {
    'uk': {
        'select_lang': "Оберіть мову / Select Language / Выберите язык:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Ваш вибір (1-3): ",
        'press_enter': "Натисніть ENTER, щоб розпочати пригоду...",
        'invalid_input': "Будь ласка, введіть 1 або 2.",
        'title': "          БРАТИ ХАРДІ ТА ТАЄМНИЦЯ СКЕЛІ ЧОРНОГО ВОВКА          ",
        'subtitle': "     Супер-детективний квест із розширеним розслідуванням та загадками     ",
        'intro_text': (
            "Ви граєте за відомих братів-детективів Френка та Джо Харді з містечка Бейпорт.\n"
            "Френк (18 років) — раціональний, логічний скептик, а Джо (17 років) —\n"
            "імпульсивний, сильний і відважний спортмен.\n"
            "Разом із найкращим другом Четом Мортоном ви опиняєтесь у центрі нової загадкової справи!"
        ),
        
        # Акт I
        'act1_title': "\n--- АКТ I: СИТИЙ ПОЧАТОК ТА ТАЄМНИЧА ПЛЯШКА ---",
        'act1_text': (
            "Ви сидите у затишній закусочній «Притулок моряка» у Бейпорті.\n"
            "На столі перед вами — справжній кулінарний шедевр: соковиті подвійні чізбургери\n"
            "із золотистою хрусткою скоринкою підсмаженого бекону, пишна гаряча картопля фрі,\n"
            "рясно присипана спеціями, та величезні ванільні молочні коктейлі зі збитими вершками.\n"
            "Ви якраз насолоджуєтесь цією чудовою їжею, коли Чет Мортон дістає з рюкзака щось дивне.\n\n"
            "— Хлопці, подивіться на це! — шепоче Чет, озираючись. — Я виловив це в бухті.\n"
            "Він кладе на стіл мокру скляну пляшку. Всередині видно старий пергамент із загадковими\n"
            "символами та грубою картою, що веде до покинутої вежі контрабандистів на скелі Чорного Вовка!"
        ),
        'act1_q': "Хто візьметься за першу ниточку розслідування?",
        'act1_opt1': "1. [Вибір Френка - Логіка] Вирушити до Міського архіву Бейпорта, щоб знайти історичний журнал і дізнатися більше про символи та контрабандистів.",
        'act1_opt2': "2. [Вибір Джо - Дія] Вирушити до гавані Бейпорта, де Чет знайшов пляшку, щоб оглянути покинуті катери та знайти фізичні докази.",
        'act1_out1': (
            "\nВи вирішуєте діяти обережно і раціонально. Поки Чет доїдає картоплю, Френк веде команду\n"
            "до затишних, наповнених запахом старої шкіри та паперу залів Міського архіву Бейпорта.\n"
            "Тут ховаються відповіді на всі історичні таємниці міста..."
        ),
        'act1_out2': (
            "\nРевіння двигунів ваших мотоциклів розриває тишу! Ви вирішуєте не втрачати часу.\n"
            "Джо веде команду прямо до старих дерев'яних причалів у північній частині гавані.\n"
            "Тут, серед іржавих барж та запаху мазуту, ховається щось підозріле..."
        ),
        
        # Акт II (Френк)
        'act2_f_title': "\n--- АКТ II: ТАЄМНИЦІ МІСЬКОГО АРХІВУ (ГІЛКА ФРЕНКА) ---",
        'act2_f_text': (
            "У тихих залах архіву панує напівтемрява. Старий архівіст містер Епплтон дрімає за столом.\n"
            "Френк знаходить покажчик старовинних книг, але потрібний історичний журнал капітана Блеквуда\n"
            "захований у секретному закритому фонді. На залізних дверцятах фонду висить кодовий замок-головоломка,\n"
            "а поруч лежить аркуш із загадкою від колишнього доглядача:\n\n"
            "«Я завжди голодний, мене треба постійно годувати. Але якщо ти напоїш мене водою — я помру.\n"
            "Відповідь на цю загадку вкаже на назву полиці, де лежить ключ від моїх таємниць»."
        ),
        'act2_f_q': "Яка правильна відповідь на загадку?",
        'act2_f_opt1': "1. ВОДА (WATER / ВОДА)",
        'act2_f_opt2': "2. ВОГОНЬ (FIRE / ОГОНЬ)",
        'act2_f_out1': (
            "\nНеправильно! Ви вводите код 'ВОДА', і раптом зверху спрацьовує стара протипилова сигналізація!\n"
            "На вас висипається хмара старого порошку. Ви кашляєте, містер Епплтон прокидається і починає бурчати.\n"
            "Проте, поки він відвертається, Френк спритно знаходить правильну полицю в секції 'Вогонь та попіл'.\n"
            "Ви забираєте журнал і поспішаєте геть, хоча на вашому одязі лишилися білі сліди (Штраф очок!)."
        ),
        'act2_f_out2': (
            "\nБлискуче! Вогонь — це правильна відповідь. Ви підходите до секції 'Вогонь та попіл'.\n"
            "Там, за обкладинкою старої книги про пожежі Бейпорта, ви знаходите залізний ключ та карту проходів!\n"
            "Ви відкриваєте сейф і дізнаєтесь, що вежа контрабандистів має секретний код від дверей.\n"
            "А також ви дізнаєтесь про легенду: 'Секретний код вежі дорівнює сумі очей Вовка та вітрил шхуни'."
        ),
        
        # Акт II (Джо)
        'act2_j_title': "\n--- АКТ II: СЛІДИ НА ПРИЧАЛІ (ГІЛКА ДЖО) ---",
        'act2_j_text': (
            "Гавань зустрічає вас густим туманом та криками чайок. Досліджуючи причал, Джо помічає\n"
            "напівзатоплений старий катер, пришвартований біля покинутого рибного складу. На його борту\n"
            "фарбою нанесено номер: 'B-7-2-5'. Катер замкнений, але крізь каламутне скло видно бортовий журнал.\n"
            "Чет Мортон шепоче:\n"
            "— Ой, хлопці, дивіться, замок на кабіні цифровий! Тут потрібен чотиризначний код,\n"
            "або нам доведеться виламати ці двері монтуванням!"
        ),
        'act2_j_q': "Як ви спробуєте відчинити кабіну катера?",
        'act2_j_opt1': "1. Зламати замок за допомогою залізного монтування з багажника мотоцикла (Швидко, але шумно).",
        'act2_j_opt2': "2. Спробувати ввести логічний код: суму цифр бортового номера катера (7 + 2 + 5 = 14) у форматі '0014'.",
        'act2_j_out1': (
            "\nКракс! Ви з силою тиснете на монтування. Замок із тріском ламається, залізо скрегоче.\n"
            "Двері відчиняються! Ви забираєте бортовий журнал, де описано графік нічних рейсів контрабандистів.\n"
            "Проте гучний звук привертає увагу місцевого сторожа. Вам доводиться швидко тікати крізь діру в паркані!\n"
            "Ви втрачаєте трохи часу, але докази у вас."
        ),
        'act2_j_out2': (
            "\nНеймовірно! Ви вводите код '0014'. Електронний замок тихо пищить і зелений світлодіод спалахує!\n"
            "Двері кабіни легко відчиняються. Ви забираєте бортовий журнал та знаходите записку від ватажка:\n"
            "«Код від підземелля вежі — це сума очей Чорного Вовка та щогл нашої шхуни в холі».\n"
            "Ви дізнаєтесь важливий доказ абсолютно тихо і без перешкод!"
        ),
        
        # Акт III
        'act3_title': "\n--- АКТ III: ВЕЖА ТА ТАЄМНИЧИЙ ХОЛ ---",
        'act3_text': (
            "Обидві ниточки розслідування знову зводять вас разом біля похмурої вікторіанської вежі\n"
            "на вершині скелі Чорного Вовка. Ніч стає холоднішою, туман повзе по камінню.\n"
            "Ви прокрадаєтесь всередину через старі дубові двері та опиняєтесь у величній, але покинутій залі.\n"
            "На стіні висить величезна, потемніла від часу картина, що зображує Чорного Вовка з криваво-червоними рубіновими очима.\n"
            "Поруч, на дерев'яному столі, стоїть детальний макет старовинної трищоглової шхуни під повними вітрилами."
        ),
        'act3_q': "Що ви зробите перед тим, як іти далі вглиб вежі?",
        'act3_opt1': "1. Уважно оглянути деталі картини вовка та макет шхуни (Запам'ятати важливі числа!).",
        'act3_opt2': "2. Не гаяти часу на старий мотлох і одразу йти коридором до кабінету контрабандистів.",
        'act3_out1': (
            "\nВи підходите ближче. На картині зображений ОДИН вовк із двома яскравими рубіновими очима (число 2).\n"
            "Макет шхуни має ТРИ високі дерев'яні щогли з вітрилами (число 3).\n"
            "Ви запам'ятовуєте ці деталі — справжній детектив ніколи не ігнорує дрібниці!\n"
            "Раптом, коли ви робите крок у бік коридору, підлога під Джо провалюється — це прихований люк-пастка!\n"
            "Ви всі разом летите в глибоку темряву!"
        ),
        'act3_out2': (
            "\nВи вирішуєте поспішати. Але варто вам зробити лише кілька кроків темним коридором,\n"
            "як Джо наступає на хитку дошку. З голосним тріском спрацьовує стародавня пастка!\n"
            "Підлога розверзається під вашими ногами, і ви з криком летите вниз, у глибоке підземелля вежі!"
        ),
        
        # Акт IV
        'act4_title': "\n--- АКТ IV: КРЕПКА ГОЛОВА ТА ЦИФРОВИЙ РЕШЕТНИК ---",
        'act4_text': (
            "Ви приземляєтесь на купу старого прілого сіна в сирому кам'яному підвалі.\n"
            "Раптом у темряві спалахує прожектор, і хтось підступно б'є Джо ззаду по голові важким предметом!\n"
            "Джо падає непритомний. Злочинці швидко зачиняють важкі залізні двері підвалу на засув.\n\n"
            "За кілька хвилин Джо приходить до тями, потираючи потилицю:\n"
            "— Ох, моя бідна потилиця... Наче по ній проїхав товарний потяг! Але нічого, моя голова міцна, бувало й гірше! (Класичний троп!)\n"
            "Ви озираєтесь. Двері підвалу зачинені на кодовий замок-решітку з великим циферблатом від 1 до 10.\n"
            "Поруч на стіні надряпано: «Введіть суму очей Вовка та щогл нашої шхуни з холу вежі»."
        ),
        'act4_q': "Яку цифру ви введете на замку?",
        'act4_opt1': "1. Спробувати ввести правильну цифру на основі побачених раніше підказок (Введіть число від 1 до 10).",
        'act4_opt2': "2. Не думати про коди та спробувати вибити двері важким металевим ломом, що лежить у кутку підвалу.",
        'act4_prompt_code': "Введіть код замка (одна цифра): ",
        'act4_out_correct': (
            "\nКлац-клац! Металеві ригелі замка з тихим шурхотом ховаються у стіну!\n"
            "Код 5 виявився абсолютно правильним (2 ока вовка + 3 щогли шхуни)!\n"
            "Ви відкриваєте двері без жодного шуму та виходите на волю. Чиста перемога вашого розуму!"
        ),
        'act4_out_wrong': (
            "\nЗамок видає неприємний гучний писк — код неправильний! Червона лампа починає блимати.\n"
            "Вам доводиться хапати важкий металевий лом і з усіх сил гатити по замку, поки не прибігла охорона.\n"
            "Зусиллями Джо та Френка ви вибиваєте двері, але втрачаєте дорогоцінний час і сили!"
        ),
        'act4_out_ram': (
            "\nВи берете лом обома руками. Джо робить глибокий вдих, розбігається і з силою\n"
            "таранного удару б'є по замку! Іржавий метал не витримує і з гуркотом ламається.\n"
            "Ви на волі, але цей гучний шум напевно почули контрабандисти внизу!"
        ),
        
        # Акт V
        'act5_title': "\n--- АКТ V: ФІНАЛЬНА СУТИЧКА В ПЕЧЕРІ ---",
        'act5_text': (
            "Ви тихо прокрадаєтесь підземним ходом до секретної морської печери під скелею.\n"
            "Там біля причалу стоїть швидкісний катер контрабандистів. Ватажок Ел «Краба» Берк\n"
            "та його повідомники квапливо вантажать останні ящики з викраденими золотими монетами.\n"
            "Вони вже збираються застрибнути на катер та відчалити!\n\n"
            "Раптом з боку суші з'являється Чет Мортон разом із шерифом Коллігом та підкріпленням!\n"
            "Поліція блокує виходи, але Ел Берк застрибує в катер і намагається завести потужний двигун!"
        ),
        'act5_q': "Як ви зупините втечу Ела Берка?",
        'act5_opt1': "1. [Дія Джо] Здійснити відчайдушний стрибок на борт катера, що відходить, і вступити у відкриту рукопашну сутичку.",
        'act5_opt2': "2. [Дія Френка] Спритно кинути камінь у гвинт двигуна або перерізати натягнутий швартовий канат ножем.",
        'act5_out1_success': (
            "\nДжо розбігається і здійснює неймовірний стрибок прямо на палубу катера!\n"
            "Він миттєво збиває Берка з ніг. Френк швидко стрибає слідом, допомагаючи братові\n"
            "скрутити ватажка бандитів. Катер успішно зупинено! Поліція Бейпорта аплодує вашій сміливості."
        ),
        'act5_out2_success': (
            "\nФренк помічає, що один із швартових канатів все ще натягнутий під водою.\n"
            "Він швидко перерізає його ножем, канат різко смикається і намотується на гвинт катера!\n"
            "Двигун глохне з гучним металевим скреготом. Катер зупиняється, і поліція затримує Берка!"
        ),
        
        # Фінал
        'final_header': "                 ФІНАЛ                       ",
        'final_high': (
            "Вітаємо! Ви блискуче і бездоганно розкрили справу! Ваш рахунок: {score} очок.\n"
            "Ви проявили себе як справжній аналітик та відважний детектив. Усі докази зібрані без зайвого шуму,\n"
            "контрабандистів заарештовано, а унікальну колекцію золотих монет повернуто до музею Бейпорта.\n"
            "Шериф Колліг щиро дякує вам та вашому батькові Фентону Харді за виховання чудових синів.\n"
            "Увечері вдома мама чекає на вас із величезним гарячим пирогом із яловичиною та картоплею,\n"
            "а Чет Мортон уже планує наступні гастрономічні пригоди!"
        ),
        'final_normal': (
            "Справу успішно закрито! Ваш рахунок: {score} очок.\n"
            "Хоча шлях до перемоги був тернистим, ви діяти галасливо і набили кілька синців,\n"
            "а потилиця Джо все ще трохи болить від удару, брати Харді знову довели,\n"
            "що Бейпорт може спати спокійно, коли вони на варті! Попереду на вас чекають нові пригоди!"
        ),
        'final_thanks': "\nДякуємо за гру! Френк та Джо пишалися б вашими рішеннями."
    },
    'en': {
        'select_lang': "Select Language / Оберіть мову / Выберите язык:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Your choice (1-3): ",
        'press_enter': "Press ENTER to start the adventure...",
        'invalid_input': "Please enter 1 or 2.",
        'title': "          THE HARDY BOYS AND THE MYSTERY OF BLACK WOLF ROCK          ",
        'subtitle': "     Super-detective quest with expanded investigation and riddles     ",
        'intro_text': (
            "You are playing as the famous detective brothers, Frank and Joe Hardy from Bayport.\n"
            "Frank (18) is the analytical, logical skeptic, while Joe (17) is\n"
            "impulsive, strong, and a brave athlete.\n"
            "Together with your best friend Chet Morton, you find yourselves at the center of a new mysterious case!"
        ),
        'act1_title': "\n--- ACT I: A FULL BEGINNING & THE MYSTERIOUS BOTTLE ---",
        'act1_text': (
            "You are sitting in the cozy 'Sailor's Haven' diner in Bayport.\n"
            "On the table before you is a culinary masterpiece: juicy double cheeseburgers\n"
            "with a golden crispy crust of toasted bacon, hot French fries heavily sprinkled with spices,\n"
            "and huge vanilla milkshakes topped with whipped cream.\n"
            "You are just enjoying this delicious food when Chet Morton pulls something strange from his backpack.\n\n"
            "— Guys, look at this! — Chet whispers, looking around. — I fished this out of the bay.\n"
            "He places a wet glass bottle on the table. Inside is an old parchment with mysterious\n"
            "symbols and a rough map leading to an abandoned smugglers' tower on Black Wolf Rock!"
        ),
        'act1_q': "Who will take on the first thread of the investigation?",
        'act1_opt1': "1. [Frank's Choice - Logic] Head to the Bayport City Archives to find an old logbook and learn about the symbols.",
        'act1_opt2': "2. [Joe's Choice - Action] Go to the Bayport Harbor where Chet found the bottle, to inspect abandoned boats for physical clues.",
        'act1_out1': (
            "\nYou decide to act carefully and rationally. While Chet finishes his fries, Frank leads the team\n"
            "to the cozy halls of the Bayport City Archives, smelling of old leather and paper.\n"
            "Here, the answers to all the historical secrets of the city are hidden..."
        ),
        'act1_out2': (
            "\nThe roar of your motorcycle engines shatters the silence! You decide not to waste time.\n"
            "Joe leads the team straight to the old wooden docks in the northern part of the harbor.\n"
            "Here, among rusty barges and the smell of fuel oil, something suspicious is hiding..."
        ),
        'act2_f_title': "\n--- ACT II: SECRETS OF THE CITY ARCHIVES (FRANK'S BRANCH) ---",
        'act2_f_text': (
            "Semi-darkness reigns in the quiet halls of the archives. The old archivist Mr. Appleton is dozing at his desk.\n"
            "Frank finds an index of ancient books, but the historical logbook of Captain Blackwood is\n"
            "locked in the secret closed archives. A combination lock puzzle hangs on the iron door,\n"
            "and next to it lies a note with a riddle from the former caretaker:\n\n"
            "\"I am always hungry, I must be fed. But if you give me water — I will die.\n"
            "The answer to this riddle will point to the shelf where the key to my secrets lies.\""
        ),
        'act2_f_q': "What is the correct answer to the riddle?",
        'act2_f_opt1': "1. WATER",
        'act2_f_opt2': "2. FIRE",
        'act2_f_out1': (
            "\nIncorrect! You enter the code 'WATER', and suddenly the old dust alarm triggers from above!\n"
            "A cloud of old powder falls on you. You cough, Mr. Appleton wakes up and begins to grumble.\n"
            "However, while his back is turned, Frank quickly finds the correct shelf in the 'Fire and Ash' section.\n"
            "You grab the logbook and hurry away, though covered in white powder (Score penalty!)."
        ),
        'act2_f_out2': (
            "\nBrilliant! Fire is the correct answer. You go to the 'Fire and Ash' section.\n"
            "There, behind the cover of an old book about Bayport fires, you find an iron key and a map of the passages!\n"
            "You open the safe and learn that the smugglers' tower has a secret code for the door.\n"
            "You also learn a legend: 'The secret code of the tower equals the sum of the Wolf's eyes and the schooner's sails.'"
        ),
        'act2_j_title': "\n--- ACT II: SHORELINE FOOTPRINTS (JOE'S BRANCH) ---",
        'act2_j_text': (
            "The harbor greets you with thick fog and screaming seagulls. Inspecting the dock, Joe notices\n"
            "a semi-submerged old speedboat moored near an abandoned fish warehouse. On its hull,\n"
            "the registration number 'B-7-2-5' is painted. The speedboat is locked, but a logbook is visible through the glass.\n"
            "Chet Morton whispers:\n"
            "— Oh, guys, look! The cabin lock is digital! It needs a four-digit code,\n"
            "or we'll have to break this door open with a crowbar!"
        ),
        'act2_j_q': "How will you try to open the speedboat's cabin?",
        'act2_j_opt1': "1. Break the lock using an iron crowbar from the motorcycle trunk (Fast but noisy).",
        'act2_j_opt2': "2. Try to enter a logical code: the sum of the digits of the registration number (7 + 2 + 5 = 14) as '0014'.",
        'act2_j_out1': (
            "\nCrack! You press hard on the crowbar. The lock breaks with a screech.\n"
            "The door swings open! You grab the logbook detailing the smugglers' night runs.\n"
            "However, the loud noise attracts a local watchman. You have to escape quickly through a hole in the fence!\n"
            "You lose some time, but the evidence is in your hands."
        ),
        'act2_j_out2': (
            "\nIncredible! You enter the code '0014'. The digital lock beeps quietly and a green LED lights up!\n"
            "The cabin door opens easily. You grab the logbook and find a note from the leader:\n"
            "\"The code for the tower cellar is the sum of the Black Wolf's eyes and the masts of our schooner in the hall.\"\n"
            "You find crucial evidence quietly and without any trouble!"
        ),
        'act3_title': "\n--- ACT III: THE TOWER & THE MYSTERIOUS HALL ---",
        'act3_text': (
            "Both threads of the investigation bring you back together at the gloomy Victorian tower\n"
            "on top of Black Wolf Rock. The night grows colder, fog creeping over the stones.\n"
            "You slip inside through the old oak doors and find yourselves in a grand but abandoned hall.\n"
            "On the wall hangs a huge painting, darkened with age, depicting a Black Wolf with blood-red ruby eyes.\n"
            "Nearby, on a wooden table, stands a detailed model of an old three-masted schooner under full sail."
        ),
        'act3_q': "What will you do before going further into the tower?",
        'act3_opt1': "1. Carefully inspect the details of the wolf painting and the schooner model (Remember important numbers!).",
        'act3_opt2': "2. Waste no time on old junk and go straight down the corridor to the smugglers' office.",
        'act3_out1': (
            "\nYou walk closer. The painting depicts ONE wolf with TWO bright ruby eyes (number 2).\n"
            "The schooner model has THREE tall wooden masts with sails (number 3).\n"
            "You memorize these details — a true detective never ignores the little things!\n"
            "Suddenly, as you take a step toward the corridor, the floor collapses under Joe — it's a hidden trapdoor!\n"
            "You all fall into the deep darkness together!"
        ),
        'act3_out2': (
            "\nYou decide to hurry. But as you take only a few steps down the dark corridor,\n"
            "Joe steps on a loose board. With a loud crack, the ancient trapdoor triggers!\n"
            "The floor opens beneath your feet, and you fall down screaming into the deep cellar of the tower!"
        ),
        'act4_title': "\n--- ACT IV: THE HARD HEAD & THE DIGITAL COMBINATION ---",
        'act4_text': (
            "You land on a pile of old damp hay in a cold stone cellar.\n"
            "Suddenly, a searchlight flashes in the dark, and someone sneakily hits Joe from behind with a heavy object!\n"
            "Joe falls unconscious. The criminals quickly lock the heavy iron door of the cellar.\n\n"
            "A few minutes later, Joe comes to, rubbing his neck:\n"
            "— Ouch, my poor head... Feels like a freight train ran over it! But hey, my head is hard, I've had worse! (Classic trope!)\n"
            "You look around. The cellar door is locked with a combination lock-grate with a large dial from 1 to 10.\n"
            "Inscribed on the wall nearby: 'Enter the sum of the Wolf's eyes and our schooner's masts from the tower hall'."
        ),
        'act4_q': "Which number will you enter on the lock?",
        'act4_opt1': "1. Try to enter the correct digit based on the clues seen earlier (Enter a number from 1 to 10).",
        'act4_opt2': "2. Don't think about codes and try to break the door with a heavy iron crowbar lying in the corner.",
        'act4_prompt_code': "Enter the lock code (one digit): ",
        'act4_out_correct': (
            "\nClick-clack! The metal bolts of the lock quietly retract into the wall!\n"
            "The code 5 was absolutely correct (2 wolf eyes + 3 schooner masts)!\n"
            "You open the door without making any noise and escape to freedom. A pure victory of your intellect!"
        ),
        'act4_out_wrong': (
            "\nThe lock makes a loud, unpleasant beep — the code is wrong! A red light starts flashing.\n"
            "You have to grab a heavy iron crowbar and smash the lock with all your might before the guards arrive.\n"
            "With Joe and Frank's combined efforts, you break the door open, but you lose precious time and energy!"
        ),
        'act4_out_ram': (
            "\nYou hold the crowbar with both hands. Joe takes a deep breath, runs, and rams the lock\n"
            "with full force! The rusty metal cannot withstand and breaks with a crash.\n"
            "You are free, but the smugglers below have definitely heard this loud noise!"
        ),
        'act5_title': "\n--- ACT V: THE FINAL CONFRONTATION IN THE CAVE ---",
        'act5_text': (
            "You quietly sneak through a secret passage to a hidden sea cave under the rock.\n"
            "There, a fast smugglers' speedboat is moored. The leader, Al 'Crab' Burke,\n"
            "and his henchmen are quickly loading the last crates of stolen gold coins.\n"
            "They are already preparing to jump onto the speedboat and set sail!\n\n"
            "Suddenly, Chet Morton appears from the landward side with Sheriff Collig and backup!\n"
            "The police block the exits, but Al Burke jumps into the speedboat and tries to start the powerful engine!"
        ),
        'act5_q': "How will you stop Al Burke's escape?",
        'act5_opt1': "1. [Joe's Action] Make a desperate leap onto the deck of the departing speedboat and engage in a fistfight.",
        'act5_opt2': "2. [Frank's Action] Throw a stone into the propeller or cut the tense mooring rope with a knife.",
        'act5_out1_success': (
            "\nJoe runs and makes an incredible leap right onto the speedboat's deck!\n"
            "He immediately knocks Burke down. Frank quickly jumps after him, helping his brother\n"
            "subdue the gang leader. The speedboat is successfully stopped! The Bayport police applaud your courage."
        ),
        'act5_out2_success': (
            "\nFrank notices that one of the mooring ropes is still stretched underwater.\n"
            "He quickly cuts it with a knife, the rope snaps back and tangles in the propeller!\n"
            "The engine stalls with a loud metallic screech. The boat stops, and the police arrest Burke!"
        ),
        'final_header': "                 THE END                       ",
        'final_high': (
            "Congratulations! You solved the case brilliantly! Your score: {score} points.\n"
            "You proved yourselves as true analysts and brave detectives. All evidence was collected quietly,\n"
            "the smugglers are arrested, and the unique gold coin collection is returned to the Bayport Museum.\n"
            "Sheriff Collig sincerely thanks you and your father Fenton Hardy for raising such fine sons.\n"
            "In the evening at home, Mom is waiting for you with a huge hot beef and potato pie,\n"
            "and Chet Morton is already planning your next food adventures!"
        ),
        'final_normal': (
            "The case is successfully closed! Your score: {score} points.\n"
            "Although the path to victory was thorny, you acted noisily and got a few bruises,\n"
            "and Joe's head still hurts from the blow, the Hardy Boys have once again proven\n"
            "that Bayport can sleep soundly with them on duty! New adventures lie ahead!"
        ),
        'final_thanks': "\nThanks for playing! Frank and Joe would be proud of your choices."
    },
    'ru': {
        'select_lang': "Выберите язык / Oберіть мову / Select Language:\n1. Українська\n2. English\n3. Русский",
        'lang_choice_prompt': "Ваш выбор (1-3): ",
        'press_enter': "Нажмите ENTER, чтобы начать приключение...",
        'invalid_input': "Пожалуйста, введите 1 или 2.",
        'title': "          БРАТЬЯ ХАРДИ И ТАЙНА СКАЛЫ ЧЕРНОГО ВОЛКА          ",
        'subtitle': "     Супер-детективный квест с расширенным расследованием и загадками     ",
        'intro_text': (
            "Вы играете за известных братьев-детективов Фрэнка и Джо Харди из городка Бейпорт.\n"
            "Фрэнк (18 лет) — рациональный, логичный скептик, а Джо (17 лет) —\n"
            "импульсивный, сильный и отважный спортсмен.\n"
            "Вместе с лучшим другом Четом Мортоном вы оказываетесь в центре нового загадочного дела!"
        ),
        'act1_title': "\n--- АКТ I: СЫТОЕ НАЧАЛО И ТАИНСТВЕННАЯ БУТЫЛКА ---",
        'act1_text': (
            "Вы сидите в уютной закусочной «Пристанище моряка» в Бейпорте.\n"
            "На столе перед вами — настоящий кулинарный шедевр: сочные двойные чизбургеры\n"
            "с золотистой хрустящей корочкой поджаренного бекона, пышный горячий картофель фри,\n"
            "обильно посыпанный специями, и огромные ванильные молочные коктейли со взбитыми сливками.\n"
            "Вы как раз наслаждаетесь этой прекрасной едой, когда Чет Мортон достает из рюкзака кое-что странное.\n\n"
            "— Ребята, посмотрите на это! — шепчет Чет, оглядываясь. — Я выловил это в бухте.\n"
            "Он кладет на стол мокрую стеклянную бутылку. Внутри виден старый пергамент с загадочными\n"
            "символами и наброском карты, ведущей к заброшенной башне контрабандистов на скале Черного Волка!"
        ),
        'act1_q': "Кто возьмется за первую ниточку расследования?",
        'act1_opt1': "1. [Выбор Фрэнка - Логика] Отправиться в Городской архив Бейпорта, чтобы найти исторический журнал и узнать больше о символах и контрабандистах.",
        'act1_opt2': "2. [Выбор Джо - Действие] Отправиться в гавань Бейпорта, где Чет нашел бутылку, чтобы осмотреть заброшенные катера и найти улики.",
        'act1_out1': (
            "\nВы решаете действовать осторожно и рационально. Пока Чет доедает картошку, Фрэнк ведет команду\n"
            "в тихие, наполненные запахом старой кожи и бумаги залы Городского архива Бейпорта.\n"
            "Здесь скрываются ответы на все исторические тайны города..."
        ),
        'act1_out2': (
            "\nРев двигателей ваших мотоциклов разрывает тишину! Вы решаете не терять времени.\n"
            "Джо ведет команду прямо к старым деревянным причалам в северной части гавани.\n"
            "Здесь, среди ржавых барж и запаха мазута, скрывается что-то подозрительное..."
        ),
        'act2_f_title': "\n--- АКТ II: ТАЙНЫ ГОРОДСКОГО АРХИВА (ВЕТКА ФРЭНКА) ---",
        'act2_f_text': (
            "В тихих залах архива царит полумрак. Старый архивариус мистер Эпплтон дремлет за столом.\n"
            "Фрэнк находит указатель старинных книг, но нужный исторический журнал капитана Блэквуда\n"
            "спрятан в секретном закрытом фонде. На железной дверце фонда висит кодовый замок-головоломка,\n"
            "а рядом лежит листок с загадкой от прежнего смотрителя:\n\n"
            "«Я всегда голоден, меня нужно постоянно кормить. Но если ты напоишь меня водой — я умру.\n"
            "Ответ на эту загадку укажет на название полки, где лежит ключ от моих тайн»."
        ),
        'act2_f_q': "Какой правильный ответ на загадку?",
        'act2_f_opt1': "1. ВОДА (WATER / ВОДА)",
        'act2_f_opt2': "2. ОГОНЬ (FIRE / ОГОНЬ)",
        'act2_f_out1': (
            "\nНеправильно! Вы вводите код 'ВОДА', и вдруг сверху срабатывает старая противопылевая сигнализация!\n"
            "На вас высыпается облако старого порошка. Вы кашляете, мистер Эпплтон просыпается и начинает ворчать.\n"
            "Однако, пока он отворачивается, Фрэнк ловко находит правильную полку в секции 'Огонь и пепел'.\n"
            "Вы забираете журнал и спешите прочь, хотя на вашей одежде остались белые следы (Штраф очков!)."
        ),
        'act2_f_out2': (
            "\nБлестяще! Огонь — это правильный ответ. Вы подходите к секции 'Огонь и пепел'.\n"
            "Там, за обложкой старой книги о пожарах Бейпорта, вы находите железный ключ и карту проходов!\n"
            "Вы открываете сейф и узнаете, что у башни контрабандистов есть секретный код от дверей.\n"
            "А также вы узнаете легенду: 'Секретный код башни равен сумме глаз Волка и парусов шхуны'."
        ),
        'act2_j_title': "\n--- АКТ II: СЛЕДЫ НА ПРИЧАЛЕ (ВЕТКА ДЖО) ---",
        'act2_j_text': (
            "Гавань встречает вас густым туманом и криками чаек. Осматривая причал, Джо замечает\n"
            "полузатопленный старый катер, пришвартованный у заброшенного рыбного склада. На его борту\n"
            "краской нанесен номер: 'B-7-2-5'. Катер заперт, но сквозь мутное стекло виден бортовой журнал.\n"
            "Чет Мортон шепчет:\n"
            "— Ой, ребята, смотрите, замок на кабине цифровой! Тут нужен четырехзначный код,\n"
            "или нам придется выломать эту дверь монтировкой!"
        ),
        'act2_j_q': "Как вы попытаетесь открыть кабину катера?",
        'act2_j_opt1': "1. Взломать замок с помощью железной монтировки из багажника мотоцикла (Быстро, но шумно).",
        'act2_j_opt2': "2. Попробовать ввести логичный код: сумму цифр бортового номера катера (7 + 2 + 5 = 14) в формате '0014'.",
        'act2_j_out1': (
            "\nХрусть! Вы с силой давите на монтировку. Замок с треском ломается, железо скрежещет.\n"
            "Дверь открывается! Вы забираете бортовой журнал, где описан график ночных рейсов контрабандистов.\n"
            "Однако громкий звук привлекает внимание местного сторожа. Вам приходится быстро убегать через дыру в заборе!\n"
            "Вы теряете немного времени, но улики у вас."
        ),
        'act2_j_out2': (
            "\nНевероятно! Вы вводите код '0014'. Электронный замок тихо пищит, и загорается зеленый светодиод!\n"
            "Дверь кабины легко открывается. Вы забираете бортовой журнал и находите записку от главаря:\n"
            "«Код от подземелья башни — это сумма глаз Черного Волка и мачт нашей шхуны в холле».\n"
            "Вы находите важную улику абсолютно тихо и без каких-либо препятствий!"
        ),
        'act3_title': "\n--- АКТ III: БАШНЯ И ТАИНСТВЕННЫЙ ХОЛ ---",
        'act3_text': (
            "Обе ниточки расследования снова сводят вас вместе у мрачной викторианской башни\n"
            "на вершине скалы Черного Волка. Ночь становится холоднее, туман ползет по камням.\n"
            "Вы пробираетесь внутрь через старые дубовые двери и оказываетесь в величественном, но заброшенном зале.\n"
            "На стене висит огромная, потемневшая от времени картина, изображающая Черного Волка с кроваво-красными рубиновыми глазами.\n"
            "Рядом, на деревянном столе, стоит детальный макет старинной трехмачтовой шхуны под полными парусами."
        ),
        'act3_q': "Что вы сделаете перед тем, как идти дальше вглубь башни?",
        'act3_opt1': "1. Внимательно осмотреть детали картины волка и макет шхуны (Запомнить важные числа!).",
        'act3_opt2': "2. Не терять времени на старый хлам и сразу идти по коридору к кабинету контрабандистов.",
        'act3_out1': (
            "\nВы подходите ближе. На картине изображен ОДИН волк с ДВУМЯ яркими рубиновыми глазами (число 2).\n"
            "Макет шхуны имеет ТРИ высокие деревянные мачты с парусами (число 3).\n"
            "Вы запоминаете эти детали — настоящий детектив никогда не игнорирует мелочи!\n"
            "Вдруг, когда вы делаете шаг в сторону коридора, пол под Джо проваливается — это скрытый люк-ловушка!\n"
            "Вы все вместе летите в глубокую темноту!"
        ),
        'act3_out2': (
            "\nВы решаете торопиться. Но стоит вам сделать лишь несколько шагов по темному коридору,\n"
            "как Джо наступает на шаткую доску. С громким треском срабатывает старинная ловушка!\n"
            "Пол разверзается под вашими ногами, и вы с криком летите вниз, в глубокое подземелье башни!"
        ),
        'act4_title': "\n--- АКТ IV: КРЕПКАЯ ГОЛОВА И ЦИФРОВОЙ РЕШАТЕЛЬ ---",
        'act4_text': (
            "Вы приземляетесь на кучу старого прелого сена в сыром каменном подвале.\n"
            "Вдруг в темноте вспыхивает прожектор, и кто-то подло бьет Джо сзади по голове тяжелым предметом!\n"
            "Джо падает без чувств. Преступники быстро закрывают тяжелую железную дверь подвала на засов.\n\n"
            "Через несколько минут Джо приходит в себя, потирая затылок:\n"
            "— Ох, моя бедная голова... Как будто по ней товарный поезд проехал! Но ничего, моя голова крепка, бывало и хуже! (Классический троп!)\n"
            "Вы осматриваетесь. Дверь подвала закрыта на кодовый замок-решетку с большим циферблатом от 1 до 10.\n"
            "Рядом на стене нацарапано: «Введите сумму глаз Волка и мачт нашей шхуны из холла башни»."
        ),
        'act4_q': "Какую цифру вы введете на замке?",
        'act4_opt1': "1. Попробовать ввести правильную цифру на основе увиденных ранее подсказок (Введите число от 1 до 10).",
        'act4_opt2': "2. Не думать о кодах и попытаться выбить дверь тяжелым металлическим ломом, лежащим в углу подвала.",
        'act4_prompt_code': "Введите код замка (одна цифра): ",
        'act4_out_correct': (
            "\nЩелк-щелк! Металлические ригели замка с тихим шорохом скрываются в стене!\n"
            "Код 5 оказался абсолютно правильным (2 глаза волка + 3 мачты шхуны)!\n"
            "Вы открываете дверь без малейшего шума и выходите на свободу. Чистая победа вашего разума!"
        ),
        'act4_out_wrong': (
            "\nЗамок издает неприятный громкий писк — код неправильный! Красная лампа начинает мигать.\n"
            "Вам приходится хватать тяжелый металлический лом и со всей силы колотить по замку, пока не прибежала охрана.\n"
            "Усилиями Джо и Фрэнка вы выбиваете дверь, но теряете драгоценное время и силы!"
        ),
        'act4_out_ram': (
            "\nВы берете лом обеими руками. Джо делает глубокий вдох, разбегается и со всей силы\n"
            "таранного удара бьет по замку! Ржавый металл не выдерживает и с грохотом ломается.\n"
            "Вы на свободе, но этот громкий шум наверняка услышали контрабандисты внизу!"
        ),
        'act5_title': "\n--- АКТ V: ФИНАЛЬНАЯ СХВАТКА В ПЕЩЕРЕ ---",
        'act5_text': (
            "Вы тихо пробираетесь по подземному ходу к секретной морской пещере под скалой.\n"
            "Там у причала стоит скоростной катер контрабандистов. Главарь Эл «Краб» Берк\n"
            "и его сообщники торопливо загружают последние ящики с похищенными золотыми монетами.\n"
            "Они уже собираются запрыгнуть на катер и отчалить!\n\n"
            "Вдруг со стороны суши появляется Чет Мортон вместе с шерифом Коллигом и подкреплением!\n"
            "Полиция блокирует выходы, но Эл Берк запрыгивает в катер и пытается завести мощный двигатель!"
        ),
        'act5_q': "Как вы остановите побег Эла Берка?",
        'act5_opt1': "1. [Действие Джо] Совершить отчаянный прыжок на борт отходящего катера и вступить в открытую рукопашную схватку.",
        'act5_opt2': "2. [Действие Фрэнка] Ловко бросить камень в винт двигателя или перерезать натянутый швартовый канат ножом.",
        'act5_out1_success': (
            "\nДжо разбегается и совершает невероятный прыжок прямо на палубу катера!\n"
            "Он мгновенно сбивает Берка с ног. Фрэнк быстро прыгает следом, помогая брату\n"
            "скрутить главаря бандитов. Катер успешно остановлен! Полиция Бейпорта аплодирует вашей смелости."
        ),
        'act5_out2_success': (
            "\nФрэнк замечает, что один из швартовых канатов все еще натянут под водой.\n"
            "Он быстро перерезает его ножом, канат резко дергается и наматывается на винт катера!\n"
            "Двигатель глохнет с громким металлическим скрежетом. Катер останавливается, и полиция задерживает Берка!"
        ),
        'final_header': "                 ФИНАЛ                       ",
        'final_high': (
            "Поздравляем! Вы блестяще и безупречно раскрыли дело! Ваш счет: {score} очков.\n"
            "Вы проявили себя как настоящий аналитик и отважный детектив. Все улики собраны без лишнего шума,\n"
            "контрабандисты арестованы, а уникальная коллекция золотых монет возвращена в музей Бейпорта.\n"
            "Шериф Коллиг искренне благодарит вас и вашего отца Фентона Харди за воспитание замечательных сыновей.\n"
            "Вечером дома мама ждет вас с огромным горячим пирогом с говядиной и картофелем,\n"
            "а Чет Мортон уже планирует следующие гастрономические приключения!"
        ),
        'final_normal': (
            "Дело успешно закрыто! Ваш счет: {score} очок.\n"
            "Хотя путь к победе был тернистым, вы действовали шумно и набили несколько синяков,\n"
            "а затылок Джо все еще немного болит от удара, братья Харди снова доказали,\n"
            "что Бейпорт может спать спокойно, когда они на посту! Впереди вас ждут новые приключения!"
        ),
        'final_thanks': "\nСпасибо за игру! Фрэнк и Джо гордились бы вашими решениями."
    }
}

class GameState:
    def __init__(self):
        self.lang = 'ru'
        self.inventory = []
        self.route_taken = None  # 'frank' or 'joe'
        self.fell_together = False
        self.knows_clues = False
        self.score = 0

def print_slow(text, delay=0.015):
    """Prints text slowly for a vintage text adventure feel."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def display_header(lang):
    print("=" * 75)
    print(LOCALIZATION[lang]['title'])
    print(LOCALIZATION[lang]['subtitle'])
    print("=" * 75)
    print()

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
        choice = input("\n-> ").strip()
        
        if choice == '1':
            state.route_taken = 'frank'
            state.score += 15
            state.inventory.append('archive_pass')
            print_slow(loc['act1_out1'])
            act_2_frank(state)
            break
        elif choice == '2':
            state.route_taken = 'joe'
            state.score += 10
            state.inventory.append('crowbar')
            print_slow(loc['act1_out2'])
            act_2_joe(state)
            break
        else:
            print(loc['invalid_input'])

def act_2_frank(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act2_f_title'])
    print_slow(loc['act2_f_text'])
    
    while True:
        print("\n" + loc['act2_f_q'])
        print(loc['act2_f_opt1'])
        print(loc['act2_f_opt2'])
        choice = input("\n-> ").strip()
        
        if choice == '1':
            state.score -= 5
            print_slow(loc['act2_f_out1'])
            break
        elif choice == '2':
            state.score += 25
            state.inventory.append('cellar_clue_paper')
            print_slow(loc['act2_f_out2'])
            break
        else:
            print(loc['invalid_input'])
            
    act_3(state)

def act_2_joe(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act2_j_title'])
    print_slow(loc['act2_j_text'])
    
    while True:
        print("\n" + loc['act2_j_q'])
        print(loc['act2_j_opt1'])
        print(loc['act2_j_opt2'])
        choice = input("\n-> ").strip()
        
        if choice == '1':
            state.score -= 5
            print_slow(loc['act2_j_out1'])
            break
        elif choice == '2':
            state.score += 25
            state.inventory.append('cellar_clue_note')
            print_slow(loc['act2_j_out2'])
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
        choice = input("\n-> ").strip()
        
        if choice == '1':
            state.knows_clues = True
            state.score += 20
            print_slow(loc['act3_out1'])
            break
        elif choice == '2':
            state.score += 5
            print_slow(loc['act3_out2'])
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
        choice = input("\n-> ").strip()
        
        if choice == '1':
            code_input = input(loc['act4_prompt_code']).strip()
            if code_input == '5':
                state.score += 30
                print_slow(loc['act4_out_correct'])
                break
            else:
                state.score -= 10
                print_slow(loc['act4_out_wrong'])
                # Proceed to raw forcing after alarm fail
                print_slow(loc['act4_out_ram'])
                break
        elif choice == '2':
            state.score += 10
            print_slow(loc['act4_out_ram'])
            break
        else:
            print(loc['invalid_input'])
            
    act_5(state)

def act_5(state):
    loc = LOCALIZATION[state.lang]
    print_slow(loc['act5_title'])
    print_slow(loc['act5_text'])
    
    while True:
        print("\n" + loc['act5_q'])
        print(loc['act5_opt1'])
        print(loc['act5_opt2'])
        choice = input("\n-> ").strip()
        
        if choice == '1':
            state.score += 20
            print_slow(loc['act5_out1_success'])
            break
        elif choice == '2':
            state.score += 25
            print_slow(loc['act5_out2_success'])
            break
        else:
            print(loc['invalid_input'])
            
    # Game Over / Final Calculation
    print_slow("\n=============================================")
    print_slow(loc['final_header'])
    print_slow("=============================================\n")
    
    if state.score >= 90:
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
