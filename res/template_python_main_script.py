from browser import document, html


parameters = (
##PARAMETERS##
)

version = parameters["version"]

stage_directions_labels = set(parameters["stage_directions"]["labels"])
main_character_labels = []
label2main = {}
for character in parameters["characters"]:
    main_label = character["labels"][0]
    main_character_labels.append(main_label)
    for label in character["labels"]:
            label2main[label] = main_label

n_scenes = len(parameters["scenes"])

raw_transcriptions = [
##RAW_TRANSCRIPTIONS##
]


def deepcopy(e):
    if isinstance(e, list):
        return [deepcopy(a) for a in e]
    elif isinstance(e, dict):
        return {deepcopy(k): deepcopy(v) for k, v in e.items()}
    else:
        return e


# inspired from https://stackoverflow.com/questions/3062746/special-simple-random-number-generator
seed = 0


def randint(n):
    global seed
    seed = (1103515245 * seed + 12345) % 2**31
    return seed % n


# Observer pattern implementation adapted from
# https://stackoverflow.com/questions/1904351/python-observer-pattern-examples-tips/1925836#1925836
# and https://stackoverflow.com/questions/6190468/how-to-trigger-function-on-value-change
class Observable:
    def __init__(self, value):
        self._old_value = None
        self._value = value
        self._callbacks = []

    @property
    def old_value(self):
        return self._old_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._old_value = self._value
        self._value = value
        self.fire()

    def subscribe(self, callback):
        self._callbacks.append(callback)

    def fire(self):
        for callback in self._callbacks:
            callback(self)


def create_question_panel(message, button_contents, callback):
    """
    Create a panel with:
    - a message
    - multiple buttons
    When a button is clicked, the panel is removed and the callback is called with the index of the clicked button.
    :param message: string
    :param button_contents: list of string
    :param callback: function (int) -> None
    :return: the panel.
    """
    panel = html.DIV()
    panel <= message
    panel <= html.HR()

    def get_question_button_action(panel, button_index, callback):
        def question_button_action(event):
            panel.remove()
            callback(button_index)

        return question_button_action

    for button_index, button_content in enumerate(button_contents):
        button = html.BUTTON(button_content)
        button.bind("click", get_question_button_action(panel, button_index, callback))
        panel <= button

    return panel


class MenuScreen:
    def __init__(self):
        self.action_observable = Observable(None)
        self.html_root = self.create_root()

    def get_html_component(self):
        return self.html_root

    def create_root(self):
        root = html.DIV()
        root <= html.DIV(html.B(f"Replicator - {parameters['play_name']} - ({version})")) + html.BR()
        root <= html.DIV(html.B("Faites un choix :")) + html.BR()

        menu_panel = html.TABLE(Id="menu_panel")
        buttons = html.TR()
        menu_panel <= buttons

        def get_button_action(action):
            def button_action(event):
                self.action_observable.value = action

            return button_action

        for action, action_pretty in zip(["read_scene", "learn_scene"], ["Lire une sc??ne", "Apprendre une sc??ne"]):
            button = html.BUTTON(action_pretty, Class="menu_button")
            button.bind("click", get_button_action(action))
            buttons <= html.TD(html.DIV(button))

        root <= menu_panel
        return root

    def remove_root(self):
        self.html_root.remove()


class ReadingSelectionScreen:
    def __init__(self, transcriptions):
        self.transcriptions = transcriptions
        self.scene_observable = Observable(None)

        self.html_root = self.create_root()

    def get_html_component(self):
        return self.html_root

    def create_root(self):
        root = html.DIV()
        root <= html.DIV(html.B(f"Replicator - {parameters['play_name']} - ({version})")) + html.BR()
        table = html.TABLE()
        table <= html.TR(html.TD("S??lectionner la sc??ne", Id="scene_sel_panel_title"))
        table <= html.TR(html.TD(self.create_scene_selection_panel(), Id="scene_sel_panel_td"))
        root <= table
        return root

    def remove_root(self):
        self.html_root.remove()

    def create_scene_selection_panel(self):
        scene_selection_panel = html.DIV()
        for i, scene in enumerate(parameters["scenes"]):
            if scene.get("missing", False):
                scene_selection_panel <= html.DIV(f"({scene['menu_name']} manquante)", Class="missing_scene")
            else:
                button = html.BUTTON(f"{scene['menu_name']}", Class="scene_button")

                def get_button_action(scene_id):
                    def button_action(event):
                        self.scene_observable.value = scene_id
                    return button_action

                button.bind("click", get_button_action(i))

                scene_selection_panel <= html.DIV(button)
        return scene_selection_panel


