# Windows Setup, Testing and Submission Guide

## 1. Install the tools
1. **Python 3.11**: go to https://www.python.org/downloads/ and download Python 3.11.x. Run the installer and **tick "Add python.exe to PATH"** on the first screen, then click Install Now.
2. **VS Code**: download from https://code.visualstudio.com/ and install with the default options.
3. **Git**: download from https://git-scm.com/download/win and install with the default options.
4. Check: open Command Prompt and run `python --version` (should show 3.11.x) and `git --version`.

## 2. Create and open the project
1. Unzip `lending-api.zip` so you have a folder called `lending-api`.
2. In VS Code: **File > Open Folder...** and choose `lending-api`.
3. Open the terminal: **Terminal > New Terminal** (shortcut Ctrl + `). If it says PowerShell, you can switch to Command Prompt with the dropdown next to the + button.

## 3. Set up and run (each command explained)
| Command | What it does |
|---|---|
| `python -m venv venv` | Makes a private folder `venv` for this project's packages, so they don't mix with other projects. |
| `venv\Scripts\activate` | Switches your terminal to use that private folder. You will see `(venv)` at the start of the line. In PowerShell, if you see a "running scripts is disabled" error, first run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. |
| `pip install -r requirements.txt` | Installs the exact package versions listed in the file. |
| `python -m database.seed` | Creates the database and the three books. Safe to repeat. |
| `python -m uvicorn app.main:app --reload` | Starts the server. `--reload` restarts it when you edit code. Stop it with Ctrl + C. |
| `pytest -v` | Runs all automated tests and lists each one as PASSED or FAILED. Run it in a second terminal (or after stopping the server), with `(venv)` active. |

## 4. Test with Swagger UI
Open **http://127.0.0.1:8000/docs** in your browser. For each endpoint: click it, click **Try it out**, fill the fields, click **Execute**, and read the "Server response" (status code and body).

Follow the sequence in `docs/manual_test_examples.md` (it tells you what to enter and what you should expect). Start from a fresh database: stop the server, delete `lending.db`, run the seed command, start the server again.

## 5. Screenshot checklist
Use the Windows Snipping Tool (Windows key + Shift + S). Save in a folder `screenshots/` using these names (the same table is in `docs/evidence_log.md`; tick it off only for screenshots you really took).

| File | Open / run | Enter | Capture |
|---|---|---|---|
| `01_seed_output.png` | terminal | `python -m database.seed` | "Validation OK: 3 books, 6 physical copies." |
| `02_swagger_home.png` | /docs | - | the list of endpoints |
| `03_list_books_200.png` | GET /books/ | nothing | status 200 and 3 books |
| `04_search_python_200.png` | GET /books/ | search = `python` | status 200 and only B1 |
| `05_book_b1_200.png` | GET /books/{book_id} | `B1` | status 200 and B1 |
| `06_book_unknown_404.png` | GET /books/{book_id} | `B99` | status 404 and the message |
| `07_borrow_success_201.png` | POST /loans/ | `{"book_id":"B1","borrower_alias":"finch","checkout_day":3}` | 201, `due_day` 10 |
| `08_borrow_no_copies_409.png` | POST /loans/ | borrow `B2` with alias `wren`, then again with `lark` | 409 on the second call |
| `09_borrow_unknown_book_404.png` | POST /loans/ | book_id `B9` | 404 |
| `10_borrow_empty_alias_422.png` | POST /loans/ | borrower_alias `""` | 422 |
| `11_return_success_200.png` | POST /loans/{loan_id}/return | `1` | 200, `returned: true` |
| `12_return_twice_409.png` | same endpoint | `1` again | 409 |
| `13_overdue_due_day_empty.png` | GET /overdue/ | current_day `10` | 200 and `[]` (loan 2 is due on day 10) |
| `14_overdue_after_due_day.png` | GET /overdue/ | current_day `11` | loan 2 listed |
| `15_overdue_after_return_empty.png` | return loan 2, then GET /overdue/ | current_day `11` | `[]` |
| `16_pytest_results.png` | terminal | `pytest -v` | the full list and the summary line |
| `17_github_repo.png` | browser | - | your repository page |

## 6. Common errors
| Problem | Fix |
|---|---|
| `python` is not recognized | Reinstall Python and tick "Add python.exe to PATH", then open a new terminal. |
| Activation blocked in PowerShell | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or use Command Prompt. |
| `ModuleNotFoundError: No module named 'app'` or `'database'` | You are in the wrong folder. `cd` into `lending-api` (the folder containing `app`). |
| `No module named fastapi` | The venv is not active or packages are not installed: run `venv\Scripts\activate`, then `pip install -r requirements.txt`. |
| Port 8000 already in use | Stop the other server (Ctrl + C) or use `--port 8001`. |
| `database is locked` | Close any other program that has `lending.db` open, then retry. |
| Tests fail | Copy the full error text and ask for help; do not edit the tests to make them pass. |

## 7. GitHub submission
1. **Account**: go to https://github.com, click **Sign up**, and follow the steps (skip if you have one).
2. **New repository**: click **+ > New repository**. Name: `lending-api`. Description: `Library lending REST API built with FastAPI, SQLAlchemy and SQLite - availability and overdue status are calculated, never stored.` Choose **Public**. Do NOT tick "Add a README" (you already have one). Click **Create repository**.
3. **Upload with Git** (in the VS Code terminal, inside `lending-api`, replacing YOUR-USERNAME):
```
git init
git add .
git commit -m "Library lending API with tests and documentation"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/lending-api.git
git push -u origin main
```
   Git may ask you to sign in through the browser. The `.gitignore` already keeps `venv/`, `*.db` and `.env` out of the upload. Alternative without Git: on the repository page click **uploading an existing file** and drag in the project files (not the `venv` folder).
4. **Check**: refresh the repository page. You should see `app`, `database`, `tests`, `docs`, `README.md`, `requirements.txt` and the README displayed below the file list. Make sure there is no `venv` folder, no `.db` file and no `.env` file.
5. **Copy the URL**: copy it from the browser address bar (`https://github.com/YOUR-USERNAME/lending-api`).
6. **Submit** that link in the CareerSwami submission form, together with the screenshots and evidence log they ask for.

Never upload passwords, tokens or personal information. This project needs none.
