#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys

# Localization Dictionary containing Ukrainian, English, and Russian languages.
LOCALIZATION = {
    'uk': {
        'title': "НЕНСІ ДРЮ ТА ТАЄМНИЧІ СХОДИ (КВЕСТ)",
        'subtitle': "За мотивами класичного детективу Керолайн Кін",
        'press_enter': "Натисніть ENTER, щоб розпочати пригоду...",
        'intro_text': (
            "Ви граєте за Ненсі Дрю — відважну 18-річну детективку з Рівер-Гайтс.\n"
            "Ваше вміння розгадувати таємниці відоме далеко за межами міста,\n"
            "а ваші найкращі подруги — кузини Бесс Марвін та Джесс Фейн — завжди поруч,\n"
            "навіть якщо Бесс часом воліла б залишитися вдома з тарілкою тістечок.\n"
        ),
        'act1_title': "\n--- АКТ I: ТРИВОЖНИЙ ДЗВІНОК З TWIN ELMS ---",
        'act1_text': (
            "Ви перебуваєте у затишній вітальні власного будинку Дрю.\n"
            "Навколо розливається аромат свіжоспеченого яблучного пирога Ганни Груен.\n"
            "Раптом гучно калатає телефон. Ви знімаєте слухавку — це ваша подруга Хелен Корнінг.\n\n"
            "— Ненсі! — схвильовано вигукує вона. — У маєтку Twin Elms моїх літніх тітоньок\n"
            "кояться дивні речі! Серед ночі чутно кроки, самі відчиняються вікна, а stara шкатулка\n"
            "грає без ключа! Вони кажуть, що в будинку привид, і якийсь забудовник Натан Гомбер\n"
            "змушує їх продати будинок за безцінь!"
        ),
        'act1_q': "Як ви вчините?",
        'act1_opt1': "1. Вирушити негайно самотужки на своєму синьому родстері, щоб не гаяти часу.",
        'act1_opt2': "2. Зателефонувати кузинам Бесс Марвін та Джесс Фейн, щоб узяти їх із собою.",
        'act1_choice_prompt': "\nВаш вибір (1 або 2): ",
        'act1_out1': (
            "\nВи вирішуєте діяти негайно! Ви берете ліхтарик і стрибаєте в синій родстер.\n"
            "Ви мчите на околицю міста до темних силуетів Twin Elms."
        ),
        'act1_out2': (
            "\nВи телефонуєте дівчатам. Через 15 хвилин ваш синій родстер уже забирає подруг.\n"
            "Джесс Фейн, поправляючи коротку зачіску, захоплено вигукує:\n"
            "— Hypers! Таємничий маєток та привиди! Оце так пригода!\n"
            "Бесс Марвін тремтить на задньому сидінні:\n"
            "— Ой, дівчата... А раптом привид справжній? І взагалі, я забула взяти кекси з собою..."
        ),
        'invalid_input': "Будь ласка, введіть 1 або 2.",
        'act2_title': "\n--- АКТ II: СЕКРЕТИ ПОДВІЙНИХ В'ЯЗІВ ---",
        'act2_text': (
            "Ви прибуваєте до Twin Elms. Маєток виглядає величним, але занедбаним.\n"
            "Сестри Тернбулл зустрічають вас на порозі, бліді від страху.\n"
            "Раптом у глибині вітальні чутно різкий звук — старовинна музична шкатулка\n"
            "починає грати сама по собі дивну, тужливу мелодію."
        ),
        'act2_team': (
            "\nБесс Марвін з вереском ховається за вашу спину:\n"
            "— А-а-а! Це він! Привид старого полковника!\n"
            "Джесс Фейн рішуче виступає вперед, стискаючи кулаки:\n"
            "— Спокійно, Бесс! Ненсі, дивись, підлога біля стіни вкрита пилом, але там є свіжі сліди!"
        ),
        'act2_solo': (
            "\nВи самостійно заходите до вітальні. Вітер свистить у щілинах дверей.\n"
            "Ви помічаєте на підлозі свіжі сліди важких чоловічих черевиків, які ведуть до стіни."
        ),
        'act2_q': "Що ви вирішите дослідити першим?",
        'act2_opt1': "1. Старовинний підлоговий годинник у кутку, з-під якого відчувається легкий протяг.",
        'act2_opt2': "2. Великий портрет засновника роду на стіні, де кузина Бесс помітила рух тіней.",
        'act2_out1': (
            "\nВи підходите до годинника. Він стоїть і показує рівно 12:00.\n"
            "Проте за ним є прихований зазор! Ви намацуєте дерев'яну панель збоку,\n"
            "натискаєте на неї, і раптом частина стіни з тихим скрипом відчиняється!\n"
            "За нею ховаються темні закинуті сходи, що ведуть углиб стін."
        ),
        'act2_out2': (
            "\nВи підходите до портрета. За ним ви не знаходите нічого, крім пилу та павутини.\n"
            "Проте, оглянувши кімнату уважніше під кутом, ви помічаєте, що протяг дме саме\n"
            "зі сторони старовинного підлогового годинника. Ви прямуєте туди і натискаєте\n"
            "секретну панель! Стіна відсувається, відкриваючи круті темні сходи."
        ),
        'act3_title': "\n--- АКТ III: ТАЄМНИЧІ СХОДИ ТА ПАСТКА ---",
        'act3_text': "Ви вмикаєте ліхтарик і починаєте спускатися по закинутих сходах.\n",
        'act3_team': (
            "Джесс Фейн рішуче йде за вами, підсвічуючи шлях екраном телефону.\n"
            "Бесс Марвін залишається нагорі охороняти сестер Тернбулл (і коробку печива).\n"
            "Сходи приводять вас до підземного ходу. На підлозі ви знаходите біле простирадло,\n"
            "яке використовували як маскування, та балончик фосфоресцентної фарби."
        ),
        'act3_solo': (
            "Сходи дуже круті й брудні. Ви спускаєтесь у підземний хід самотужки.\n"
            "Тут пахне сирістю. Ви знаходите докази перебування людини: недопалки та брудну білу тканину."
        ),
        'act3_trap': (
            "\nРаптом важкі залізні двері позаду вас зачиняються з голосним металевим брязкотом!\n"
            "Зверху лунає задоволений сміх Натана Гомбера:\n"
            "— Розумна Дрю! Тобі не варто було сюди лізти. Посидьте тут із подружкою у темряві,\n"
            "поки старі Тернбулл підписують документи про передачу маєтку!\n\n"
            "Ви опинилися у темній пастці. Потрібно негайно вибиратися!"
        ),
        'act3_q': "Як ви спробуєте відчинити замок залізних дверей?",
        'act3_opt1': "1. Спробувати вибити замок силою (використати стару дерев'яну балку, що лежить поруч).",
        'act3_opt2': "2. Використати металеву шпильку для волосся з вашого інвентарю та зламати механізм.",
        'act3_out1_team': (
            "\nВи берете балку разом із Джесс Фейн. Джесс вигукує 'Hypers!' і ви робите сильний таран!\n"
            "З другої спроби старий іржавий замок вилітає з кріплень! Ви вільні!"
        ),
        'act3_out1_solo': (
            "\nВи намагаєтесь вдарити балкою замок самостійно, але вам бракує сили.\n"
            "Ви лише сильно втомлюєтеся. Доведеться шукати інший спосіб..."
        ),
        'act3_out2': (
            "\nКласичний трюк Ненсі Дрю! Ви дістаєте металеву шпильку для волосся,\n"
            "вставляєте її в замкову щілину та обережно повертаєте, прислухаючись до клацання механізму.\n"
            "Кілька секунд напруженого очікування... Клац! Замок піддався! Двері відчиняються!"
        ),
        'act4_title': "\n--- АКТ IV: ВИТОРЖЕННЯ СПРАВЕДЛИВОСТІ ---",
        'act4_text': (
            "Ви вибираєтесь із підземелля через вугільний люк і біжите назад до вітальні маєтку.\n"
            "Там Натан Гомбер уже поклав ручку в тремтячі руки сестри Розмарі, змушуючи її підписати папери.\n"
            "Віллі Вортон стоїть поруч, задоволено потираючи руки."
        ),
        'act4_team': (
            "\nРаптом Бесс Марвін робить неймовірне! Вона хапає важку диванну подушку,\n"
            "штовхає Віллі Вортона на підлогу та сідає зверху на нього!\n"
            "— Тільки спробуй поворухнутися, привиде нещасний! — сердито вигукує вона.\n"
            "Ви з Джесс забігаєте до кімнати і вириваєте контракт з рук Гомбера!"
        ),
        'act4_solo': (
            "\nВи стрімко вриваєтесь до кімнати, вириваєте контракт з рук Гомбера та вигукуєте:\n"
            "— Зупиніться! Ваша таємниця розкрита, містере Гомбер! Вашого 'привида' викрито в підземеллі!\n"
            "Віллі Вортон з переляку намагається втекти, але ви спритно підставляєте йому підніжку."
        ),
        'act4_sheriff': (
            "\nУ цей момент двері маєтку відчиняються, і на порозі з'являється ваш батько Карсон Дрю\n"
            "разом із шерифом МакГіннісом та двома офіцерами поліції!\n\n"
            "— Чудова робота, Ненсі! — каже шериф МакГіннісом. — Ми якраз шукали докази незаконних дій Гомбера.\n"
            "Завдяки твоїй сміливості та доказам з підземелля він проведе багато років за ґратами."
        ),
        'final_header': "                 ФІНАЛ                       ",
        'final_win': (
            "Вам вдалося розкрити справу з максимальним тріумфом! Ваш рахунок: {score} очок.\n"
            "Сестри Тернбулл безмежно вдячні вам та вашим подругам. Вони влаштували велике чаювання\n"
            "зі свіжими шоколадними кексами. Бесс нарешті сита й щаслива, Джесс обговорює нові пригоди,\n"
            "а ваш батько пишається вашим детективним талантом. Рівер-Гайтс у безпеці!"
        ),
        'final_normal': (
            "Ви успішно розкрили справу та врятували маєток! Ваш рахунок: {score} очок.\n"
            "Хоча деякі моменти далися вам непросто, справедливість восторжествувала.\n"
            "Попереду на вас чекають нові таємниці!"
        ),
        'final_thanks': "\nДякуємо за гру! Справжня Ненсі Дрю пишалася б вами."
    },
    'en': {
        'title': "NANCY DREW AND THE HIDDEN STAIRCASE (QUEST)",
        'subtitle': "Based on the classic mystery by Carolyn Keene",
        'press_enter': "Press ENTER to begin your adventure...",
        'intro_text': (
            "You are playing as Nancy Drew — the daring 18-year-old detective from River Heights.\n"
            "Your knack for solving mysteries is known far and wide,\n"
            "and your best friends — cousins Bess Marvin and George Fayne — are always by your side,\n"
            "even if Bess sometimes prefers staying home with a plate of pastries.\n"
        ),
        'act1_title': "\n--- ACT I: A DISTURBING CALL FROM TWIN ELMS ---",
        'act1_text': (
            "You are in the cozy living room of the Drew home.\n"
            "The delightful aroma of Hannah Gruen's freshly baked apple pie fills the air.\n"
            "Suddenly, the phone rings loudly. You pick it up — it's your friend Helen Corning.\n\n"
            "— Nancy! — she gasps. — Strange things are happening at Twin Elms, my elderly aunts' estate!\n"
            "Footsteps are heard at night, windows open on their own, and an old music box\n"
            "plays without a key! They think the house is haunted, and a developer named Nathan Gomber\n"
            "is pressuring them to sell the property for next to nothing!"
        ),
        'act1_q': "What will you do?",
        'act1_opt1': "1. Set off immediately on your own in your blue roadster to save time.",
        'act1_opt2': "2. Call your cousins Bess Marvin and George Fayne to bring them along.",
        'act1_choice_prompt': "\nYour choice (1 or 2): ",
        'act1_out1': (
            "\nYou decide to act immediately! You grab a flashlight and jump into your blue roadster.\n"
            "You speed off to the outskirts of town towards the dark silhouettes of Twin Elms."
        ),
        'act1_out2': (
            "\nYou call the girls. Within 15 minutes, your blue roadster is picking them up.\n"
            "George Fayne, ruffling her short hair, exclaims excitedly:\n"
            "— Hypers! A mysterious estate and ghosts! What an adventure!\n"
            "Bess Marvin shivers in the back seat:\n"
            "— Oh, girls... What if the ghost is real? And besides, I forgot to bring cupcakes with me..."
        ),
        'invalid_input': "Please enter 1 or 2.",
        'act2_title': "\n--- ACT II: THE SECRETS OF TWIN ELMS ---",
        'act2_text': (
            "You arrive at Twin Elms. The estate looks grand but neglected.\n"
            "The Turnbull sisters meet you at the threshold, pale with fear.\n"
            "Suddenly, a sharp sound echoes from the depth of the living room — an antique music box\n"
            "starts playing a strange, mournful melody on its own."
        ),
        'act2_team': (
            "\nBess Marvin screeches and hides behind your back:\n"
            "— Aaaah! It's him! The ghost of the old colonel!\n"
            "George Fayne steps forward resolutely, clenching her fists:\n"
            "— Calm down, Bess! Nancy, look, the floor near the wall is covered in dust, but there are fresh footprints!"
        ),
        'act2_solo': (
            "\nYou enter the living room alone. The wind whistles through the door cracks.\n"
            "You notice fresh footprints of heavy men's boots on the floor leading to the wall."
        ),
        'act2_q': "What will you decide to investigate first?",
        'act2_opt1': "1. The antique grandfather clock in the corner, from which a light draft is felt.",
        'act2_opt2': "2. The grand portrait of the family founder on the wall, where Bess noticed moving shadows.",
        'act2_out1': (
            "\nYou approach the clock. It has stopped and shows exactly 12:00.\n"
            "However, there is a hidden gap behind it! You feel a wooden panel on the side,\n"
            "press it, and suddenly a section of the wall opens with a quiet creak!\n"
            "Behind it lie dark, hidden stairs leading deep into the walls."
        ),
        'act2_out2': (
            "\nYou approach the portrait. Behind it, you find nothing but dust and cobwebs.\n"
            "However, looking around the room more closely, you notice the draft is coming\n"
            "specifically from the direction of the antique grandfather clock. You head there,\n"
            "press the secret panel! The wall slides back, revealing steep, dark stairs."
        ),
        'act3_title': "\n--- ACT III: THE HIDDEN STAIRCASE AND THE TRAP ---",
        'act3_text': "You switch on your flashlight and begin descending the hidden staircase.\n",
        'act3_team': (
            "George Fayne resolutely follows you, lighting the way with her phone screen.\n"
            "Bess Marvin stays upstairs to guard the Turnbull sisters (and the box of cookies).\n"
            "The stairs lead you to an underground passage. On the floor, you find a white sheet\n"
            "used as a disguise, and a can of phosphorescent paint."
        ),
        'act3_solo': (
            "The stairs are very steep and dirty. You descend into the underground passage alone.\n"
            "It smells damp here. You find evidence of human presence: cigarette butts and a dirty white cloth."
        ),
        'act3_trap': (
            "\nSuddenly, the heavy iron door behind you slams shut with a loud metallic clang!\n"
            "From above, Nathan Gomber's satisfied laughter echoes:\n"
            "— Smart Drew! You shouldn't have snooped around. Sit here in the dark with your friend,\n"
            "while the old Turnbulls sign the estate transfer papers!\n\n"
            "You are trapped in the dark. Must get out immediately!"
        ),
        'act3_q': "How will you try to unlock the iron door?",
        'act3_opt1': "1. Try to force the lock (use an old wooden beam lying nearby).",
        'act3_opt2': "2. Use the metal hairpin from your inventory to pick the lock.",
        'act3_out1_team': (
            "\nYou take the beam together with George Fayne. George yells 'Hypers!' and you make a powerful ram!\n"
            "On the second try, the old rusty lock flies off its hinges! You are free!"
        ),
        'act3_out1_solo': (
            "\nYou try to hit the lock with the beam on your own, but you lack the strength.\n"
            "You only get exhausted. You must find another way..."
        ),
        'act3_out2': (
            "\nClassic Nancy Drew trick! You retrieve your metal hairpin,\n"
            "insert it into the keyhole, and gently turn it, listening to the clicks of the mechanism.\n"
            "A few seconds of tense anticipation... Click! The lock gives way! The door opens!"
        ),
        'act4_title': "\n--- ACT IV: JUSTICE PREVAILS ---",
        'act4_text': (
            "You escape the underground through a coal chute and race back to the estate's living room.\n"
            "There, Nathan Gomber has already placed a pen into Rosemary's trembling hands, forcing her to sign.\n"
            "Willie Wharton stands nearby, smugly rubbing his hands."
        ),
        'act4_team': (
            "\nSuddenly Bess Marvin does the unthinkable! She grabs a heavy sofa cushion,\n"
            "shoves Willie Wharton to the floor, and sits right on top of him!\n"
            "— Don't you dare move, you miserable ghost! — she yells angrily.\n"
            "You and George burst into the room and snatch the contract from Gomber's hands!"
        ),
        'act4_solo': (
            "\nYou dash into the room, rip the contract from Gomber's hands, and shout:\n"
            "— Stop! Your secret is out, Mr. Gomber! Your 'ghost' has been exposed in the cellar!\n"
            "Willie Wharton tries to flee in a panic, but you deftly trip him."
        ),
        'act4_sheriff': (
            "\nAt that moment, the estate doors swing open, and your father Carson Drew appears\n"
            "alongside Sheriff McGinnis and two police officers!\n\n"
            "— Great work, Nancy! — says Sheriff McGinnis. — We were just looking for evidence of Gomber's illegal activities.\n"
            "Thanks to your bravery and the clues from the cellar, he will spend many years behind bars."
        ),
        'final_header': "                 FINALE                      ",
        'final_win': (
            "You successfully solved the case with maximum triumph! Your score: {score} points.\n"
            "The Turnbull sisters are immensely grateful to you and your friends. They throw a grand tea party\n"
            "with fresh chocolate cupcakes. Bess is finally full and happy, George is eager for new adventures,\n"
            "and your father is extremely proud of your sleuthing talent. River Heights is safe!"
        ),
        'final_normal': (
            "You successfully solved the case and saved the estate! Your score: {score} points.\n"
            "Even though some moments were tough, justice prevailed.\n"
            "New mysteries lie ahead!"
        ),
        'final_thanks': "\nThank you for playing! The real Nancy Drew would be proud of you."
    },
    'ru': {
        'title': "НЭНСИ ДРЮ И ТАИНСТВЕННАЯ ЛЕСТНИЦА (КВЕСТ)",
        'subtitle': "По мотивам классического детектива Кэролайн Кин",
        'press_enter': "Нажмите ENTER, чтобы начать приключение...",
        'intro_text': (
            "Вы играете за Нэнси Дрю — отважную 18-летнюю детективку из Ривер-Хайтс.\n"
            "Ваше умение распутывать тайны известно далеко за пределами города,\n"
            "а ваши лучшие подруги — кузины Бесс Марвин и Джесс Фейн — всегда рядом,\n"
            "хотя Бесс иногда предпочла бы остаться дома с тарелкой пирожных.\n"
        ),
        'act1_title': "\n--- АКТ I: ТРЕВОЖНЫЙ ЗВОНОК ИЗ TWIN ELMS ---",
        'act1_text': (
            "Вы находитесь в уютной гостиной дома Дрю.\n"
            "По дому разливается аромат свежеиспеченного яблочного пирога Ханны Груэн.\n"
            "Вдруг громко звонит телефон. Вы снимаете трубку — это ваша подруга Хелен Корнинг.\n\n"
            "— Нэнси! — взволнованно кричит она. — В поместье Twin Elms моих пожилых тетушек\n"
            "творятся странные дела! По ночам слышны шаги, сами открываются окна, а старая шкатулка\n"
            "играет без ключа! Они говорят, что в доме призрак, а какой-то застройщик Натан Гомбер\n"
            "вынуждает их продать дом за бесценок!"
        ),
        'act1_q': "Как вы поступите?",
        'act1_opt1': "1. Отправиться немедленно в одиночку на своем синем родстере, чтобы не терять времени.",
        'act1_opt2': "2. Позвонить кузинам Бесс Марвин и Джесс Фейн, чтобы взять их с собой.",
        'act1_choice_prompt': "\nВаш выбор (1 или 2): ",
        'act1_out1': (
            "\nВы решаете действовать незамедлительно! Вы берете фонарик и прыгаете в синий родстер.\n"
            "Вы мчитесь на окраину города к темным силуэтам Twin Elms."
        ),
        'act1_out2': (
            "\nВы звоните девочкам. Через 15 минут ваш синий родстер уже забирает подруг.\n"
            "Джесс Фейн, поправляя короткую прическу, восторженно восклицает:\n"
            "— Hypers! Таинственное поместье и привидения! Вот это приключение!\n"
            "Бесс Марвин дрожит на заднем сиденье:\n"
            "— Ой, девочки... А вдруг призрак настоящий? И вообще, я забыла взять кексы с собой..."
        ),
        'invalid_input': "Пожалуйста, введите 1 или 2.",
        'act2_title': "\n--- АКТ II: СЕКРЕТЫ ДВОЙНЫХ ВЯЗОВ ---",
        'act2_text': (
            "Вы прибываете в Twin Elms. Поместье выглядит величественным, но запущенным.\n"
            "Сестры Тернбулл встречают вас на пороге, бледные от страха.\n"
            "Вдруг в глубине гостиной раздается резкий звук — старинная музыкальная шкатулка\n"
            "начинает играть сама по себе странную, заунывную мелодию."
        ),
        'act2_team': (
            "\nБесс Марвин с визгом прячется за вашу спину:\n"
            "— А-а-а! Это он! Призрак старого полковника!\n"
            "Джесс Фейн решительно выступает вперед, сжимая кулаки:\n"
            "— Спокойно, Бесс! Нэнси, смотри, пол у стены покрыт пылью, но там есть свежие следы!"
        ),
        'act2_solo': (
            "\nВы самостоятельно заходите в гостиную. Ветер свистит в щелях дверей.\n"
            "Вы замечаете на полу свежие следы тяжелых мужских ботинок, ведущие к стене."
        ),
        'act2_q': "Что вы решите исследовать первым?",
        'act2_opt1': "1. Старинные напольные часы в углу, из-под которых чувствуется легкий сквозняк.",
        'act2_opt2': "2. Большой портрет основателя рода на стене, где кузина Бесс заметила движение теней.",
        'act2_out1': (
            "\nВы подходите к часам. Они стоят и показывают ровно 12:00.\n"
            "Однако за ними есть скрытый зазор! Вы нащупываете деревянную панель сбоку,\n"
            "нажимаете на нее, и вдруг часть стены с тихим скрипом открывается!\n"
            "За ней скрывается темная заброшенная лестница, ведущая вглубь стен."
        ),
        'act2_out2': (
            "\nВы подходите к портрету. За ним вы не находите ничего, кроме пыли и паутины.\n"
            "Однако, осмотрев комнату внимательнее под углом, вы замечаете, что сквозняк дует именно\n"
            "со стороны старинных напольных часов. Вы направляетесь туда и нажимаете\n"
            "секретную панель! Стена отодвигается, открывая крутую темную лестницу."
        ),
        'act3_title': "\n--- АКТ III: ТАИНСТВЕННАЯ ЛЕСТНИЦА И ЛОВУШКА ---",
        'act3_text': "Вы включаете фонарик и начинаете спускаться по заброшенной лестнице.\n",
        'act3_team': (
            "Джесс Фейн решительно идет за вами, подсвечивая путь экраном телефона.\n"
            "Бесс Марвин остается наверху охранять сестер Тернбулл (и коробку печенья).\n"
            "Лестница приводит вас к подземному ходу. На полу вы находите белую простыню,\n"
            "которую использовали для маскировки, и баллончик фосфоресцентной краски."
        ),
        'act3_solo': (
            "Лестница очень крутая и грязная. Вы спускаетесь в подземный ход в одиночку.\n"
            "Здесь пахнет сыростью. Вы находите улики пребывания человека: окурки и грязную белую ткань."
        ),
        'act3_trap': (
            "\nВдруг тяжелая железная дверь позади вас захлопывается с громким металлическим лязгом!\n"
            "Сверху раздается удовлетворенный смех Натана Гомбера:\n"
            "— Умная Дрю! Тебе не следовало сюда соваться. Посидите здесь с подружкой в темноте,\n"
            "поки старые Тернбулл подписывают документы о передаче поместья!\n\n"
            "Вы оказались в темной ловушке. Нужно немедленно выбираться!"
        ),
        'act3_q': "Как вы попытаетесь открыть замок железной двери?",
        'act3_opt1': "1. Попробовать выбить замок силой (использовать старую деревянную балку, лежащую рядом).",
        'act3_opt2': "2. Использовать металлическую шпильку для волос из вашего инвентаря и взломать механизм.",
        'act3_out1_team': (
            "\nВы берете балку вместе с Джесс Фейн. Джесс восклицает 'Hypers!' и вы делаете сильный таран!\n"
            "Со второй попытки старый ржавый замок вылетает из креплений! Вы свободны!"
        ),
        'act3_out1_solo': (
            "\nВы пытаетесь ударить балкой замок самостоятельно, но вам не хватает сил.\n"
            "Вы только сильно устаете. Придется искать другой способ..."
        ),
        'act3_out2': (
            "\nКлассический трюк Нэнси Дрю! Вы достаете металлическую шпильку для волос,\n"
            "вставляете ее в замочную скважину и осторожно поворачиваете, прислушиваясь к щелчкам механизма.\n"
            "Несколько секунд напряженного ожидания... Щелк! Замок поддался! Дверь открывается!"
        ),
        'act4_title': "\n--- АКТ IV: ТОРЖЕСТВО СПРАВЕДЛИВОСТИ ---",
        'act4_text': (
            "Вы выбираетесь из подземелья через угольный люк и бежите назад в гостиную поместья.\n"
            "Там Натан Гомбер уже вложил ручку в дрожащие руки сестры Розмари, заставляя ее подписать бумаги.\n"
            "Вилли Уортон стоит рядом, удовлетворенно потирая руки."
        ),
        'act4_team': (
            "\nВдруг Бесс Марвин делает невероятное! Она хватает тяжелую диванную подушку,\n"
            "толкает Вилли Уортона на пол и садится сверху на него!\n"
            "— Только попробуй пошевелиться, призрак несчастный! — сердито восклицает она.\n"
            "Вы с Джесс забегаете в комнату и вырываете контракт из рук Гомбера!"
        ),
        'act4_solo': (
            "\nВы стремительно врываетесь в комнату, вырываете контракт из рук Гомбера и восклицаете:\n"
            "— Остановитесь! Ваша тайна раскрыта, мистер Гомбер! Ваш 'призрак' разоблачен в подземелье!\n"
            "Вилли Уортон с перепугу пытается сбежать, но вы ловко подставляете ему подножку."
        ),
        'act4_sheriff': (
            "\nВ этот момент двери поместья открываются, и на пороге появляется ваш отец Карсон Дрю\n"
            "вместе с шерифом МакГиннисом и двумя офицерами полиции!\n\n"
            "— Отличная работа, Нэнси! — говорит шериф МакГиннис. — Мы как раз искали улики незаконных действий Гомбера.\n"
            "Благодаря твоей смелости и доказательствам из подземелья он проведет много лет за решеткой."
        ),
        'final_header': "                 ФИНАЛ                       ",
        'final_win': (
            "Вам удалось раскрыть дело с максимальным триумфом! Ваш счет: {score} очков.\n"
            "Сестры Тернбулл бесконечно благодарны вам и вашим подругам. Они устроили большое чаепитие\n"
            "со свежими шоколадными кексами. Бесс наконец-то сыта и счастлива, Джесс обсуждает новые приключения,\n"
            "а ваш отец гордится вашим детективным талантом. Ривер-Хайтс в безопасности!"
        ),
        'final_normal': (
            "Вы успешно раскрыли дело и спасли поместье! Ваш счет: {score} очков.\n"
            "Хотя некоторые моменты дались вам нелегко, справедливость восторжествовала.\n"
            "Впереди вас ждут новые тайны!"
        ),
        'final_thanks': "\nСпасибо за игру! Настоящая Нэнси Дрю гордилась бы вами."
    }
}

