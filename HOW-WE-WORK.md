# HOW WE WORK — the EDEN harness build

### A step-by-step guide written for someone who has never built software before
*Written 12 Aug 2026. Keep this file open in a tab. Nothing in it assumes you know anything.*

---

## PART 0 · THE MAP — there are three "Claudes and computers", and confusing them is the #1 way this goes wrong

Read this part twice. Everything else makes sense once you have this picture.

| # | What it is | Where it lives | What it can do | What it CANNOT do |
|---|---|---|---|---|
| **1** | **Me** — this chat window | A Linux computer in Anthropic's cloud | Read every brief; write code; read and write files in your `Apart\` folder through a bridge | **Reach the OpenAI / DeepSeek APIs.** Blocked. I cannot run a single episode |
| **2** | **Your PC** — VS Code + its terminal | Your Razer, Windows | Run the code, reach the internet, hold your API keys | Nothing — this is where the real work happens |
| **3** | **The Claude Code extension** inside VS Code | Your Razer | Edit local files, explain code, small fixes | It has **not** read the briefs. It has no idea what EDEN is. It has a totally separate memory from me |

**The single most important consequence:** I write the code, **you run it.** I will never see a real model response unless you paste it back to me. That is not a limitation to work around — it is just the shape of the job, and it works fine.

**Rule of thumb for #3:** think of the VS Code extension as a helpful stranger who is very good at Python and knows nothing about your project. Use it for *"what does this line do?"* and *"fix this typo."* Use **me** for anything involving the protocol, the corpus, the measures, or the paper — I have all of that loaded.

**The one hard rule:** never have both of us editing the same file at the same time. Whoever is editing, the other one waits. If you ask the extension to change something I wrote, tell me afterwards so I don't overwrite it.

---

## PART 1 · ONE-TIME SETUP

Do this once. Budget 30 minutes, mostly waiting for downloads. If a step already works, skip it.

### Step 1.1 — Open the terminal in VS Code

The **terminal** is a text box where you type commands and the computer does them. It is not scary; it is just a chat window with your computer.

