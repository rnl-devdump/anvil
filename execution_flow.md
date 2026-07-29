# Anvil App Execution Flow

This document explains the lifecycle of the Anvil application from startup to UI rendering. If you are coming from Java, you can think of this as tracking the `public static void main(String[] args)` method and seeing how all the dependencies and UI panels are wired together.

## 1. The Entry Point (`src/app.py`)
When you run the application, Python executes `src/app.py` as the main script. 
At the very bottom of this file, you'll see this block:
```python
if __name__ == "__main__":
    app = App()
    app.mainloop()
```
* **Java Equivalent**: `public static void main(String[] args)`
* **What happens**: 
  1. It instantiates the `App` class (the main window).
  2. It calls `.mainloop()`, which hands control over to the operating system to start listening for mouse clicks and keyboard events. (Similar to how Java's Swing starts its Event Dispatch Thread).

## 2. Instantiating the Main Window (`App.__init__`)
When `app = App()` is called, the constructor (`__init__`) of the `App` class runs. `App` extends `ctk.CTk`, which means it is a window (like a `JFrame` in Java).

Inside the `App` constructor, two major phases occur:

### Phase A: Controller and Core Services Initialization
```python
self.controller = AppController(self)
```
Before building the UI, the App creates its "Brain" — the `AppController`.
When `AppController` is instantiated, it automatically acts as a factory, creating all the underlying core service instances:
1. `self.db = Db()`: Connects to the local SQLite database (Like a JDBC Connection Manager).
2. `self.file_service = File()`: Handles reading PDFs and text files.
3. `self.llm_service = LlmService()`: Connects to the local AI and vector database.
4. `self.quiz_store = QuizStore(self.db)`: The data access object (DAO) for saving/loading quizzes.

### Phase B: UI View Initialization
Once the controller and services are ready, the `App` creates the individual screens (like `JPanel`s):
1. `self.home_view = HomeView(..., controller=self.controller, ...)`
2. `self.quiz_view = QuizView(..., controller=self.controller, ...)`
3. `self.assistant_view = AssistantView(..., controller=self.controller, ...)`

Notice that when these views are created, they are passed a reference to `self.controller`. This allows the buttons inside the UI to trigger actions in the central controller (The **Model-View-Controller** or MVC pattern).

## 3. Rendering the First Screen
Still inside the `App.__init__` constructor, after creating all the views, it calls:
```python
self.show_home()
```
This method takes the `HomeView` and brings it to the front using `tkraise()` (which means "put this panel on top of the others"). 

## 4. The Event Loop (`app.mainloop()`)
At this point, the initialization is done. The code returns to the `if __name__ == "__main__":` block and hits `app.mainloop()`.
The application now waits indefinitely. When a user clicks "Quiz Me!" on the `HomeView`:
1. The button triggers its callback function.
2. The `App` class hides the Home screen and brings the `QuizView` to the front.
3. If the user asks a question, the `QuizView` calls `controller.ask()`, which routes to the `LlmService`, doing the heavy lifting in a background thread so the UI doesn't freeze.

---

### Summary of Instances Created (In Order)
1. **`App`** (The main window, acts like a JFrame)
2. **`AppController`** (The central logic coordinator, acts like a Presenter/Controller)
   - **`Db`** (Database)
   - **`File`** (File parser)
   - **`LlmService`** (AI engine)
   - **`QuizStore`** (Quiz repository DAO)
3. **`HomeView`** (UI Panel)
4. **`QuizView`** (UI Panel)
5. **`AssistantView`** (UI Panel)
