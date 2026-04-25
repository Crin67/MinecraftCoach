const siteConfig = window.MinecraftCoachSiteConfig || {};
const apiBaseUrl = String(siteConfig.apiBaseUrl || "").replace(/\/+$/, "");
const buildApiUrl = (path) => `${apiBaseUrl}${path}`;

const loginUrl = buildApiUrl("/auth/login");
const dashboardUrl = buildApiUrl("/dashboard");
const sessionStorageKey = "minecraft-coach-session-token";
const languageStorageKey = "minecraft-coach-language";
const supportedLanguages = ["ru", "pl", "en", "it", "de", "uk"];
const defaultLanguage = "en";

const languageNames = {
  ru: "Русский",
  pl: "Polski",
  en: "English",
  it: "Italiano",
  de: "Deutsch",
  uk: "Українська",
};

const languageLocales = {
  ru: "ru-RU",
  pl: "pl-PL",
  en: "en-US",
  it: "it-IT",
  de: "de-DE",
  uk: "uk-UA",
};

const translations = {
  ru: {
    meta: {
      title: "Minecraft Coach - обучение прямо во время игры",
      description:
        "Minecraft Coach вовремя ставит игру на паузу, показывает ребёнку мини-уроки и задания, а родителю даёт мониторинг сессии по ID программы и паролю.",
    },
    brand: {
      tagline: "Пауза. Учёба. Продолжение.",
    },
    language: {
      label: "Язык",
      selectAria: "Выбор языка сайта",
    },
    nav: {
      ariaLabel: "Главная навигация",
      download: "Скачать",
      modules: "Модули",
      howItWorks: "Как работает",
      monitoring: "Мониторинг",
      updates: "Обновление",
      login: "Войти по ID",
    },
    hero: {
      eyebrow: "Обучение внутри игры",
      title: "Приложение, которое вовремя останавливает игру и возвращает ребёнка к обучению.",
      lead:
        "Minecraft Coach показывает темы, мини-уроки и задания прямо во время отдыха или игры, считает статистику, хранит модули и позволяет родителю следить за конкретной сессией по ID программы и паролю.",
      primaryCta: "Скачать приложение",
      secondaryCta: "Как это работает",
      signalPauseLabel: "Пауза",
      signalPauseTitle: "Урок в нужный момент",
      signalModulesLabel: "Модули",
      signalModulesTitle: "Темы загружаются отдельно",
      signalMonitoringLabel: "Мониторинг",
      signalMonitoringTitle: "Родитель видит сессию онлайн",
      sceneAlt: "Интерфейс Minecraft Coach с паузой игры и карточкой вопроса",
      overlay: {
        pauseTitle: "Авто-пауза",
        pauseLead: "встраивается в игровой ритм",
        pausedState: "Пауза",
        question: "Сколько будет 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "Время учиться!",
        ctaBody: "Ответьте на вопрос, чтобы продолжить.",
      },
    },
    quick: {
      eyebrow: "Продуктовая логика",
      title: "Один стек для Minecraft, видео, desktop-приложений и родительского контроля.",
      cardOneTitle: "Игровая пауза",
      cardOneText:
        "Ребёнок не выпадает из привычного сценария, а мягко переключается на учебный этап.",
      cardTwoTitle: "Короткий цикл",
      cardTwoText:
        "Небольшие уроки и задания дают результат без перегруза и без долгих остановок.",
      cardThreeTitle: "Контроль для родителя",
      cardThreeText:
        "Сайт показывает актуальное состояние конкретной сессии, статистику и настройки.",
    },
    download: {
      eyebrow: "Скачать",
      title: "Всегда актуальная desktop-версия без ручного поиска файлов.",
      lead: "Сайт сам показывает текущую сборку приложения и даёт прямую ссылку на свежий `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Проверяем наличие файла...",
      button: "Скачать .exe",
      statusWaiting: "Если кнопка неактивна, значит актуальная сборка ещё не загружена в папку dist/.",
      sideOneTitle: "Каталог читается с backend API",
      sideOneText: "Версия, размер файла и дата обновления подтягиваются автоматически.",
      sideTwoTitle: "Hero-кнопка и раздел загрузки синхронизированы",
      sideTwoText:
        "Пользователь всегда скачивает один и тот же актуальный билд из двух точек лендинга.",
      sideThreeTitle: "Подходит для статического хостинга",
      sideThreeText:
        "Фронт остаётся лёгким и быстрым, а функциональность берёт из уже существующих API-эндпойнтов.",
    },
    integration: {
      eyebrow: "Интеграции",
      title: "Сайт визуально поддерживает идею мульти-приложения и умных учебных пауз.",
      lead:
        "Блок вдохновлён вашим референсом и объясняет, как одна логика управляет игрой, видео и desktop-активностью.",
      imageAlt: "Схема интеграции Minecraft Coach с Minecraft, YouTube и desktop apps",
      minecraftTitle: "Minecraft",
      minecraftText:
        "Программа ставит игру на паузу, выводит вопрос или мини-урок и возвращает ребёнка обратно в игровой поток.",
      videoTitle: "YouTube и видео",
      videoText:
        "Та же логика подходит для обучающих и развлекательных видео, когда нужен короткий учебный interrupt.",
      desktopTitle: "Desktop apps",
      desktopText:
        "Сценарий масштабируется на другие приложения, сохраняя единый формат паузы, задания и продолжения.",
      noteTitle: "Главная мысль",
      noteText:
        "Minecraft Coach выглядит не как обычный лендинг про “скачать exe”, а как технологическая система, которая связывает игру, обучение и удалённый контроль в одном опыте.",
    },
    modules: {
      eyebrow: "Модули",
      title: "Выберите и скачайте нужный учебный модуль.",
      lead:
        "Модули подгружаются с сервера автоматически. После скачивания достаточно положить их в папку <code>modules</code> вашей программы.",
    },
    how: {
      eyebrow: "Как работает",
      title: "Путь от установки до обучающей сессии.",
      stepOneTitle: "Скачайте приложение",
      stepOneText:
        "На сайте всегда лежит свежая сборка, так что пользователю не нужно искать правильную версию вручную.",
      stepTwoTitle: "Добавьте нужные модули",
      stepTwoText:
        "Темы и наборы контента загружаются отдельно, поэтому программу можно расширять без новой сборки сайта.",
      stepThreeTitle: "Настройте интервалы и пароль",
      stepThreeText:
        "Родитель выбирает темп учебных пауз, объём заданий и защищает доступ к мониторингу паролем.",
      stepFourTitle: "Следите за сессией онлайн",
      stepFourText:
        "По ID программы и паролю сайт показывает текущее состояние, статистику и последнее обновление.",
      whyLabel: "Почему это работает",
      statusOneLabel: "Урок встроен в привычный игровой цикл",
      statusOneValue: "без резкой смены контекста",
      statusTwoLabel: "Референсный стиль держит ощущение технологичности",
      statusTwoValue: "неон, схемы, глубокий тёмный фон",
      statusThreeLabel: "Фронт связан с существующим backend",
      statusThreeValue: "без переписывания API",
      statusFourLabel: "Блоки легко расширять новыми разделами",
      statusFourValue: "например, закрытыми roadmap-фичами",
    },
    monitor: {
      eyebrow: "Мониторинг",
      title: "Подключение к конкретной сессии по ID программы.",
      lead:
        "Введите <strong>ID программы</strong> и <strong>пароль родителя</strong>. После входа сайт начнёт автоматически обновлять состояние сессии.",
      form: {
        programIdLabel: "ID программы",
        programIdPlaceholder: "Например AB12CD34",
        passwordLabel: "Пароль родителя",
        passwordPlaceholder: "Введите пароль",
        submit: "Войти и открыть мониторинг",
      },
      emptyLabel: "Онлайн-доступ",
      emptyTitle:
        "Родитель подключается по ID программы и паролю, без лишних экранов и сложного онбординга.",
      emptyText:
        "После входа открывается живая сводка: текущий режим, активная тема, монеты, ошибки, число пауз и параметры сессии.",
      previewOneLabel: "ID программы",
      previewOneValue: "точечный доступ",
      previewTwoLabel: "Пароль родителя",
      previewTwoValue: "защищённый вход",
      previewThreeLabel: "Автообновление",
      previewThreeValue: "каждые 15 секунд",
      previewFourLabel: "Dashboard",
      previewFourValue: "статистика + статус",
      dashboardLabel: "Активная сессия",
      refresh: "Обновить сейчас",
      logout: "Выйти",
      runtimeTitle: "Состояние сессии",
      settingsTitle: "Настройки программы",
    },
    updates: {
      eyebrow: "Обновление",
      title: "Чтобы выложить новую версию, не нужно заново проектировать сайт.",
      cardOneTitle: "Обновление приложения",
      cardOneText:
        "Достаточно заменить <code>dist/MinecraftCoach.exe</code>. Каталог загрузок начнёт отдавать новую сборку автоматически.",
      cardTwoTitle: "Обновление модулей",
      cardTwoText:
        "Добавьте или обновите папки в <code>modules/</code>, и сайт сам покажет их в каталоге для скачивания.",
      cardThreeTitle: "Новые секции сайта",
      cardThreeText:
        "Страница собрана как набор выразительных блоков, которые легко расширять под roadmap, кейсы и новые функции.",
    },
    secret: {
      eyebrow: "Секретный блок",
      title: "Визуально заложили место под будущие закрытые функции и новые режимы обучения.",
      lead:
        "Этот блок продолжает атмосферу продукта и работает как тизер следующего этапа развития.",
      badge: "Тизер roadmap",
      text: "Подготовили зону для закрытых режимов, специальных сценариев и следующей волны фич.",
      imageAlt: "Тизер секретного блока Minecraft Coach",
    },
    footer: {
      text:
        "Лендинг загрузки, модулей и мониторинга учебных сессий, собранный в технологичном стиле ваших референсов.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Размер пока неизвестен",
      noData: "Нет данных",
      downloadMeta: "Файл: {filename} · {size} · обновлён {updatedAt}",
      downloadReady: "Сборка доступна для прямого скачивания с сайта.",
      downloadMissingMeta: "Файл приложения пока не найден в папке dist/.",
      downloadMissingStatus:
        "Загрузите или замените dist/MinecraftCoach.exe, и кнопки станут активными автоматически.",
      moduleFallbackDescription:
        "Описание пока не заполнено, но модуль уже можно скачать и подключить в программу.",
      moduleCardLabel: "Учебный модуль",
      moduleTopics: "Тем: {count}",
      moduleLevels: "Уровней: {count}",
      moduleDownload: "Скачать модуль",
      modulesEmptyTitle: "Пока нет доступных модулей",
      modulesEmptyText:
        "Добавьте папки модулей в каталог <code>modules/</code>, и они появятся здесь автоматически.",
      catalogErrorMeta: "Не удалось получить каталог загрузок.",
      catalogErrorStatus: "Ошибка загрузки каталога: {error}",
      catalogErrorTitle: "Каталог модулей недоступен",
      catalogErrorText:
        "Проверьте, что backend запущен и отвечает на маршрут <code>/downloads/catalog</code>.",
      sessionTitle: "Сессия {programId}",
      sessionUpdated: "Последнее обновление: {updatedAt}",
      stats: {
        coins: "Монеты",
        correct: "Правильных",
        wrong: "Ошибок",
        completedBreaks: "Завершённых пауз",
        topics: "Тем всего",
        tasks: "Заданий",
        childTopics: "Детских тем",
        adultTopics: "Взрослых тем",
      },
      runtime: {
        currentModule: "Текущий модуль",
        currentTopic: "Текущая тема",
        currentTask: "Текущее задание",
        state: "Состояние",
        nextBreak: "До следующей паузы",
        manualPause: "Ручная пауза",
        lastMode: "Последний режим",
        lastActivity: "Последняя активность",
        notSelectedModule: "Не выбран",
        notSelectedTopic: "Не выбрана",
        noActiveTask: "Нет активного задания",
        unknown: "Неизвестно",
        noData: "Нет данных",
        manualPauseActive: "Активна",
        manualPauseInactive: "Не активна",
      },
      settings: {
        programId: "ID программы",
        windowLanguage: "Язык окна",
        breakInterval: "Интервал между паузами",
        tasksPerBreak: "Заданий в паузе",
        lessonTime: "Время урока",
        serverUrl: "URL сервера",
        notSet: "Не задан",
      },
      loginChecking: "Проверяем доступ...",
      loginLoading: "Вход выполнен. Загружаем данные...",
      monitorOpenError: "Не удалось открыть мониторинг: {error}",
      loginError: "Ошибка входа: {error}",
      sessionClosed: "Сессия закрыта на этом устройстве.",
    },
  },
  pl: {
    meta: {
      title: "Minecraft Coach - nauka podczas gry",
      description:
        "Minecraft Coach zatrzymuje grę we właściwym momencie, pokazuje dziecku mini-lekcje i zadania, a rodzicowi daje podgląd sesji po ID programu i haśle.",
    },
    brand: {
      tagline: "Pauza. Nauka. Powrót.",
    },
    language: {
      label: "Język",
      selectAria: "Wybór języka strony",
    },
    nav: {
      ariaLabel: "Nawigacja główna",
      download: "Pobierz",
      modules: "Moduły",
      howItWorks: "Jak działa",
      monitoring: "Monitoring",
      updates: "Aktualizacje",
      login: "Wejdź po ID",
    },
    hero: {
      eyebrow: "Nauka w trakcie gry",
      title: "Aplikacja, która zatrzymuje grę we właściwym momencie i prowadzi dziecko z powrotem do nauki.",
      lead:
        "Minecraft Coach pokazuje tematy, mini-lekcje i zadania podczas przerwy lub gry, liczy statystyki, przechowuje moduły i pozwala rodzicowi śledzić konkretną sesję po ID programu i haśle.",
      primaryCta: "Pobierz aplikację",
      secondaryCta: "Jak to działa",
      signalPauseLabel: "Pauza",
      signalPauseTitle: "Lekcja w odpowiednim momencie",
      signalModulesLabel: "Moduły",
      signalModulesTitle: "Tematy pobierają się osobno",
      signalMonitoringLabel: "Monitoring",
      signalMonitoringTitle: "Rodzic widzi sesję online",
      sceneAlt: "Interfejs Minecraft Coach z pauzą gry i kartą pytania",
      overlay: {
        pauseTitle: "Auto-pauza",
        pauseLead: "dopasowuje się do rytmu gry",
        pausedState: "Wstrzymano",
        question: "Ile to 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "Czas na naukę!",
        ctaBody: "Odpowiedz na pytanie, aby kontynuować.",
      },
    },
    quick: {
      eyebrow: "Logika produktu",
      title: "Jeden system dla Minecrafta, wideo, aplikacji desktopowych i kontroli rodzicielskiej.",
      cardOneTitle: "Pauza w grze",
      cardOneText: "Dziecko nie wypada z naturalnego rytmu, tylko płynnie przechodzi do etapu nauki.",
      cardTwoTitle: "Krótki cykl",
      cardTwoText: "Małe lekcje i zadania dają efekt bez przeciążenia i bez długich przerw.",
      cardThreeTitle: "Kontrola dla rodzica",
      cardThreeText: "Strona pokazuje bieżący stan konkretnej sesji, statystyki i ustawienia.",
    },
    download: {
      eyebrow: "Pobierz",
      title: "Zawsze aktualna wersja desktop bez ręcznego szukania plików.",
      lead: "Strona sama pokazuje bieżący build aplikacji i daje bezpośredni link do najnowszego `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Sprawdzamy dostępność pliku...",
      button: "Pobierz .exe",
      statusWaiting: "Jeśli przycisk jest nieaktywny, aktualny build nie został jeszcze dodany do folderu dist/.",
      sideOneTitle: "Katalog pobierany z backend API",
      sideOneText: "Wersja, rozmiar pliku i data aktualizacji pojawiają się automatycznie.",
      sideTwoTitle: "Przycisk w hero i sekcja pobierania są zsynchronizowane",
      sideTwoText: "Użytkownik pobiera ten sam aktualny build z dwóch miejsc na landing page.",
      sideThreeTitle: "Działa dobrze na hostingu statycznym",
      sideThreeText: "Frontend pozostaje lekki i szybki, a funkcje korzystają z istniejących endpointów API.",
    },
    integration: {
      eyebrow: "Integracje",
      title: "Strona wizualnie wspiera ideę wielu aplikacji i inteligentnych przerw edukacyjnych.",
      lead:
        "Ten blok został zbudowany na bazie Twojego referensu i pokazuje, jak jedna logika steruje grą, wideo i aktywnością desktopową.",
      imageAlt: "Schemat integracji Minecraft Coach z Minecraftem, YouTube i aplikacjami desktopowymi",
      minecraftTitle: "Minecraft",
      minecraftText:
        "Program zatrzymuje grę, pokazuje pytanie lub mini-lekcję i płynnie przywraca dziecko do rozgrywki.",
      videoTitle: "YouTube i wideo",
      videoText:
        "Ta sama logika działa także przy materiałach edukacyjnych i rozrywkowych, gdy potrzebna jest krótka przerwa na naukę.",
      desktopTitle: "Aplikacje desktopowe",
      desktopText:
        "Scenariusz można rozszerzyć na inne programy, zachowując wspólny format pauzy, zadania i powrotu.",
      noteTitle: "Najważniejsze",
      noteText:
        "Minecraft Coach wygląda nie jak zwykła strona do pobrania pliku, lecz jak technologiczny system łączący grę, naukę i zdalny nadzór w jednym doświadczeniu.",
    },
    modules: {
      eyebrow: "Moduły",
      title: "Wybierz i pobierz potrzebny moduł edukacyjny.",
      lead:
        "Moduły pobierają się automatycznie z serwera. Po pobraniu wystarczy umieścić je w folderze <code>modules</code> Twojego programu.",
    },
    how: {
      eyebrow: "Jak działa",
      title: "Droga od instalacji do sesji edukacyjnej.",
      stepOneTitle: "Pobierz aplikację",
      stepOneText:
        "Na stronie zawsze znajduje się aktualny build, więc użytkownik nie musi ręcznie szukać właściwej wersji.",
      stepTwoTitle: "Dodaj potrzebne moduły",
      stepTwoText:
        "Tematy i zestawy treści są pobierane osobno, dlatego program można rozwijać bez nowej wersji strony.",
      stepThreeTitle: "Ustaw interwały i hasło",
      stepThreeText:
        "Rodzic wybiera tempo przerw edukacyjnych, liczbę zadań i zabezpiecza monitoring hasłem.",
      stepFourTitle: "Śledź sesję online",
      stepFourText:
        "Po ID programu i haśle strona pokazuje aktualny stan, statystyki i czas ostatniej aktualizacji.",
      whyLabel: "Dlaczego to działa",
      statusOneLabel: "Lekcja jest wpisana w naturalny rytm gry",
      statusOneValue: "bez gwałtownej zmiany kontekstu",
      statusTwoLabel: "Styl referencyjny buduje wrażenie technologii",
      statusTwoValue: "neon, układy, głębokie ciemne tło",
      statusThreeLabel: "Frontend jest połączony z istniejącym backendem",
      statusThreeValue: "bez przepisywania API",
      statusFourLabel: "Bloki łatwo rozbudować o nowe sekcje",
      statusFourValue: "na przykład o zamknięte funkcje roadmapy",
    },
    monitor: {
      eyebrow: "Monitoring",
      title: "Połączenie z konkretną sesją po ID programu.",
      lead:
        "Wprowadź <strong>ID programu</strong> i <strong>hasło rodzica</strong>. Po zalogowaniu strona zacznie automatycznie odświeżać stan sesji.",
      form: {
        programIdLabel: "ID programu",
        programIdPlaceholder: "Na przykład AB12CD34",
        passwordLabel: "Hasło rodzica",
        passwordPlaceholder: "Wpisz hasło",
        submit: "Zaloguj i otwórz monitoring",
      },
      emptyLabel: "Dostęp online",
      emptyTitle: "Rodzic łączy się po ID programu i haśle bez zbędnych ekranów i skomplikowanego onboardingu.",
      emptyText:
        "Po zalogowaniu otwiera się żywy panel: aktualny tryb, aktywny temat, monety, błędy, liczba przerw i parametry sesji.",
      previewOneLabel: "ID programu",
      previewOneValue: "dostęp punktowy",
      previewTwoLabel: "Hasło rodzica",
      previewTwoValue: "bezpieczne logowanie",
      previewThreeLabel: "Auto-odświeżanie",
      previewThreeValue: "co 15 sekund",
      previewFourLabel: "Dashboard",
      previewFourValue: "statystyki + status",
      dashboardLabel: "Aktywna sesja",
      refresh: "Odśwież teraz",
      logout: "Wyloguj",
      runtimeTitle: "Stan sesji",
      settingsTitle: "Ustawienia programu",
    },
    updates: {
      eyebrow: "Aktualizacje",
      title: "Aby opublikować nową wersję, nie trzeba projektować strony od zera.",
      cardOneTitle: "Aktualizacja aplikacji",
      cardOneText:
        "Wystarczy podmienić <code>dist/MinecraftCoach.exe</code>. Katalog pobierania zacznie automatycznie zwracać nowy build.",
      cardTwoTitle: "Aktualizacja modułów",
      cardTwoText:
        "Dodaj lub zaktualizuj foldery w <code>modules/</code>, a strona sama pokaże je w katalogu pobierania.",
      cardThreeTitle: "Nowe sekcje strony",
      cardThreeText:
        "Strona została zbudowana jako zestaw wyrazistych bloków, które łatwo rozszerzać o roadmapę, case studies i nowe funkcje.",
    },
    secret: {
      eyebrow: "Sekretny blok",
      title: "Celowo zostawiliśmy miejsce na przyszłe zamknięte funkcje i nowe tryby nauki.",
      lead:
        "Ten blok podtrzymuje atmosferę produktu i działa jak teaser następnego etapu rozwoju.",
      badge: "Teaser roadmapy",
      text: "Przygotowaliśmy miejsce dla zamkniętych trybów, specjalnych scenariuszy i kolejnej fali funkcji.",
      imageAlt: "Teaser sekretnego bloku Minecraft Coach",
    },
    footer: {
      text:
        "Landing page pobierania, modułów i monitoringu sesji edukacyjnych, zbudowany w technologicznym stylu Twoich referensów.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Rozmiar jest jeszcze nieznany",
      noData: "Brak danych",
      downloadMeta: "Plik: {filename} · {size} · zaktualizowano {updatedAt}",
      downloadReady: "Build jest dostępny do bezpośredniego pobrania ze strony.",
      downloadMissingMeta: "Plik aplikacji nie został jeszcze znaleziony w folderze dist/.",
      downloadMissingStatus:
        "Wgraj lub podmień dist/MinecraftCoach.exe, a przyciski staną się aktywne automatycznie.",
      moduleFallbackDescription:
        "Opis nie jest jeszcze uzupełniony, ale moduł można już pobrać i podłączyć do programu.",
      moduleCardLabel: "Moduł edukacyjny",
      moduleTopics: "Tematów: {count}",
      moduleLevels: "Poziomów: {count}",
      moduleDownload: "Pobierz moduł",
      modulesEmptyTitle: "Brak dostępnych modułów",
      modulesEmptyText:
        "Dodaj foldery modułów do katalogu <code>modules/</code>, a pojawią się tutaj automatycznie.",
      catalogErrorMeta: "Nie udało się pobrać katalogu pobierania.",
      catalogErrorStatus: "Błąd ładowania katalogu: {error}",
      catalogErrorTitle: "Katalog modułów jest niedostępny",
      catalogErrorText:
        "Sprawdź, czy backend jest uruchomiony i odpowiada pod adresem <code>/downloads/catalog</code>.",
      sessionTitle: "Sesja {programId}",
      sessionUpdated: "Ostatnia aktualizacja: {updatedAt}",
      stats: {
        coins: "Monety",
        correct: "Poprawne",
        wrong: "Błędne",
        completedBreaks: "Ukończone przerwy",
        topics: "Tematy łącznie",
        tasks: "Zadania",
        childTopics: "Tematy dziecięce",
        adultTopics: "Tematy dla dorosłych",
      },
      runtime: {
        currentModule: "Aktualny moduł",
        currentTopic: "Aktualny temat",
        currentTask: "Aktualne zadanie",
        state: "Stan",
        nextBreak: "Do następnej przerwy",
        manualPause: "Ręczna pauza",
        lastMode: "Ostatni tryb",
        lastActivity: "Ostatnia aktywność",
        notSelectedModule: "Nie wybrano",
        notSelectedTopic: "Nie wybrano",
        noActiveTask: "Brak aktywnego zadania",
        unknown: "Nieznane",
        noData: "Brak danych",
        manualPauseActive: "Aktywna",
        manualPauseInactive: "Nieaktywna",
      },
      settings: {
        programId: "ID programu",
        windowLanguage: "Język okna",
        breakInterval: "Odstęp między przerwami",
        tasksPerBreak: "Zadań w przerwie",
        lessonTime: "Czas lekcji",
        serverUrl: "URL serwera",
        notSet: "Nie ustawiono",
      },
      loginChecking: "Sprawdzamy dostęp...",
      loginLoading: "Logowanie zakończone. Ładujemy dane...",
      monitorOpenError: "Nie udało się otworzyć monitoringu: {error}",
      loginError: "Błąd logowania: {error}",
      sessionClosed: "Sesja została zamknięta na tym urządzeniu.",
    },
  },
  en: {
    meta: {
      title: "Minecraft Coach - learning during gameplay",
      description:
        "Minecraft Coach pauses the game at the right moment, shows mini-lessons and tasks, and gives parents a live session view by program ID and password.",
    },
    brand: {
      tagline: "Pause. Learn. Continue.",
    },
    language: {
      label: "Language",
      selectAria: "Website language selector",
    },
    nav: {
      ariaLabel: "Main navigation",
      download: "Download",
      modules: "Modules",
      howItWorks: "How it works",
      monitoring: "Monitoring",
      updates: "Updates",
      login: "Login by ID",
    },
    hero: {
      eyebrow: "Learning inside the game",
      title: "The app that pauses the game at the right moment and brings children back to learning.",
      lead:
        "Minecraft Coach shows topics, mini-lessons, and tasks during breaks or gameplay, tracks stats, stores modules, and lets a parent follow a specific session using the program ID and password.",
      primaryCta: "Download app",
      secondaryCta: "How it works",
      signalPauseLabel: "Pause",
      signalPauseTitle: "A lesson at the right moment",
      signalModulesLabel: "Modules",
      signalModulesTitle: "Topics download separately",
      signalMonitoringLabel: "Monitoring",
      signalMonitoringTitle: "Parents see the session online",
      sceneAlt: "Minecraft Coach interface with a paused game and a quiz card",
      overlay: {
        pauseTitle: "Auto-pause",
        pauseLead: "fits the rhythm of the game",
        pausedState: "Paused",
        question: "What is 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "Time to learn!",
        ctaBody: "Answer the question to continue.",
      },
    },
    quick: {
      eyebrow: "Product logic",
      title: "One system for Minecraft, video, desktop apps, and parental control.",
      cardOneTitle: "Gameplay pause",
      cardOneText: "Children stay inside a familiar flow and smoothly switch into a learning moment.",
      cardTwoTitle: "Short cycle",
      cardTwoText: "Compact lessons and tasks create progress without overload or long interruptions.",
      cardThreeTitle: "Parental control",
      cardThreeText: "The website shows the live state of a specific session, including stats and settings.",
    },
    download: {
      eyebrow: "Download",
      title: "An always up-to-date desktop version without manually searching for files.",
      lead: "The website automatically shows the current build and provides a direct link to the latest `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Checking file availability...",
      button: "Download .exe",
      statusWaiting: "If the button is disabled, the latest build has not been uploaded to the dist/ folder yet.",
      sideOneTitle: "Catalog is read from the backend API",
      sideOneText: "Version, file size, and update date are pulled in automatically.",
      sideTwoTitle: "Hero button and download section stay in sync",
      sideTwoText: "Users always download the same current build from both key points on the landing page.",
      sideThreeTitle: "Works well on static hosting",
      sideThreeText: "The frontend stays fast and lightweight while functionality comes from existing API endpoints.",
    },
    integration: {
      eyebrow: "Integrations",
      title: "The website now supports the multi-app idea and smart learning pauses visually.",
      lead:
        "This block is based on your reference and explains how one logic can control gameplay, video, and desktop activity.",
      imageAlt: "Diagram of Minecraft Coach integration with Minecraft, YouTube, and desktop apps",
      minecraftTitle: "Minecraft",
      minecraftText:
        "The app pauses the game, shows a question or mini-lesson, and smoothly returns the child to the gameplay loop.",
      videoTitle: "YouTube and video",
      videoText:
        "The same logic works for educational and entertainment video when you need a short learning interrupt.",
      desktopTitle: "Desktop apps",
      desktopText:
        "The scenario scales to other applications while keeping one shared format for pause, task, and resume.",
      noteTitle: "Main idea",
      noteText:
        "Minecraft Coach no longer feels like a simple “download the exe” page, but like a technology system connecting gameplay, learning, and remote supervision.",
    },
    modules: {
      eyebrow: "Modules",
      title: "Choose and download the right learning module.",
      lead:
        "Modules are loaded automatically from the server. After downloading, simply place them into your program’s <code>modules</code> folder.",
    },
    how: {
      eyebrow: "How it works",
      title: "From installation to an active learning session.",
      stepOneTitle: "Download the app",
      stepOneText:
        "The latest build is always available on the website, so users do not need to hunt for the right version.",
      stepTwoTitle: "Add the right modules",
      stepTwoText:
        "Topics and content packs are downloaded separately, so the program can grow without rebuilding the site.",
      stepThreeTitle: "Set intervals and password",
      stepThreeText:
        "Parents choose the pace of learning breaks, the number of tasks, and protect monitoring access with a password.",
      stepFourTitle: "Track the session online",
      stepFourText:
        "Using the program ID and password, the site shows the current state, statistics, and latest update.",
      whyLabel: "Why it works",
      statusOneLabel: "The lesson is inserted into a familiar gameplay loop",
      statusOneValue: "without a harsh context switch",
      statusTwoLabel: "The visual reference keeps a technological feel",
      statusTwoValue: "neon, circuits, deep dark background",
      statusThreeLabel: "The frontend stays connected to the existing backend",
      statusThreeValue: "without rewriting the API",
      statusFourLabel: "Blocks are easy to extend with new sections",
      statusFourValue: "for example with closed roadmap features",
    },
    monitor: {
      eyebrow: "Monitoring",
      title: "Connect to a specific session by program ID.",
      lead:
        "Enter the <strong>program ID</strong> and the <strong>parent password</strong>. After login, the site will automatically refresh the session state.",
      form: {
        programIdLabel: "Program ID",
        programIdPlaceholder: "For example AB12CD34",
        passwordLabel: "Parent password",
        passwordPlaceholder: "Enter the password",
        submit: "Login and open monitoring",
      },
      emptyLabel: "Online access",
      emptyTitle: "Parents connect by program ID and password without extra screens or a complex onboarding flow.",
      emptyText:
        "After login, they get a live summary: current mode, active topic, coins, mistakes, break count, and session settings.",
      previewOneLabel: "Program ID",
      previewOneValue: "targeted access",
      previewTwoLabel: "Parent password",
      previewTwoValue: "protected login",
      previewThreeLabel: "Auto refresh",
      previewThreeValue: "every 15 seconds",
      previewFourLabel: "Dashboard",
      previewFourValue: "stats + status",
      dashboardLabel: "Active session",
      refresh: "Refresh now",
      logout: "Logout",
      runtimeTitle: "Session state",
      settingsTitle: "Program settings",
    },
    updates: {
      eyebrow: "Updates",
      title: "Publishing a new version does not require redesigning the site.",
      cardOneTitle: "App update",
      cardOneText:
        "Just replace <code>dist/MinecraftCoach.exe</code>. The download catalog will automatically serve the new build.",
      cardTwoTitle: "Module update",
      cardTwoText:
        "Add or update folders inside <code>modules/</code>, and the site will show them in the download catalog automatically.",
      cardThreeTitle: "New site sections",
      cardThreeText:
        "The page is built as a set of expressive blocks that are easy to extend with roadmap items, case studies, and new features.",
    },
    secret: {
      eyebrow: "Secret block",
      title: "We intentionally reserved visual space for future private features and new learning modes.",
      lead:
        "This block keeps the product atmosphere and works as a teaser for the next development phase.",
      badge: "Roadmap teaser",
      text: "We prepared space for closed modes, special scenarios, and the next wave of features.",
      imageAlt: "Teaser for the secret Minecraft Coach block",
    },
    footer: {
      text:
        "A landing page for downloads, modules, and monitoring of learning sessions, designed in the technological language of your references.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Size is not available yet",
      noData: "No data",
      downloadMeta: "File: {filename} · {size} · updated {updatedAt}",
      downloadReady: "The build is available for direct download from the site.",
      downloadMissingMeta: "The application file was not found in the dist/ folder yet.",
      downloadMissingStatus:
        "Upload or replace dist/MinecraftCoach.exe and the buttons will become active automatically.",
      moduleFallbackDescription:
        "The description is not filled in yet, but the module can already be downloaded and connected to the app.",
      moduleCardLabel: "Learning module",
      moduleTopics: "Topics: {count}",
      moduleLevels: "Levels: {count}",
      moduleDownload: "Download module",
      modulesEmptyTitle: "No modules available yet",
      modulesEmptyText:
        "Add module folders to the <code>modules/</code> directory and they will appear here automatically.",
      catalogErrorMeta: "Could not load the download catalog.",
      catalogErrorStatus: "Catalog loading error: {error}",
      catalogErrorTitle: "The module catalog is unavailable",
      catalogErrorText:
        "Make sure the backend is running and serving <code>/downloads/catalog</code>.",
      sessionTitle: "Session {programId}",
      sessionUpdated: "Last update: {updatedAt}",
      stats: {
        coins: "Coins",
        correct: "Correct",
        wrong: "Wrong",
        completedBreaks: "Completed breaks",
        topics: "Total topics",
        tasks: "Tasks",
        childTopics: "Child topics",
        adultTopics: "Adult topics",
      },
      runtime: {
        currentModule: "Current module",
        currentTopic: "Current topic",
        currentTask: "Current task",
        state: "State",
        nextBreak: "Until next break",
        manualPause: "Manual pause",
        lastMode: "Last mode",
        lastActivity: "Last activity",
        notSelectedModule: "Not selected",
        notSelectedTopic: "Not selected",
        noActiveTask: "No active task",
        unknown: "Unknown",
        noData: "No data",
        manualPauseActive: "Active",
        manualPauseInactive: "Inactive",
      },
      settings: {
        programId: "Program ID",
        windowLanguage: "Window language",
        breakInterval: "Break interval",
        tasksPerBreak: "Tasks per break",
        lessonTime: "Lesson time",
        serverUrl: "Server URL",
        notSet: "Not set",
      },
      loginChecking: "Checking access...",
      loginLoading: "Login successful. Loading data...",
      monitorOpenError: "Could not open monitoring: {error}",
      loginError: "Login error: {error}",
      sessionClosed: "The session has been closed on this device.",
    },
  },
  it: {
    meta: {
      title: "Minecraft Coach - imparare mentre si gioca",
      description:
        "Minecraft Coach mette in pausa il gioco al momento giusto, mostra mini-lezioni e compiti e offre ai genitori il monitoraggio della sessione tramite ID programma e password.",
    },
    brand: {
      tagline: "Pausa. Studio. Riprendi.",
    },
    language: {
      label: "Lingua",
      selectAria: "Selettore della lingua del sito",
    },
    nav: {
      ariaLabel: "Navigazione principale",
      download: "Scarica",
      modules: "Moduli",
      howItWorks: "Come funziona",
      monitoring: "Monitoraggio",
      updates: "Aggiornamenti",
      login: "Accedi con ID",
    },
    hero: {
      eyebrow: "Apprendimento durante il gioco",
      title: "L'app che mette in pausa il gioco al momento giusto e riporta il bambino allo studio.",
      lead:
        "Minecraft Coach mostra argomenti, mini-lezioni e attività durante le pause o il gioco, tiene traccia delle statistiche, conserva i moduli e permette ai genitori di seguire una sessione specifica tramite ID programma e password.",
      primaryCta: "Scarica l'app",
      secondaryCta: "Come funziona",
      signalPauseLabel: "Pausa",
      signalPauseTitle: "Una lezione al momento giusto",
      signalModulesLabel: "Moduli",
      signalModulesTitle: "Gli argomenti si scaricano separatamente",
      signalMonitoringLabel: "Monitoraggio",
      signalMonitoringTitle: "Il genitore vede la sessione online",
      sceneAlt: "Interfaccia di Minecraft Coach con il gioco in pausa e una scheda domanda",
      overlay: {
        pauseTitle: "Auto-pausa",
        pauseLead: "si adatta al ritmo del gioco",
        pausedState: "In pausa",
        question: "Quanto fa 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "È ora di imparare!",
        ctaBody: "Rispondi alla domanda per continuare.",
      },
    },
    quick: {
      eyebrow: "Logica del prodotto",
      title: "Un unico sistema per Minecraft, video, app desktop e controllo parentale.",
      cardOneTitle: "Pausa di gioco",
      cardOneText: "Il bambino resta nel suo flusso abituale e passa in modo naturale al momento di studio.",
      cardTwoTitle: "Ciclo breve",
      cardTwoText: "Mini-lezioni e attività brevi portano risultati senza sovraccarico e senza lunghe interruzioni.",
      cardThreeTitle: "Controllo genitori",
      cardThreeText: "Il sito mostra lo stato attuale di una sessione specifica, con statistiche e impostazioni.",
    },
    download: {
      eyebrow: "Scarica",
      title: "Sempre la versione desktop più recente senza cercare i file manualmente.",
      lead: "Il sito mostra automaticamente la build attuale dell'app e offre un link diretto all'ultimo `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Verifica disponibilità file...",
      button: "Scarica .exe",
      statusWaiting: "Se il pulsante è disattivato, la build più recente non è ancora stata caricata nella cartella dist/.",
      sideOneTitle: "Il catalogo arriva dal backend API",
      sideOneText: "Versione, dimensione del file e data di aggiornamento vengono caricate automaticamente.",
      sideTwoTitle: "Pulsante hero e sezione download restano sincronizzati",
      sideTwoText: "L'utente scarica sempre la stessa build aggiornata dai due punti principali della landing page.",
      sideThreeTitle: "Ottimo per hosting statico",
      sideThreeText: "Il frontend resta leggero e veloce, mentre le funzioni sfruttano gli endpoint API esistenti.",
    },
    integration: {
      eyebrow: "Integrazioni",
      title: "Il sito supporta visivamente l'idea multi-app e le pause intelligenti di apprendimento.",
      lead:
        "Questo blocco nasce dal tuo riferimento e spiega come una sola logica possa governare gioco, video e attività desktop.",
      imageAlt: "Schema di integrazione di Minecraft Coach con Minecraft, YouTube e app desktop",
      minecraftTitle: "Minecraft",
      minecraftText:
        "L'app mette in pausa il gioco, mostra una domanda o una mini-lezione e riporta il bambino nel flusso di gioco.",
      videoTitle: "YouTube e video",
      videoText:
        "La stessa logica funziona anche per contenuti educativi e video, quando serve una breve interruzione per imparare.",
      desktopTitle: "App desktop",
      desktopText:
        "Lo scenario si estende ad altre applicazioni mantenendo lo stesso formato di pausa, attività e ripresa.",
      noteTitle: "Idea chiave",
      noteText:
        "Minecraft Coach non sembra più una semplice pagina per scaricare un file, ma un sistema tecnologico che unisce gioco, apprendimento e supervisione remota.",
    },
    modules: {
      eyebrow: "Moduli",
      title: "Scegli e scarica il modulo didattico giusto.",
      lead:
        "I moduli vengono caricati automaticamente dal server. Dopo il download basta inserirli nella cartella <code>modules</code> del programma.",
    },
    how: {
      eyebrow: "Come funziona",
      title: "Dal download alla sessione educativa attiva.",
      stepOneTitle: "Scarica l'app",
      stepOneText:
        "L'ultima build è sempre disponibile sul sito, quindi l'utente non deve cercare manualmente la versione corretta.",
      stepTwoTitle: "Aggiungi i moduli giusti",
      stepTwoText:
        "Argomenti e pacchetti di contenuti si scaricano separatamente, così il programma cresce senza rifare il sito.",
      stepThreeTitle: "Imposta intervalli e password",
      stepThreeText:
        "Il genitore sceglie il ritmo delle pause didattiche, il numero di attività e protegge l'accesso al monitoraggio con una password.",
      stepFourTitle: "Segui la sessione online",
      stepFourText:
        "Con ID programma e password, il sito mostra stato corrente, statistiche e ultimo aggiornamento.",
      whyLabel: "Perché funziona",
      statusOneLabel: "La lezione entra nel ritmo naturale del gioco",
      statusOneValue: "senza uno stacco brusco di contesto",
      statusTwoLabel: "Lo stile di riferimento mantiene un tono tecnologico",
      statusTwoValue: "neon, circuiti e sfondo scuro profondo",
      statusThreeLabel: "Il frontend resta connesso al backend esistente",
      statusThreeValue: "senza riscrivere l'API",
      statusFourLabel: "I blocchi si estendono facilmente con nuove sezioni",
      statusFourValue: "per esempio con funzioni roadmap riservate",
    },
    monitor: {
      eyebrow: "Monitoraggio",
      title: "Connessione a una sessione specifica tramite ID programma.",
      lead:
        "Inserisci <strong>ID programma</strong> e <strong>password del genitore</strong>. Dopo l'accesso, il sito aggiornerà automaticamente lo stato della sessione.",
      form: {
        programIdLabel: "ID programma",
        programIdPlaceholder: "Per esempio AB12CD34",
        passwordLabel: "Password del genitore",
        passwordPlaceholder: "Inserisci la password",
        submit: "Accedi e apri il monitoraggio",
      },
      emptyLabel: "Accesso online",
      emptyTitle: "Il genitore si collega con ID programma e password senza schermate inutili e senza onboarding complesso.",
      emptyText:
        "Dopo l'accesso compare un riepilogo live: modalità attuale, argomento attivo, monete, errori, numero di pause e parametri della sessione.",
      previewOneLabel: "ID programma",
      previewOneValue: "accesso mirato",
      previewTwoLabel: "Password genitore",
      previewTwoValue: "accesso protetto",
      previewThreeLabel: "Aggiornamento automatico",
      previewThreeValue: "ogni 15 secondi",
      previewFourLabel: "Dashboard",
      previewFourValue: "statistiche + stato",
      dashboardLabel: "Sessione attiva",
      refresh: "Aggiorna ora",
      logout: "Esci",
      runtimeTitle: "Stato della sessione",
      settingsTitle: "Impostazioni del programma",
    },
    updates: {
      eyebrow: "Aggiornamenti",
      title: "Pubblicare una nuova versione non richiede di riprogettare il sito.",
      cardOneTitle: "Aggiornamento dell'app",
      cardOneText:
        "Basta sostituire <code>dist/MinecraftCoach.exe</code>. Il catalogo download servirà automaticamente la nuova build.",
      cardTwoTitle: "Aggiornamento dei moduli",
      cardTwoText:
        "Aggiungi o aggiorna le cartelle in <code>modules/</code> e il sito le mostrerà nel catalogo download.",
      cardThreeTitle: "Nuove sezioni del sito",
      cardThreeText:
        "La pagina è costruita come un insieme di blocchi forti, facili da estendere con roadmap, casi d'uso e nuove funzioni.",
    },
    secret: {
      eyebrow: "Blocco segreto",
      title: "Abbiamo lasciato spazio visivo per future funzioni private e nuovi modi di apprendere.",
      lead:
        "Questo blocco mantiene l'atmosfera del prodotto e funziona come teaser della prossima fase.",
      badge: "Teaser roadmap",
      text: "Abbiamo preparato uno spazio per modalità chiuse, scenari speciali e la prossima ondata di funzioni.",
      imageAlt: "Teaser del blocco segreto di Minecraft Coach",
    },
    footer: {
      text:
        "Landing page per download, moduli e monitoraggio delle sessioni di apprendimento, progettata nel linguaggio tecnologico dei tuoi riferimenti.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Dimensione non ancora disponibile",
      noData: "Nessun dato",
      downloadMeta: "File: {filename} · {size} · aggiornato {updatedAt}",
      downloadReady: "La build è disponibile per il download diretto dal sito.",
      downloadMissingMeta: "Il file dell'app non è ancora stato trovato nella cartella dist/.",
      downloadMissingStatus:
        "Carica o sostituisci dist/MinecraftCoach.exe e i pulsanti diventeranno attivi automaticamente.",
      moduleFallbackDescription:
        "La descrizione non è ancora pronta, ma il modulo può già essere scaricato e collegato all'app.",
      moduleCardLabel: "Modulo didattico",
      moduleTopics: "Argomenti: {count}",
      moduleLevels: "Livelli: {count}",
      moduleDownload: "Scarica modulo",
      modulesEmptyTitle: "Nessun modulo disponibile",
      modulesEmptyText:
        "Aggiungi le cartelle dei moduli alla directory <code>modules/</code> e appariranno qui automaticamente.",
      catalogErrorMeta: "Impossibile caricare il catalogo download.",
      catalogErrorStatus: "Errore nel caricamento del catalogo: {error}",
      catalogErrorTitle: "Il catalogo dei moduli non è disponibile",
      catalogErrorText:
        "Assicurati che il backend sia in esecuzione e che risponda a <code>/downloads/catalog</code>.",
      sessionTitle: "Sessione {programId}",
      sessionUpdated: "Ultimo aggiornamento: {updatedAt}",
      stats: {
        coins: "Monete",
        correct: "Corrette",
        wrong: "Errate",
        completedBreaks: "Pause completate",
        topics: "Argomenti totali",
        tasks: "Attività",
        childTopics: "Argomenti bimbo",
        adultTopics: "Argomenti adulto",
      },
      runtime: {
        currentModule: "Modulo attuale",
        currentTopic: "Argomento attuale",
        currentTask: "Attività attuale",
        state: "Stato",
        nextBreak: "Alla prossima pausa",
        manualPause: "Pausa manuale",
        lastMode: "Ultima modalità",
        lastActivity: "Ultima attività",
        notSelectedModule: "Non selezionato",
        notSelectedTopic: "Non selezionato",
        noActiveTask: "Nessuna attività attiva",
        unknown: "Sconosciuto",
        noData: "Nessun dato",
        manualPauseActive: "Attiva",
        manualPauseInactive: "Non attiva",
      },
      settings: {
        programId: "ID programma",
        windowLanguage: "Lingua finestra",
        breakInterval: "Intervallo tra le pause",
        tasksPerBreak: "Attività per pausa",
        lessonTime: "Durata lezione",
        serverUrl: "URL server",
        notSet: "Non impostato",
      },
      loginChecking: "Verifica accesso...",
      loginLoading: "Accesso riuscito. Caricamento dati...",
      monitorOpenError: "Impossibile aprire il monitoraggio: {error}",
      loginError: "Errore di accesso: {error}",
      sessionClosed: "La sessione è stata chiusa su questo dispositivo.",
    },
  },
  de: {
    meta: {
      title: "Minecraft Coach - Lernen während des Spielens",
      description:
        "Minecraft Coach pausiert das Spiel im richtigen Moment, zeigt Mini-Lektionen und Aufgaben und gibt Eltern eine Live-Ansicht der Sitzung per Programm-ID und Passwort.",
    },
    brand: {
      tagline: "Pause. Lernen. Weiter.",
    },
    language: {
      label: "Sprache",
      selectAria: "Sprachauswahl der Website",
    },
    nav: {
      ariaLabel: "Hauptnavigation",
      download: "Download",
      modules: "Module",
      howItWorks: "So funktioniert es",
      monitoring: "Monitoring",
      updates: "Updates",
      login: "Login per ID",
    },
    hero: {
      eyebrow: "Lernen im Spiel",
      title: "Die App, die das Spiel im richtigen Moment pausiert und Kinder zurück zum Lernen bringt.",
      lead:
        "Minecraft Coach zeigt Themen, Mini-Lektionen und Aufgaben während Pausen oder beim Spielen, sammelt Statistiken, speichert Module und ermöglicht Eltern, eine bestimmte Sitzung per Programm-ID und Passwort zu verfolgen.",
      primaryCta: "App herunterladen",
      secondaryCta: "So funktioniert es",
      signalPauseLabel: "Pause",
      signalPauseTitle: "Lernen im richtigen Moment",
      signalModulesLabel: "Module",
      signalModulesTitle: "Themen werden separat geladen",
      signalMonitoringLabel: "Monitoring",
      signalMonitoringTitle: "Eltern sehen die Sitzung online",
      sceneAlt: "Minecraft-Coach-Oberfläche mit pausiertem Spiel und Quizkarte",
      overlay: {
        pauseTitle: "Auto-Pause",
        pauseLead: "passt sich dem Spielrhythmus an",
        pausedState: "Pausiert",
        question: "Wie viel ist 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "Zeit zum Lernen!",
        ctaBody: "Beantworte die Frage, um fortzufahren.",
      },
    },
    quick: {
      eyebrow: "Produktlogik",
      title: "Ein System für Minecraft, Video, Desktop-Apps und elterliche Kontrolle.",
      cardOneTitle: "Spielpause",
      cardOneText: "Kinder bleiben im vertrauten Flow und wechseln sanft in einen Lernmoment.",
      cardTwoTitle: "Kurzer Zyklus",
      cardTwoText: "Kompakte Lektionen und Aufgaben bringen Fortschritt ohne Überlastung und ohne lange Unterbrechungen.",
      cardThreeTitle: "Kontrolle für Eltern",
      cardThreeText: "Die Website zeigt den aktuellen Stand einer bestimmten Sitzung mit Statistiken und Einstellungen.",
    },
    download: {
      eyebrow: "Download",
      title: "Immer die aktuelle Desktop-Version ohne manuelle Dateisuche.",
      lead: "Die Website zeigt automatisch den aktuellen Build und bietet einen direkten Link zur neuesten `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Dateiverfügbarkeit wird geprüft...",
      button: ".exe herunterladen",
      statusWaiting: "Wenn die Schaltfläche deaktiviert ist, wurde der neueste Build noch nicht in den dist/-Ordner hochgeladen.",
      sideOneTitle: "Der Katalog wird aus dem Backend-API gelesen",
      sideOneText: "Version, Dateigröße und Aktualisierungsdatum werden automatisch geladen.",
      sideTwoTitle: "Hero-Button und Download-Bereich bleiben synchron",
      sideTwoText: "Nutzer laden denselben aktuellen Build von beiden zentralen Stellen der Landingpage.",
      sideThreeTitle: "Geeignet für statisches Hosting",
      sideThreeText: "Das Frontend bleibt leicht und schnell, während die Funktionen über bestehende API-Endpunkte laufen.",
    },
    integration: {
      eyebrow: "Integrationen",
      title: "Die Website unterstützt jetzt die Multi-App-Idee und intelligente Lernpausen auch visuell.",
      lead:
        "Dieser Block basiert auf deiner Referenz und zeigt, wie eine Logik Spiel, Video und Desktop-Aktivität steuern kann.",
      imageAlt: "Integrationsdiagramm von Minecraft Coach mit Minecraft, YouTube und Desktop-Apps",
      minecraftTitle: "Minecraft",
      minecraftText:
        "Die App pausiert das Spiel, zeigt eine Frage oder Mini-Lektion und bringt das Kind zurück in den Spielfluss.",
      videoTitle: "YouTube und Video",
      videoText:
        "Dieselbe Logik funktioniert auch bei Lern- und Unterhaltungsvideos, wenn ein kurzer Lern-Interrupt nötig ist.",
      desktopTitle: "Desktop-Apps",
      desktopText:
        "Das Szenario lässt sich auf andere Anwendungen ausweiten und behält dasselbe Format für Pause, Aufgabe und Fortsetzung.",
      noteTitle: "Kerngedanke",
      noteText:
        "Minecraft Coach wirkt nicht mehr wie eine einfache Seite zum Herunterladen einer Datei, sondern wie ein technologisches System, das Spiel, Lernen und Fernaufsicht verbindet.",
    },
    modules: {
      eyebrow: "Module",
      title: "Wähle das passende Lernmodul und lade es herunter.",
      lead:
        "Module werden automatisch vom Server geladen. Nach dem Download genügt es, sie in den <code>modules</code>-Ordner des Programms zu legen.",
    },
    how: {
      eyebrow: "So funktioniert es",
      title: "Vom Download bis zur aktiven Lernsitzung.",
      stepOneTitle: "App herunterladen",
      stepOneText:
        "Der aktuelle Build liegt immer auf der Website, sodass Nutzer die richtige Version nicht manuell suchen müssen.",
      stepTwoTitle: "Passende Module hinzufügen",
      stepTwoText:
        "Themen und Inhalte werden separat geladen, sodass das Programm wachsen kann, ohne die Website neu zu bauen.",
      stepThreeTitle: "Intervalle und Passwort festlegen",
      stepThreeText:
        "Eltern wählen das Tempo der Lernpausen, die Anzahl der Aufgaben und schützen den Monitoring-Zugriff mit einem Passwort.",
      stepFourTitle: "Sitzung online verfolgen",
      stepFourText:
        "Mit Programm-ID und Passwort zeigt die Website Status, Statistiken und letzte Aktualisierung an.",
      whyLabel: "Warum es funktioniert",
      statusOneLabel: "Die Lektion wird in den vertrauten Spielfluss eingebettet",
      statusOneValue: "ohne harten Kontextwechsel",
      statusTwoLabel: "Die Referenzoptik hält den Tech-Charakter",
      statusTwoValue: "Neon, Schaltkreise, tiefer dunkler Hintergrund",
      statusThreeLabel: "Das Frontend bleibt mit dem bestehenden Backend verbunden",
      statusThreeValue: "ohne API-Umbau",
      statusFourLabel: "Blöcke lassen sich leicht um neue Bereiche erweitern",
      statusFourValue: "zum Beispiel um geschlossene Roadmap-Funktionen",
    },
    monitor: {
      eyebrow: "Monitoring",
      title: "Verbindung zu einer bestimmten Sitzung per Programm-ID.",
      lead:
        "Gib die <strong>Programm-ID</strong> und das <strong>Elternpasswort</strong> ein. Nach dem Login aktualisiert die Website den Sitzungsstatus automatisch.",
      form: {
        programIdLabel: "Programm-ID",
        programIdPlaceholder: "Zum Beispiel AB12CD34",
        passwordLabel: "Elternpasswort",
        passwordPlaceholder: "Passwort eingeben",
        submit: "Einloggen und Monitoring öffnen",
      },
      emptyLabel: "Online-Zugang",
      emptyTitle: "Eltern verbinden sich per Programm-ID und Passwort ohne unnötige Bildschirme oder kompliziertes Onboarding.",
      emptyText:
        "Nach dem Login erscheint eine Live-Übersicht: aktueller Modus, aktives Thema, Münzen, Fehler, Pausenanzahl und Sitzungsparameter.",
      previewOneLabel: "Programm-ID",
      previewOneValue: "gezielter Zugriff",
      previewTwoLabel: "Elternpasswort",
      previewTwoValue: "geschützter Login",
      previewThreeLabel: "Automatische Aktualisierung",
      previewThreeValue: "alle 15 Sekunden",
      previewFourLabel: "Dashboard",
      previewFourValue: "Statistiken + Status",
      dashboardLabel: "Aktive Sitzung",
      refresh: "Jetzt aktualisieren",
      logout: "Abmelden",
      runtimeTitle: "Sitzungsstatus",
      settingsTitle: "Programmeinstellungen",
    },
    updates: {
      eyebrow: "Updates",
      title: "Eine neue Version zu veröffentlichen erfordert kein komplettes Redesign der Website.",
      cardOneTitle: "App-Update",
      cardOneText:
        "Einfach <code>dist/MinecraftCoach.exe</code> ersetzen. Der Download-Katalog liefert den neuen Build automatisch aus.",
      cardTwoTitle: "Modul-Update",
      cardTwoText:
        "Ordner in <code>modules/</code> hinzufügen oder aktualisieren, und die Website zeigt sie automatisch im Download-Katalog an.",
      cardThreeTitle: "Neue Website-Bereiche",
      cardThreeText:
        "Die Seite besteht aus markanten Blöcken, die sich leicht um Roadmap-Punkte, Cases und neue Funktionen erweitern lassen.",
    },
    secret: {
      eyebrow: "Geheimer Block",
      title: "Wir haben bewusst Platz für zukünftige geschlossene Funktionen und neue Lernmodi reserviert.",
      lead:
        "Dieser Block hält die Produktatmosphäre aufrecht und funktioniert als Teaser für die nächste Phase.",
      badge: "Roadmap-Teaser",
      text: "Wir haben Platz für geschlossene Modi, spezielle Szenarien und die nächste Welle von Funktionen vorbereitet.",
      imageAlt: "Teaser für den geheimen Minecraft-Coach-Block",
    },
    footer: {
      text:
        "Landingpage für Downloads, Module und das Monitoring von Lernsitzungen, gestaltet in der technologischen Sprache deiner Referenzen.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Größe noch nicht verfügbar",
      noData: "Keine Daten",
      downloadMeta: "Datei: {filename} · {size} · aktualisiert {updatedAt}",
      downloadReady: "Der Build steht direkt auf der Website zum Download bereit.",
      downloadMissingMeta: "Die Anwendungsdatei wurde im dist/-Ordner noch nicht gefunden.",
      downloadMissingStatus:
        "Lade dist/MinecraftCoach.exe hoch oder ersetze die Datei, dann werden die Schaltflächen automatisch aktiv.",
      moduleFallbackDescription:
        "Die Beschreibung ist noch nicht ausgefüllt, aber das Modul kann bereits heruntergeladen und verbunden werden.",
      moduleCardLabel: "Lernmodul",
      moduleTopics: "Themen: {count}",
      moduleLevels: "Level: {count}",
      moduleDownload: "Modul herunterladen",
      modulesEmptyTitle: "Noch keine Module verfügbar",
      modulesEmptyText:
        "Füge Modulordner zum Verzeichnis <code>modules/</code> hinzu, dann erscheinen sie hier automatisch.",
      catalogErrorMeta: "Der Download-Katalog konnte nicht geladen werden.",
      catalogErrorStatus: "Fehler beim Laden des Katalogs: {error}",
      catalogErrorTitle: "Der Modulkatalog ist nicht verfügbar",
      catalogErrorText:
        "Stelle sicher, dass das Backend läuft und <code>/downloads/catalog</code> bereitstellt.",
      sessionTitle: "Sitzung {programId}",
      sessionUpdated: "Letzte Aktualisierung: {updatedAt}",
      stats: {
        coins: "Münzen",
        correct: "Richtig",
        wrong: "Falsch",
        completedBreaks: "Abgeschlossene Pausen",
        topics: "Themen gesamt",
        tasks: "Aufgaben",
        childTopics: "Kinderthemen",
        adultTopics: "Erwachsenenthemen",
      },
      runtime: {
        currentModule: "Aktuelles Modul",
        currentTopic: "Aktuelles Thema",
        currentTask: "Aktuelle Aufgabe",
        state: "Status",
        nextBreak: "Bis zur nächsten Pause",
        manualPause: "Manuelle Pause",
        lastMode: "Letzter Modus",
        lastActivity: "Letzte Aktivität",
        notSelectedModule: "Nicht ausgewählt",
        notSelectedTopic: "Nicht ausgewählt",
        noActiveTask: "Keine aktive Aufgabe",
        unknown: "Unbekannt",
        noData: "Keine Daten",
        manualPauseActive: "Aktiv",
        manualPauseInactive: "Inaktiv",
      },
      settings: {
        programId: "Programm-ID",
        windowLanguage: "Fenstersprache",
        breakInterval: "Pausenintervall",
        tasksPerBreak: "Aufgaben pro Pause",
        lessonTime: "Lektionszeit",
        serverUrl: "Server-URL",
        notSet: "Nicht gesetzt",
      },
      loginChecking: "Zugang wird geprüft...",
      loginLoading: "Login erfolgreich. Daten werden geladen...",
      monitorOpenError: "Monitoring konnte nicht geöffnet werden: {error}",
      loginError: "Login-Fehler: {error}",
      sessionClosed: "Die Sitzung wurde auf diesem Gerät geschlossen.",
    },
  },
  uk: {
    meta: {
      title: "Minecraft Coach - навчання під час гри",
      description:
        "Minecraft Coach вчасно ставить гру на паузу, показує міні-уроки й завдання та дає батькам моніторинг сесії за ID програми і паролем.",
    },
    brand: {
      tagline: "Пауза. Навчання. Продовження.",
    },
    language: {
      label: "Мова",
      selectAria: "Вибір мови сайту",
    },
    nav: {
      ariaLabel: "Головна навігація",
      download: "Завантажити",
      modules: "Модулі",
      howItWorks: "Як це працює",
      monitoring: "Моніторинг",
      updates: "Оновлення",
      login: "Увійти за ID",
    },
    hero: {
      eyebrow: "Навчання прямо в грі",
      title: "Застосунок, який вчасно зупиняє гру й повертає дитину до навчання.",
      lead:
        "Minecraft Coach показує теми, міні-уроки й завдання прямо під час відпочинку або гри, веде статистику, зберігає модулі й дозволяє батькам стежити за конкретною сесією за ID програми та паролем.",
      primaryCta: "Завантажити застосунок",
      secondaryCta: "Як це працює",
      signalPauseLabel: "Пауза",
      signalPauseTitle: "Урок у потрібний момент",
      signalModulesLabel: "Модулі",
      signalModulesTitle: "Теми завантажуються окремо",
      signalMonitoringLabel: "Моніторинг",
      signalMonitoringTitle: "Батьки бачать сесію онлайн",
      sceneAlt: "Інтерфейс Minecraft Coach із паузою гри та карткою запитання",
      overlay: {
        pauseTitle: "Автопауза",
        pauseLead: "вбудовується в ритм гри",
        pausedState: "Пауза",
        question: "Скільки буде 2 + 2?",
        optionOne: "2",
        optionTwo: "3",
        optionThree: "4",
        optionFour: "5",
        ctaTitle: "Час вчитися!",
        ctaBody: "Дайте відповідь, щоб продовжити.",
      },
    },
    quick: {
      eyebrow: "Логіка продукту",
      title: "Єдина система для Minecraft, відео, desktop-застосунків і батьківського контролю.",
      cardOneTitle: "Ігрова пауза",
      cardOneText: "Дитина не випадає зі звичного сценарію, а м'яко переходить до навчального етапу.",
      cardTwoTitle: "Короткий цикл",
      cardTwoText: "Невеликі уроки й завдання дають результат без перевантаження й довгих зупинок.",
      cardThreeTitle: "Контроль для батьків",
      cardThreeText: "Сайт показує актуальний стан конкретної сесії, статистику й налаштування.",
    },
    download: {
      eyebrow: "Завантажити",
      title: "Завжди актуальна desktop-версія без ручного пошуку файлів.",
      lead: "Сайт сам показує поточну збірку застосунку й дає пряме посилання на свіжий `.exe`.",
      cardLabel: "Desktop build",
      metaLoading: "Перевіряємо наявність файла...",
      button: "Завантажити .exe",
      statusWaiting: "Якщо кнопка неактивна, актуальну збірку ще не завантажено в папку dist/.",
      sideOneTitle: "Каталог читається з backend API",
      sideOneText: "Версія, розмір файла та дата оновлення підтягуються автоматично.",
      sideTwoTitle: "Hero-кнопка і секція завантаження синхронізовані",
      sideTwoText: "Користувач завжди завантажує ту саму актуальну збірку з двох ключових точок лендингу.",
      sideThreeTitle: "Підходить для статичного хостингу",
      sideThreeText: "Фронтенд залишається легким і швидким, а функціональність працює через існуючі API-ендпоїнти.",
    },
    integration: {
      eyebrow: "Інтеграції",
      title: "Сайт візуально підтримує ідею мультизастосунку та розумних навчальних пауз.",
      lead:
        "Блок побудований на вашому референсі й пояснює, як одна логіка керує грою, відео й desktop-активністю.",
      imageAlt: "Схема інтеграції Minecraft Coach з Minecraft, YouTube і desktop-застосунками",
      minecraftTitle: "Minecraft",
      minecraftText:
        "Програма ставить гру на паузу, показує запитання або міні-урок і повертає дитину назад у ігровий потік.",
      videoTitle: "YouTube і відео",
      videoText:
        "Та сама логіка працює і для навчальних та розважальних відео, коли потрібен короткий навчальний interrupt.",
      desktopTitle: "Desktop apps",
      desktopText:
        "Сценарій масштабується на інші застосунки, зберігаючи єдиний формат паузи, завдання і продовження.",
      noteTitle: "Головна ідея",
      noteText:
        "Minecraft Coach виглядає не як звичайний лендинг про “завантажити exe”, а як технологічна система, що поєднує гру, навчання та віддалений контроль.",
    },
    modules: {
      eyebrow: "Модулі",
      title: "Оберіть і завантажте потрібний навчальний модуль.",
      lead:
        "Модулі автоматично завантажуються із сервера. Після завантаження достатньо покласти їх у папку <code>modules</code> вашої програми.",
    },
    how: {
      eyebrow: "Як це працює",
      title: "Шлях від встановлення до навчальної сесії.",
      stepOneTitle: "Завантажте застосунок",
      stepOneText:
        "На сайті завжди доступна свіжа збірка, тому користувачу не потрібно шукати правильну версію вручну.",
      stepTwoTitle: "Додайте потрібні модулі",
      stepTwoText:
        "Теми й набори контенту завантажуються окремо, тому програму можна розширювати без нової збірки сайту.",
      stepThreeTitle: "Налаштуйте інтервали і пароль",
      stepThreeText:
        "Батьки задають ритм навчальних пауз, кількість завдань і захищають доступ до моніторингу паролем.",
      stepFourTitle: "Стежте за сесією онлайн",
      stepFourText:
        "За ID програми й паролем сайт показує поточний стан, статистику та час останнього оновлення.",
      whyLabel: "Чому це працює",
      statusOneLabel: "Урок вбудований у звичний ігровий цикл",
      statusOneValue: "без різкої зміни контексту",
      statusTwoLabel: "Референсний стиль підтримує технологічне відчуття",
      statusTwoValue: "неон, схеми, глибокий темний фон",
      statusThreeLabel: "Фронтенд підключений до існуючого backend",
      statusThreeValue: "без переписування API",
      statusFourLabel: "Блоки легко розширювати новими секціями",
      statusFourValue: "наприклад, закритими roadmap-функціями",
    },
    monitor: {
      eyebrow: "Моніторинг",
      title: "Підключення до конкретної сесії за ID програми.",
      lead:
        "Введіть <strong>ID програми</strong> і <strong>пароль батьків</strong>. Після входу сайт автоматично оновлюватиме стан сесії.",
      form: {
        programIdLabel: "ID програми",
        programIdPlaceholder: "Наприклад AB12CD34",
        passwordLabel: "Пароль батьків",
        passwordPlaceholder: "Введіть пароль",
        submit: "Увійти і відкрити моніторинг",
      },
      emptyLabel: "Онлайн-доступ",
      emptyTitle: "Батьки підключаються за ID програми й паролем без зайвих екранів і складного онбордингу.",
      emptyText:
        "Після входу відкривається жива зведена панель: поточний режим, активна тема, монети, помилки, кількість пауз і параметри сесії.",
      previewOneLabel: "ID програми",
      previewOneValue: "точковий доступ",
      previewTwoLabel: "Пароль батьків",
      previewTwoValue: "захищений вхід",
      previewThreeLabel: "Автооновлення",
      previewThreeValue: "кожні 15 секунд",
      previewFourLabel: "Dashboard",
      previewFourValue: "статистика + статус",
      dashboardLabel: "Активна сесія",
      refresh: "Оновити зараз",
      logout: "Вийти",
      runtimeTitle: "Стан сесії",
      settingsTitle: "Налаштування програми",
    },
    updates: {
      eyebrow: "Оновлення",
      title: "Щоб опублікувати нову версію, не потрібно заново проєктувати сайт.",
      cardOneTitle: "Оновлення застосунку",
      cardOneText:
        "Достатньо замінити <code>dist/MinecraftCoach.exe</code>. Каталог завантажень автоматично віддаватиме нову збірку.",
      cardTwoTitle: "Оновлення модулів",
      cardTwoText:
        "Додайте або оновіть папки в <code>modules/</code>, і сайт сам покаже їх у каталозі завантажень.",
      cardThreeTitle: "Нові секції сайту",
      cardThreeText:
        "Сторінка зібрана як набір виразних блоків, які легко розширювати під roadmap, кейси й нові функції.",
    },
    secret: {
      eyebrow: "Секретний блок",
      title: "Ми навмисно залишили простір під майбутні закриті функції та нові режими навчання.",
      lead:
        "Цей блок підтримує атмосферу продукту і працює як тизер наступного етапу розвитку.",
      badge: "Тизер roadmap",
      text: "Підготували місце для закритих режимів, спеціальних сценаріїв і наступної хвилі функцій.",
      imageAlt: "Тизер секретного блоку Minecraft Coach",
    },
    footer: {
      text:
        "Лендинг завантажень, модулів і моніторингу навчальних сесій, зібраний у технологічному стилі ваших референсів.",
    },
    dynamic: {
      appTitleDefault: "Minecraft Coach Desktop",
      sizeUnknown: "Розмір поки невідомий",
      noData: "Немає даних",
      downloadMeta: "Файл: {filename} · {size} · оновлено {updatedAt}",
      downloadReady: "Збірка доступна для прямого завантаження із сайту.",
      downloadMissingMeta: "Файл застосунку ще не знайдено в папці dist/.",
      downloadMissingStatus:
        "Завантажте або замініть dist/MinecraftCoach.exe, і кнопки стануть активними автоматично.",
      moduleFallbackDescription:
        "Опис поки не заповнено, але модуль уже можна завантажити й підключити до програми.",
      moduleCardLabel: "Навчальний модуль",
      moduleTopics: "Тем: {count}",
      moduleLevels: "Рівнів: {count}",
      moduleDownload: "Завантажити модуль",
      modulesEmptyTitle: "Поки немає доступних модулів",
      modulesEmptyText:
        "Додайте папки модулів у каталог <code>modules/</code>, і вони з'являться тут автоматично.",
      catalogErrorMeta: "Не вдалося отримати каталог завантажень.",
      catalogErrorStatus: "Помилка завантаження каталогу: {error}",
      catalogErrorTitle: "Каталог модулів недоступний",
      catalogErrorText:
        "Перевірте, що backend запущений і відповідає на маршрут <code>/downloads/catalog</code>.",
      sessionTitle: "Сесія {programId}",
      sessionUpdated: "Останнє оновлення: {updatedAt}",
      stats: {
        coins: "Монети",
        correct: "Правильних",
        wrong: "Помилок",
        completedBreaks: "Завершених пауз",
        topics: "Тем усього",
        tasks: "Завдань",
        childTopics: "Дитячих тем",
        adultTopics: "Дорослих тем",
      },
      runtime: {
        currentModule: "Поточний модуль",
        currentTopic: "Поточна тема",
        currentTask: "Поточне завдання",
        state: "Стан",
        nextBreak: "До наступної паузи",
        manualPause: "Ручна пауза",
        lastMode: "Останній режим",
        lastActivity: "Остання активність",
        notSelectedModule: "Не вибрано",
        notSelectedTopic: "Не вибрано",
        noActiveTask: "Немає активного завдання",
        unknown: "Невідомо",
        noData: "Немає даних",
        manualPauseActive: "Активна",
        manualPauseInactive: "Не активна",
      },
      settings: {
        programId: "ID програми",
        windowLanguage: "Мова вікна",
        breakInterval: "Інтервал між паузами",
        tasksPerBreak: "Завдань у паузі",
        lessonTime: "Час уроку",
        serverUrl: "URL сервера",
        notSet: "Не задано",
      },
      loginChecking: "Перевіряємо доступ...",
      loginLoading: "Вхід виконано. Завантажуємо дані...",
      monitorOpenError: "Не вдалося відкрити моніторинг: {error}",
      loginError: "Помилка входу: {error}",
      sessionClosed: "Сесію закрито на цьому пристрої.",
    },
  },
};