1. In VS Code, press **Ctrl + `** (that's the backtick key, top-left of your keyboard, under Escape).
2. A panel opens at the bottom. That's the terminal.
3. Look at the dropdown on the right of that panel. Make sure it says **PowerShell**. If it says something else, click the **+** dropdown arrow → **PowerShell**.

You will type things here and press Enter. That's the whole skill.

### Step 1.2 — Check whether Python is installed

Type this and press Enter:

```powershell
py --version
```

**Three things can happen:**

- It prints something like `Python 3.12.4` → **you're done, go to Step 1.4.**
- It says `py is not recognized` → try `python --version`. If that prints a version, use the word `python` everywhere below instead of `py`.
- A Microsoft Store window pops open → Python is **not** installed. Close the Store. Go to Step 1.3.

### Step 1.3 — Install Python (only if 1.2 failed)

1. Go to **python.org/downloads** and click the big yellow "Download Python 3.x" button.
2. Run the installer.
3. ⚠️ **On the very first screen, tick the box that says "Add python.exe to PATH".** It is at the bottom and it is easy to miss. If you miss it, nothing below will work and the error will be confusing.
4. Click "Install Now". Wait.
5. **Close VS Code completely and reopen it** (the terminal only notices new programs when it restarts).
6. Redo Step 1.2.

### Step 1.4 — Open the right folder in VS Code

In VS Code: **File → Open Folder…** and choose:

```
C:\Users\willi\Dropbox\NON-Academics\Job Applications\AI\Apart
```

VS Code will show the file tree on the left. You should see `Chatbot_EDA`, `Report`, `00_Sprint-Overview` and so on. If VS Code asks *"Do you trust the authors of the files in this folder?"* → **Yes, I trust the authors** (it's your own folder).

The harness will live in a new subfolder called **`eden-harness`**, which I have already created for you.

### Step 1.5 — Create the virtual environment

A **virtual environment** ("venv") is a private box of Python packages that belongs to this project only, so installing something here can't break anything else on your machine. It's a folder full of thousands of small files.

⚠️ **It must NOT go inside Dropbox.** Dropbox would try to sync thousands of tiny files, which is slow and can corrupt the environment. So we put it in your home folder instead.

Type this **exactly**, one line at a time:

```powershell
py -m venv C:\Users\willi\eden-venv
```

Wait ~20 seconds. Nothing will print. That's success — in a terminal, silence means it worked.

### Step 1.6 — Turn the environment on

```powershell
C:\Users\willi\eden-venv\Scripts\Activate.ps1
```

**If you get a red error containing the words "running scripts is disabled on this system"** — this is normal on Windows and is not your fault. Run this once, then run the activate line again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**How you know it worked:** your terminal prompt now starts with `(eden-venv)`. Like this:

```
(eden-venv) PS C:\Users\willi\Dropbox\...\Apart>
```

⚠️ **You must do Step 1.6 every time you open a new terminal.** Not the whole setup — just this one line. If a command ever fails with "no module named…", the first thing to check is whether `(eden-venv)` is showing.

### Step 1.7 — Install the packages we need

With `(eden-venv)` showing:

```powershell
pip install openai python-dotenv
```

Lots of text will scroll past. It ends with `Successfully installed…`. That's it.

*(`openai` is the library that talks to OpenAI — DeepSeek uses the same one, pointed at a different address, so this single package covers both subject families. `python-dotenv` is what reads your API keys out of a file.)*

### Step 1.8 — Put your API keys somewhere safe

You need two keys:

- **OpenAI** — platform.openai.com → left sidebar → API keys → "Create new secret key". Copy it immediately; it is shown once.
- **DeepSeek** — platform.deepseek.com → API keys → create. Same deal.

Both cost money per run, but this project is small — a 16-page packet is a few thousand words, and twelve episodes will land in the low single-digit dollars. Put ~$10 on each account and you will not run out.

Now, in VS Code:

1. Right-click the `eden-harness` folder in the left sidebar → **New File**.
2. Name it exactly **`.env`** — yes, starting with a dot, and with no name before the dot.
3. Paste this in, replacing the `sk-...` bits with your real keys:

```
OPENAI_API_KEY=sk-paste-your-real-openai-key-here
DEEPSEEK_API_KEY=sk-paste-your-real-deepseek-key-here
```

4. Save with **Ctrl + S**.

> **On privacy, plainly:** I have read access to that whole folder, so I *could* open `.env`. **I won't, and I never need to** — the code reads the keys at runtime on your machine, and I only ever need to see them if you paste them, which you should never do. If you'd rather they weren't in a file at all, tell me and I'll switch the code to read Windows environment variables instead.

**Setup is done.** You never do Part 1 again — only Step 1.6 (activate), once per terminal.

---

## PART 2 · THE LOOP — what we actually do, over and over

This is the whole job. Six steps, maybe twenty times a day, each cycle taking a few minutes.

```
   ┌─────────────────────────────────────────────────────────┐
   │                                                         │
   │   1. YOU ask for something, here in chat                │
   │              ↓                                          │
   │   2. I write the code in my cloud workspace             │
   │              ↓                                          │
   │   3. I push the files into your eden-harness folder     │
   │              ↓                                          │
   │   4. VS Code shows them appear (no refresh needed)      │
   │              ↓                                          │
   │   5. YOU run one command in the VS Code terminal        │
   │              ↓                                          │
   │   6. YOU paste what happened back to me                 │
   │              ↓                                          │
   │      it worked → next thing.   it broke → I fix it,     │
   │      and we're back at step 3.                          │
   │                                                         │
   └─────────────────────────────────────────────────────────┘
