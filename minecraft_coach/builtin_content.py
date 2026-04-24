from __future__ import annotations

from typing import Any


BUILT_IN_CONTENT_VERSION = 2


def adult_topic_descriptions() -> dict[str, dict[str, str]]:
    return {
        "topic-adult-basics": {
            "ru": "Напряжение, ток, сопротивление, мощность и закон Ома.",
            "pl": "Napięcie, prąd, rezystancja, moc i prawo Ohma.",
            "en": "Voltage, current, resistance, power, and Ohm's law.",
        },
        "topic-adult-safety": {
            "ru": "Автомат, УЗО, PE и базовые правила электрозащиты.",
            "pl": "Wyłącznik, RCD, PE i podstawowe zasady ochrony.",
            "en": "Circuit breaker, RCD, PE, and basic protection rules.",
        },
        "topic-adult-cables": {
            "ru": "Материал жил, сечение, сопротивление, нагрев и падение напряжения.",
            "pl": "Materiał żył, przekrój, rezystancja, nagrzewanie i spadek napięcia.",
            "en": "Conductor material, cross-section, resistance, heating, and voltage drop.",
        },
        "topic-adult-motors": {
            "ru": "Индукция, типы двигателей и базовая защита моторов.",
            "pl": "Indukcja, typy silników i podstawowa ochrona silników.",
            "en": "Induction, motor types, and basic motor protection.",
        },
        "topic-adult-practice": {
            "ru": "Индикатор напряжения, LED и практические безопасные шаги.",
            "pl": "Wskaźnik napięcia, LED i praktyczne bezpieczne kroki.",
            "en": "Voltage tester, LED, and practical safe steps.",
        },
        "topic-memory-core": {
            "ru": "Формулы и короткие правила для быстрого запоминания.",
            "pl": "Wzory i krótkie zasady do szybkiego zapamiętania.",
            "en": "Formulas and short rules for fast memorization.",
        },
    }


