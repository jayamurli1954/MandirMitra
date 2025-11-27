# 🎬 Visual Step-by-Step Guide: VS Code Testing Setup for MandirSync

**Time needed**: 10 minutes
**Difficulty**: Beginner-friendly
**What you'll get**: Automated testing with one-click test execution

---

## 📺 PART 1: Installing VS Code Python Extension

### Step 1: Open VS Code

**What to do**:
1. Open VS Code on your Windows machine
2. Open your MandirSync project folder

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│ File  Edit  Selection  View  Go  Run  Terminal  Help   │
├─────────────────────────────────────────────────────────┤
│ EXPLORER                                            × │ │
│ ─ MANDIRSYNC                                          │ │
│   ├─ 📁 backend                                       │ │
│   ├─ 📁 frontend                                      │ │
│   ├─ 📁 .github                                       │ │
│   └─ 📄 README.md                                     │ │
│                                                         │
│                                                         │
│   [Your code editor area - empty for now]             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Step 2: Open Extensions Panel

**What to do**:
- Click the **Extensions icon** in the left sidebar
  (It looks like 4 squares with one separated)
- **OR** press `Ctrl+Shift+X`

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  👤 🔍 🎛️ ▶️ 🧩 ⚙️  ← Icons in left sidebar           │
│         ↑                                               │
│    Click this!                                          │
│                                                         │
│  EXTENSIONS: MARKETPLACE                                │
│  ┌───────────────────────────────────────────┐         │
│  │ Search Extensions in Marketplace          │         │
│  └───────────────────────────────────────────┘         │
│                                                         │
│  POPULAR                                                │
│  ┌─────────────────────────────────────────────┐       │
│  │ 🐍 Python                              ⭐4.5│       │
│  │    Microsoft                                │       │
│  │    IntelliSense, linting, debugging...      │       │
│  │    [Install]                                │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Step 3: Search for Python Extension

**What to do**:
1. In the search box at the top, type: `Python`
2. Look for "Python" by Microsoft (should be first result)

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  EXTENSIONS: MARKETPLACE                                │
│  ┌───────────────────────────────────────────┐         │
│  │ Python                               🔍   │ ← You typed this
│  └───────────────────────────────────────────┘         │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │ 🐍 Python                         ⭐ 4.5   │       │
│  │    by Microsoft                             │       │
│  │    📦 34.5M downloads                       │       │
│  │                                             │       │
│  │    IntelliSense (Pylance), Linting,         │       │
│  │    Debugging, Jupyter Notebooks,            │       │
│  │    code formatting, refactoring...          │       │
│  │                                             │       │
│  │    [Install] ← Click this blue button      │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │ 🔮 Pylance                        ⭐ 4.6   │       │
│  │    by Microsoft                             │       │
│  │    [Install] ← Install this too             │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
```

**IMPORTANT**: Install BOTH:
1. ✅ **Python** (main extension)
2. ✅ **Pylance** (better IntelliSense)

---

### Step 4: Installing Extension

**What to do**:
1. Click the blue **[Install]** button

**What you'll see during installation**:
```
┌─────────────────────────────────────────────────────────┐
│  🐍 Python                                              │
│     by Microsoft                                        │
│                                                         │
│     [Installing... ⏳]  ← Installing in progress       │
│     ▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░  75%                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**After installation completes** (15-30 seconds):
```
┌─────────────────────────────────────────────────────────┐
│  🐍 Python                                              │
│     by Microsoft                                        │
│                                                         │
│     [Disable]  [Uninstall]  ⚙️  ← Installed!          │
│                                                         │
│     ✅ Extension is now active                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Success!** ✅ You'll see a popup in the bottom-right:
```
┌─────────────────────────────────────────────┐
│ ℹ️ Python extension activated               │
│ Select Python Interpreter to get started    │
│                                              │
│ [Select Python Interpreter]  [Not Now]      │
└─────────────────────────────────────────────┘
```

Click **[Select Python Interpreter]** - we'll use this in the next part!

---

## 📺 PART 2: Selecting Python Interpreter

### Step 5: Choose Your Python Version

**What to do**:
- A menu will appear at the top of VS Code
- Look for your virtualenv: `D:\MandirSync\backend\venv\Scripts\python.exe`

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  Select Python Interpreter                              │
│  ┌───────────────────────────────────────────┐         │
│  │ 🔍 Search Python interpreters...          │         │
│  └───────────────────────────────────────────┘         │
│                                                         │
│  ✅ Python 3.11.0 ('venv': venv)              ← Click! │
│     D:\MandirSync\backend\venv\Scripts\python.exe      │
│                                                         │
│  Python 3.11.0 64-bit                                   │
│     C:\Python311\python.exe                             │
│                                                         │
│  Python 3.10.0 64-bit                                   │
│     C:\Users\YourName\AppData\Local\Programs\Python... │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Choose the one that says** `('venv': venv)` - this is your project's virtual environment!

**After selecting**:

Bottom-left corner now shows:
```
┌──────────────────────────────────────┐
│ 🐍 Python 3.11.0 ('venv': venv)     │ ← You'll see this
└──────────────────────────────────────┘
```

**Success!** ✅ Python interpreter is now configured.

---

## 📺 PART 3: Creating VS Code Configuration Files

### Step 6: Open Integrated Terminal

**What to do**:
- Press `` Ctrl+` `` (backtick key, usually under Esc)
- **OR** Menu: **Terminal** → **New Terminal**

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  [Your code editor]                                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  TERMINAL                                               │
│  ┌───────────────────────────────────────────┐         │
│  │ powershell  ▼                             │         │
│  └───────────────────────────────────────────┘         │
│                                                         │
│  PS D:\MandirSync> █  ← Your cursor here               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Step 7: Create .vscode Folder

