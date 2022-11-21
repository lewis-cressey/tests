from browser import document, window
import traceback
import io
import random
from types import SimpleNamespace

page = SimpleNamespace()

class Question:
    instances = []

    @classmethod
    def instance(self):
        current_index = page.question_select.selectedIndex
        return self.instances[current_index]
    
    def __init__(self, title, html, use_turtle=False):
        qid = 1 + len(self.instances)
        self.name = f"q{qid}"
        self.title = title
        self.html = html
        self.use_turtle = use_turtle
        self.is_complete = False
        self.input_queue = []
        self.output_words = []

        self.option_element = document.createElement("option")
        page.question_select.append(self.option_element)
        self.instances.append(self)
        self.update_option()

    def update_option(self):
        if self.is_complete: checkbox = "☑ "
        else: checkbox = "☐ "
        self.option_element.textContent = f"{checkbox} {self.title}"

    def clear(self):
        self.input_queue.clear()
        self.output_words.clear()
    
    def reinit(self):
        pass

    def enqueue(self, *values):
        self.input_queue.extend(values)
        return self

    def input(self, prompt = "Enter data >"):
        if len(self.input_queue) > 0:
            result = self.input_queue.pop(0)
            page.terminal.innerHTML += f'<div class="input">{prompt} {result}</div>'
        else:
            result = ""
        return result

    def print(self, *args, **kwargs):
        result = io.StringIO()
        print(*args, file=result, **kwargs)
        result = result.getvalue()
        page.terminal.innerHTML += f'<div class="output">{result}</div>'
        self.output_words.extend(result.lower().split())
        return None

    def get_terminal(self):
        return " ".join(self.output_words)

    def get_turtle_history(self):
        history = window.turtle.getHistory().to_dict()
        return history["angles"], history["lengths"]

    def check_regular_polygon(self, num_sides):
        angles, lengths = self.get_turtle_history()
        
        if len(angles) != num_sides: return False
        angle = 360 / num_sides
        length = lengths[0]

        if length == 0: return False

        for i in range(1, num_sides):
            if angles[i] - angles[i - 1] != angle: return False
            if lengths[i] != length: return False

        return True

    def set_complete(self, value):
        self.is_complete = value
        self.update_option()
        return value

#############################################################################
## Questions                                                               ##
#############################################################################

class Question01(Question):
    def __init__(self):
        super().__init__("Simple printing", """
            <p>Print the text 'Hello world' on the screen.</p>
        """)

    def check(self):
        text = self.get_terminal()
        return self.set_complete("hello world" in text)

class Question02(Question):
    def __init__(self):
        super().__init__("Input and output", """
            <p>Ask for the user's name, then say hello to them by name.</p>
        """)

    def reinit(self):
        id = random.randint(1, 10000)
        self.name = f"Human {id}"
        self.enqueue(self.name)
                
    def check(self):
        result = self.get_terminal()
        print(result)
        return result == f"hello {self.name}".lower()

class Question03(Question):
    def __init__(self):
        super().__init__("Inputting numbers", """
            <p>Ask the user to enter two numbers. Then display the sum of the numbers.</p>
        """)

    def reinit(self):
        self.a = random.randint(1, 100)
        self.b = random.randint(1, 100)
        self.enqueue(self.a, self.b)
                
    def check(self):
        result = self.get_terminal()
        return int(result) == self.a + self.b

class Question04(Question):
    def __init__(self):
        super().__init__("Counting from zero", """
            <p>Print the numbers from 0 to 9 on the screen.</p>
        """)
        
    def check(self):
        values = [ int(word) for word in self.get_terminal().split() ]
        return values == list(range(10))

class Question05(Question):
    def __init__(self):
        super().__init__("Counting from 1", """
            <p>Print the numbers from 1 to 100 on the screen.</p>
        """)
        
    def check(self):
        values = [ int(word) for word in self.get_terminal().split() ]
        return values == list(range(1, 101))
              
class Question06(Question):
    def __init__(self):
        super().__init__("Counting in steps", """
            <p>Print all the numbers in the 7 times table from 7 to 700.</p>
        """)
        
    def check(self):
        values = [ int(word) for word in self.get_terminal().split() ]
        return values == list(range(7, 707, 7))