def lesson_blocks_by_topic() -> dict[str, list[dict[str, str]]]:
    return {
        "topic-adult-basics": [
            {
                "title_ru": "Напряжение, ток и сопротивление",
                "title_pl": "Napięcie, prąd i rezystancja",
                "title_en": "Voltage, current, and resistance",
                "content_ru": (
                    "Напряжение U показывает, с какой силой источник «толкает» заряд.\n"
                    "Ток I показывает, сколько заряда проходит по цепи.\n"
                    "Сопротивление R мешает току.\n"
                    "База для расчётов: U = I × R, I = U / R, R = U / I."
                ),
                "content_pl": (
                    "Napięcie U pokazuje, z jaką siłą źródło «pcha» ładunek.\n"
                    "Prąd I pokazuje, ile ładunku płynie w obwodzie.\n"
                    "Rezystancja R utrudnia przepływ prądu.\n"
                    "Podstawa obliczeń: U = I × R, I = U / R, R = U / I."
                ),
                "content_en": (
                    "Voltage U is the electrical push.\n"
                    "Current I is the flow of charge.\n"
                    "Resistance R opposes the current.\n"
                    "Core formulas: U = I × R, I = U / R, R = U / I."
                ),
            },
            {
                "title_ru": "Мощность и коэффициент мощности",
                "title_pl": "Moc i współczynnik mocy",
                "title_en": "Power and power factor",
                "content_ru": (
                    "Активная мощность показывает полезную работу нагрузки: P = U × I.\n"
                    "Полная мощность для однофазной цепи: S = U × I.\n"
                    "Коэффициент мощности: cosφ = P / S.\n"
                    "Из формул для однофазной цепи можно вывести связь Q = S × sinφ."
                ),
                "content_pl": (
                    "Moc czynna pokazuje użyteczną pracę odbiornika: P = U × I.\n"
                    "Moc pozorna dla obwodu jednofazowego: S = U × I.\n"
                    "Współczynnik mocy: cosφ = P / S.\n"
                    "Z zależności dla obwodu jednofazowego można wyprowadzić Q = S × sinφ."
                ),
                "content_en": (
                    "Active power is useful work: P = U × I.\n"
                    "Apparent power in a single-phase circuit: S = U × I.\n"
                    "Power factor: cosφ = P / S.\n"
                    "From the single-phase formulas you can derive Q = S × sinφ."
                ),
            },
            {
                "title_ru": "Что запомнить перед тестом",
                "title_pl": "Co zapamiętać przed testem",
                "title_en": "What to remember before the test",
                "content_ru": (
                    "Если напряжение неизменно, то большее сопротивление даёт меньший ток.\n"
                    "Если знаешь любые две величины из U, I и R, третью можно вычислить.\n"
                    "Для быстрых задач сначала выбери нужную формулу, а потом подставляй числа."
                ),
                "content_pl": (
                    "Przy stałym napięciu większa rezystancja daje mniejszy prąd.\n"
                    "Jeśli znasz dowolne dwie wielkości z U, I i R, trzecią można obliczyć.\n"
                    "W szybkich zadaniach najpierw wybierz właściwy wzór, a dopiero potem podstaw liczby."
                ),
                "content_en": (
                    "At constant voltage, more resistance means less current.\n"
                    "If you know any two of U, I, and R, you can calculate the third.\n"
                    "In quick tasks, choose the formula first and substitute numbers second."
                ),
            },
        ],
        "topic-adult-safety": [
            {
                "title_ru": "Автомат и перегрузка",
                "title_pl": "Wyłącznik i przeciążenie",
                "title_en": "Breaker and overload",
                "content_ru": (
                    "Автоматический выключатель защищает проводку и аппарат от перегрузки и короткого замыкания.\n"
                    "Он должен отключить цепь до того, как кабель и аппарат начнут опасно нагреваться.\n"
                    "Автомат защищает прежде всего цепь, а не заменяет все остальные меры защиты."
                ),
                "content_pl": (
                    "Wyłącznik automatyczny chroni przewody i aparat przed przeciążeniem oraz zwarciem.\n"
                    "Ma odłączyć obwód zanim kabel i aparat zaczną niebezpiecznie się nagrzewać.\n"
                    "Wyłącznik chroni przede wszystkim obwód i nie zastępuje wszystkich innych środków ochrony."
                ),
                "content_en": (
                    "A circuit breaker protects wiring and equipment against overload and short circuit.\n"
                    "It should disconnect the circuit before dangerous heating occurs.\n"
                    "A breaker protects the circuit first and does not replace every other protective measure."
                ),
            },
            {
                "title_ru": "УЗО и ток утечки",
                "title_pl": "RCD i prąd upływu",
                "title_en": "RCD and leakage current",
                "content_ru": (
                    "УЗО сравнивает ток, уходящий по фазе, и ток, возвращающийся по нейтрали.\n"
                    "Если появляется разница, это похоже на ток утечки, и устройство отключает цепь.\n"
                    "УЗО повышает защиту человека, но не заменяет защиту от перегрузки и короткого замыкания."
                ),
                "content_pl": (
                    "RCD porównuje prąd wypływający fazą z prądem wracającym przewodem neutralnym.\n"
                    "Jeśli pojawi się różnica, wygląda to jak prąd upływu i urządzenie wyłącza obwód.\n"
                    "RCD zwiększa ochronę człowieka, ale nie zastępuje ochrony przed przeciążeniem i zwarciem."
                ),
                "content_en": (
                    "An RCD compares outgoing and returning current.\n"
                    "If a difference appears, it looks like leakage current and the device disconnects the circuit.\n"
                    "An RCD improves personal protection, but it does not replace overload or short-circuit protection."
                ),
            },
            {
                "title_ru": "PE и выравнивание потенциалов",
                "title_pl": "PE i połączenia wyrównawcze",
                "title_en": "PE and equipotential bonding",
                "content_ru": (
                    "PE-проводник соединяет открытые проводящие части в общую систему защитного уравнивания потенциалов.\n"
                    "При повреждении изоляции по PE может уйти ток повреждения к источнику.\n"
                    "Это снижает опасную разность потенциалов и помогает защитным устройствам отключить цепь."
                ),
                "content_pl": (
                    "Przewód PE łączy dostępne części przewodzące w główny system połączeń wyrównawczych.\n"
                    "Przy uszkodzeniu izolacji prąd uszkodzeniowy może popłynąć przewodem PE do źródła.\n"
                    "To zmniejsza niebezpieczną różnicę potencjałów i pomaga aparaturze ochronnej odłączyć obwód."
                ),
                "content_en": (
                    "The PE conductor bonds exposed conductive parts into the main equipotential system.\n"
                    "During insulation failure it can carry fault current back to the source.\n"
                    "That reduces dangerous touch voltage and helps protective devices disconnect the circuit."
                ),
            },
        ],
        "topic-adult-cables": [
            {
                "title_ru": "Материал и сопротивление",
                "title_pl": "Materiał i rezystancja",
                "title_en": "Material and resistance",
                "content_ru": (
                    "Сопротивление зависит от материала, длины, сечения и температуры проводника.\n"
                    "Медь и алюминий часто используют как проводники, потому что они проводят ток лучше многих других материалов.\n"
                    "Чем выше сопротивление, тем при той же нагрузке больше потери и нагрев."
                ),
                "content_pl": (
                    "Rezystancja zależy od materiału, długości, przekroju i temperatury przewodnika.\n"
                    "Miedź i aluminium są częstymi materiałami żył, bo dobrze przewodzą prąd.\n"
                    "Im większa rezystancja, tym większe straty i nagrzewanie przy tym samym obciążeniu."
                ),
                "content_en": (
                    "Resistance depends on conductor material, length, cross-section, and temperature.\n"
                    "Copper and aluminum are common conductors because they carry current well.\n"
                    "Higher resistance means higher losses and heating under the same load."
                ),
            },
            {
                "title_ru": "Формула проводника",
                "title_pl": "Wzór dla przewodnika",
                "title_en": "Conductor formula",
                "content_ru": (
                    "Для проводника часто используют связь R = ρ × l / S.\n"
                    "Длина l увеличивает сопротивление, а площадь сечения S его уменьшает.\n"
                    "Поэтому длинный и тонкий кабель сильнее греется и даёт большее падение напряжения."
                ),
                "content_pl": (
                    "Dla przewodnika często stosuje się zależność R = ρ × l / S.\n"
                    "Długość l zwiększa rezystancję, a pole przekroju S ją zmniejsza.\n"
                    "Dlatego długi i cienki kabel bardziej się nagrzewa i daje większy spadek napięcia."
                ),
                "content_en": (
                    "For a conductor, a common relation is R = ρ × l / S.\n"
                    "Length l increases resistance, while cross-sectional area S reduces it.\n"
                    "That is why a long, thin cable heats more and causes more voltage drop."
                ),
            },
            {
                "title_ru": "Что проверяют на практике",
                "title_pl": "Co sprawdza się w praktyce",
                "title_en": "What is checked in practice",
                "content_ru": (
                    "Сечение подбирают не «на глаз», а по току, длине линии и условиям монтажа.\n"
                    "Если кабель слишком тонкий, он может перегреваться.\n"
                    "Если линия длинная, может понадобиться большее сечение, чтобы уменьшить падение напряжения."
                ),
                "content_pl": (
                    "Przekrój dobiera się nie «na oko», lecz według prądu, długości linii i warunków montażu.\n"
                    "Jeśli kabel jest zbyt cienki, może się przegrzewać.\n"
                    "Jeśli linia jest długa, może być potrzebny większy przekrój, aby zmniejszyć spadek napięcia."
                ),
                "content_en": (
                    "Cross-section is chosen by current, line length, and installation conditions.\n"
                    "If the cable is too thin, it may overheat.\n"
                    "If the line is long, a larger cross-section may be needed to limit voltage drop."
                ),
            },
        ],
        "topic-adult-motors": [
            {
                "title_ru": "Что делает двигатель",
                "title_pl": "Co robi silnik",
                "title_en": "What a motor does",
                "content_ru": (
                    "Электродвигатель преобразует электрическую энергию в механическое вращение.\n"
                    "На практике часто встречаются двигатели постоянного тока, асинхронные двигатели переменного тока и BLDC.\n"
                    "Для выбора двигателя важны тип нагрузки, режим пуска и защита."
                ),
                "content_pl": (
                    "Silnik elektryczny zamienia energię elektryczną na ruch obrotowy.\n"
                    "W praktyce często spotyka się silniki prądu stałego, silniki indukcyjne AC i BLDC.\n"
                    "Przy doborze ważne są typ obciążenia, rozruch i ochrona."
                ),
                "content_en": (
                    "An electric motor converts electrical energy into mechanical rotation.\n"
                    "Common examples are DC motors, AC induction motors, and BLDC motors.\n"
                    "Load type, start mode, and protection are important when choosing a motor."
                ),
            },
            {
                "title_ru": "Индукция",
                "title_pl": "Indukcja",
                "title_en": "Induction",
                "content_ru": (
                    "Электромагнитная индукция появляется, когда меняется магнитный поток.\n"
                    "Именно эта идея лежит в основе генераторов, трансформаторов и индукционных процессов в электромашинах.\n"
                    "Майкл Фарадей связан с открытием закона электромагнитной индукции."
                ),
                "content_pl": (
                    "Indukcja elektromagnetyczna pojawia się wtedy, gdy zmienia się strumień magnetyczny.\n"
                    "Ta idea leży u podstaw generatorów, transformatorów i procesów indukcyjnych w maszynach elektrycznych.\n"
                    "Michael Faraday jest związany z odkryciem prawa indukcji elektromagnetycznej."
                ),
                "content_en": (
                    "Electromagnetic induction appears when magnetic flux changes.\n"
                    "This idea is fundamental for generators, transformers, and induction effects in electric machines.\n"
                    "Michael Faraday is associated with the discovery of electromagnetic induction."
                ),
            },
            {
                "title_ru": "Защита двигателя",
                "title_pl": "Ochrona silnika",
                "title_en": "Motor protection",
                "content_ru": (
                    "Двигателю мало только обычного автомата: иногда нужна отдельная защита от длительного пуска, заклинивания и обрыва фазы.\n"
                    "Перегрузочное реле подбирают под характеристики мотора.\n"
                    "Защита должна учитывать и двигатель, и кабель двигателя."
                ),
                "content_pl": (
                    "Sam zwykły wyłącznik nie zawsze wystarcza: silnik może wymagać ochrony przed długim rozruchem, zablokowanym wirnikiem i zanikiem fazy.\n"
                    "Przekaźnik przeciążeniowy dobiera się do charakterystyki silnika.\n"
                    "Ochrona powinna uwzględniać zarówno silnik, jak i jego kabel."
                ),
                "content_en": (
                    "A standard breaker is not always enough: a motor may need protection against long start, stalled rotor, and phase loss.\n"
                    "An overload relay is selected to match the motor characteristics.\n"
                    "Protection should cover both the motor and its cable."
                ),
            },
        ],
        "topic-adult-practice": [
            {
                "title_ru": "Проверка напряжения",
                "title_pl": "Sprawdzenie napięcia",
                "title_en": "Checking voltage",
                "content_ru": (
                    "Для проверки наличия напряжения нужен подходящий индикатор напряжения.\n"
                    "Линейка, кисточка или случайный металлический предмет для этого не годятся.\n"
                    "Перед практической работой сначала проверяют, что именно и чем измеряют."
                ),
                "content_pl": (
                    "Do sprawdzania obecności napięcia potrzebny jest odpowiedni wskaźnik napięcia.\n"
                    "Linijka, pędzel ani przypadkowy metalowy przedmiot się do tego nie nadają.\n"
                    "Przed pracą praktyczną trzeba wiedzieć, co i czym mierzymy."
                ),
                "content_en": (
                    "Use a proper voltage indicator to check for voltage.\n"
                    "A ruler, brush, or random metal object is not a measurement tool.\n"
                    "Before practical work, know what you are measuring and which tool you are using."
                ),
            },
            {
                "title_ru": "LED и питание",
                "title_pl": "LED i zasilanie",
                "title_en": "LED and power supply",
                "content_ru": (
                    "Светодиодной ленте нужен подходящий блок питания по напряжению и мощности.\n"
                    "Запас по мощности нужен, чтобы блок не работал всё время на пределе.\n"
                    "Нельзя выбирать источник питания «примерно похожий» по параметрам."
                ),
                "content_pl": (
                    "Taśma LED potrzebuje odpowiedniego zasilacza pod względem napięcia i mocy.\n"
                    "Zapas mocy jest potrzebny, aby zasilacz nie pracował cały czas na granicy możliwości.\n"
                    "Nie wolno wybierać zasilacza tylko dlatego, że jest «mniej więcej podobny»."
                ),
                "content_en": (
                    "An LED strip needs a matching power supply in voltage and power.\n"
                    "A power reserve helps avoid constant full-load operation.\n"
                    "Do not choose a supply just because it looks roughly similar."
                ),
            },
            {
                "title_ru": "Практический выбор кабеля",
                "title_pl": "Praktyczny dobór kabla",
                "title_en": "Practical cable choice",
                "content_ru": (
                    "Перед подключением нагрузки оцени ток, длину линии и сечение кабеля.\n"
                    "Тонкий кабель на большой ток может перегреваться.\n"
                    "Безопасная практика начинается с правильного выбора инструмента и проводника."
                ),
                "content_pl": (
                    "Przed podłączeniem odbiornika oceń prąd, długość linii i przekrój kabla.\n"
                    "Cienki kabel przy dużym prądzie może się przegrzewać.\n"
                    "Bezpieczna praktyka zaczyna się od poprawnego doboru narzędzia i przewodu."
                ),
                "content_en": (
                    "Before connecting a load, estimate the current, line length, and cable cross-section.\n"
                    "A thin cable under high current can overheat.\n"
                    "Safe practice starts with the right tool and the right conductor."
                ),
            },
        ],
        "topic-memory-core": [
            {
                "title_ru": "Как пользоваться карточками",
                "title_pl": "Jak korzystać z fiszek",
                "title_en": "How to use the cards",
                "content_ru": (
                    "Сначала спокойно прочитай формулу или правило.\n"
                    "Попробуй повторить его своими словами.\n"
                    "Потом подтверждай запоминание и переходи к следующей карточке."
                ),
                "content_pl": (
                    "Najpierw spokojnie przeczytaj wzór lub zasadę.\n"
                    "Spróbuj powtórzyć ją własnymi słowami.\n"
                    "Potem potwierdź zapamiętanie i przejdź do kolejnej fiszki."
                ),
                "content_en": (
                    "Read the formula or rule calmly first.\n"
                    "Try to repeat it in your own words.\n"
                    "Then confirm that you remember it and continue."
                ),
            }
        ],
    }