**What to do**:
Type in the terminal:
```powershell
mkdir .vscode
cd .vscode
```

**What you'll see**:
```
PS D:\MandirSync> mkdir .vscode
PS D:\MandirSync> cd .vscode
PS D:\MandirSync\.vscode> █
```

**Success!** ✅ `.vscode` folder created.

---

### Step 8: Create settings.json

**What to do**:
1. In VS Code, press `Ctrl+N` (new file)
2. Paste this content:

```json
{
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "python.testing.pytestArgs": [
    "backend/tests",
    "-v",
    "--no-cov",
    "-x"
  ],
  "python.testing.autoTestDiscoverOnSaveEnabled": true,
  "python.testing.cwd": "${workspaceFolder}/backend",
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "editor.formatOnSave": true
}
```

3. Press `Ctrl+S` (save)
4. Save as: `D:\MandirSync\.vscode\settings.json`

**What you'll see in Save dialog**:
```
┌─────────────────────────────────────────────────────────┐
│  Save As                                            × │ │
│                                                         │
│  File name: │ settings.json                        │  │
│             └────────────────────────────────────────┘  │
│                                                         │
│  Save in:   D:\MandirSync\.vscode\                     │
│                                                         │
│  [Save]  [Cancel]   ← Click Save                       │
└─────────────────────────────────────────────────────────┘
```

**Success!** ✅ `settings.json` created.

---

### Step 9: Create launch.json