```

### On step 1 — how to ask

Plain English is correct. You do not need technical vocabulary. All of these are good asks:

- *"Build corpus.py."*
- *"The audit is firing on the wrong packet — it should aim at whatever the answer key says was decided wrong."*
- *"Make the episode stop after 6 packets instead of 8."*
- *"I don't understand what this file does. Walk me through it."*

If you can describe it to a colleague, you can ask me for it.

### On step 5 — how to run something

Every run has the same shape. Click into the terminal, and:

```powershell
cd "C:\Users\willi\Dropbox\NON-Academics\Job Applications\AI\Apart\eden-harness"
py run.py --model gpt-mock --arm no-partner
```

⚠️ **The quotation marks around the path are mandatory** — your folder path contains spaces ("Job Applications", "NON-Academics"), and without quotes Windows reads it as several separate commands and gives you a baffling error.

I will always tell you the exact command to paste. You never have to invent one.

### On step 6 — how to report back

This is the step that determines whether we move fast or slowly. **Paste the actual text, not a description of it.**

❌ *"it didn't work"* — I can't do anything with this.
✅ Select the last ~20 lines of the terminal, Ctrl+C, paste into chat.

Red text is not a disaster; it is information. The last line of a Python error is usually the useful one, but paste the whole block — the lines above it say where it happened.

**And when it *does* work, tell me that too**, with the output. "It printed 16 pages for packet 1" tells me the parser is right and I can move on.

---

## PART 3 · THE THREE COMMANDS YOU'LL ACTUALLY USE

Everything else I hand you individually. These three are yours to know by heart.

**Start of every work session** (two lines, always in this order):

```powershell
C:\Users\willi\eden-venv\Scripts\Activate.ps1
cd "C:\Users\willi\Dropbox\NON-Academics\Job Applications\AI\Apart\eden-harness"
```

**Stop something that's running away** (a run stuck in a loop, burning tokens):

> Press **Ctrl + C** in the terminal. Press it twice if once doesn't take.

**See what's in the folder right now:**

```powershell
ls
```

---

## PART 4 · WHAT "VIBE CODING" ACTUALLY MEANS HERE, AND THE FOUR RULES

Vibe coding means you direct and judge; I type. You are not going to read the Python line by line, and you don't need to. **But you are still the one responsible for whether it's right** — because you're the only one who knows what the experiment is supposed to measure.

So the division is:

- **You own:** what it should do, whether the output looks like the protocol, whether a number is plausible, what goes in the paper.
- **I own:** that the code does what you said, that it doesn't crash, that the log format is clean.

Four rules that keep this from going wrong:

**Rule 1 — Read the *output*, never the code.** When I hand you something, don't try to read the Python. Run it and look at what it prints and what lands in the log. If the log says the model read pages 1,2,3 and it should have been 1–16, that's a real bug and you found it without reading a line.

**Rule 2 — One change at a time.** If we change three things and the result gets worse, we don't know which one did it. Boring and slow beats clever and confused, especially with a Friday deadline.

**Rule 3 — Say "that's wrong" freely.** You caught two authoring errors in your own corpus with your own eyes, and two of your pilot subjects caught more. Same instinct applies to me. If output looks off, say so — being wrong out loud costs a minute; being wrong silently costs a run.

**Rule 4 — Nothing is precious.** Every file can be regenerated in seconds. If something gets into a mess, "delete it and rebuild" is a completely legitimate move and often the fastest one. The only irreplaceable things are your **corpus**, your **pilot transcripts**, and — once runs start — the **`results/` folder**. Those three, we never touch destructively.

---

## PART 5 · ERRORS YOU WILL DEFINITELY HIT, AND WHAT THEY MEAN

Every one of these has happened to everyone. None of them means anything is broken.

| What you see | What it means in English | What to do |
|---|---|---|
| `ModuleNotFoundError: No module named 'openai'` | The private package box isn't switched on | Run the activate line (Step 1.6). Check for `(eden-venv)` |
| `py : The term 'py' is not recognized` | Python isn't installed, or wasn't added to PATH | Redo Step 1.3, tick the PATH box |
| `running scripts is disabled on this system` | Windows' default security setting | Run the `Set-ExecutionPolicy` line in Step 1.6 |
| `FileNotFoundError: ... packet-1.txt` | The code is looking in the wrong place | Check you ran the `cd` line. Paste me the error; usually it's a path I got wrong |
| `KeyError: 'OPENAI_API_KEY'` | The `.env` file is missing, misnamed, or in the wrong folder | It must be called exactly `.env` and sit inside `eden-harness` |
| `RateLimitError` / `429` | You're calling the API faster than your account tier allows | Wait a minute. Tell me — I'll add a pause between calls |
| `InsufficientQuotaError` | No money on the account | Top up at the provider's billing page |
| Terminal just sits there doing nothing | Usually normal — it's waiting on the model, which can take 30+ seconds per turn | Give it a minute. If it's genuinely stuck, Ctrl+C and tell me |
| Red squiggly underlines in the VS Code editor | VS Code guessing about code style | **Ignore completely.** Only terminal errors are real |

---

## PART 6 · WHAT A GOOD DAY LOOKS LIKE

Concretely, mapped onto the sprint calendar in the handoff brief.

**Wednesday (today) — get one thing running end to end.**
The milestone is *not* a finished harness. It is: **one packet, parsed, served page by page to one real model, with a JSONL log you can open and read.** Everything after that is repetition. Expect the first working version to arrive in a couple of hours of back-and-forth, most of it small fixes.

**Thursday — make it a full episode, then a second arm.**
The scripted events at their fixed points, the waiver, the probes, the audit. Then run the same thing with Agent E removed — the no-partner baseline. Then `score.py`, which is mostly arithmetic against the answer key.

**Friday–Sunday — runs and analysis.**
By this point you are not coding; you are launching runs and reading logs. Twelve episodes, two model families, three seeds, two arms.

**A realistic expectation about the first hour:** the first version of anything usually fails on something dull — a path, a missing package, a Windows quirk. That is not a sign the plan is bad. Three or four dull failures in a row is a completely normal start, and each one takes about ninety seconds to fix.

---

## PART 7 · GLOSSARY

Plain-English definitions. No shame in coming back to this.

- **Terminal** — the text box where you type commands. Ctrl+` in VS Code.
- **Command** — one line you type and press Enter on.
- **Path** — a file's full address, like `C:\Users\willi\...\packet-1.txt`. Needs quotes if it has spaces.
- **Package / library** — someone else's pre-written code that you install and use. `openai` is a package.
- **`pip`** — the tool that installs packages.
- **Virtual environment (venv)** — a private box of packages for one project. Must be switched on each session.
- **Script / module** — one file of Python code, ending in `.py`.
- **Run** — executing a script: `py run.py`.
- **API** — how one program talks to another over the internet. Calling the OpenAI API = sending your text to their model and getting a reply.
- **API key** — your password for that. Secret. Never paste it into chat.
- **JSONL** — a text file with one record per line, each line a small structured chunk of data. Human-readable — you can open it in VS Code and read it. **This is where your experiment lives.**
- **Log** — in this project, the JSONL record of everything: every page requested, every decision, every scripted event, with round index and timestamp. The handoff brief's line *"the log is the experiment"* is literal.
- **Repo / repository** — the project folder, `eden-harness`.
- **Harness** — the whole program that runs an episode. The thing we're building.
- **Episode** — one condition × one model × one seed = one complete queue session in one conversation.
- **Arm / condition** — a variant of the setup you compare against another. We're building two: partner-present, and no-partner baseline.
- **Seed** — a number that makes a random process repeatable. Three seeds per cell = three runs of the same condition.
- **Mock model** — a fake subject I write that follows a fixed script instead of calling a real API. Lets us test the entire harness for free, offline, and deterministically, before spending a cent. We'll use one heavily on day one.

---

## PART 8 · WHAT I NEED FROM YOU BEFORE THE FIRST LINE OF CODE

Still open from your §9 list and from what I found reading the corpus:

1. **The R-7 naming call** (the corpus prints `Assigned Reviewer: R-7` on page 1 of every packet).
2. **Exact API model identifiers** — the precise strings, e.g. `gpt-...` and `deepseek-...`, from each provider's docs. These change often and I should not guess them.
3. **Temperature and seeds** — or say "use the defaults and log them," which is what the pilot did and is perfectly defensible.
4. **Where `prereg.md` gets posted**, since it has to be up before the first analysed run.
5. **Whether the discretionary battery makes the cut** (packets 7–10 after the waiver).

Answers to 1 and 2 unblock everything. The rest can be decided while I build.