const translationOverrides = {
  en: {
    meta: {
      title: "Minecraft Coach - learning breaks during Minecraft",
      description:
        "Minecraft Coach is a Windows app that pauses Minecraft at chosen intervals, shows a short quiz or mini-lesson, and lets parents review the session with a program ID and password.",
    },
    brand: {
      tagline: "Short learning breaks during play.",
    },
    language: {
      label: "Language",
      selectAria: "Choose site language",
    },
    languagePrompt: {
      eyebrow: "Choose a language",
      title: "Which language would you like to use?",
      text: "You can change it later from the menu in the top-right corner. English is the default option.",
      continue: "Continue in English",
    },
    nav: {
      ariaLabel: "Main navigation",
      download: "Download",
      modules: "Learning packs",
      howItWorks: "How it works",
      monitoring: "Parent view",
      login: "Open parent view",
    },
    hero: {
      eyebrow: "Made for short study breaks",
      title: "Minecraft Coach pauses Minecraft, shows a short learning task, and then lets the child continue playing.",
      lead:
        "It is a Windows app for families who want to add short quizzes or mini-lessons to game time. The goal is simple: pause for a moment, complete one small task, and return to the game.",
      primaryCta: "Download for Windows",
      secondaryCta: "See how it works",
      signalPauseLabel: "Game pause",
      signalPauseTitle: "Minecraft stops at the chosen time",
      signalModulesLabel: "Short task",
      signalModulesTitle: "A question or mini-lesson appears",
      signalMonitoringLabel: "Parent view",
      signalMonitoringTitle: "Session data can be reviewed later",
      sceneAlt: "Minecraft Coach interface showing a paused game and a short question",
      overlay: {
        pauseTitle: "Auto pause",
        pauseLead: "fits into the game routine",
        pausedState: "Paused",
        question: "What is 2 + 2?",
        ctaTitle: "Time for a short task",
        ctaBody: "Answer to continue.",
      },
    },
    quick: {
      eyebrow: "Overview",
      title: "What the app does",
      cardOneTitle: "Pauses the game",
      cardOneText: "The app stops Minecraft at the interval set by the adult.",
      cardTwoTitle: "Shows one short task",
      cardTwoText: "The child sees a short question or mini-lesson instead of a long interruption.",
      cardThreeTitle: "Saves session information",
      cardThreeText: "The app records progress so the session can be reviewed later.",
    },
    download: {
      eyebrow: "Download",
      title: "Start with the current Windows version",
      lead: "Download the desktop app first. If learning packs are available, you can add them separately afterward.",
      cardLabel: "Windows app",
      metaLoading: "Checking the current build...",
      button: "Download .exe",
      statusWaiting: "If the button is inactive, the current build has not been uploaded yet.",
      sideOneTitle: "Windows desktop app",
      sideOneText: "The site shows the current build, file size, and update time.",
      sideTwoTitle: "Learning packs are optional",
      sideTwoText: "You can start with the app alone and add packs later if you need ready-made topics.",
      sideThreeTitle: "Parent view uses a program ID",
      sideThreeText: "The session page is opened with the program ID and the parent password set in the app.",
    },
    modules: {
      eyebrow: "Learning packs",
      title: "Add a pack if you want ready-made topics and tasks",
      lead: "Learning packs are downloaded separately. After downloading, place them in the <code>modules</code> folder used by the app.",
    },
    how: {
      eyebrow: "How it works",
      title: "What a family usually does",
      stepOneTitle: "Install the app",
      stepOneText: "Download the Windows version and start the program on the computer used for Minecraft.",
      stepTwoTitle: "Choose settings",
      stepTwoText: "An adult chooses the break interval, the number of tasks, and a parent password.",
      stepThreeTitle: "Add learning packs if needed",
      stepThreeText: "You can use ready-made packs or keep the setup simple and start with the app only.",
      stepFourTitle: "Use the parent view",
      stepFourText: "Open the session page with the program ID and password to check what is happening during the session.",
      whyLabel: "Useful to know",
      statusOneLabel: "The app is for Windows",
      statusOneValue: "designed for desktop use",
      statusTwoLabel: "Tasks are meant to be short",
      statusTwoValue: "one small step before returning",
      statusThreeLabel: "Learning packs are optional",
      statusThreeValue: "the app can work without them",
      statusFourLabel: "Parent view needs ID and password",
      statusFourValue: "set inside the app",
    },
    monitor: {
      eyebrow: "Parent view",
      title: "Parents can open a session page with the program ID and password",
      lead:
        "Enter the <strong>program ID</strong> shown by the app and the <strong>parent password</strong> created during setup. The page will then refresh the session data automatically.",
      form: {
        programIdLabel: "Program ID",
        programIdPlaceholder: "For example AB12CD34",
        passwordLabel: "Parent password",
        passwordPlaceholder: "Enter password",
        submit: "Open session page",
      },
      emptyLabel: "Session page",
      emptyTitle: "After login, this page shows the current state of one running session.",
      emptyText:
        "It can display the active topic, recent activity, number of pauses, answers, coins, and the main settings used by the app.",
      previewOneLabel: "Program ID",
      previewOneValue: "one session only",
      previewTwoLabel: "Parent password",
      previewTwoValue: "private access",
      previewThreeLabel: "Auto refresh",
      previewThreeValue: "every 15 seconds",
      previewFourLabel: "Live data",
      previewFourValue: "status and statistics",
      dashboardLabel: "Current session",
      refresh: "Refresh now",
      logout: "Sign out",
      runtimeTitle: "Session status",
      settingsTitle: "App settings",
    },
    footer: {
      text: "Minecraft Coach is a Windows app that adds short learning breaks to Minecraft sessions and provides a simple parent view.",
    },
    dynamic: {
      moduleCardLabel: "Learning pack",
      moduleFallbackDescription: "A ready-made description has not been added yet, but the pack can already be downloaded and used in the app.",
      moduleTopics: "Topics: {count}",
      moduleLevels: "Levels: {count}",
      moduleDownload: "Download pack",
      modulesEmptyTitle: "No learning packs are available yet",
      modulesEmptyText: "When packs are added to the <code>modules/</code> catalog, they will appear here automatically.",
      downloadReady: "The current Windows build is ready to download.",
      downloadMissingMeta: "The Windows build is not available right now.",
      downloadMissingStatus: "Please try again later or upload a new build to make the download button active.",
      catalogErrorMeta: "Could not load the download catalog.",
      catalogErrorStatus: "Catalog error: {error}",
      catalogErrorTitle: "Learning packs are not available right now",
      catalogErrorText: "Please check that the backend is running and the <code>/downloads/catalog</code> route is available.",
      loginLoading: "Login succeeded. Loading session data...",
      monitorOpenError: "Could not open the session page: {error}",
      loginError: "Login error: {error}",
    },
  },
  ru: {
    meta: {
      title: "Minecraft Coach - короткие учебные паузы в Minecraft",
      description:
        "Minecraft Coach — это Windows-приложение, которое ставит Minecraft на паузу через выбранные интервалы, показывает короткий вопрос или мини-урок и позволяет родителю просматривать сессию по ID программы и паролю.",
    },
    brand: {
      tagline: "Короткие учебные паузы во время игры.",
    },
    language: {
      label: "Язык",
      selectAria: "Выбрать язык сайта",
    },
    languagePrompt: {
      eyebrow: "Выбор языка",
      title: "На каком языке вам удобнее читать сайт?",
      text: "Позже язык можно изменить в меню справа вверху. По умолчанию выбран английский.",
      continue: "Продолжить на английском",
    },
    nav: {
      ariaLabel: "Главная навигация",
      download: "Скачать",
      modules: "Учебные пакеты",
      howItWorks: "Как это работает",
      monitoring: "Родительский просмотр",
      login: "Открыть родительский просмотр",
    },
    hero: {
      eyebrow: "Для коротких учебных пауз",
      title: "Minecraft Coach ставит Minecraft на короткую паузу, показывает небольшое учебное задание и потом возвращает ребёнка в игру.",
      lead:
        "Это Windows-приложение для семей, которые хотят добавить в игровое время короткие вопросы или мини-уроки. Идея простая: небольшая пауза, одно короткое задание и возврат к игре.",
      primaryCta: "Скачать для Windows",
      secondaryCta: "Посмотреть, как это работает",
      signalPauseLabel: "Пауза в игре",
      signalPauseTitle: "Minecraft останавливается в выбранный момент",
      signalModulesLabel: "Короткое задание",
      signalModulesTitle: "Появляется вопрос или мини-урок",
      signalMonitoringLabel: "Родительский просмотр",
      signalMonitoringTitle: "Данные сессии можно посмотреть позже",
      sceneAlt: "Интерфейс Minecraft Coach с паузой игры и коротким вопросом",
      overlay: {
        pauseTitle: "Авто-пауза",
        pauseLead: "встраивается в игровой ритм",
        pausedState: "Пауза",
        question: "Сколько будет 2 + 2?",
        ctaTitle: "Время для короткого задания",
        ctaBody: "Ответьте, чтобы продолжить.",
      },
    },
    quick: {
      eyebrow: "Обзор",
      title: "Что делает приложение",
      cardOneTitle: "Ставит игру на паузу",
      cardOneText: "Приложение останавливает Minecraft через интервал, который задаёт взрослый.",
      cardTwoTitle: "Показывает одно короткое задание",
      cardTwoText: "Ребёнок видит короткий вопрос или мини-урок вместо долгого отвлечения.",
      cardThreeTitle: "Сохраняет данные сессии",
      cardThreeText: "Приложение записывает прогресс, чтобы к нему можно было вернуться позже.",
    },
    download: {
      eyebrow: "Скачать",
      title: "Начните с актуальной версии для Windows",
      lead: "Сначала скачайте desktop-приложение. Если доступны учебные пакеты, их можно добавить отдельно позже.",
      cardLabel: "Windows-приложение",
      metaLoading: "Проверяем текущую сборку...",
      button: "Скачать .exe",
      statusWaiting: "Если кнопка неактивна, актуальная сборка ещё не загружена.",
      sideOneTitle: "Desktop-приложение для Windows",
      sideOneText: "Сайт показывает текущую сборку, размер файла и время обновления.",
      sideTwoTitle: "Учебные пакеты необязательны",
      sideTwoText: "Можно начать только с приложения и добавить пакеты позже, если нужны готовые темы.",
      sideThreeTitle: "Родительский просмотр работает по ID программы",
      sideThreeText: "Страница сессии открывается по ID программы и родительскому паролю, который задаётся в приложении.",
    },
    modules: {
      eyebrow: "Учебные пакеты",
      title: "Добавьте пакет, если нужны готовые темы и задания",
      lead: "Учебные пакеты скачиваются отдельно. После загрузки поместите их в папку <code>modules</code>, которую использует приложение.",
    },
    how: {
      eyebrow: "Как это работает",
      title: "Как обычно выглядит работа с приложением",
      stepOneTitle: "Установите приложение",
      stepOneText: "Скачайте версию для Windows и запустите программу на компьютере, где используется Minecraft.",
      stepTwoTitle: "Выберите настройки",
      stepTwoText: "Взрослый задаёт интервал пауз, количество заданий и родительский пароль.",
      stepThreeTitle: "Добавьте учебные пакеты при необходимости",
      stepThreeText: "Можно использовать готовые пакеты или оставить настройку простой и начать только с приложения.",
      stepFourTitle: "Откройте родительский просмотр",
      stepFourText: "По ID программы и паролю можно открыть страницу сессии и посмотреть, что происходит во время игры.",
      whyLabel: "Важно знать",
      statusOneLabel: "Приложение рассчитано на Windows",
      statusOneValue: "для работы на настольном компьютере",
      statusTwoLabel: "Задания задуманы короткими",
      statusTwoValue: "одно небольшое действие перед возвращением",
      statusThreeLabel: "Учебные пакеты необязательны",
      statusThreeValue: "приложение может работать и без них",
      statusFourLabel: "Для родительского просмотра нужны ID и пароль",
      statusFourValue: "они задаются внутри приложения",
    },
    monitor: {
      eyebrow: "Родительский просмотр",
      title: "Родитель может открыть страницу сессии по ID программы и паролю",
      lead:
        "Введите <strong>ID программы</strong>, который показывает приложение, и <strong>родительский пароль</strong>, созданный при настройке. После этого страница начнёт автоматически обновлять данные сессии.",
      form: {
        programIdLabel: "ID программы",
        programIdPlaceholder: "Например AB12CD34",
        passwordLabel: "Родительский пароль",
        passwordPlaceholder: "Введите пароль",
        submit: "Открыть страницу сессии",
      },
      emptyLabel: "Страница сессии",
      emptyTitle: "После входа здесь отображается текущее состояние одной активной сессии.",
      emptyText:
        "Здесь могут показываться активная тема, последние действия, количество пауз, ответы, монеты и основные настройки приложения.",
      previewOneLabel: "ID программы",
      previewOneValue: "только одна сессия",
      previewTwoLabel: "Родительский пароль",
      previewTwoValue: "закрытый доступ",
      previewThreeLabel: "Автообновление",
      previewThreeValue: "каждые 15 секунд",
      previewFourLabel: "Живые данные",
      previewFourValue: "статус и статистика",
      dashboardLabel: "Текущая сессия",
      refresh: "Обновить сейчас",
      logout: "Выйти",
      runtimeTitle: "Состояние сессии",
      settingsTitle: "Настройки приложения",
    },
    footer: {
      text: "Minecraft Coach — это Windows-приложение, которое добавляет короткие учебные паузы в сессии Minecraft и даёт простой родительский просмотр.",
    },
    dynamic: {
      moduleCardLabel: "Учебный пакет",
      moduleFallbackDescription: "Подробное описание пока не добавлено, но пакет уже можно скачать и использовать в приложении.",
      moduleTopics: "Тем: {count}",
      moduleLevels: "Уровней: {count}",
      moduleDownload: "Скачать пакет",
      modulesEmptyTitle: "Учебные пакеты пока недоступны",
      modulesEmptyText: "Когда пакеты появятся в каталоге <code>modules/</code>, они автоматически отобразятся здесь.",
      downloadReady: "Актуальная сборка для Windows готова к скачиванию.",
      downloadMissingMeta: "Сборка для Windows сейчас недоступна.",
      downloadMissingStatus: "Попробуйте позже или загрузите новую сборку, чтобы кнопка скачивания снова стала активной.",
      catalogErrorMeta: "Не удалось получить каталог загрузок.",
      catalogErrorStatus: "Ошибка каталога: {error}",
      catalogErrorTitle: "Учебные пакеты сейчас недоступны",
      catalogErrorText: "Проверьте, что backend запущен и маршрут <code>/downloads/catalog</code> доступен.",
      loginLoading: "Вход выполнен. Загружаем данные сессии...",
      monitorOpenError: "Не удалось открыть страницу сессии: {error}",
      loginError: "Ошибка входа: {error}",
    },
  },
  pl: {
    meta: {
      title: "Minecraft Coach - krótkie przerwy edukacyjne w Minecraft",
      description:
        "Minecraft Coach to aplikacja dla Windows, która zatrzymuje Minecrafta w wybranych odstępach, pokazuje krótkie pytanie lub mini-lekcję i pozwala rodzicowi przeglądać sesję po ID programu i haśle.",
    },
    brand: {
      tagline: "Krótkie przerwy edukacyjne podczas gry.",
    },
    language: {
      label: "Język",
      selectAria: "Wybierz język strony",
    },
    languagePrompt: {
      eyebrow: "Wybór języka",
      title: "W jakim języku chcesz przeglądać stronę?",
      text: "Później możesz zmienić język z menu w prawym górnym rogu. Domyślnie wybrany jest angielski.",
      continue: "Kontynuuj po angielsku",
    },
    nav: {
      ariaLabel: "Główna nawigacja",
      download: "Pobierz",
      modules: "Pakiety nauki",
      howItWorks: "Jak to działa",
      monitoring: "Widok rodzica",
      login: "Otwórz widok rodzica",
    },
    hero: {
      eyebrow: "Do krótkich przerw edukacyjnych",
      title: "Minecraft Coach zatrzymuje Minecraft na chwilę, pokazuje krótkie zadanie i pozwala dziecku wrócić do gry.",
      lead:
        "To aplikacja Windows dla rodzin, które chcą dodać do czasu gry krótkie pytania lub mini-lekcje. Pomysł jest prosty: krótka pauza, jedno małe zadanie i powrót do gry.",
      primaryCta: "Pobierz dla Windows",
      secondaryCta: "Zobacz, jak to działa",
      signalPauseLabel: "Pauza w grze",
      signalPauseTitle: "Minecraft zatrzymuje się w wybranym momencie",
      signalModulesLabel: "Krótkie zadanie",
      signalModulesTitle: "Pojawia się pytanie lub mini-lekcja",
      signalMonitoringLabel: "Widok rodzica",
      signalMonitoringTitle: "Dane sesji można sprawdzić później",
      sceneAlt: "Interfejs Minecraft Coach z pauzą gry i krótkim pytaniem",
      overlay: {
        pauseTitle: "Auto-pauza",
        pauseLead: "pasuje do rytmu gry",
        pausedState: "Pauza",
        question: "Ile to 2 + 2?",
        ctaTitle: "Czas na krótkie zadanie",
        ctaBody: "Odpowiedz, aby kontynuować.",
      },
    },
    quick: {
      eyebrow: "Przegląd",
      title: "Co robi aplikacja",
      cardOneTitle: "Zatrzymuje grę",
      cardOneText: "Aplikacja zatrzymuje Minecrafta zgodnie z interwałem ustawionym przez dorosłego.",
      cardTwoTitle: "Pokazuje jedno krótkie zadanie",
      cardTwoText: "Dziecko widzi krótkie pytanie lub mini-lekcję zamiast długiego oderwania od gry.",
      cardThreeTitle: "Zapisuje dane sesji",
      cardThreeText: "Aplikacja zapisuje postęp, aby można go było później sprawdzić.",
    },
    download: {
      eyebrow: "Pobierz",
      title: "Zacznij od aktualnej wersji dla Windows",
      lead: "Najpierw pobierz aplikację desktopową. Jeśli dostępne są pakiety nauki, możesz dodać je osobno później.",
      cardLabel: "Aplikacja Windows",
      metaLoading: "Sprawdzamy bieżącą wersję...",
      button: "Pobierz .exe",
      statusWaiting: "Jeśli przycisk jest nieaktywny, aktualna wersja nie została jeszcze przesłana.",
      sideOneTitle: "Aplikacja desktopowa dla Windows",
      sideOneText: "Strona pokazuje bieżący build, rozmiar pliku i czas aktualizacji.",
      sideTwoTitle: "Pakiety nauki są opcjonalne",
      sideTwoText: "Możesz zacząć od samej aplikacji i dodać pakiety później, jeśli potrzebujesz gotowych tematów.",
      sideThreeTitle: "Widok rodzica działa przez ID programu",
      sideThreeText: "Strona sesji otwiera się przy użyciu ID programu i hasła rodzica ustawionego w aplikacji.",
    },
    modules: {
      eyebrow: "Pakiety nauki",
      title: "Dodaj pakiet, jeśli chcesz gotowe tematy i zadania",
      lead: "Pakiety nauki pobiera się osobno. Po pobraniu umieść je w folderze <code>modules</code> używanym przez aplikację.",
    },
    how: {
      eyebrow: "Jak to działa",
      title: "Jak zwykle korzysta z tego rodzina",
      stepOneTitle: "Zainstaluj aplikację",
      stepOneText: "Pobierz wersję dla Windows i uruchom program na komputerze używanym do Minecrafta.",
      stepTwoTitle: "Wybierz ustawienia",
      stepTwoText: "Dorosły ustawia interwał przerw, liczbę zadań i hasło rodzica.",
      stepThreeTitle: "Dodaj pakiety nauki, jeśli trzeba",
      stepThreeText: "Możesz używać gotowych pakietów albo zacząć od prostego ustawienia tylko z aplikacją.",
      stepFourTitle: "Otwórz widok rodzica",
      stepFourText: "Za pomocą ID programu i hasła możesz otworzyć stronę sesji i sprawdzić, co dzieje się podczas gry.",
      whyLabel: "Warto wiedzieć",
      statusOneLabel: "Aplikacja jest przeznaczona dla Windows",
      statusOneValue: "do pracy na komputerze desktopowym",
      statusTwoLabel: "Zadania mają być krótkie",
      statusTwoValue: "jeden mały krok przed powrotem",
      statusThreeLabel: "Pakiety nauki są opcjonalne",
      statusThreeValue: "aplikacja może działać bez nich",
      statusFourLabel: "Widok rodzica wymaga ID i hasła",
      statusFourValue: "ustawianych w aplikacji",
    },
    monitor: {
      eyebrow: "Widok rodzica",
      title: "Rodzic może otworzyć stronę sesji przy użyciu ID programu i hasła",
      lead:
        "Wpisz <strong>ID programu</strong> widoczne w aplikacji oraz <strong>hasło rodzica</strong> utworzone podczas konfiguracji. Strona zacznie wtedy automatycznie odświeżać dane sesji.",
      form: {
        programIdLabel: "ID programu",
        programIdPlaceholder: "Na przykład AB12CD34",
        passwordLabel: "Hasło rodzica",
        passwordPlaceholder: "Wpisz hasło",
        submit: "Otwórz stronę sesji",
      },
      emptyLabel: "Strona sesji",
      emptyTitle: "Po zalogowaniu ta strona pokazuje bieżący stan jednej aktywnej sesji.",
      emptyText:
        "Może pokazywać aktywny temat, ostatnie działania, liczbę przerw, odpowiedzi, monety i główne ustawienia używane przez aplikację.",
      previewOneLabel: "ID programu",
      previewOneValue: "tylko jedna sesja",
      previewTwoLabel: "Hasło rodzica",
      previewTwoValue: "prywatny dostęp",
      previewThreeLabel: "Auto-odświeżanie",
      previewThreeValue: "co 15 sekund",
      previewFourLabel: "Dane na żywo",
      previewFourValue: "status i statystyki",
      dashboardLabel: "Bieżąca sesja",
      refresh: "Odśwież teraz",
      logout: "Wyloguj",
      runtimeTitle: "Stan sesji",
      settingsTitle: "Ustawienia aplikacji",
    },
    footer: {
      text: "Minecraft Coach to aplikacja dla Windows, która dodaje krótkie przerwy edukacyjne do sesji Minecraft i zapewnia prosty widok rodzica.",
    },
    dynamic: {
      moduleCardLabel: "Pakiet nauki",
      moduleFallbackDescription: "Szczegółowy opis nie został jeszcze dodany, ale pakiet można już pobrać i używać w aplikacji.",
      moduleTopics: "Tematy: {count}",
      moduleLevels: "Poziomy: {count}",
      moduleDownload: "Pobierz pakiet",
      modulesEmptyTitle: "Pakiety nauki nie są jeszcze dostępne",
      modulesEmptyText: "Gdy pakiety pojawią się w katalogu <code>modules/</code>, zostaną pokazane tutaj automatycznie.",
      downloadReady: "Aktualny build dla Windows jest gotowy do pobrania.",
      downloadMissingMeta: "Build dla Windows nie jest teraz dostępny.",
      downloadMissingStatus: "Spróbuj ponownie później albo prześlij nowy build, aby przycisk pobierania znów był aktywny.",
      catalogErrorMeta: "Nie udało się wczytać katalogu pobierania.",
      catalogErrorStatus: "Błąd katalogu: {error}",
      catalogErrorTitle: "Pakiety nauki są teraz niedostępne",
      catalogErrorText: "Sprawdź, czy backend działa i czy trasa <code>/downloads/catalog</code> jest dostępna.",
      loginLoading: "Logowanie zakończone. Ładujemy dane sesji...",
      monitorOpenError: "Nie udało się otworzyć strony sesji: {error}",
      loginError: "Błąd logowania: {error}",
    },
  },
  it: {
    meta: {
      title: "Minecraft Coach - brevi pause educative in Minecraft",
      description:
        "Minecraft Coach è un'app per Windows che mette in pausa Minecraft a intervalli scelti, mostra una breve domanda o mini-lezione e permette ai genitori di controllare la sessione con ID programma e password.",
    },
    brand: {
      tagline: "Brevi pause educative durante il gioco.",
    },
    language: {
      label: "Lingua",
      selectAria: "Scegli la lingua del sito",
    },
    languagePrompt: {
      eyebrow: "Scelta della lingua",
      title: "In quale lingua vuoi leggere il sito?",
      text: "Puoi cambiarla più tardi dal menu in alto a destra. L'inglese è l'opzione predefinita.",
      continue: "Continua in inglese",
    },
    nav: {
      ariaLabel: "Navigazione principale",
      download: "Scarica",
      modules: "Pacchetti didattici",
      howItWorks: "Come funziona",
      monitoring: "Vista genitore",
      login: "Apri la vista genitore",
    },
    hero: {
      eyebrow: "Per brevi pause di studio",
      title: "Minecraft Coach mette Minecraft in pausa per un momento, mostra un breve compito e poi lascia continuare il gioco.",
      lead:
        "È un'app per Windows pensata per le famiglie che vogliono inserire brevi domande o mini-lezioni nel tempo di gioco. L'idea è semplice: una piccola pausa, un solo compito breve e ritorno al gioco.",
      primaryCta: "Scarica per Windows",
      secondaryCta: "Vedi come funziona",
      signalPauseLabel: "Pausa di gioco",
      signalPauseTitle: "Minecraft si ferma nel momento scelto",
      signalModulesLabel: "Compito breve",
      signalModulesTitle: "Compare una domanda o una mini-lezione",
      signalMonitoringLabel: "Vista genitore",
      signalMonitoringTitle: "I dati della sessione si possono controllare dopo",
      sceneAlt: "Interfaccia di Minecraft Coach con gioco in pausa e una breve domanda",
      overlay: {
        pauseTitle: "Pausa automatica",
        pauseLead: "si inserisce nel ritmo del gioco",
        pausedState: "In pausa",
        question: "Quanto fa 2 + 2?",
        ctaTitle: "È il momento di un compito breve",
        ctaBody: "Rispondi per continuare.",
      },
    },
    quick: {
      eyebrow: "Panoramica",
      title: "Cosa fa l'app",
      cardOneTitle: "Mette in pausa il gioco",
      cardOneText: "L'app ferma Minecraft in base all'intervallo impostato dall'adulto.",
      cardTwoTitle: "Mostra un solo compito breve",
      cardTwoText: "Il bambino vede una domanda breve o una mini-lezione invece di una lunga interruzione.",
      cardThreeTitle: "Salva i dati della sessione",
      cardThreeText: "L'app registra i progressi così da poterli controllare più tardi.",
    },
    download: {
      eyebrow: "Scarica",
      title: "Inizia con la versione attuale per Windows",
      lead: "Scarica prima l'app desktop. Se ci sono pacchetti didattici disponibili, puoi aggiungerli separatamente in seguito.",
      cardLabel: "App Windows",
      metaLoading: "Controllo della build in corso...",
      button: "Scarica .exe",
      statusWaiting: "Se il pulsante è inattivo, la build attuale non è stata ancora caricata.",
      sideOneTitle: "App desktop per Windows",
      sideOneText: "Il sito mostra la build corrente, la dimensione del file e l'orario di aggiornamento.",
      sideTwoTitle: "I pacchetti didattici sono opzionali",
      sideTwoText: "Puoi iniziare solo con l'app e aggiungere i pacchetti più tardi se ti servono argomenti già pronti.",
      sideThreeTitle: "La vista genitore usa l'ID del programma",
      sideThreeText: "La pagina della sessione si apre con l'ID del programma e la password genitore impostata nell'app.",
    },
    modules: {
      eyebrow: "Pacchetti didattici",
      title: "Aggiungi un pacchetto se vuoi argomenti e compiti già pronti",
      lead: "I pacchetti didattici vengono scaricati separatamente. Dopo il download, copiali nella cartella <code>modules</code> usata dall'app.",
    },
    how: {
      eyebrow: "Come funziona",
      title: "Come di solito lo usa una famiglia",
      stepOneTitle: "Installa l'app",
      stepOneText: "Scarica la versione per Windows e avvia il programma sul computer usato per Minecraft.",
      stepTwoTitle: "Scegli le impostazioni",
      stepTwoText: "Un adulto imposta l'intervallo delle pause, il numero di compiti e una password genitore.",
      stepThreeTitle: "Aggiungi pacchetti didattici se servono",
      stepThreeText: "Puoi usare pacchetti pronti oppure iniziare con una configurazione semplice usando solo l'app.",
      stepFourTitle: "Apri la vista genitore",
      stepFourText: "Con l'ID del programma e la password puoi aprire la pagina della sessione e vedere cosa succede durante il gioco.",
      whyLabel: "Da sapere",
      statusOneLabel: "L'app è pensata per Windows",
      statusOneValue: "uso su computer desktop",
      statusTwoLabel: "I compiti devono essere brevi",
      statusTwoValue: "un piccolo passo prima di tornare",
      statusThreeLabel: "I pacchetti didattici sono opzionali",
      statusThreeValue: "l'app può funzionare anche senza",
      statusFourLabel: "La vista genitore richiede ID e password",
      statusFourValue: "impostati dentro l'app",
    },
    monitor: {
      eyebrow: "Vista genitore",
      title: "I genitori possono aprire una pagina della sessione con ID programma e password",
      lead:
        "Inserisci l'<strong>ID del programma</strong> mostrato dall'app e la <strong>password genitore</strong> creata durante la configurazione. La pagina inizierà poi ad aggiornare automaticamente i dati della sessione.",
      form: {
        programIdLabel: "ID programma",
        programIdPlaceholder: "Per esempio AB12CD34",
        passwordLabel: "Password genitore",
        passwordPlaceholder: "Inserisci la password",
        submit: "Apri la pagina della sessione",
      },
      emptyLabel: "Pagina della sessione",
      emptyTitle: "Dopo l'accesso, questa pagina mostra lo stato corrente di una sessione attiva.",
      emptyText:
        "Può mostrare l'argomento attivo, le attività recenti, il numero di pause, le risposte, le monete e le principali impostazioni usate dall'app.",
      previewOneLabel: "ID programma",
      previewOneValue: "una sola sessione",
      previewTwoLabel: "Password genitore",
      previewTwoValue: "accesso privato",
      previewThreeLabel: "Aggiornamento automatico",
      previewThreeValue: "ogni 15 secondi",
      previewFourLabel: "Dati in tempo reale",
      previewFourValue: "stato e statistiche",
      dashboardLabel: "Sessione attuale",
      refresh: "Aggiorna ora",
      logout: "Esci",
      runtimeTitle: "Stato della sessione",
      settingsTitle: "Impostazioni dell'app",
    },
    footer: {
      text: "Minecraft Coach è un'app per Windows che aggiunge brevi pause educative alle sessioni di Minecraft e offre una semplice vista genitore.",
    },
    dynamic: {
      moduleCardLabel: "Pacchetto didattico",
      moduleFallbackDescription: "La descrizione dettagliata non è ancora disponibile, ma il pacchetto può già essere scaricato e usato nell'app.",
      moduleTopics: "Argomenti: {count}",
      moduleLevels: "Livelli: {count}",
      moduleDownload: "Scarica pacchetto",
      modulesEmptyTitle: "Nessun pacchetto didattico disponibile per ora",
      modulesEmptyText: "Quando i pacchetti verranno aggiunti al catalogo <code>modules/</code>, appariranno qui automaticamente.",
      downloadReady: "La build attuale per Windows è pronta per il download.",
      downloadMissingMeta: "La build per Windows non è disponibile in questo momento.",
      downloadMissingStatus: "Riprova più tardi oppure carica una nuova build per riattivare il pulsante di download.",
      catalogErrorMeta: "Impossibile caricare il catalogo dei download.",
      catalogErrorStatus: "Errore del catalogo: {error}",
      catalogErrorTitle: "I pacchetti didattici non sono disponibili in questo momento",
      catalogErrorText: "Controlla che il backend sia attivo e che la rotta <code>/downloads/catalog</code> sia disponibile.",
      loginLoading: "Accesso eseguito. Caricamento dei dati della sessione...",
      monitorOpenError: "Impossibile aprire la pagina della sessione: {error}",
      loginError: "Errore di accesso: {error}",
    },
  },
  de: {
    meta: {
      title: "Minecraft Coach - kurze Lernpausen in Minecraft",
      description:
        "Minecraft Coach ist eine Windows-App, die Minecraft in gewählten Abständen pausiert, eine kurze Frage oder Mini-Lektion zeigt und Eltern erlaubt, die Sitzung mit Programm-ID und Passwort anzusehen.",
    },
    brand: {
      tagline: "Kurze Lernpausen während des Spielens.",
    },
    language: {
      label: "Sprache",
      selectAria: "Seitensprache auswählen",
    },
    languagePrompt: {
      eyebrow: "Sprachauswahl",
      title: "In welcher Sprache möchtest du die Seite lesen?",
      text: "Du kannst die Sprache später über das Menü oben rechts ändern. Standardmäßig ist Englisch ausgewählt.",
      continue: "Auf Englisch fortfahren",
    },
    nav: {
      ariaLabel: "Hauptnavigation",
      download: "Download",
      modules: "Lernpakete",
      howItWorks: "So funktioniert es",
      monitoring: "Elternansicht",
      login: "Elternansicht öffnen",
    },
    hero: {
      eyebrow: "Für kurze Lernpausen",
      title: "Minecraft Coach pausiert Minecraft kurz, zeigt eine kleine Lernaufgabe und lässt das Kind danach weiterspielen.",
      lead:
        "Es ist eine Windows-App für Familien, die kurze Fragen oder Mini-Lektionen in die Spielzeit einbauen möchten. Die Idee ist einfach: kurz pausieren, eine kleine Aufgabe lösen und zurück ins Spiel.",
      primaryCta: "Für Windows herunterladen",
      secondaryCta: "So funktioniert es",
      signalPauseLabel: "Spielpause",
      signalPauseTitle: "Minecraft stoppt zum gewählten Zeitpunkt",
      signalModulesLabel: "Kurze Aufgabe",
      signalModulesTitle: "Eine Frage oder Mini-Lektion erscheint",
      signalMonitoringLabel: "Elternansicht",
      signalMonitoringTitle: "Sitzungsdaten lassen sich später prüfen",
      sceneAlt: "Minecraft-Coach-Oberfläche mit pausiertem Spiel und kurzer Frage",
      overlay: {
        pauseTitle: "Auto-Pause",
        pauseLead: "passt zum Spielrhythmus",
        pausedState: "Pausiert",
        question: "Wie viel ist 2 + 2?",
        ctaTitle: "Zeit für eine kurze Aufgabe",
        ctaBody: "Antworte, um fortzufahren.",
      },
    },
    quick: {
      eyebrow: "Überblick",
      title: "Was die App macht",
      cardOneTitle: "Pausiert das Spiel",
      cardOneText: "Die App stoppt Minecraft in dem Abstand, den der Erwachsene festlegt.",
      cardTwoTitle: "Zeigt eine kurze Aufgabe",
      cardTwoText: "Das Kind sieht eine kurze Frage oder Mini-Lektion statt einer langen Unterbrechung.",
      cardThreeTitle: "Speichert Sitzungsdaten",
      cardThreeText: "Die App speichert den Fortschritt, damit er später geprüft werden kann.",
    },
    download: {
      eyebrow: "Download",
      title: "Starte mit der aktuellen Windows-Version",
      lead: "Lade zuerst die Desktop-App herunter. Wenn Lernpakete verfügbar sind, kannst du sie später separat hinzufügen.",
      cardLabel: "Windows-App",
      metaLoading: "Aktuellen Build prüfen...",
      button: "Download .exe",
      statusWaiting: "Wenn die Schaltfläche inaktiv ist, wurde der aktuelle Build noch nicht hochgeladen.",
      sideOneTitle: "Desktop-App für Windows",
      sideOneText: "Die Website zeigt den aktuellen Build, die Dateigröße und die Aktualisierungszeit.",
      sideTwoTitle: "Lernpakete sind optional",
      sideTwoText: "Du kannst nur mit der App starten und später Pakete hinzufügen, wenn du fertige Themen brauchst.",
      sideThreeTitle: "Die Elternansicht nutzt eine Programm-ID",
      sideThreeText: "Die Sitzungsseite wird mit der Programm-ID und dem in der App gesetzten Elternpasswort geöffnet.",
    },
    modules: {
      eyebrow: "Lernpakete",
      title: "Füge ein Paket hinzu, wenn du fertige Themen und Aufgaben möchtest",
      lead: "Lernpakete werden separat heruntergeladen. Lege sie nach dem Download in den Ordner <code>modules</code>, den die App verwendet.",
    },
    how: {
      eyebrow: "So funktioniert es",
      title: "So nutzt eine Familie die App normalerweise",
      stepOneTitle: "App installieren",
      stepOneText: "Lade die Windows-Version herunter und starte das Programm auf dem Computer, auf dem Minecraft läuft.",
      stepTwoTitle: "Einstellungen wählen",
      stepTwoText: "Ein Erwachsener legt das Pausenintervall, die Anzahl der Aufgaben und ein Elternpasswort fest.",
      stepThreeTitle: "Bei Bedarf Lernpakete hinzufügen",
      stepThreeText: "Du kannst fertige Pakete nutzen oder mit einer einfachen Einrichtung nur mit der App beginnen.",
      stepFourTitle: "Elternansicht öffnen",
      stepFourText: "Mit Programm-ID und Passwort lässt sich die Sitzungsseite öffnen, um zu sehen, was während des Spiels passiert.",
      whyLabel: "Gut zu wissen",
      statusOneLabel: "Die App ist für Windows gedacht",
      statusOneValue: "für die Nutzung auf dem Desktop",
      statusTwoLabel: "Aufgaben sollen kurz sein",
      statusTwoValue: "ein kleiner Schritt vor der Rückkehr",
      statusThreeLabel: "Lernpakete sind optional",
      statusThreeValue: "die App funktioniert auch ohne sie",
      statusFourLabel: "Die Elternansicht braucht ID und Passwort",
      statusFourValue: "sie werden in der App festgelegt",
    },
    monitor: {
      eyebrow: "Elternansicht",
      title: "Eltern können eine Sitzungsseite mit Programm-ID und Passwort öffnen",
      lead:
        "Gib die <strong>Programm-ID</strong> aus der App und das <strong>Elternpasswort</strong> aus der Einrichtung ein. Danach aktualisiert die Seite die Sitzungsdaten automatisch.",
      form: {
        programIdLabel: "Programm-ID",
        programIdPlaceholder: "Zum Beispiel AB12CD34",
        passwordLabel: "Elternpasswort",
        passwordPlaceholder: "Passwort eingeben",
        submit: "Sitzungsseite öffnen",
      },
      emptyLabel: "Sitzungsseite",
      emptyTitle: "Nach dem Login zeigt diese Seite den aktuellen Stand einer aktiven Sitzung.",
      emptyText:
        "Sie kann das aktive Thema, letzte Aktivitäten, die Zahl der Pausen, Antworten, Münzen und die wichtigsten App-Einstellungen anzeigen.",
      previewOneLabel: "Programm-ID",
      previewOneValue: "nur eine Sitzung",
      previewTwoLabel: "Elternpasswort",
      previewTwoValue: "privater Zugriff",
      previewThreeLabel: "Auto-Aktualisierung",
      previewThreeValue: "alle 15 Sekunden",
      previewFourLabel: "Live-Daten",
      previewFourValue: "Status und Statistik",
      dashboardLabel: "Aktuelle Sitzung",
      refresh: "Jetzt aktualisieren",
      logout: "Abmelden",
      runtimeTitle: "Sitzungsstatus",
      settingsTitle: "App-Einstellungen",
    },
    footer: {
      text: "Minecraft Coach ist eine Windows-App, die kurze Lernpausen in Minecraft-Sitzungen einfügt und eine einfache Elternansicht bietet.",
    },
    dynamic: {
      moduleCardLabel: "Lernpaket",
      moduleFallbackDescription: "Eine ausführliche Beschreibung fehlt noch, aber das Paket kann bereits heruntergeladen und in der App verwendet werden.",
      moduleTopics: "Themen: {count}",
      moduleLevels: "Stufen: {count}",
      moduleDownload: "Paket herunterladen",
      modulesEmptyTitle: "Noch keine Lernpakete verfügbar",
      modulesEmptyText: "Sobald Pakete im Katalog <code>modules/</code> hinzugefügt werden, erscheinen sie hier automatisch.",
      downloadReady: "Der aktuelle Windows-Build steht zum Download bereit.",
      downloadMissingMeta: "Der Windows-Build ist im Moment nicht verfügbar.",
      downloadMissingStatus: "Bitte versuche es später erneut oder lade einen neuen Build hoch, damit die Download-Schaltfläche wieder aktiv wird.",
      catalogErrorMeta: "Der Download-Katalog konnte nicht geladen werden.",
      catalogErrorStatus: "Katalogfehler: {error}",
      catalogErrorTitle: "Lernpakete sind derzeit nicht verfügbar",
      catalogErrorText: "Prüfe bitte, ob das Backend läuft und die Route <code>/downloads/catalog</code> verfügbar ist.",
      loginLoading: "Anmeldung erfolgreich. Sitzungsdaten werden geladen...",
      monitorOpenError: "Die Sitzungsseite konnte nicht geöffnet werden: {error}",
      loginError: "Anmeldefehler: {error}",
    },
  },
  uk: {
    meta: {
      title: "Minecraft Coach - короткі навчальні паузи в Minecraft",
      description:
        "Minecraft Coach — це застосунок для Windows, який ставить Minecraft на паузу через вибрані інтервали, показує коротке запитання або міні-урок і дозволяє батькам переглядати сесію за ID програми та паролем.",
    },
    brand: {
      tagline: "Короткі навчальні паузи під час гри.",
    },
    language: {
      label: "Мова",
      selectAria: "Вибрати мову сайту",
    },
    languagePrompt: {
      eyebrow: "Вибір мови",
      title: "Якою мовою вам зручніше переглядати сайт?",
      text: "Пізніше мову можна змінити в меню праворуч угорі. За замовчуванням вибрано англійську.",
      continue: "Продовжити англійською",
    },
    nav: {
      ariaLabel: "Головна навігація",
      download: "Завантажити",
      modules: "Навчальні пакети",
      howItWorks: "Як це працює",
      monitoring: "Батьківський перегляд",
      login: "Відкрити батьківський перегляд",
    },
    hero: {
      eyebrow: "Для коротких навчальних пауз",
      title: "Minecraft Coach ненадовго ставить Minecraft на паузу, показує невелике навчальне завдання і потім повертає дитину до гри.",
      lead:
        "Це застосунок для Windows для сімей, які хочуть додати до ігрового часу короткі запитання або міні-уроки. Ідея проста: невелика пауза, одне коротке завдання і повернення до гри.",
      primaryCta: "Завантажити для Windows",
      secondaryCta: "Подивитися, як це працює",
      signalPauseLabel: "Пауза в грі",
      signalPauseTitle: "Minecraft зупиняється в обраний момент",
      signalModulesLabel: "Коротке завдання",
      signalModulesTitle: "З'являється запитання або міні-урок",
      signalMonitoringLabel: "Батьківський перегляд",
      signalMonitoringTitle: "Дані сесії можна переглянути пізніше",
      sceneAlt: "Інтерфейс Minecraft Coach із паузою гри та коротким запитанням",
      overlay: {
        pauseTitle: "Авто-пауза",
        pauseLead: "вбудовується в ритм гри",
        pausedState: "Пауза",
        question: "Скільки буде 2 + 2?",
        ctaTitle: "Час для короткого завдання",
        ctaBody: "Дайте відповідь, щоб продовжити.",
      },
    },
    quick: {
      eyebrow: "Огляд",
      title: "Що робить застосунок",
      cardOneTitle: "Ставить гру на паузу",
      cardOneText: "Застосунок зупиняє Minecraft через інтервал, який задає дорослий.",
      cardTwoTitle: "Показує одне коротке завдання",
      cardTwoText: "Дитина бачить коротке запитання або міні-урок замість довгого відволікання від гри.",
      cardThreeTitle: "Зберігає дані сесії",
      cardThreeText: "Застосунок зберігає прогрес, щоб його можна було переглянути пізніше.",
    },
    download: {
      eyebrow: "Завантажити",
      title: "Почніть з актуальної версії для Windows",
      lead: "Спочатку завантажте desktop-застосунок. Якщо доступні навчальні пакети, їх можна додати окремо пізніше.",
      cardLabel: "Застосунок для Windows",
      metaLoading: "Перевіряємо поточну збірку...",
      button: "Завантажити .exe",
      statusWaiting: "Якщо кнопка неактивна, актуальну збірку ще не завантажено.",
      sideOneTitle: "Desktop-застосунок для Windows",
      sideOneText: "Сайт показує поточну збірку, розмір файлу та час оновлення.",
      sideTwoTitle: "Навчальні пакети необов'язкові",
      sideTwoText: "Можна почати тільки із застосунку і додати пакети пізніше, якщо потрібні готові теми.",
      sideThreeTitle: "Батьківський перегляд працює через ID програми",
      sideThreeText: "Сторінка сесії відкривається за ID програми та батьківським паролем, який задається в застосунку.",
    },
    modules: {
      eyebrow: "Навчальні пакети",
      title: "Додайте пакет, якщо потрібні готові теми та завдання",
      lead: "Навчальні пакети завантажуються окремо. Після завантаження помістіть їх у папку <code>modules</code>, яку використовує застосунок.",
    },
    how: {
      eyebrow: "Як це працює",
      title: "Як зазвичай користуються застосунком",
      stepOneTitle: "Установіть застосунок",
      stepOneText: "Завантажте версію для Windows і запустіть програму на комп'ютері, де використовується Minecraft.",
      stepTwoTitle: "Виберіть налаштування",
      stepTwoText: "Дорослий задає інтервал пауз, кількість завдань і батьківський пароль.",
      stepThreeTitle: "Додайте навчальні пакети за потреби",
      stepThreeText: "Можна використовувати готові пакети або почати з простої конфігурації лише із застосунком.",
      stepFourTitle: "Відкрийте батьківський перегляд",
      stepFourText: "За ID програми та паролем можна відкрити сторінку сесії і подивитися, що відбувається під час гри.",
      whyLabel: "Що варто знати",
      statusOneLabel: "Застосунок розрахований на Windows",
      statusOneValue: "для роботи на настільному комп'ютері",
      statusTwoLabel: "Завдання мають бути короткими",
      statusTwoValue: "одна невелика дія перед поверненням",
      statusThreeLabel: "Навчальні пакети необов'язкові",
      statusThreeValue: "застосунок може працювати і без них",
      statusFourLabel: "Для батьківського перегляду потрібні ID та пароль",
      statusFourValue: "вони задаються в застосунку",
    },
    monitor: {
      eyebrow: "Батьківський перегляд",
      title: "Батьки можуть відкрити сторінку сесії за ID програми та паролем",
      lead:
        "Введіть <strong>ID програми</strong>, який показує застосунок, і <strong>батьківський пароль</strong>, створений під час налаштування. Після цього сторінка почне автоматично оновлювати дані сесії.",
      form: {
        programIdLabel: "ID програми",
        programIdPlaceholder: "Наприклад AB12CD34",
        passwordLabel: "Батьківський пароль",
        passwordPlaceholder: "Введіть пароль",
        submit: "Відкрити сторінку сесії",
      },
      emptyLabel: "Сторінка сесії",
      emptyTitle: "Після входу тут показується поточний стан однієї активної сесії.",
      emptyText:
        "Тут можуть відображатися активна тема, останні дії, кількість пауз, відповіді, монети та основні налаштування застосунку.",
      previewOneLabel: "ID програми",
      previewOneValue: "лише одна сесія",
      previewTwoLabel: "Батьківський пароль",
      previewTwoValue: "приватний доступ",
      previewThreeLabel: "Автооновлення",
      previewThreeValue: "кожні 15 секунд",
      previewFourLabel: "Живі дані",
      previewFourValue: "статус і статистика",
      dashboardLabel: "Поточна сесія",
      refresh: "Оновити зараз",
      logout: "Вийти",
      runtimeTitle: "Стан сесії",
      settingsTitle: "Налаштування застосунку",
    },
    footer: {
      text: "Minecraft Coach — це застосунок для Windows, який додає короткі навчальні паузи до сесій Minecraft і дає простий батьківський перегляд.",
    },
    dynamic: {
      moduleCardLabel: "Навчальний пакет",
      moduleFallbackDescription: "Детальний опис ще не додано, але пакет уже можна завантажити і використовувати в застосунку.",
      moduleTopics: "Тем: {count}",
      moduleLevels: "Рівнів: {count}",
      moduleDownload: "Завантажити пакет",
      modulesEmptyTitle: "Навчальні пакети поки недоступні",
      modulesEmptyText: "Коли пакети з'являться в каталозі <code>modules/</code>, вони автоматично відобразяться тут.",
      downloadReady: "Актуальна збірка для Windows готова до завантаження.",
      downloadMissingMeta: "Збірка для Windows зараз недоступна.",
      downloadMissingStatus: "Спробуйте пізніше або завантажте нову збірку, щоб кнопка знову стала активною.",
      catalogErrorMeta: "Не вдалося отримати каталог завантажень.",
      catalogErrorStatus: "Помилка каталогу: {error}",
      catalogErrorTitle: "Навчальні пакети зараз недоступні",
      catalogErrorText: "Перевірте, що backend запущений і маршрут <code>/downloads/catalog</code> доступний.",
      loginLoading: "Вхід виконано. Завантажуємо дані сесії...",
      monitorOpenError: "Не вдалося відкрити сторінку сесії: {error}",
      loginError: "Помилка входу: {error}",
    },
  },
};