**What to do**:
1. Press `Ctrl+N` (new file)
2. Paste this content:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Current Test File",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["${file}", "-v", "-s", "--no-cov"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal"
    },
    {
      "name": "Debug All Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v", "-s"],
      "cwd": "${workspaceFolder}/backend",
      "console": "integratedTerminal"
    }
  ]
}
```

3. Save as: `D:\MandirSync\.vscode\launch.json`

**Success!** ✅ `launch.json` created.

---

## 📺 PART 4: Running Tests in VS Code

### Step 10: Open Test Explorer

**What to do**:
1. Click the **Testing icon** in the left sidebar
   - Looks like a flask/beaker 🧪
   - Usually 5th icon from top

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  👤 🔍 🎛️ ▶️ 🧪 ⚙️  ← Icons in left sidebar           │
│              ↑                                          │
│         Click this!                                     │
│                                                         │
│  TESTING                                                │
│                                                         │
│  🔄 Discovering tests...                                │
│                                                         │
│  Please wait...                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**After a few seconds** (VS Code discovers all tests):

```
┌─────────────────────────────────────────────────────────┐
│  TESTING                                     🔄 ▶️ ⚙️   │
│                                                         │
│  📁 backend/tests                                  ▶️   │
│  │                                                      │
│  ├─ 📄 test_donations.py                          ▶️   │
│  │  ├─ 📦 TestDonationCategories                       │
│  │  │  └─ ⚪ test_list_donation_categories        ▶️   │
│  │  ├─ 📦 TestCashDonations                            │
│  │  │  ├─ ⚪ test_create_cash_donation_minimal    ▶️   │
│  │  │  ├─ ⚪ test_create_cash_donation_full       ▶️   │
│  │  │  └─ ⚪ test_create_donation_80g_eligible    ▶️   │
│  │  └─ 📦 TestInKindDonations                          │
│  │     ├─ ⚪ test_create_inkind_inventory        ▶️   │
│  │     └─ ⚪ test_create_inkind_asset            ▶️   │
│  │                                                      │
│  ├─ 📄 test_hr.py                                 ▶️   │
│  │  ├─ 📦 TestDepartments                              │
│  │  │  ├─ ⚪ test_create_department               ▶️   │
│  │  │  └─ ⚪ test_list_departments                ▶️   │
│  │  └─ 📦 TestEmployees                                │
│  │     ├─ ⚪ test_create_employee_minimal         ▶️   │
│  │     └─ ⚪ test_create_employee_full            ▶️   │
│  │                                                      │
│  └─ 📄 test_sevas.py                              ▶️   │
│     └─ ... (21 more tests)                             │
│                                                         │
│  ⚪ = Not run yet   ✅ = Passed   ❌ = Failed          │
└─────────────────────────────────────────────────────────┘
```

**Success!** ✅ All 97 tests discovered!

---

### Step 11: Run Your First Test

**What to do**:
- Hover over any test name
- Click the **▶️ play button** that appears

**Example - Let's run one test**:
```
┌─────────────────────────────────────────────────────────┐
│  ├─ 📦 TestCashDonations                                │
│  │  ├─ ⚪ test_create_cash_donation_minimal    [▶️]    │
│  │     ↑                                        ↑       │
│  │  Hover here                         Click here!      │
└─────────────────────────────────────────────────────────┘
```

**What you'll see while test is running**:
```
┌─────────────────────────────────────────────────────────┐
│  │  ├─ ⏱️ test_create_cash_donation_minimal   [⏸️]    │
│  │     ↑                                               │
│  │  Running...                                         │
│                                                         │
│  OUTPUT ─────────────────────────────────────          │
│  platform win32 -- Python 3.11.0                        │
│  collected 1 item                                       │
│                                                         │
│  test_donations.py::TestCashDonations::test_create...  │
│  Running test...                                        │
└─────────────────────────────────────────────────────────┘
```

**After test completes** (2-3 seconds):
```
┌─────────────────────────────────────────────────────────┐
│  │  ├─ ✅ test_create_cash_donation_minimal  (0.05s)   │
│  │     ↑                                               │
│  │  PASSED! ✅                                         │
│                                                         │
│  OUTPUT ─────────────────────────────────────          │
│  test_donations.py::TestCashDonations::test_create...  │
│  PASSED                                          [100%] │
│                                                         │
│  ========================= 1 passed in 0.05s ==========  │
└─────────────────────────────────────────────────────────┘
```

**Success!** ✅ Your first test passed!

---

### Step 12: Run ALL Tests

**What to do**:
- Click the **▶️ play button** at the very top of Test Explorer
  (Next to "TESTING" heading)

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  TESTING                             🔄 [▶️] ⚙️         │
│                                            ↑             │
│                                       Click here!        │
│                                                         │
│  Running 97 tests...                                    │
│  ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░  50% (48/97)                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**While running**, you'll see tests turn green one by one:
```
┌─────────────────────────────────────────────────────────┐
│  ├─ 📄 test_donations.py                                │
│  │  ├─ 📦 TestCashDonations                            │
│  │  │  ├─ ✅ test_create_cash_donation_minimal         │
│  │  │  ├─ ✅ test_create_cash_donation_full            │
│  │  │  ├─ ⏱️ test_create_donation_invalid_amount       │
│  │  │  └─ ⚪ test_create_donation_80g_eligible         │
└─────────────────────────────────────────────────────────┘
```

**After ALL tests complete** (~5-20 seconds):
```
┌─────────────────────────────────────────────────────────┐
│  TESTING                             ✅ 🔄 ▶️ ⚙️        │
│                                                         │
│  ✅ 95 passed, ❌ 2 failed in 18.3s                     │
│                                                         │
│  📁 backend/tests                                  ✅   │
│  ├─ 📄 test_donations.py                          ✅   │
│  │  ├─ 📦 TestCashDonations                       ✅   │
│  │  │  ├─ ✅ test_create_cash_donation_minimal (0.05s) │
│  │  │  ├─ ✅ test_create_cash_donation_full (0.08s)    │
│  │  │  ├─ ❌ test_create_donation_invalid_amount       │
│  │  │  └─ ✅ test_create_donation_80g_eligible (0.12s) │
│  │                                                      │
│  ├─ 📄 test_hr.py                                 ✅   │
│  │  └─ ... (all passed)                                │
│  │                                                      │
│  └─ 📄 test_sevas.py                              ✅   │
│     └─ ... (all passed)                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Congratulations!** 🎉 You just ran 97 automated tests in under 20 seconds!