class SelectionScreen:
    def __init__(self, transcriptions):
        self.transcriptions = transcriptions
        self.character_observable = Observable(None)
        self.scene_observable = Observable(None)
        self.start_observable = Observable(False)

        self.html_root = self.create_root()

        self.character_observable.fire()
        self.scene_observable.fire()

    def get_html_component(self):
        return self.html_root

    def create_root(self):
        root = html.DIV()
        root <= html.DIV(html.B(f"Replicator - {parameters['play_name']} - ({version})")) + html.BR()
        table = html.TABLE()
        table <= html.TR(html.TD("1. S??lectionner le personnage", Id="char_sel_panel_title")
                        + html.TD("2. S??lectionner la sc??ne", Id="scene_sel_panel_title"))
        table <= html.TR(html.TD(self.create_character_selection_panel(), Id="char_sel_panel_td")
                        + html.TD(self.create_scene_selection_panel(), Id="scene_sel_panel_td"))
        root <= table
        root <= html.HR()
        root <= html.DIV("3. Jouer", Id="start_game_panel_title")
        root <= html.DIV(self.create_start_game_panel(), Id="start_game_panel")
        return root

    def remove_root(self):
        self.html_root.remove()

    def create_character_selection_panel(self):
        character_selection_panel = html.DIV(Id="char_sel")
        for character in main_character_labels:
            button = html.BUTTON(character, Class="char_button")

            def get_button_action(character):
                def button_action(event):
                    self.character_observable.value = character
                    self.scene_observable.value = None
                    # print(self.character_observable.value)
                return button_action

            button.bind("click", get_button_action(character))

            def get_character_callback(button, character):
                def callback(observable):
                    if character == observable.value:
                        if "char_button_selected" not in button.classList:
                            button.classList.add("char_button_selected")
                    else:
                        if "char_button_selected" in button.classList:
                            button.classList.remove("char_button_selected")
                return callback

            self.character_observable.subscribe(get_character_callback(button, character))

            character_selection_panel <= html.DIV(button)
        return character_selection_panel

    def create_scene_selection_panel(self):
        scene_selection_panel = html.DIV()
        for i, scene in enumerate(parameters["scenes"]):
            if scene.get("missing", False):
                scene_selection_panel <= html.DIV(f"({scene['menu_name']} manquante)", Class="missing_scene")
            else:
                button = html.BUTTON(f"{scene['menu_name']}", Class="scene_button")

                def get_button_action(scene_id):
                    def button_action(event):
                        self.scene_observable.value = scene_id
                    return button_action

                button.bind("click", get_button_action(i))

                def get_character_callback(button, scene_id):
                    def callback(observable):
                        if observable.value in self.transcriptions[scene_id]["characters"]:
                            if "disabled" in button.attrs:
                                del button.attrs["disabled"]
                        else:
                            button.attrs["disabled"] = None
                    return callback

                self.character_observable.subscribe(get_character_callback(button, i))

                def get_scene_callback(button, scene_id):
                    def callback(observable):
                        if scene_id == observable.value:
                            if "scene_button_selected" not in button.classList:
                                button.classList.add("scene_button_selected")
                        else:
                            if "scene_button_selected" in button.classList:
                                button.classList.remove("scene_button_selected")
                    return callback

                self.scene_observable.subscribe(get_scene_callback(button, i))

                scene_selection_panel <= html.DIV(button)
        return scene_selection_panel

    def create_start_game_panel(self):
        start_game_panel = html.DIV()

        button = html.BUTTON("Commencer !", Id="start_game_button")

        def button_action(event):
            self.start_observable.value = True

        button.bind("click", button_action)

        def get_scene_callback(button):
            def callback(observable):
                if observable.value is not None:
                    if "disabled" in button.attrs:
                        del button.attrs["disabled"]
                else:
                    button.attrs["disabled"] = None
            return callback

        self.scene_observable.subscribe(get_scene_callback(button))

        start_game_panel <= button

        return start_game_panel


def format_line(raw_line):
    div = html.DIV()
    while raw_line:
        if raw_line[0] == "(":
            end = raw_line.find(')')
            if end == -1:
                end = len(raw_line) - 1
            div <= html.EM(raw_line[:end + 1])
            raw_line = raw_line[end + 1:]
        else:
            begin = raw_line.find('(')
            if begin == -1:
                begin = len(raw_line)
            div <= html.SPAN(raw_line[:begin])
            raw_line = raw_line[begin:]
    return div