function deepMergeTranslations(target, source) {
  Object.entries(source).forEach(([key, value]) => {
    if (value && typeof value === "object" && !Array.isArray(value)) {
      if (!target[key] || typeof target[key] !== "object" || Array.isArray(target[key])) {
        target[key] = {};
      }
      deepMergeTranslations(target[key], value);
      return;
    }

    target[key] = value;
  });

  return target;
}

Object.entries(translationOverrides).forEach(([language, override]) => {
  if (!translations[language]) {
    translations[language] = {};
  }
  deepMergeTranslations(translations[language], override);
});

let refreshTimer = null;
let lastDashboardPayload = null;
let loginMessageState = null;
let currentLanguage = resolveInitialLanguage();

function normalizeLanguage(language) {
  const code = String(language || "")
    .trim()
    .toLowerCase()
    .replace("_", "-")
    .split("-", 1)[0];

  return supportedLanguages.includes(code) ? code : defaultLanguage;
}

function resolveInitialLanguage() {
  const params = new URLSearchParams(window.location.search);
  const rawQueryLanguage = params.get("lang");
  const queryLanguage = normalizeLanguage(rawQueryLanguage);

  if (rawQueryLanguage && supportedLanguages.includes(queryLanguage)) {
    return queryLanguage;
  }

  const savedRaw = localStorage.getItem(languageStorageKey);
  if (savedRaw) {
    const saved = normalizeLanguage(savedRaw);
    if (supportedLanguages.includes(saved)) {
      return saved;
    }
  }

  return defaultLanguage;
}