class GameState:
    def __init__(self):
        self.inventory = ["металева шпилька" if sys.platform.startswith('win') else "hairpin"]
        self.team_assembled = False
        self.investigated_clock = False
        self.score = 0
        self.lang = 'uk'

    def get_text(self, key, **kwargs):
        text = LOCALIZATION[self.lang].get(key, "")
        if kwargs:
            return text.format(**kwargs)
        return text

def print_slow(text, delay=0.015):
    """Prints text slowly for vintage retro-adventure effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def select_language(state):
    while True:
        print("=" * 60)
        print(" SELECT LANGUAGE / ОБЕРІТЬ МОВУ / ВЫБЕРИТЕ ЯЗЫК")
        print("=" * 60)
        print("1. Українська (Ukrainian)")
        print("2. English (англійська)")
        print("3. Русский (Russian)")
        print("=" * 60)
        choice = input("\nChoice (1-3): ").strip()
        if choice == "1":
            state.lang = "uk"
            state.inventory = ["металева шпилька"]
            break
        elif choice == "2":
            state.lang = "en"
            state.inventory = ["metal hairpin"]
            break
        elif choice == "3":
            state.lang = "ru"
            state.inventory = ["металлическая шпилька"]
            break
        else:
            print("\nInvalid choice / Неправильний вибір / Неверный выбор. Try again.\n")

def display_header(state):
    print("=" * 65)
    print(f"           {state.get_text('title')}            ")
    print(f"        {state.get_text('subtitle')}       ")
    print("=" * 65)
    print()

def intro(state):
    select_language(state)
    display_header(state)
    print_slow(state.get_text('intro_text'))
    print_slow(state.get_text('press_enter'))
    input()
    act_1(state)

def act_1(state):
    print_slow(state.get_text('act1_title'))
    print_slow(state.get_text('act1_text'))
    
    while True:
        print(f"\n{state.get_text('act1_q')}")
        print(state.get_text('act1_opt1'))
        print(state.get_text('act1_opt2'))
        choice = input(state.get_text('act1_choice_prompt')).strip()
        
        if choice == "1":
            state.score += 5
            print_slow(state.get_text('act1_out1'))
            state.inventory.append("flashlight" if state.lang == "en" else "фонарик" if state.lang == "ru" else "ліхтарик")
            break
        elif choice == "2":
            state.team_assembled = True
            state.score += 15
            print_slow(state.get_text('act1_out2'))
            state.inventory.append("flashlight" if state.lang == "en" else "фонарик" if state.lang == "ru" else "ліхтарик")
            break
        else:
            print(state.get_text('invalid_input'))
            
    act_2(state)

def act_2(state):
    print_slow(state.get_text('act2_title'))
    print_slow(state.get_text('act2_text'))
    
    if state.team_assembled:
        print_slow(state.get_text('act2_team'))
    else:
        print_slow(state.get_text('act2_solo'))
        
    while True:
        print(f"\n{state.get_text('act2_q')}")
        print(state.get_text('act2_opt1'))
        print(state.get_text('act2_opt2'))
        choice = input(state.get_text('act1_choice_prompt')).strip()
        
        if choice == "1":
            state.investigated_clock = True
            state.score += 20
            print_slow(state.get_text('act2_out1'))
            break
        elif choice == "2":
            state.score += 10
            print_slow(state.get_text('act2_out2'))
            break
        else:
            print(state.get_text('invalid_input'))
            
    act_3(state)

def act_3(state):
    print_slow(state.get_text('act3_title'))
    print_slow(state.get_text('act3_text'))
    
    if state.team_assembled:
        print_slow(state.get_text('act3_team'))
    else:
        print_slow(state.get_text('act3_solo'))
        
    print_slow(state.get_text('act3_trap'))
    
    while True:
        print(f"\n{state.get_text('act3_q')}")
        print(state.get_text('act3_opt1'))
        print(state.get_text('act3_opt2'))
        choice = input(state.get_text('act1_choice_prompt')).strip()
        
        if choice == "1":
            if state.team_assembled:
                state.score += 15
                print_slow(state.get_text('act3_out1_team'))
            else:
                state.score += 5
                print_slow(state.get_text('act3_out1_solo'))
                continue
            break
        elif choice == "2":
            state.score += 25
            print_slow(state.get_text('act3_out2'))
            break
        else:
            print(state.get_text('invalid_input'))
            
    act_4(state)

def act_4(state):
    print_slow(state.get_text('act4_title'))
    print_slow(state.get_text('act4_text'))
    
    if state.team_assembled:
        print_slow(state.get_text('act4_team'))
    else:
        print_slow(state.get_text('act4_solo'))
        
    print_slow(state.get_text('act4_sheriff'))
    
    # Finale block
    print_slow("\n=============================================")
    print_slow(state.get_text('final_header'))
    print_slow("=============================================")
    
    if state.score >= 50:
        print_slow(state.get_text('final_win', score=state.score))
    else:
        print_slow(state.get_text('final_normal', score=state.score))
        
    print_slow(state.get_text('final_thanks'))

if __name__ == "__main__":
    state = GameState()
    intro(state)