def adult_tasks() -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []

    def add(
        theme: str,
        index: int,
        task_type: str,
        title_ru: str,
        title_pl: str,
        prompt_ru: str,
        prompt_pl: str,
        answer: str | list[str],
        *,
        options: list[str] | None = None,
        support_ru: str = "",
        support_pl: str = "",
    ) -> None:
        tasks.append(
            {
                "id": f"a_{theme}_{index:02d}",
                "mode": "adult",
                "theme": theme,
                "type": task_type,
                "title_ru": title_ru,
                "title_pl": title_pl,
                "prompt_ru": prompt_ru,
                "prompt_pl": prompt_pl,
                "answer": answer,
                "options": options or [],
                "hint_type": "lesson",
                "sort_order": index,
                "source": "built_in",
                "metadata": {
                    "support_ru": support_ru,
                    "support_pl": support_pl,
                },
            }
        )

    add(
        "basics",
        1,
        "choice",
        "Закон Ома",
        "Prawo Ohma",
        "Какая формула выражает напряжение через ток и сопротивление?",
        "Który wzór wyraża napięcie przez prąd i rezystancję?",
        "U = I × R",
        options=["U = I × R", "U = I / R", "U = R / I", "U = P / I"],
        support_ru="Запомни базовую связь: напряжение равно току, умноженному на сопротивление.",
        support_pl="Zapamiętaj podstawową zależność: napięcie równa się prądowi pomnożonemu przez rezystancję.",
    )
    add(
        "basics",
        2,
        "choice",
        "Расчёт тока",
        "Obliczanie prądu",
        "Если U = 12 V и R = 6 Ω, какой ток в цепи?",
        "Jeśli U = 12 V i R = 6 Ω, jaki prąd płynie w obwodzie?",
        "2 A",
        options=["2 A", "6 A", "12 A", "72 A"],
        support_ru="Для тока используй I = U / R. Сначала делим напряжение на сопротивление.",
        support_pl="Dla prądu użyj I = U / R. Najpierw dzielimy napięcie przez rezystancję.",
    )
    add(
        "basics",
        3,
        "choice",
        "Активная мощность",
        "Moc czynna",
        "Какая формула показывает активную мощность в простой цепи?",
        "Który wzór pokazuje moc czynną w prostym obwodzie?",
        "P = U × I",
        options=["P = U × I", "P = U / I", "P = R × I", "P = U + I"],
        support_ru="Активная мощность показывает полезную работу нагрузки. В простом виде: P = U × I.",
        support_pl="Moc czynna opisuje użyteczną pracę odbiornika. W prostym ujęciu: P = U × I.",
    )
    add(
        "basics",
        4,
        "choice",
        "Коэффициент мощности",
        "Współczynnik mocy",
        "Что показывает коэффициент мощности cosφ?",
        "Co pokazuje współczynnik mocy cosφ?",
        "Отношение активной мощности к полной",
        options=[
            "Отношение активной мощности к полной",
            "Отношение сопротивления к току",
            "Отношение частоты к напряжению",
            "Отношение длины кабеля к сечению",
        ],
        support_ru="По определению cosφ = P / S, то есть отношение активной мощности к полной.",
        support_pl="Z definicji cosφ = P / S, czyli stosunek mocy czynnej do mocy pozornej.",
    )
    add(
        "basics",
        5,
        "choice",
        "Сопротивление и ток",
        "Rezystancja i prąd",
        "Что произойдёт с током, если напряжение то же, а сопротивление стало больше?",
        "Co stanie się z prądem, jeśli napięcie pozostaje takie samo, a rezystancja rośnie?",
        "Ток уменьшится",
        options=["Ток уменьшится", "Ток увеличится", "Ничего не изменится", "Напряжение исчезнет"],
        support_ru="При постоянном напряжении ток считают по формуле I = U / R. Большее R даёт меньший I.",
        support_pl="Przy stałym napięciu prąd liczymy ze wzoru I = U / R. Większe R daje mniejszy I.",
    )

    add(
        "safety",
        1,
        "choice",
        "Автомат",
        "Wyłącznik",
        "Что защищает автоматический выключатель?",
        "Co chroni wyłącznik automatyczny?",
        "Проводку от перегрузки и короткого замыкания",
        options=[
            "Проводку от перегрузки и короткого замыкания",
            "Только лампы",
            "Только счётчик",
            "Любую опасность вообще",
        ],
        support_ru="Автомат относится к защите цепи: он нужен против перегрузки и короткого замыкания.",
        support_pl="Wyłącznik należy do ochrony obwodu: działa przeciw przeciążeniu i zwarciu.",
    )
    add(
        "safety",
        2,
        "choice",
        "УЗО",
        "RCD",
        "Для чего нужно УЗО?",
        "Do czego służy RCD?",
        "Для защиты от тока утечки",
        options=[
            "Для защиты от тока утечки",
            "Для повышения напряжения",
            "Для охлаждения кабеля",
            "Для работы двигателя",
        ],
        support_ru="УЗО следит за разницей токов и реагирует на утечку. Это не устройство повышения напряжения.",
        support_pl="RCD śledzi różnicę prądów i reaguje na upływ. To nie jest urządzenie do podnoszenia napięcia.",
    )
    add(
        "safety",
        3,
        "choice",
        "Чего УЗО не заменяет",
        "Czego RCD nie zastępuje",
        "Что УЗО не должно заменять в цепи?",
        "Czego RCD nie powinno zastępować w obwodzie?",
        "Защиту от перегрузки и короткого замыкания",
        options=[
            "Защиту от перегрузки и короткого замыкания",
            "Маркировку проводов",
            "Освещение в комнате",
            "Работу переключателя языка",
        ],
        support_ru="УЗО повышает защиту человека, но защита от перегрузки и КЗ должна оставаться отдельно.",
        support_pl="RCD zwiększa ochronę człowieka, ale ochrona przed przeciążeniem i zwarciem musi pozostać osobno.",
    )
    add(
        "safety",
        4,
        "choice",
        "PE-проводник",
        "Przewód PE",
        "Для чего нужен защитный проводник PE?",
        "Do czego służy przewód ochronny PE?",
        "Для тока повреждения и выравнивания потенциалов",
        options=[
            "Для тока повреждения и выравнивания потенциалов",
            "Только для увеличения частоты",
            "Только для красоты щита",
            "Для питания двигателя",
        ],
        support_ru="PE участвует в системе защитного уравнивания потенциалов и может проводить ток повреждения.",
        support_pl="PE należy do systemu połączeń wyrównawczych i może przewodzić prąd uszkodzeniowy.",
    )
    add(
        "safety",
        5,
        "choice",
        "Повреждение изоляции",
        "Uszkodzenie izolacji",
        "Почему важно быстрое автоматическое отключение при повреждении изоляции?",
        "Dlaczego ważne jest szybkie automatyczne odłączenie przy uszkodzeniu izolacji?",
        "Чтобы уменьшить опасность поражения и перегрева",
        options=[
            "Чтобы уменьшить опасность поражения и перегрева",
            "Чтобы кабель стал мягче",
            "Чтобы увеличить напряжение",
            "Чтобы спрятать ошибку",
        ],
        support_ru="Защита должна ограничить опасные последствия повреждения: риск удара током и нагрев цепи.",
        support_pl="Ochrona ma ograniczyć niebezpieczne skutki uszkodzenia: ryzyko porażenia i nagrzewania obwodu.",
    )

    add(
        "cables",
        1,
        "choice",
        "Материал жил",
        "Materiał żył",
        "Из чего обычно делают токопроводящие жилы кабеля?",
        "Z czego zwykle wykonuje się żyły przewodzące kabla?",
        "Из меди или алюминия",
        options=["Из меди или алюминия", "Из бумаги", "Из резины", "Из стекла"],
        support_ru="Медь и алюминий часто применяют как проводники благодаря хорошей проводимости.",
        support_pl="Miedź i aluminium są częstymi materiałami przewodzącymi dzięki dobrej przewodności.",
    )
    add(
        "cables",
        2,
        "choice",
        "От чего зависит сопротивление",
        "Od czego zależy rezystancja",
        "Что сильнее всего влияет на сопротивление проводника?",
        "Co najbardziej wpływa na rezystancję przewodnika?",
        "Материал, длина, сечение и температура",
        options=[
            "Материал, длина, сечение и температура",
            "Только цвет изоляции",
            "Только название кабеля",
            "Только положение розетки",
        ],
        support_ru="Сопротивление связано с материалом, длиной, сечением и температурой проводника.",
        support_pl="Rezystancja wiąże się z materiałem, długością, przekrojem i temperaturą przewodnika.",
    )
    add(
        "cables",
        3,
        "choice",
        "Формула проводника",
        "Wzór przewodnika",
        "Какая запись соответствует связи R = ρ × l / S?",
        "Który zapis odpowiada zależności R = ρ × l / S?",
        "Длина увеличивает R, а сечение уменьшает R",
        options=[
            "Длина увеличивает R, а сечение уменьшает R",
            "Длина уменьшает R, а сечение увеличивает R",
            "Материал не влияет на R",
            "Температура не влияет на R",
        ],
        support_ru="По формуле R = ρ × l / S длина стоит в числителе, а сечение в знаменателе.",
        support_pl="We wzorze R = ρ × l / S długość jest w liczniku, a przekrój w mianowniku.",
    )
    add(
        "cables",
        4,
        "choice",
        "Тонкий кабель",
        "Cienki kabel",
        "Почему слишком тонкий кабель опасен?",
        "Dlaczego zbyt cienki kabel jest niebezpieczny?",
        "Он может перегреваться",
        options=["Он может перегреваться", "Он всегда охлаждает цепь", "Он повышает частоту", "Разницы нет"],
        support_ru="При том же токе тонкий провод имеет большее сопротивление и сильнее нагревается.",
        support_pl="Przy tym samym prądzie cienki przewód ma większą rezystancję i mocniej się nagrzewa.",
    )
    add(
        "cables",
        5,
        "choice",
        "Длинная линия",
        "Długa linia",
        "Почему для длинной линии иногда берут большее сечение?",
        "Dlaczego dla długiej linii czasem stosuje się większy przekrój?",
        "Чтобы уменьшить сопротивление и падение напряжения",
        options=[
            "Чтобы уменьшить сопротивление и падение напряжения",
            "Чтобы изменить частоту сети",
            "Чтобы убрать автомат",
            "Только чтобы сделать кабель красивее",
        ],
        support_ru="Длинная линия даёт большее сопротивление, поэтому большее сечение помогает уменьшить потери.",
        support_pl="Długa linia daje większą rezystancję, dlatego większy przekrój pomaga zmniejszyć straty.",
    )

    add(
        "motors",
        1,
        "choice",
        "Электромагнитная индукция",
        "Indukcja elektromagnetyczna",
        "Кто связан с открытием закона электромагнитной индукции?",
        "Kto jest związany z odkryciem prawa indukcji elektromagnetycznej?",
        "Michael Faraday",
        options=["Michael Faraday", "Thomas Edison", "Georg Ohm", "James Watt"],
        support_ru="В базовом курсе электрики с законом индукции связывают имя Майкла Фарадея.",
        support_pl="W podstawowej elektrotechnice z prawem indukcji łączy się nazwisko Michaela Faradaya.",
    )
    add(
        "motors",
        2,
        "choice",
        "Что вызывает индукцию",
        "Co wywołuje indukcję",
        "Что нужно для появления электромагнитной индукции?",
        "Co jest potrzebne do pojawienia się indukcji elektromagnetycznej?",
        "Изменение магнитного потока",
        options=["Изменение магнитного потока", "Только красный провод", "Только постоянная температура", "Отсутствие поля"],
        support_ru="Индукция связана не просто с полем, а именно с его изменением во времени.",
        support_pl="Indukcja jest związana nie tylko z polem, lecz właśnie ze zmianą strumienia w czasie.",
    )
    add(
        "motors",
        3,
        "choice",
        "Защита двигателя",
        "Ochrona silnika",
        "Какая дополнительная защита может понадобиться двигателю?",
        "Jaka dodatkowa ochrona może być potrzebna silnikowi?",
        "От длительного пуска, заклинивания и обрыва фазы",
        options=[
            "От длительного пуска, заклинивания и обрыва фазы",
            "Только от языка интерфейса",
            "Только от цвета кнопок",
            "Никакая",
        ],
        support_ru="Для двигателей применяют защиту от перегрузки и аварийных режимов, например длительного пуска и заклинивания.",
        support_pl="Dla silników stosuje się ochronę przed przeciążeniem i stanami awaryjnymi, np. długim rozruchem i zablokowaniem.",
    )
    add(
        "motors",
        4,
        "choice",
        "Тип двигателя",
        "Typ silnika",
        "Как называется бесщёточный двигатель постоянного тока?",
        "Jak nazywa się bezszczotkowy silnik prądu stałego?",
        "BLDC",
        options=["BLDC", "RCD", "PE", "MCB"],
        support_ru="BLDC означает brushless DC motor, то есть бесщёточный двигатель постоянного тока.",
        support_pl="BLDC oznacza brushless DC motor, czyli bezszczotkowy silnik prądu stałego.",
    )

    add(
        "practice",
        1,
        "choice",
        "Индикатор напряжения",
        "Wskaźnik napięcia",
        "Чем проверяют наличие напряжения?",
        "Czym sprawdza się obecność napięcia?",
        "Индикатором напряжения",
        options=["Индикатором напряжения", "Кисточкой", "Линейкой", "Скрепкой"],
        support_ru="Для проверки напряжения нужен измерительный инструмент, а не случайный предмет.",
        support_pl="Do sprawdzenia napięcia potrzebne jest narzędzie pomiarowe, a nie przypadkowy przedmiot.",
    )
    add(
        "practice",
        2,
        "choice",
        "LED-питание",
        "Zasilanie LED",
        "Что нужно светодиодной ленте для нормальной работы?",
        "Czego potrzebuje taśma LED do poprawnej pracy?",
        "Подходящий блок питания по напряжению и мощности",
        options=[
            "Подходящий блок питания по напряжению и мощности",
            "Любой провод без проверки",
            "Только более высокое напряжение",
            "Только холодная комната",
        ],
        support_ru="Для LED важны совпадение по напряжению и достаточный запас по мощности блока питания.",
        support_pl="Dla LED ważna jest zgodność napięcia i odpowiedni zapas mocy zasilacza.",
    )
    add(
        "practice",
        3,
        "choice",
        "Выбор кабеля",
        "Dobór kabla",
        "Что нужно оценить перед выбором кабеля для нагрузки?",
        "Co trzeba ocenić przed doborem kabla do obciążenia?",
        "Ток, длину линии и сечение",
        options=[
            "Ток, длину линии и сечение",
            "Только цвет стены",
            "Только название магазина",
            "Только размер коробки",
        ],
        support_ru="Практический выбор кабеля связан с током нагрузки, длиной линии и требуемым сечением.",
        support_pl="Praktyczny dobór kabla jest związany z prądem obciążenia, długością linii i wymaganym przekrojem.",
    )
    add(
        "practice",
        4,
        "choice",
        "Перегрев линии",
        "Przegrzewanie linii",
        "Что может случиться, если на большой ток взять слишком тонкий провод?",
        "Co może się stać, jeśli do dużego prądu użyje się zbyt cienkiego przewodu?",
        "Провод может перегреваться",
        options=[
            "Провод может перегреваться",
            "Провод автоматически станет толще",
            "Напряжение исчезнет навсегда",
            "Опасности нет",
        ],
        support_ru="Безопасная практика начинается с того, чтобы ток не был слишком велик для выбранного проводника.",
        support_pl="Bezpieczna praktyka zaczyna się od tego, by prąd nie był zbyt duży dla wybranego przewodnika.",
    )

    memory_cards = [
        (
            1,
            "Формула: закон Ома",
            "Wzór: prawo Ohma",
            "Запомни: U = I × R, I = U / R, R = U / I.",
            "Zapamiętaj: U = I × R, I = U / R, R = U / I.",
        ),
        (
            2,
            "Формула: мощность",
            "Wzór: moc",
            "Запомни: P = U × I, а для однофазной цепи S = U × I.",
            "Zapamiętaj: P = U × I, a dla obwodu jednofazowego S = U × I.",
        ),
        (
            3,
            "Формула: коэффициент мощности",
            "Wzór: współczynnik mocy",
            "Запомни: cosφ = P / S.",
            "Zapamiętaj: cosφ = P / S.",
        ),
        (
            4,
            "Формула: реактивная мощность",
            "Wzór: moc bierna",
            "Запомни: для однофазной нагрузки можно получить Q = S × sinφ.",
            "Zapamiętaj: dla obciążenia jednofazowego można otrzymać Q = S × sinφ.",
        ),
        (
            5,
            "Правило: автомат",
            "Zasada: wyłącznik",
            "Автомат защищает проводку от перегрузки и короткого замыкания.",
            "Wyłącznik chroni przewody przed przeciążeniem i zwarciem.",
        ),
        (
            6,
            "Правило: УЗО",
            "Zasada: RCD",
            "УЗО реагирует на ток утечки и не заменяет защиту от перегрузки и КЗ.",
            "RCD reaguje na prąd upływu i nie zastępuje ochrony przed przeciążeniem i zwarciem.",
        ),
        (
            7,
            "Правило: проводник",
            "Zasada: przewodnik",
            "Для проводника полезно помнить связь R = ρ × l / S.",
            "Dla przewodnika warto pamiętać zależność R = ρ × l / S.",
        ),
        (
            8,
            "Правило: индукция",
            "Zasada: indukcja",
            "Индукция связана с изменением магнитного потока.",
            "Indukcja jest związana ze zmianą strumienia magnetycznego.",
        ),
    ]

    for index, title_ru, title_pl, prompt_ru, prompt_pl in memory_cards:
        tasks.append(
            {
                "id": f"a_memory_{index:02d}",
                "mode": "adult",
                "theme": "memory",
                "type": "memory",
                "title_ru": title_ru,
                "title_pl": title_pl,
                "prompt_ru": prompt_ru,
                "prompt_pl": prompt_pl,
                "answer": "__memory__",
                "options": [],
                "hint_type": "lesson",
                "sort_order": index,
                "source": "built_in",
                "metadata": {
                    "support_ru": "Сначала прочитай формулу или правило целиком, потом повтори его вслух.",
                    "support_pl": "Najpierw przeczytaj wzór lub zasadę w całości, a potem powtórz ją na głos.",
                },
            }
        )

    return tasks
