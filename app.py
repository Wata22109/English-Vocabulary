import sys
import os
import pickle
import random
import PySide6.QtWidgets as Qw
import PySide6.QtCore as Qc

class WordApp(Qw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.words = {}

        self.load_data()

        self.setWindowTitle("English Vocabulary App")
        rect = Qc.QRect()
        rect.setSize(Qc.QSize(640,480))
        rect.moveTopLeft(Qc.QPoint(100,50))
        self.setGeometry(rect) 

        self.central_widget = Qw.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = Qw.QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        scroll_area = Qw.QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.words_widget = Qw.QWidget()
        self.words_layout = Qw.QVBoxLayout(self.words_widget)
        scroll_area.setWidget(self.words_widget)
        self.layout.addWidget(scroll_area)

        button_widget = Qw.QWidget()
        button_layout = Qw.QHBoxLayout(button_widget)

        self.add_word_button = Qw.QPushButton("単語の追加")
        self.add_word_button.clicked.connect(self.add_word_dialog)
        button_layout.addWidget(self.add_word_button)

        self.study_button = Qw.QPushButton("勉強")
        self.study_button.clicked.connect(self.study_words)
        button_layout.addWidget(self.study_button)

        self.random_quiz_button = Qw.QPushButton("ランダム出題")
        self.random_quiz_button.clicked.connect(self.random_quiz)  
        button_layout.addWidget(self.random_quiz_button)

        self.delete_word_button = Qw.QPushButton("単語の削除")
        self.delete_word_button.clicked.connect(self.delete_word_dialog)
        button_layout.addWidget(self.delete_word_button)

        self.layout.addWidget(button_widget)

        self.display_saved_words()

        self.quiz_word_label = Qw.QLabel()
        self.quiz_answer_label = Qw.QLabel()
        self.next_question_button = Qw.QPushButton("次の問題")
        self.next_question_button.clicked.connect(self.next_question)
        self.show_answer_button = Qw.QPushButton("答え")
        self.show_answer_button.clicked.connect(self.show_answer)

    def add_word_dialog(self):
        dialog = AddWordDialog()
        if dialog.exec_():
            word = dialog.word_edit.text()
            meaning = dialog.meaning_edit.text()
            example = dialog.example_edit.text()
            self.words[word] = {"意味": meaning, "例文": example}
            self.save_data()
            self.display_word(word, meaning, example)

    def study_words(self):
        for i in reversed(range(self.words_layout.count())):
            self.words_layout.itemAt(i).widget().setParent(None)

        for word, details in self.words.items():
            word_widget = WordWidget(word, details.get("意味", ""), details.get("例文", ""))
            self.words_layout.addWidget(word_widget)

    def random_quiz(self):
        if not self.words:
            Qw.QMessageBox.warning(self, "Error", "単語が存在しません。")
            return

        self.quiz_words = random.sample(list(self.words.items()), len(self.words))
        self.current_quiz_index = 0
        self.show_quiz()

    def show_quiz(self):
        if self.current_quiz_index < len(self.quiz_words):
            word, details = self.quiz_words[self.current_quiz_index]
            self.quiz_word_label.setText(word)
            self.quiz_answer_label.clear()
            self.layout.addWidget(self.quiz_word_label)
            self.layout.addWidget(self.show_answer_button)
            self.layout.addWidget(self.next_question_button)
        else:
            Qw.QMessageBox.information(self, "終了", "全ての単語が出題されました。")

    def show_answer(self):
        if self.current_quiz_index < len(self.quiz_words):
            word, details = self.quiz_words[self.current_quiz_index]
            self.quiz_answer_label.setText(f"意味: {details.get('意味', '')}\n例文: {details.get('例文', '')}")
            self.layout.addWidget(self.quiz_answer_label)
        else:
            Qw.QMessageBox.warning(self, "Error", "これ以上表示するものはありません。")

    def next_question(self):
        self.current_quiz_index += 1
        self.show_quiz()

    def delete_word_dialog(self):
        dialog = DeleteWordDialog(self.words.keys())
        if dialog.exec_():
            selected_word = dialog.selected_word
            if selected_word in self.words:
                del self.words[selected_word]
                self.save_data()
                self.display_saved_words()
                Qw.QMessageBox.information(self, "Success", "単語が削除されました。")
            else:
                Qw.QMessageBox.warning(self, "Error", "選択した単語は存在しません。")

    def save_data(self):
        with open("data.pkl", "wb") as f:
            pickle.dump(self.words, f)

    def load_data(self):
        if os.path.exists("data.pkl"):
            with open("data.pkl", "rb") as f:
                self.words = pickle.load(f)

    def display_saved_words(self):
        for i in reversed(range(self.words_layout.count())):
            self.words_layout.itemAt(i).widget().setParent(None)
        for word, details in self.words.items():
            word_widget = WordWidget(word, details.get("意味", ""), details.get("例文", ""))
            self.words_layout.addWidget(word_widget)

    def display_word(self, word, meaning, example):
        word_widget = WordWidget(word, meaning, example)
        self.words_layout.addWidget(word_widget)

class AddWordDialog(Qw.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Add Word")
        self.setGeometry(200, 200, 300, 200)

        self.layout = Qw.QVBoxLayout()
        self.setLayout(self.layout)

        self.word_edit = Qw.QLineEdit()
        self.layout.addWidget(Qw.QLabel("Word:"))
        self.layout.addWidget(self.word_edit)

        self.meaning_edit = Qw.QLineEdit()
        self.layout.addWidget(Qw.QLabel("意味:"))
        self.layout.addWidget(self.meaning_edit)

        self.example_edit = Qw.QLineEdit()
        self.layout.addWidget(Qw.QLabel("例文:"))
        self.layout.addWidget(self.example_edit)

        self.add_button = Qw.QPushButton("Add")
        self.add_button.clicked.connect(self.accept)
        self.layout.addWidget(self.add_button)

    def accept(self):
        if self.word_edit.text().strip() == "" or self.meaning_edit.text().strip() == "" or self.example_edit.text().strip() == "":
            Qw.QMessageBox.warning(self, "Error", "単語、意味、例文のそれぞれに一文字以上入力してください。")
        else:
            super().accept()

class DeleteWordDialog(Qw.QDialog):
    def __init__(self, word_list):
        super().__init__()

        self.setWindowTitle("Delete Word")
        self.setGeometry(200, 200, 300, 200)

        self.layout = Qw.QVBoxLayout()
        self.setLayout(self.layout)

        self.word_list = word_list

        self.word_combobox = Qw.QComboBox()
        self.word_combobox.addItems(self.word_list)
        self.layout.addWidget(Qw.QLabel("削除する単語を選んでください。"))
        self.layout.addWidget(self.word_combobox)

        self.delete_button = Qw.QPushButton("削除")
        self.delete_button.clicked.connect(self.delete_word)
        self.layout.addWidget(self.delete_button)

        self.selected_word = None

    def delete_word(self):
        self.selected_word = self.word_combobox.currentText()
        self.accept()

class WordWidget(Qw.QWidget):
    def __init__(self, word, meaning, example):
        super().__init__()

        self.word = word
        self.meaning = meaning
        self.example = example

        self.layout = Qw.QHBoxLayout()
        self.setLayout(self.layout)

        self.word_label = Qw.QLabel(word)
        self.layout.addWidget(self.word_label)

        self.answer_button = Qw.QPushButton("Answer")
        self.answer_button.clicked.connect(self.show_answer)
        self.layout.addWidget(self.answer_button)

        self.answer_label = Qw.QLabel("")
        self.answer_label.hide()
        self.layout.addWidget(self.answer_label)

        self.displayed = False

    def show_answer(self):
        if self.displayed:
            self.answer_label.hide()            
            self.displayed = False
        else:
            self.answer_label.setText(f"意味: {self.meaning}\n例文: {self.example}")
            self.answer_label.show()
            self.displayed = True            


if __name__ == "__main__":
    app = Qw.QApplication(sys.argv)
    window = WordApp()
    window.show()
    sys.exit(app.exec())