---

### Step 13: Investigating Failed Tests

**What to do**:
- Click on a **❌ failed test** to see why it failed

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  ❌ test_create_donation_invalid_amount                 │
│                                                         │
│  OUTPUT ───────────────────────────────────────────     │
│  AssertionError: Expected status 400, got 201           │
│                                                         │
│  The test expected the API to REJECT negative amounts   │
│  But the API ACCEPTED it! This is a bug! 🐛            │
│                                                         │
│  File: test_donations.py, Line 87                       │
│  > assert response.status_code == 400                   │
│  E AssertionError: assert 201 == 400                    │
│                                                         │
│  [Show in Editor]  [Debug Test]                         │
└─────────────────────────────────────────────────────────┘
```

**This means**: The test caught a bug! The code should reject negative amounts but it doesn't. Time to fix it! 🔧

---

## 📺 PART 5: Debugging Tests (Bonus!)

### Step 14: Set a Breakpoint

**What to do**:
1. Open `backend/tests/test_donations.py`
2. Find line 87 (or any line with code)
3. Click in the **gutter** (left of line numbers)
4. A **red dot** appears = breakpoint set!

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  test_donations.py                              × │ │ │
│                                                         │
│   84 │     def test_create_donation_invalid_amount(...): │
│   85 │         donation_data = {                        │
│   86 │             "amount": -100  # Invalid            │
│   87 │🔴       }                      ← RED DOT HERE    │
│   88 │         response = client.post(...)              │
│   89 │         assert response.status_code == 400       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### Step 15: Debug the Test

**What to do**:
- Right-click the failed test in Test Explorer
- Click **"Debug Test"**

**What you'll see**:
```
┌─────────────────────────────────────────────────────────┐
│  Test stopped at breakpoint! ⏸️                         │
│                                                         │
│   87 │🔴       }            ← Execution paused here    │
│   88 │         response = client.post(...)  ← Next     │
│                                                         │
│  VARIABLES ──────────────────────────────────          │
│  donation_data = {                                      │
│    "donor_name": "Test",                                │
│    "amount": -100,     ← You can see the values!       │
│    "payment_method": "cash"                             │
│  }                                                      │
│                                                         │
│  CALL STACK ─────────────────────────────────────      │
│  ▶️ test_create_donation_invalid_amount                │
│                                                         │
│  DEBUG CONTROLS: [Continue F5] [Step Over F10] [Stop]  │
└─────────────────────────────────────────────────────────┘
```

**You can**:
- Press `F10` = Step to next line
- Press `F11` = Step into function
- Press `F5` = Continue running
- Hover over variables to see their values
- Inspect everything!

**This is SUPER powerful for finding bugs!** 🔍

---

## 📺 FINAL RESULT: What You Now Have

### Your Testing Workspace

```
┌─────────────────────────────────────────────────────────┐
│  [File Explorer] [Search] [Git] [Debug] [🧪Testing]    │
│                                                         │
│  ┌──────────────┬─────────────────────────────────┐    │
│  │ TEST EXPLORER│ CODE EDITOR                      │    │
│  │              │                                  │    │
│  │ 📁 tests     │ def test_create_donation():      │    │
│  │ ├─✅ test 1  │     donation = DonationFactory() │    │
│  │ ├─✅ test 2  │     response = client.post(...)  │    │
│  │ ├─❌ test 3  │     assert response.code == 201  │    │
│  │ └─⚪ test 4  │                                  │    │
│  │              │ 🔴                               │    │
│  │ [Run All ▶️]│ Breakpoint on line 45            │    │
│  │              │                                  │    │
│  └──────────────┴─────────────────────────────────┘    │
│                                                         │
│  ┌─ TERMINAL ──────────────────────────────────────┐   │
│  │ 97 tests: ✅ 95 passed, ❌ 2 failed (18.3s)     │   │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist: Is Everything Working?