function getLocale() {
  return languageLocales[currentLanguage] || languageLocales[defaultLanguage];
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => {
    const replacements = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return replacements[char] || char;
  });
}

function getNestedValue(object, path) {
  return String(path || "")
    .split(".")
    .reduce((current, segment) => (current && current[segment] !== undefined ? current[segment] : undefined), object);
}

function translate(key, replacements = {}, language = currentLanguage) {
  let value = getNestedValue(translations[language], key);
  if (value === undefined) {
    value = getNestedValue(translations[defaultLanguage], key);
  }
  if (typeof value !== "string") {
    return key;
  }

  return value.replace(/\{(\w+)\}/g, (_, token) => {
    const replacement = replacements[token];
    return replacement === undefined || replacement === null ? "" : String(replacement);
  });
}

function formatBytes(bytes) {
  const value = Number(bytes || 0);
  if (!value) return translate("dynamic.sizeUnknown");

  const units = ["B", "KB", "MB", "GB"];
  let current = value;
  let index = 0;

  while (current >= 1024 && index < units.length - 1) {
    current /= 1024;
    index += 1;
  }

  return `${current.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function formatTimestamp(timestamp) {
  if (!timestamp) return translate("dynamic.noData");

  const date = new Date(
    typeof timestamp === "number" && timestamp < 1000000000000 ? timestamp * 1000 : timestamp
  );

  if (Number.isNaN(date.getTime())) {
    return String(timestamp);
  }

  return new Intl.DateTimeFormat(getLocale(), {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function humanize(value, fallbackKey = "dynamic.noData") {
  if (value === null || value === undefined || value === "") {
    return translate(fallbackKey);
  }
  return String(value);
}

function humanizeBoolean(value, truthyKey, falsyKey, fallbackKey = "dynamic.noData") {
  if (value === true) return translate(truthyKey);
  if (value === false) return translate(falsyKey);
  return translate(fallbackKey);
}

function setButtonState(button, href, enabled) {
  if (!button) return;

  if (enabled) {
    button.href = href;
    button.classList.remove("is-disabled");
    return;
  }

  button.removeAttribute("href");
  button.classList.add("is-disabled");
}

function setSessionVisibility(isVisible) {
  const dashboard = document.getElementById("monitor-dashboard");
  const emptyState = document.getElementById("monitor-empty-state");

  if (dashboard) {
    dashboard.classList.toggle("hidden", !isVisible);
  }

  if (emptyState) {
    emptyState.classList.toggle("hidden", isVisible);
  }
}

function setLoginMessage(key = "", replacements = {}) {
  loginMessageState = key ? { key, replacements } : null;
  const message = document.getElementById("login-message");
  if (!message) return;
  message.textContent = key ? translate(key, replacements) : "";
}

function refreshLoginMessage() {
  if (!loginMessageState) {
    setLoginMessage();
    return;
  }
  setLoginMessage(loginMessageState.key, loginMessageState.replacements);
}

function createModuleCard(module) {
  const title = escapeHtml(module.title || module.slug || translate("dynamic.moduleCardLabel"));
  const slug = escapeHtml(module.slug || "");
  const description = escapeHtml(
    module.description || translate("dynamic.moduleFallbackDescription")
  );
  const topicCount = module.topic_count ?? 0;
  const levelCount = module.level_count ?? 0;
  const downloadUrl = escapeHtml(module.download_url || "#");

  return `
    <article class="module-card panel">
      <div class="module-card__header">
        <div>
          <div class="card-label">${escapeHtml(translate("dynamic.moduleCardLabel"))}</div>
          <h3>${title}</h3>
        </div>
        <span class="module-slug">${slug}</span>
      </div>
      <p>${description}</p>
      <div class="module-meta">
        <span class="meta-chip">${escapeHtml(translate("dynamic.moduleTopics", { count: topicCount }))}</span>
        <span class="meta-chip">${escapeHtml(translate("dynamic.moduleLevels", { count: levelCount }))}</span>
      </div>
      <a class="button button-outline" href="${downloadUrl}">${escapeHtml(translate("dynamic.moduleDownload"))}</a>
    </article>
  `;
}

function getCatalogUrl() {
  const query = new URLSearchParams({ lang: currentLanguage });
  return `${buildApiUrl("/downloads/catalog")}?${query.toString()}`;
}

async function loadCatalog() {
  const appMeta = document.getElementById("app-meta");
  const appTitle = document.getElementById("app-title");
  const appButton = document.getElementById("download-app-btn");
  const heroButton = document.getElementById("hero-download-btn");
  const status = document.getElementById("download-status");
  const modulesGrid = document.getElementById("modules-grid");

  if (!appMeta || !appTitle || !appButton || !heroButton || !status || !modulesGrid) {
    return;
  }

  try {
    const response = await fetch(getCatalogUrl(), {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const payload = await response.json();
    const appInfo = payload.app || {};
    appTitle.textContent = appInfo.title || translate("dynamic.appTitleDefault");

    if (appInfo.available) {
      const directUrl = appInfo.download_url || "/downloads/app/latest";
      appMeta.textContent = translate("dynamic.downloadMeta", {
        filename: appInfo.filename,
        size: formatBytes(appInfo.size_bytes),
        updatedAt: formatTimestamp(appInfo.updated_at),
      });
      status.textContent = translate("dynamic.downloadReady");
      setButtonState(appButton, directUrl, true);
      setButtonState(heroButton, directUrl, true);
    } else {
      appMeta.textContent = translate("dynamic.downloadMissingMeta");
      status.textContent = translate("dynamic.downloadMissingStatus");
      setButtonState(appButton, "", false);
      setButtonState(heroButton, "", false);
    }

    const modules = Array.isArray(payload.modules) ? payload.modules : [];

    if (!modules.length) {
      modulesGrid.innerHTML = `
        <article class="module-card panel">
          <div class="card-label">${escapeHtml(translate("modules.eyebrow"))}</div>
          <h3>${escapeHtml(translate("dynamic.modulesEmptyTitle"))}</h3>
          <p>${translate("dynamic.modulesEmptyText")}</p>
        </article>
      `;
      return;
    }

    modulesGrid.innerHTML = modules.map(createModuleCard).join("");
  } catch (error) {
    appMeta.textContent = translate("dynamic.catalogErrorMeta");
    status.textContent = translate("dynamic.catalogErrorStatus", {
      error: error instanceof Error ? error.message : String(error),
    });
    setButtonState(appButton, "", false);
    setButtonState(heroButton, "", false);
    modulesGrid.innerHTML = `
      <article class="module-card panel">
        <div class="card-label">${escapeHtml(translate("nav.modules"))}</div>
        <h3>${escapeHtml(translate("dynamic.catalogErrorTitle"))}</h3>
        <p>${translate("dynamic.catalogErrorText")}</p>
      </article>
    `;
  }
}

function renderStateList(target, rows) {
  if (!target) return;

  target.innerHTML = `
    <div class="state-list">
      ${rows
        .map(
          (row) => `
            <div class="state-row">
              <span>${escapeHtml(row.label)}</span>
              <strong>${escapeHtml(row.value)}</strong>
            </div>
          `
        )
        .join("")}
    </div>
  `;
}

function renderDashboard(payload) {
  const sessionTitle = document.getElementById("session-title");
  const sessionUpdated = document.getElementById("session-updated");
  const statsGrid = document.getElementById("stats-grid");
  const dashboard = payload.dashboard || {};
  const stats = dashboard.stats || {};
  const counts = dashboard.counts || {};
  const settings = dashboard.settings || {};
  const runtime = payload.runtime || {};

  lastDashboardPayload = payload;
  setSessionVisibility(true);

  if (sessionTitle) {
    sessionTitle.textContent = translate("dynamic.sessionTitle", {
      programId: payload.program_id || dashboard.program_id || "",
    }).trim();
  }

  if (sessionUpdated) {
    sessionUpdated.textContent = translate("dynamic.sessionUpdated", {
      updatedAt: formatTimestamp(payload.updated_at),
    });
  }

  if (statsGrid) {
    const statCards = [
      { label: translate("dynamic.stats.coins"), value: humanize(stats.coins, "dynamic.noData") },
      { label: translate("dynamic.stats.correct"), value: humanize(stats.correct, "dynamic.noData") },
      { label: translate("dynamic.stats.wrong"), value: humanize(stats.wrong, "dynamic.noData") },
      {
        label: translate("dynamic.stats.completedBreaks"),
        value: humanize(stats.completed_breaks, "dynamic.noData"),
      },
      { label: translate("dynamic.stats.topics"), value: humanize(counts.topics, "dynamic.noData") },
      { label: translate("dynamic.stats.tasks"), value: humanize(counts.tasks, "dynamic.noData") },
      {
        label: translate("dynamic.stats.childTopics"),
        value: humanize(counts.child_topics, "dynamic.noData"),
      },
      {
        label: translate("dynamic.stats.adultTopics"),
        value: humanize(counts.adult_topics, "dynamic.noData"),
      },
    ];

    statsGrid.innerHTML = statCards
      .map(
        (card) => `
          <article class="stat-card">
            <div>${escapeHtml(card.label)}</div>
            <strong>${escapeHtml(card.value)}</strong>
          </article>
        `
      )
      .join("");
  }

  renderStateList(document.getElementById("runtime-state"), [
    {
      label: translate("dynamic.runtime.currentModule"),
      value: humanize(runtime.current_module, "dynamic.runtime.notSelectedModule"),
    },
    {
      label: translate("dynamic.runtime.currentTopic"),
      value: humanize(runtime.current_topic, "dynamic.runtime.notSelectedTopic"),
    },
    {
      label: translate("dynamic.runtime.currentTask"),
      value: humanize(runtime.current_task, "dynamic.runtime.noActiveTask"),
    },
    {
      label: translate("dynamic.runtime.state"),
      value: humanize(runtime.state_label || runtime.state, "dynamic.runtime.unknown"),
    },
    {
      label: translate("dynamic.runtime.nextBreak"),
      value: humanize(runtime.remaining_break, "dynamic.runtime.noData"),
    },
    {
      label: translate("dynamic.runtime.manualPause"),
      value: humanizeBoolean(
        runtime.manual_pause,
        "dynamic.runtime.manualPauseActive",
        "dynamic.runtime.manualPauseInactive",
        "dynamic.runtime.noData"
      ),
    },
    {
      label: translate("dynamic.runtime.lastMode"),
      value: humanize(stats.last_mode, "dynamic.runtime.noData"),
    },
    {
      label: translate("dynamic.runtime.lastActivity"),
      value: humanize(stats.last_activity, "dynamic.runtime.noData"),
    },
  ]);

  renderStateList(document.getElementById("settings-state"), [
    {
      label: translate("dynamic.settings.programId"),
      value: humanize(payload.program_id || dashboard.program_id, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.windowLanguage"),
      value: humanize(settings.window_language, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.breakInterval"),
      value: `${humanize(settings.break_seconds, "dynamic.noData")} sec`,
    },
    {
      label: translate("dynamic.settings.tasksPerBreak"),
      value: humanize(settings.tasks_per_break, "dynamic.noData"),
    },
    {
      label: translate("dynamic.settings.lessonTime"),
      value: `${humanize(settings.lesson_seconds, "dynamic.noData")} sec`,
    },
    {
      label: translate("dynamic.settings.serverUrl"),
      value: humanize(settings.server_base_url, "dynamic.settings.notSet"),
    },
  ]);
}

function clearSessionState() {
  sessionStorage.removeItem(sessionStorageKey);
  lastDashboardPayload = null;
  setSessionVisibility(false);

  if (refreshTimer) {
    window.clearInterval(refreshTimer);
    refreshTimer = null;
  }
}

async function loadSessionDashboard() {
  const token = sessionStorage.getItem(sessionStorageKey);

  if (!token) {
    setSessionVisibility(false);
    return;
  }

  try {
    const response = await fetch(dashboardUrl, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      throw new Error(errorPayload.detail || `HTTP ${response.status}`);
    }

    const payload = await response.json();
    renderDashboard(payload);
    setLoginMessage();
  } catch (error) {
    clearSessionState();
    setLoginMessage("dynamic.monitorOpenError", {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

async function loginToSession(event) {
  event.preventDefault();

  const form = event.currentTarget;
  const body = {
    program_id: form.program_id.value.trim(),
    parent_password: form.parent_password.value,
  };

  setLoginMessage("dynamic.loginChecking");

  try {
    const response = await fetch(loginUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(body),
    });

    const payload = await response.json().catch(() => ({}));

    if (!response.ok || !payload.session_token) {
      throw new Error(payload.detail || payload.message || `HTTP ${response.status}`);
    }

    sessionStorage.setItem(sessionStorageKey, payload.session_token);
    setLoginMessage("dynamic.loginLoading");

    await loadSessionDashboard();

    if (refreshTimer) {
      window.clearInterval(refreshTimer);
    }

    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
    form.parent_password.value = "";
  } catch (error) {
    clearSessionState();
    setLoginMessage("dynamic.loginError", {
      error: error instanceof Error ? error.message : String(error),
    });
  }
}

function applyTranslations() {
  document.documentElement.lang = currentLanguage;
  document.documentElement.dataset.language = currentLanguage;
  if (document.body) {
    document.body.dataset.language = currentLanguage;
  }
  document.title = translate("meta.title");

  const metaDescription = document.querySelector('meta[name="description"]');
  if (metaDescription) {
    metaDescription.setAttribute("content", translate("meta.description"));
  }

  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = translate(element.dataset.i18n);
  });

  document.querySelectorAll("[data-i18n-html]").forEach((element) => {
    element.innerHTML = translate(element.dataset.i18nHtml);
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", translate(element.dataset.i18nPlaceholder));
  });

  document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => {
    element.setAttribute("aria-label", translate(element.dataset.i18nAriaLabel));
  });

  document.querySelectorAll("[data-i18n-alt]").forEach((element) => {
    element.setAttribute("alt", translate(element.dataset.i18nAlt));
  });

  updateLanguageControls();

  refreshLoginMessage();
}

function setLanguage(language, options = {}) {
  currentLanguage = normalizeLanguage(language);
  if (options.persist !== false) {
    localStorage.setItem(languageStorageKey, currentLanguage);
  }
  applyTranslations();

  if (options.reloadCatalog !== false) {
    loadCatalog();
  }

  if (lastDashboardPayload && options.rerenderDashboard !== false) {
    renderDashboard(lastDashboardPayload);
  }
}

function hasSavedLanguage() {
  const savedRaw = localStorage.getItem(languageStorageKey);
  return Boolean(savedRaw && supportedLanguages.includes(normalizeLanguage(savedRaw)));
}

function hasQueryLanguage() {
  const rawQueryLanguage = new URLSearchParams(window.location.search).get("lang");
  return Boolean(rawQueryLanguage && supportedLanguages.includes(normalizeLanguage(rawQueryLanguage)));
}

function shouldPromptForLanguageChoice() {
  return !hasQueryLanguage() && !hasSavedLanguage();
}

function updateLanguageControls() {
  const currentLabel = document.getElementById("language-current-label");
  if (currentLabel) {
    currentLabel.textContent = languageNames[currentLanguage] || languageNames[defaultLanguage];
  }

  document.querySelectorAll("[data-language-choice]").forEach((button) => {
    const isActive = button.dataset.languageChoice === currentLanguage;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-pressed", String(isActive));
  });
}

function closeLanguageMenu() {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  if (!trigger || !panel) return;

  panel.classList.add("hidden");
  trigger.setAttribute("aria-expanded", "false");
}

function toggleLanguageMenu(forceOpen) {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  if (!trigger || !panel) return;

  const shouldOpen = typeof forceOpen === "boolean" ? forceOpen : panel.classList.contains("hidden");
  panel.classList.toggle("hidden", !shouldOpen);
  trigger.setAttribute("aria-expanded", String(shouldOpen));
}

function showLanguagePrompt() {
  const modal = document.getElementById("language-modal");
  if (!modal) return;

  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  document.body.classList.add("modal-open");
}

function hideLanguagePrompt() {
  const modal = document.getElementById("language-modal");
  if (!modal) return;

  modal.classList.add("hidden");
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open");
}

function initLanguageControls() {
  const trigger = document.getElementById("language-trigger");
  const panel = document.getElementById("language-menu-panel");
  const modal = document.getElementById("language-modal");
  const modalDialog = modal?.querySelector(".language-modal__dialog");
  const continueButton = document.getElementById("language-modal-continue");

  updateLanguageControls();

  if (trigger) {
    trigger.addEventListener("click", (event) => {
      event.stopPropagation();
      toggleLanguageMenu();
    });
  }

  if (panel) {
    panel.addEventListener("click", (event) => {
      event.stopPropagation();
    });
  }

  if (modalDialog) {
    modalDialog.addEventListener("click", (event) => {
      event.stopPropagation();
    });
  }

  document.querySelectorAll("[data-language-choice]").forEach((button) => {
    button.addEventListener("click", () => {
      setLanguage(button.dataset.languageChoice);
      closeLanguageMenu();
      hideLanguagePrompt();
    });
  });

  if (continueButton) {
    continueButton.addEventListener("click", () => {
      setLanguage(defaultLanguage);
      hideLanguagePrompt();
    });
  }

  document.addEventListener("click", () => {
    closeLanguageMenu();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;

    closeLanguageMenu();
    if (modal && !modal.classList.contains("hidden")) {
      setLanguage(currentLanguage);
      hideLanguagePrompt();
    }
  });
}

function initRevealAnimations() {
  const items = document.querySelectorAll(".reveal");

  if (!items.length) {
    return;
  }

  if (!("IntersectionObserver" in window)) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    {
      threshold: 0.16,
      rootMargin: "0px 0px -8% 0px",
    }
  );

  items.forEach((item) => observer.observe(item));
}

function initHeaderState() {
  const header = document.querySelector(".site-header");

  if (!header) return;

  const sync = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 12);
  };

  sync();
  window.addEventListener("scroll", sync, { passive: true });
}

document.addEventListener("DOMContentLoaded", () => {
  const promptForLanguage = shouldPromptForLanguageChoice();

  setLanguage(currentLanguage, {
    reloadCatalog: false,
    rerenderDashboard: false,
    persist: !promptForLanguage,
  });

  initLanguageControls();
  if (promptForLanguage) {
    showLanguagePrompt();
  }
  initRevealAnimations();
  initHeaderState();
  loadCatalog();
  setSessionVisibility(false);

  const form = document.getElementById("monitor-login-form");
  const refreshButton = document.getElementById("refresh-session-btn");
  const logoutButton = document.getElementById("logout-session-btn");

  if (form) {
    form.addEventListener("submit", loginToSession);
  }

  if (refreshButton) {
    refreshButton.addEventListener("click", loadSessionDashboard);
  }

  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      clearSessionState();
      setLoginMessage("dynamic.sessionClosed");
    });
  }

  if (sessionStorage.getItem(sessionStorageKey)) {
    loadSessionDashboard();
    refreshTimer = window.setInterval(loadSessionDashboard, 15000);
  }
});