def remove_inline_stage_directions(line):
    clean_line_chunks = []
    while line:
        if line[0] == "(":
            end = line.find(")")
            if end == -1:
                len(line) - 1
            line = line[end + 1:]
        else:
            begin = line.find("(")
            if begin == -1:
                begin = len(line)
            clean_line_chunks.append(line[:begin])
            line = line[begin:]
    return "".join(clean_line_chunks)


class App:

    HISTORY_LENGTH = 4

    def __init__(self):
        self.selected_character = None
        self.selected_scene = None
        self.selected_blocs = None
        self.selected_bloc_lines = None
        self.sequential_progress = None
        self.base_line_scores = None
        self.base_line_score_resume = None
        self.total_line_scores = None
        self.final_line_scores = None
        self.final_line_score_resume = None

        self.transcriptions = []
        for scene_id, raw_transcription in enumerate(raw_transcriptions):
            blocs = []
            scene_characters = set()
            new_character = True
            for file_line in raw_transcription.split("\n"):
                file_line = file_line.strip()
                if not file_line:
                    new_character = True
                elif file_line[0] != "#":
                    if new_character:
                        line_characters = [
                            line_character
                            for w in remove_inline_stage_directions(file_line).split(",")
                            if (line_character := w.strip()) != ""]
                        blocs.append({"characters": line_characters, "lines": [], "characters_line": file_line})
                        if line_characters[0] not in stage_directions_labels:
                            scene_characters.update([label2main[char] for char in line_characters])
                        new_character = False
                    else:
                        blocs[-1]["lines"].append(file_line)

            self.transcriptions.append({
                "blocs": blocs,
                "characters": scene_characters
            })

        home_button = html.BUTTON("???", id="home_button")

        def home_button_action(event):
            self.start()

        home_button.bind("click", home_button_action)

        document <= home_button + html.DIV(id="main_div")

    def start(self):
        self.start_menu()

    def start_menu(self):
        menu_screen = MenuScreen()

        def start_observable_callback(observable):
            if observable.value is not None:
                menu_screen.remove_root()
                self.selected_action = menu_screen.action_observable.value
                assert self.selected_action in ["read_scene", "learn_scene"]
                if self.selected_action == "read_scene":
                    self.start_reading_scene()
                else:
                    self.start_selection()

        menu_screen.action_observable.subscribe(start_observable_callback)
        document["main_div"].clear()
        document["main_div"] <= menu_screen.get_html_component()

    def start_reading_scene(self):
        reading_selection_screen = ReadingSelectionScreen(self.transcriptions)

        def scene_observable_callback(observable):
            if observable.value is not None:
                reading_selection_screen.remove_root()

                self.selected_scene = reading_selection_screen.scene_observable.value
                self.selected_blocs = self.transcriptions[self.selected_scene]["blocs"]

                self.simple_reading()

        reading_selection_screen.scene_observable.subscribe(scene_observable_callback)
        document["main_div"].clear()
        document["main_div"] <= reading_selection_screen.get_html_component()

    def start_selection(self):
        selection_screen = SelectionScreen(self.transcriptions)

        def start_observable_callback(observable):
            if observable.value:
                selection_screen.remove_root()

                self.selected_character = selection_screen.character_observable.value
                self.selected_scene = selection_screen.scene_observable.value
                self.selected_blocs = self.transcriptions[self.selected_scene]["blocs"]

                self.selected_bloc_lines = [
                    (bloc_index, line_index)
                    for bloc_index, bloc in enumerate(self.selected_blocs)
                    if self.selected_character in [
                        label2main[char] for char in bloc["characters"] if char in label2main]
                    for line_index in range(len(bloc["lines"]))
                    if remove_inline_stage_directions(bloc["lines"][line_index]).strip() != ""
                ]

                self.base_evaluation_introduction()

        selection_screen.start_observable.subscribe(start_observable_callback)
        document["main_div"].clear()
        document["main_div"] <= selection_screen.get_html_component()

    def simple_reading(self):
        # construct text
        text = []
        bloc_index = len(self.selected_blocs) - 1
        line_index = len(self.selected_blocs[bloc_index]["lines"]) - 1
        while True:
            raw_line = self.selected_blocs[bloc_index]["lines"][line_index]
            div = format_line(raw_line)
            bloc_characters = self.selected_blocs[bloc_index]["characters"]
            if bloc_characters[0] in stage_directions_labels:
                div.classList.add("didascalie")
            text.insert(0, div)
            if line_index == 0:
                if bloc_characters[0] not in stage_directions_labels:
                    text.insert(0, html.DIV(format_line(self.selected_blocs[bloc_index]["characters_line"]),
                                            Class="character_in_text"))
                text.insert(0, html.BR())
            if line_index > 0:
                line_index -= 1
            else:
                if bloc_index > 0:
                    bloc_index -= 1
                    line_index = len(self.selected_blocs[bloc_index]["lines"]) - 1
                else:
                    break

        document["main_div"].clear()
        document["main_div"] <= text

    def base_evaluation_introduction(self):
        message = html.DIV("""\
            Le jeu commence d'abord en mode s??quentiel.
            Les r??pliques du personnage sont pr??sent??es dans l'ordre.""")
        button_contents = ["C'est parti !"]

        def callback(button_index):
            self.base_evaluation()

        document["main_div"].clear()
        document["main_div"] <= create_question_panel(message, button_contents, callback)

    def base_evaluation(self):
        def callback(line_scores):
            self.base_line_scores = line_scores
            self.total_line_scores = deepcopy(self.base_line_scores)
            self.set_random_seed()
            self.show_base_scores()
        self.evaluation(callback)

    def set_random_seed(self):
        global seed
        seed = 0
        for line_score in self.base_line_scores.values():
            seed *= 3
            seed += line_score["almost"] + 2*line_score["ko"]
            seed %= 2**31

    def evaluation(self, parent_callback, bloc_line_index=0, line_scores=None):
        if line_scores is None:
            line_scores = {line: {"perfect": 0, "almost": 0, "ko": 0} for line in self.selected_bloc_lines}
        if bloc_line_index < len(self.selected_bloc_lines):
            def callback(result):
                line_scores[self.selected_bloc_lines[bloc_line_index]][result] += 1
                self.evaluation(parent_callback, bloc_line_index=bloc_line_index+1, line_scores=line_scores)
            self.line_evaluation(callback, bloc_line_index)
        else:
            parent_callback(line_scores)

    def line_evaluation(self, parent_callback, bloc_line_index):
        # construct text
        text = []
        bloc_index, line_index = self.selected_bloc_lines[bloc_line_index]
        for back_count in range(self.HISTORY_LENGTH):
            raw_line = self.selected_blocs[bloc_index]["lines"][line_index]
            div = format_line(raw_line)
            div.classList.add(f"bloc_line_back_{back_count}")
            bloc_characters = self.selected_blocs[bloc_index]["characters"]
            if bloc_characters[0] in stage_directions_labels:
                div.classList.add("didascalie")
            text.insert(0, div)
            if line_index == 0 or back_count == self.HISTORY_LENGTH - 1:
                if bloc_characters[0] not in stage_directions_labels:
                    text.insert(0, html.DIV(format_line(self.selected_blocs[bloc_index]["characters_line"]),
                                            Class="character_in_text"))
                text.insert(0, html.BR())
            if line_index > 0:
                line_index -= 1
            else:
                if bloc_index > 0:
                    bloc_index -= 1
                    line_index = len(self.selected_blocs[bloc_index]["lines"]) - 1
                else:
                    break

        def autonote_callback(button_index):
            result = ["perfect", "almost", "ko"][button_index]
            if button_index == 0:
                parent_callback(result)
            else:
                text.extend([html.HR(), html.DIV("R??p??ter les phrases en couleur jusqu'?? les conna??tre par c??ur.")])
                button_contents = ["C'est fait."]
                document["main_div"].clear()
                document["main_div"] <= create_question_panel(text, button_contents, lambda i: parent_callback(result))

        def question_callback(button_index):
            text[-1].classList.remove("hidden")
            if button_index == 0:
                button_contents = ["J'ai tout bon ????", "Presque ????", "Pas bon ????"]
                document["main_div"].clear()
                document["main_div"] <= create_question_panel(text, button_contents, autonote_callback)
            else:
                autonote_callback(2)

        # question
        question_button_contents = ["Je me souviens de la suite et je l'ai r??cit??e.",
                                    "Je ne me souviens pas de la suite ????"]
        text[-1].classList.add("hidden")
        document["main_div"].clear()
        document["main_div"] <= create_question_panel(text, question_button_contents, question_callback)

    def show_base_scores(self):
        self.base_line_score_resume = {"perfect": 0, "almost": 0, "ko": 0}
        for v in self.base_line_scores.values():
            for k in self.base_line_score_resume:
                self.base_line_score_resume[k] += v[k]
        # print("show_base_scores")
        # print(self.base_line_scores)
        # print(self.base_line_score_resume)

        message = html.DIV()
        message <= html.DIV("Voici votre score de base :")
        message <= html.DIV(f"???? (Parfait !!!) : {self.base_line_score_resume['perfect']}")
        message <= html.DIV(f"????  (Presque !)  : {self.base_line_score_resume['almost']}")
        message <= html.DIV(f"????  (?? r??viser)  : {self.base_line_score_resume['ko']}")

        message <= html.BR() + html.DIV("Maintenant, le programme va vous soumettre des r??pliques dans un ordre "
                                        "al??atoire, en privil??giant celles posant difficult??s.")

        button_contents = [
            "Ok, c'est parti en mode al??atoire !",
            "Non, je pr??f??re recommencer en mode s??quentiel.",
            "Non, je veux revenir ?? l'??cran de s??lection."
        ]

        def callback(button_index):
            if button_index == 0:
                self.random_focus(0, None)
            elif button_index == 1:
                self.final_evaluation()
            else:
                self.start_selection()

        document["main_div"].clear()
        document["main_div"] <= create_question_panel(message, button_contents, callback)

    def random_focus(self, progress, last_bloc_line_index):
        progress += 1
        if progress == 2 * len(self.selected_bloc_lines):
            self.show_final_evaluation_message()
        else:
            # print("choosing random bloc line")
            # print(self.total_line_scores)
            # choose bloc line. Lexicographic order. Don't choose last bloc/line
            worst_score_tuple = (1000000000, 1000000000, 1000000000)
            worst_indexes = []
            for bloc_line_index, (bloc, line) in enumerate(self.selected_bloc_lines):
                if bloc_line_index == last_bloc_line_index:
                    continue
                score = self.total_line_scores[(bloc, line)]
                score_tuple = (score["perfect"], score["almost"], score["ko"])
                if score_tuple < worst_score_tuple:
                    worst_score_tuple = score_tuple
                    worst_indexes = []
                if score_tuple == worst_score_tuple:
                    worst_indexes.append(bloc_line_index)
            bloc_line_index = worst_indexes[randint(len(worst_indexes))]
            # print(self.selected_bloc_lines[bloc_line_index])

            def callback(result):
                self.total_line_scores[self.selected_bloc_lines[bloc_line_index]][result] += 1
                self.random_focus(progress, bloc_line_index)

            self.line_evaluation(callback, bloc_line_index)

    def show_final_evaluation_message(self):
        message = html.DIV()
        message <= html.DIV("On y est presque !")
        message <= html.BR()
        message <= html.DIV("La derni??re ??tape reprend le texte dans l'ordre pour remettre les choses en place "
                            "et ??valuer la progression.")

        button_contents = ["Allons-y ! [Alonzo]"]

        def callback(button_index):
            self.final_evaluation()

        document["main_div"].clear()
        document["main_div"] <= create_question_panel(message, button_contents, callback)

    def final_evaluation(self):
        def callback(line_scores):
            self.final_line_scores = line_scores
            for k, v in line_scores.items():
                for result in ["perfect", "almost", "ko"]:
                    self.total_line_scores[k][result] += v[result]
            self.show_final_scores()
        self.evaluation(callback)

    def show_final_scores(self):
        self.final_line_score_resume = {"perfect": 0, "almost": 0, "ko": 0}
        for v in self.final_line_scores.values():
            for k in self.final_line_score_resume:
                self.final_line_score_resume[k] += v[k]

        message = html.DIV()
        message <= html.DIV("Bravo ! Vous ??tes all?? jusqu'au bout !")
        message <= html.BR()
        message <= html.DIV("Voici votre progression :")
        message <= html.DIV(f"???? (Parfait !!!) : {self.base_line_score_resume['perfect']} => {self.final_line_score_resume['perfect']}")
        message <= html.DIV(f"????  (Presque !)  : {self.base_line_score_resume['almost']} => {self.final_line_score_resume['almost']}")
        message <= html.DIV(f"????  (?? r??viser)  : {self.base_line_score_resume['ko']} => {self.final_line_score_resume['ko']}")
        message <= html.BR()
        message <= html.DIV("Vous pouvez maintenant continuer ?? travailler sur cette sc??ne ou revenir ?? l'??cran de "
                            "s??lection.")

        button_contents = [
            "Continuer avec cette sc??ne en mode al??atoire",
            "Continuer avec cette sc??ne en mode s??quentiel",
            "Revenir ?? l'??cran de s??lection",
        ]

        def callback(button_index):
            if button_index == 0:
                self.random_focus(0, None)
            elif button_index == 1:
                self.final_evaluation()
            else:
                self.start_selection()

        document["main_div"].clear()
        document["main_div"] <= create_question_panel(message, button_contents, callback)


if __name__ == '__main__':
    app = App()
    app.start()