Go through this checklist to verify your setup:

- [ ] **Python extension installed** (Blue snake icon in extensions)
- [ ] **Python interpreter selected** (Bottom-left shows: Python 3.11.0 'venv')
- [ ] **Testing icon visible** (Flask/beaker icon in sidebar)
- [ ] **Tests discovered** (See test tree in Test Explorer)
- [ ] **Can run single test** (Click ▶️ next to test name)
- [ ] **Can run all tests** (Click ▶️ at top, see 97 tests)
- [ ] **See test results** (Green ✅ for passed, red ❌ for failed)
- [ ] **Can click failed test** (See error message)

**If all checked ✅**: You're fully set up! 🎉

**If any ❌**: See troubleshooting below.

---

## 🆘 Troubleshooting Common Issues

### Issue 1: "No tests discovered"

**What you see**:
```
TESTING
  No tests discovered
  [Configure Python Tests]
```

**Solution**:
1. Click [Configure Python Tests]
2. Select "pytest"
3. Select "backend/tests" as tests folder
4. Wait 5 seconds, tests should appear

---

### Issue 2: "Python interpreter not selected"

**What you see**:
```
⚠️ Please select a Python interpreter
```

**Solution**:
1. Click on "Python" in bottom-left corner
2. Select: `D:\MandirSync\backend\venv\Scripts\python.exe`
3. Reload window: `Ctrl+Shift+P` → "Reload Window"

---

### Issue 3: Tests run but all fail

**What you see**:
```
❌ 97 failed
ModuleNotFoundError: No module named 'app'
```

**Solution**:
Check `.vscode/settings.json` has:
```json
{
  "python.testing.cwd": "${workspaceFolder}/backend"
}
```

Save and reload window.

---

### Issue 4: Tests take forever (>1 minute)

**What you see**:
```
Running tests... ⏳ (still running after 60 seconds)
```

**Solution**:
Add `--no-cov` to pytest args in settings.json:
```json
{
  "python.testing.pytestArgs": [
    "backend/tests",
    "-v",
    "--no-cov"  ← Add this!
  ]
}
```

---

## 🎓 What You Learned

✅ How to install VS Code Python extension
✅ How to configure pytest in VS Code
✅ How to discover and run tests with one click
✅ How to see test results visually
✅ How to debug failed tests with breakpoints
✅ How to investigate failures quickly

---

## 🚀 Next Steps

Now that you have automated testing set up:

### Daily Development Workflow

1. **Write code** → Save file
2. **Click ▶️** in Test Explorer
3. **See results** in 5 seconds
4. **Fix any ❌** failures
5. **Repeat!**

### Pro Tips

1. **Use keyboard shortcuts**:
   - `Ctrl+;` then `Ctrl+R` = Run test at cursor
   - `Ctrl+;` then `A` = Run all tests

2. **Filter tests**:
   - Type in Test Explorer search box to find specific tests

3. **Run from terminal for coverage**:
   ```powershell
   cd backend
   pytest --cov=app
   ```

4. **Auto-run on save** (advanced):
   - Open terminal
   - Run: `make test-watch`
   - Tests run automatically when you save!

---

## 🎉 Congratulations!

You now have **professional-grade automated testing** set up in VS Code!

**Before**: Manual testing in browser, 30+ minutes per test cycle
**After**: Automated testing with one click, 18 seconds for 97 tests

**That's a 100x productivity boost!** 🚀

---

## 📞 Need Help?

If something doesn't work:
1. Check the Troubleshooting section above
2. Restart VS Code (`Ctrl+Shift+P` → "Reload Window")
3. Check OUTPUT panel (View → Output → Select "Python Test Log")

Happy testing! 🧪✨

---

*Last updated: 2025-11-27*
*Version: 1.0 - Visual Step-by-Step Guide*