class Question07(Question):
    def __init__(self):
        super().__init__("Counting while omitting numbers", """
            <p>Print all numbers from 7 to 700 <b>except</b> for numbers which are divisible by 7.</p>
        """)
        
    def check(self):
        values = [ int(word) for word in self.get_terminal().split() ]
        return values == [ x for x in range(7, 701) if x % 7 != 0 ]
        
class Question08(Question):
    def __init__(self):
        super().__init__("Adding up numbers", """
            <p>Ask the user to enter 10 numbers. Then print the total of all 10 numbers.</p>
        """)
        
    def reinit(self):
        self.total = 0
        for count in range(10):
            value = random.randint(1, 30)
            self.total += value
            self.enqueue(value)
        
    def check(self):
        total = self.get_terminal()
        return int(total) == self.total

class Question09(Question):
    def __init__(self):
        super().__init__("Draw a square", """
            <p>Use the turtle to draw a square.</p>
        """, use_turtle = True)
        
    def check(self):
        return self.check_regular_polygon(4)

class Question10(Question):
    def __init__(self):
        super().__init__("Draw a hexagon", """
            <p>Use the turtle to draw a regular hexagon.</p>
        """, use_turtle = True)
        
    def check(self):
        return self.check_regular_polygon(6)
        
#############################################################################
## Other stuff                                                             ##
#############################################################################

class Turtle:
    def __init__(self, js_turtle):
        self.js_turtle = js_turtle
        js_turtle.reset()

    def left(self, degrees):
        self.js_turtle.turn(-degrees)

    def right(self, degrees):
        self.js_turtle.turn(degrees)

    def forward(self, length):
        self.js_turtle.move(length)

    def backward(self, length):
        self.js_turtle.move(-length)

def update_score():
    instances = Question.instances
    max_score = len(instances)
    score = 0
    for instance in instances:
        if instance.is_complete: score += 1
    document["score-text"].textContent = f"{score}/{max_score}"

def clear(event = None):
    question = Question.instance()
    text = window.localStorage.getItem(question.name)
    
    if text is not None: page.editor.session.setValue(text)
    else: page.editor.session.setValue("")
    
    page.question_text.innerHTML = Question.instance().html
    page.terminal.innerHTML = ""   
    page.canvas.classList.toggle("hidden", not question.use_turtle)
    hide_popup()
    update_score()

def show_popup(text):
    page.stderr.textContent = text
    page.popup_layer.setAttribute("class", "")

def hide_popup(*args):
    page.popup_layer.setAttribute("class", "hidden")

def run_program(*args):
    question = Question.instance()
    success = False
    text = page.editor.getValue()
    window.localStorage.setItem(question.name, text.strip())
    
    clear()
    question.clear()
    question.reinit()

    local_vars = {
        "input" : question.input,
        "print" : question.print,
        "turtle" : Turtle(window.turtle)
    }

    try:
        exec(text, globals(), dict(local_vars))
    except Exception as e:
        text = traceback.format_exc()
        show_popup(text)

    try:
        success = Question.instance().check()
    except Exception as e:
        print(e)

    if success:
        Question.instance().set_complete(True)
        update_score()
        show_popup("Congratulations! You have finished this question!")

def main():
    window.ace.config.set("basePath", "https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.13/")

    page.question_select = document["question-select"]
    page.question_text = document["question-text"]
    page.run_button = document["run-button"]    
    page.stderr = document["stderr"]
    page.popup_layer = document["popup-layer"]
    page.editor = window.ace.edit("editor")
    page.terminal = document["terminal"]
    page.canvas = document["turtle-canvas"]
   
    page.popup_layer.addEventListener("click", hide_popup)
    
    page.editor.setOptions({
        "mode": 'ace/mode/python',
    });

    page.question_select.bind("change", clear)
    page.run_button.bind("click", run_program)
    
    Question01()
    Question02()
    Question03()
    Question04()
    Question05()
    Question06()
    Question07()
    Question08()
    Question09()
    Question10()
    clear()

main()
